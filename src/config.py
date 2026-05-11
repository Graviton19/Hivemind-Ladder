from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class Config:
    model_id: str = "accounts/fireworks/models/llama-v3p3-70b-instruct"
    model_display_name: str = "Llama-3.3-70B-Instruct"
    base_url: str = "https://api.fireworks.ai/inference/v1"

    embed_model_id: str = "sentence-transformers/all-MiniLM-L6-v2"

    K: int = 30 
    max_tokens: int = 250
    temperature: float = 0.9
    top_p: float = 0.92

    dpp_overgen_ratio: float = 2.0 
    dpp_quality_weight: float = 0.5

    max_retries: int = 5
    retry_base_delay: float = 2.0

    repulsion_max_previous: int = 5

    output_dir: str = "results"
    seed: int = 42

    @property
    def M(self) -> int:
        return int(self.K * self.dpp_overgen_ratio)
