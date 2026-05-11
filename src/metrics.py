import re
import numpy as np
from typing import List
from sentence_transformers import SentenceTransformer


class MetricsComputer:
    def __init__(self, embed_model_id: str = "sentence-transformers/all-MiniLM-L6-v2"):
        print(f"Loading embedding model: {embed_model_id}")
        self.embed_model = SentenceTransformer(embed_model_id)
        print("Embedding model ready.")

    def embed(self, texts: List[str]) -> np.ndarray:
        return self.embed_model.encode(
            texts, batch_size=64,
            show_progress_bar=False,
            normalize_embeddings=True,
        )

    @staticmethod
    def avg_pairwise_similarity(embs: np.ndarray) -> float:
        n = len(embs)
        if n < 2:
            return 1.0
        sim = embs @ embs.T
        return float(np.mean(sim[np.triu_indices(n, k=1)]))

    @staticmethod
    def semantic_diversity(embs: np.ndarray) -> float:
        return 1.0 - MetricsComputer.avg_pairwise_similarity(embs)

    @staticmethod
    def vendi_score(embs: np.ndarray) -> float:
        n = len(embs)
        K = (embs @ embs.T) / n
        eigs = np.linalg.eigvalsh(K)
        eigs = eigs[eigs > 1e-10]
        return float(np.exp(-np.sum(eigs * np.log(eigs))))

    @staticmethod
    def lexical_diversity(texts: List[str], n: int = 2) -> float:
        union, total = set(), 0
        for t in texts:
            toks = re.findall(r'\b\w+\b', t.lower())
            ngs = [tuple(toks[i:i+n]) for i in range(len(toks) - n + 1)]
            union.update(ngs)
            total += len(ngs)
        return len(union) / total if total else 0.0

    @staticmethod
    def prompt_relevance(embs: np.ndarray, prompt_emb: np.ndarray) -> float:
        return float(np.mean(embs @ prompt_emb.T))

    def compute_all(self, texts: List[str], prompt: str) -> dict:
        embs = self.embed(texts)
        prompt_emb = self.embed([prompt])

        return {
            "AvgSim": self.avg_pairwise_similarity(embs),
            "SemDiv": self.semantic_diversity(embs),
            "Vendi": self.vendi_score(embs),
            "LexDiv": self.lexical_diversity(texts),
            "Quality": self.prompt_relevance(embs, prompt_emb),
            "n_responses": len(texts),
        }


METRIC_NAMES = ["AvgSim", "SemDiv", "Vendi", "LexDiv", "Quality"]
METRIC_DIRS = ["↓", "↑", "↑", "↑", "↑"]
