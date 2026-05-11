import random
import re
import numpy as np
from typing import List, Optional
from .api_client import FireworksClient
from .prompts import CULTURAL_FRAMES, CULTURAL_EXEMPLARS, DEFAULT_EXEMPLARS
from .metrics import MetricsComputer


def level0_naive(
    client: FireworksClient, prompt: str, k: int, **kwargs
) -> List[str]:
    results = []
    for i in range(k):
        text = client.generate(prompt)
        results.append(text)
    return results


def level1_temperature(
    client: FireworksClient, prompt: str, k: int, **kwargs
) -> List[str]:
    temps = np.linspace(0.5, 1.3, k)
    results = []
    for t in temps:
        text = client.generate(prompt, temperature=float(t))
        results.append(text)
    return results


def level3_cultural_prompt(
    client: FireworksClient, prompt: str, k: int, **kwargs
) -> List[str]:
    results = []
    for i in range(k):
        frame = CULTURAL_FRAMES[i % len(CULTURAL_FRAMES)][0]
        framed_prompt = (
            f"Responding from the perspective of {frame}:\n\n{prompt}"
        )
        text = client.generate(framed_prompt)
        results.append(text)
    return results


def _get_exemplars(prompt: str) -> list:
    if prompt in CULTURAL_EXEMPLARS:
        return CULTURAL_EXEMPLARS[prompt]
    return DEFAULT_EXEMPLARS


def _build_fewshot_prompt(prompt: str, n_examples: int = 3) -> str:
    exemplars = _get_exemplars(prompt)
    chosen = random.sample(exemplars, min(n_examples, len(exemplars)))

    examples_text = "\n\n".join(
        f"[{culture} perspective]: {response}"
        for culture, response in chosen
    )

    return (
        f"Here is how people from different cultures answered this question:\n\n"
        f"{examples_text}\n\n"
        f"Now give YOUR unique response to: {prompt}\n"
        f"Draw from a perspective not already represented above. "
        f"Be authentic and specific to a cultural worldview."
    )


def level4_fewshot(
    client: FireworksClient, prompt: str, k: int, **kwargs
) -> List[str]:
    """Generate K responses with few-shot cultural exemplars."""
    results = []
    for _ in range(k):
        fewshot_prompt = _build_fewshot_prompt(prompt, n_examples=3)
        text = client.generate(fewshot_prompt)
        results.append(text)
    return results


def _truncate_response(text: str, max_chars: int = 150) -> str:
    text = text.replace("\n", " ").strip()
    if len(text) > max_chars:
        return text[:max_chars] + "..."
    return text


def level5_fewshot_repulsion(
    client: FireworksClient, prompt: str, k: int,
    max_previous: int = 5, **kwargs
) -> List[str]:
    results = []

    for i in range(k):
        fewshot_prompt = _build_fewshot_prompt(prompt, n_examples=3)

        if i > 0 and results:
            n_prev = min(i, max_previous)
            prev_texts = results[-n_prev:]
            prev_section = "\n".join(
                f"  - \"{_truncate_response(r)}\""
                for r in prev_texts
            )
            fewshot_prompt += (
                f"\n\nIMPORTANT: The following perspectives have ALREADY been given. "
                f"You MUST provide a COMPLETELY DIFFERENT perspective, different "
                f"cultural frame, different metaphors, different values:\n{prev_section}"
            )

        text = client.generate(fewshot_prompt)
        results.append(text)

    return results


def _dpp_select(
    texts: List[str],
    metrics: MetricsComputer,
    prompt: str,
    k: int,
    quality_weight: float = 0.5,
) -> List[str]:
    embs = metrics.embed(texts)
    prompt_emb = metrics.embed([prompt])

    raw_quality = np.clip((embs * prompt_emb).sum(axis=1), 0.1, 1.0)
    quality = (1.0 - quality_weight) + quality_weight * raw_quality

    S = np.clip(embs @ embs.T, 0, 1)
    L = np.outer(quality, quality) * S

    n = len(texts)
    selected = []
    remaining = set(range(n))

    for t in range(min(k, n)):
        best_idx, best_gain = -1, -np.inf
        for j in remaining:
            if t == 0:
                gain = L[j, j]
            else:
                sel = selected
                try:
                    v = np.linalg.solve(
                        L[np.ix_(sel, sel)] + 1e-8 * np.eye(t),
                        L[sel, j]
                    )
                    gain = L[j, j] - L[sel, j] @ v
                except np.linalg.LinAlgError:
                    gain = L[j, j]
            if gain > best_gain:
                best_gain, best_idx = gain, j
        if best_idx < 0:
            break
        selected.append(best_idx)
        remaining.discard(best_idx)

    return [texts[i] for i in selected]


def level6_full_pipeline(
    client: FireworksClient, prompt: str, k: int,
    metrics: MetricsComputer = None,
    overgen_ratio: float = 2.0,
    quality_weight: float = 0.5,
    max_previous: int = 5,
    **kwargs,
) -> List[str]:

    if metrics is None:
        raise ValueError("L6 requires a MetricsComputer instance")

    m = int(k * overgen_ratio)
    candidates = level5_fewshot_repulsion(
        client, prompt, m, max_previous=max_previous
    )

    selected = _dpp_select(candidates, metrics, prompt, k, quality_weight)
    return selected

LEVELS = {
    "L0": ("Naive", level0_naive),
    "L1": ("Temperature sweep", level1_temperature),
    "L3": ("Cultural prompt", level3_cultural_prompt),
    "L4": ("Few-shot exemplars", level4_fewshot),
    "L5": ("Few-shot + repulsion", level5_fewshot_repulsion),
    "L6": ("Full pipeline + DPP", level6_full_pipeline),
}
