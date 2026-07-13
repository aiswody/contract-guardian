"""누락 조항 탐지 — 문장 임베딩 유사도 매칭 (스펙 §4.4).

분류가 아니라 "존재 여부" 문제이므로 검색(유사도 매칭)으로 푼다 (스펙 §10).
필수 조항의 대표 문형(match_texts)들과 계약서 조항들의 코사인 유사도를 재고,
최고 유사도가 threshold 미만이면 "누락 가능성"으로 표시한다.

임베딩: jhgan/ko-sroberta-multitask (한국어 문장 유사도 특화, 무료 공개, CPU 추론).
"""
import os

from sentence_transformers import SentenceTransformer, util

from .standard_clauses import STANDARD_CLAUSES

EMBED_MODEL = os.environ.get("EMBED_MODEL", "jhgan/ko-sroberta-multitask")
# 0.70 근거(실측): 무관 조항의 가짜 매칭 최대 0.647 / 패러프레이즈 진짜 매칭 대부분 0.69+.
# 누락 탐지의 최악 오류는 "없는데 있다고 안심"이므로 높은 쪽을 택한다 — 애매하면 누락 가능성으로.
SIM_THRESHOLD = float(os.environ.get("MISSING_SIM_THRESHOLD", "0.7"))


class MissingDetector:
    def __init__(self):
        self.model = SentenceTransformer(EMBED_MODEL)
        # 필수 조항 대표 문형들을 기동 시 1회 임베딩
        self._refs = []
        for std in STANDARD_CLAUSES:
            emb = self.model.encode(std["match_texts"], convert_to_tensor=True,
                                    normalize_embeddings=True)
            self._refs.append((std, emb))

    def detect(self, clause_texts: list[str]) -> list[dict]:
        if not clause_texts:
            return [self._entry(std, False, 0.0) for std, _ in self._refs]
        clause_emb = self.model.encode(clause_texts, convert_to_tensor=True,
                                       normalize_embeddings=True)
        results = []
        for std, ref_emb in self._refs:
            sim = float(util.cos_sim(ref_emb, clause_emb).max())
            results.append(self._entry(std, sim >= SIM_THRESHOLD, sim))
        return results

    @staticmethod
    def _entry(std: dict, present: bool, sim: float) -> dict:
        return {
            "name": std["name"],
            "description": std["description"],
            "is_present": present,
            "similarity": round(sim, 3),
            "recommended_text": None if present else std["recommended_text"],
        }
