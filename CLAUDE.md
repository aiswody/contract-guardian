# 계약서 지킴이 (Contract Guardian)

사회초년생을 위한 전월세 계약서 특약 조항 AI 분석 웹 서비스.
전체 기획은 `docs/contract-guardian-spec.md`를 참고할 것. 스펙 문서가 이 프로젝트의 단일 진실 공급원(source of truth)이다.

## 작업 방식 (중요)

- 모든 응답은 **한국어**로 한다.
- 명령어를 실행하거나 제안할 때는 **왜 그 명령어를 쓰는지 이유를 함께 설명**한다.
- `main` 브랜치에 직접 커밋하지 않는다. 기능 단위로 `feature/<기능명>` 브랜치를 만들어 작업한다.
- 큰 작업은 단계를 나눠 진행하고, 각 단계 시작 전에 무엇을 할지 먼저 요약한다.
- 스펙 문서와 다른 방향으로 구현해야 할 상황이면, 먼저 이유를 설명하고 확인을 받는다.

## 프로젝트 구조 (목표)

```
contract-guardian/
├── web/                  # React (Vite) 프론트엔드 — Vercel 배포
├── model-server/         # FastAPI 모델 서버 — Docker, Cloud Run 배포
│   ├── app/              # API 라우터, 추론 파이프라인
│   └── models/           # 학습된 모델 아티팩트 (git 미포함, 용량 문제)
├── ml/                   # 데이터·학습 파이프라인
│   ├── data/             # 데이터셋 (원본 raw는 git 미포함)
│   ├── notebooks/        # 학습/평가 노트북
│   └── scripts/          # 학습·평가·재학습 스크립트
├── supabase/             # 마이그레이션 SQL, RLS 정책
└── docs/
    ├── contract-guardian-spec.md
    ├── labeling-guideline.md
    └── development_process.md
```

## 기술 스택

- **Frontend**: React 18 + Vite, PWA(vite-plugin-pwa), 모바일 퍼스트
- **Backend/DB**: Supabase (PostgreSQL, Auth, Storage, RLS, pgvector)
- **모델 서버**: FastAPI + Docker, HuggingFace transformers
- **ML**: KLUE-RoBERTa-base 파인튜닝 (위험도 3-class, 카테고리 7-class)
- **LLM**: 설명 생성 전용 (판별 금지 — 스펙 §2 설계 원칙 참조)
- **v2**: Capacitor로 iOS/Android 확장 예정 → hash 라우팅 금지, 브라우저 전용 API는 추상화 레이어를 거칠 것

## 핵심 설계 원칙 (스펙에서 발췌 — 항상 준수)

1. **판별은 학습 모델, 설명은 LLM.** LLM이 위험 여부를 판단하는 코드를 작성하지 않는다.
2. **False Negative 최소화.** 위험 조항을 정상으로 분류하는 것이 최악의 오류. confidence 임계값 미만은 `uncertain` 처리.
3. **OCR 결과는 사용자 교정을 거친 후에만 분석에 사용한다.**
4. **법률 자문 아님 고지**를 모든 결과 화면과 LLM 출력에 포함한다.
5. **개인정보 보호**: 계약서 이미지는 비공개 버킷, RLS로 소유자만 접근, 자동 삭제 옵션 제공.

## DB 스키마

스펙 문서 §7 참조. 테이블: `profiles`, `contracts`, `clauses`, `standard_clauses`, `missing_checks`, `feedback`.
마이그레이션은 `supabase/migrations/`에 SQL 파일로 관리한다.

## 자주 쓰는 명령어

```bash
# 프론트 개발 서버
cd web && npm run dev

# 모델 서버 로컬 실행
cd model-server && uvicorn app.main:app --reload

# Supabase 마이그레이션 적용
supabase db push
```

## 커밋 컨벤션

- `feat:` 기능 추가 / `fix:` 버그 수정 / `docs:` 문서 / `ml:` 데이터·모델 작업 / `chore:` 설정
- 커밋 메시지는 한국어로 작성한다.

## 현재 단계

로드맵 3주차: Baseline 2종 + KLUE-RoBERTa 파인튜닝, 평가 (스펙 §11 참조)
2주차 완료: dataset v1 — train 643(증강 483 포함) / val 34 / test 34 (`docs/development_process.md` 참조)
**test set은 학습·튜닝 전 과정에서 참조 금지** (스펙 §5.2 Step 4)
이 섹션은 주차가 넘어갈 때마다 갱신한다.
