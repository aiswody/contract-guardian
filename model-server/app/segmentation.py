"""조항 세그멘테이션 — 특약 텍스트를 조항 단위로 분리 (rule-based, 스펙 §4.2).

분리 기준: 번호 매김(1. / 1) / ① / 제1조 / - / •) 우선, 그다음 줄바꿈,
마지막으로 문장 경계("~다." 뒤 공백). 분리 결과는 프론트에서 사용자가
병합/분리 수정할 수 있으므로 완벽할 필요는 없고 보수적으로 나눈다.
"""
import re

BULLET = re.compile(r"^\s*(제\s*\d+\s*[조항호]\s*[.)]?|\d+\s*[.)]|[①-⑳]|[-•▪*])\s*")
SENTENCE_END = re.compile(r"(?<=다\.)\s+")
MIN_LENGTH = 8  # 이보다 짧은 조각은 앞 조항의 잔여물로 간주


def segment(text: str) -> list[str]:
    """특약 텍스트를 조항 문장 리스트로 분리한다."""
    items: list[str] = []
    buf: list[str] = []

    def flush():
        if buf:
            merged = " ".join(buf).strip()
            if merged:
                items.append(merged)
            buf.clear()

    for line in text.splitlines():
        line = line.strip()
        if not line:
            flush()
            continue
        if BULLET.match(line):
            flush()
            buf.append(BULLET.sub("", line))
        else:
            buf.append(line)  # 번호 없는 줄은 이전 조항의 연속으로 본다
    flush()

    # 한 항목에 문장이 여러 개면 문장 경계로 추가 분리
    clauses: list[str] = []
    for item in items:
        clauses += [s.strip() for s in SENTENCE_END.split(item)]

    return [c for c in clauses if len(c) >= MIN_LENGTH]
