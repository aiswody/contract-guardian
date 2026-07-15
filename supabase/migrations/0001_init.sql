-- 계약서 지킴이 초기 스키마 (스펙 §7)
-- 원칙: contracts/clauses/feedback은 본인 소유만, standard_clauses는 전체 읽기 전용.

create extension if not exists vector;

-- 사용자 프로필 (auth.users 1:1)
create table profiles (
  id uuid primary key references auth.users (id) on delete cascade,
  nickname text,
  created_at timestamptz not null default now()
);

-- 가입 시 프로필 자동 생성
create function public.handle_new_user()
returns trigger
language plpgsql security definer set search_path = public
as $$
begin
  insert into public.profiles (id, nickname)
  values (new.id, split_part(new.email, '@', 1));
  return new;
end;
$$;

create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function public.handle_new_user();

-- 계약서 분석 세션
create table contracts (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references profiles (id) on delete cascade,  -- nullable: 비로그인 체험(저장 안 함) 허용
  title text,
  contract_type text check (contract_type in ('jeonse', 'monthly')),
  image_paths text[],
  ocr_text text,
  status text not null default 'done'
    check (status in ('uploaded', 'analyzing', 'done', 'failed')),
  model_version text,
  created_at timestamptz not null default now()
);

-- 조항 분석 결과
create table clauses (
  id uuid primary key default gen_random_uuid(),
  contract_id uuid not null references contracts (id) on delete cascade,
  order_index int not null,
  text text not null,
  category text not null,
  risk_level text not null
    check (risk_level in ('safe', 'caution', 'danger', 'uncertain')),
  confidence float,
  reason text,
  explanation text,
  suggestion text
);

-- 필수 조항 마스터 (쓰기는 service role만)
create table standard_clauses (
  id uuid primary key default gen_random_uuid(),
  name text not null unique,
  description text,
  recommended_text text,
  embedding vector(768)
);

-- 누락 탐지 결과
create table missing_checks (
  contract_id uuid not null references contracts (id) on delete cascade,
  standard_clause_id uuid not null references standard_clauses (id) on delete cascade,
  is_present boolean not null,
  similarity float,
  primary key (contract_id, standard_clause_id)
);

-- 판정 피드백 (재학습 데이터원, 스펙 §5.5)
create table feedback (
  id uuid primary key default gen_random_uuid(),
  clause_id uuid not null references clauses (id) on delete cascade,
  user_id uuid references profiles (id) on delete set null,
  verdict text not null check (verdict in ('helpful', 'wrong')),
  comment text,
  created_at timestamptz not null default now()
);

create index idx_contracts_user on contracts (user_id, created_at desc);
create index idx_clauses_contract on clauses (contract_id, order_index);
create index idx_feedback_clause on feedback (clause_id);

-- ===== RLS =====
alter table profiles enable row level security;
alter table contracts enable row level security;
alter table clauses enable row level security;
alter table standard_clauses enable row level security;
alter table missing_checks enable row level security;
alter table feedback enable row level security;

create policy "본인 프로필 조회" on profiles
  for select using (auth.uid() = id);
create policy "본인 프로필 수정" on profiles
  for update using (auth.uid() = id);

create policy "본인 계약서 조회" on contracts
  for select using (auth.uid() = user_id);
create policy "본인 계약서 생성" on contracts
  for insert with check (auth.uid() = user_id);
create policy "본인 계약서 삭제" on contracts
  for delete using (auth.uid() = user_id);

create policy "본인 조항 조회" on clauses
  for select using (
    exists (select 1 from contracts c where c.id = contract_id and c.user_id = auth.uid()));
create policy "본인 조항 생성" on clauses
  for insert with check (
    exists (select 1 from contracts c where c.id = contract_id and c.user_id = auth.uid()));

create policy "필수 조항 전체 읽기" on standard_clauses
  for select using (true);
-- standard_clauses 쓰기 정책 없음 = service role만 가능

create policy "본인 누락 결과 조회" on missing_checks
  for select using (
    exists (select 1 from contracts c where c.id = contract_id and c.user_id = auth.uid()));
create policy "본인 누락 결과 생성" on missing_checks
  for insert with check (
    exists (select 1 from contracts c where c.id = contract_id and c.user_id = auth.uid()));

create policy "본인 피드백 생성" on feedback
  for insert with check (auth.uid() = user_id);
create policy "본인 피드백 조회" on feedback
  for select using (auth.uid() = user_id);
