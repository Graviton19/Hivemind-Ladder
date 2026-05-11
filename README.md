# Mitigating the Artificial Hivemind: A Study of Intervention Strength for Diverse LLM Generation

> **Research paper codebase** — A systematic ladder of interventions to break LLM mode collapse on open-ended creative prompts. We discover a sharp *intervention cliff*: sampling level and adapter level perturbations fail entirely, while prompt-level cultural steering succeeds immediately.

## The Problem

When you ask an LLM "What does home mean to you?" 30 times, you get the same answer 30 times:

```
"Home is a place where I feel safe, comfortable, and welcomed..."
"Home is a place where I feel safe, comfortable, and surrounded..."
"Home is a place where I feel safe, comfortable, and relaxed..."
```

This is the **Artificial Hivemind** effect ([Jiang et al., NeurIPS 2025 Best Paper](https://arxiv.org/abs/2510.22954)). They diagnosed the problem across 70+ models. We measure what it takes to **mitigate** it.

## The Ladder

We test 6 interventions ordered by strength. The central finding is a **sharp cliff** between levels that fail and levels that work:

| Level | Intervention | SemDiv ↑ | Vendi ↑ | Significance |
|-------|-------------|----------|---------|-------------|
| L0 | Naive (same prompt K times) | 0.109 | 1.91 | baseline |
| L1 | Temperature sweep (0.5 → 1.3) | 0.108 | 1.90 | ns |
| ─── | **THE CLIFF** | ─── | ─── | ─── |
| L3 | Cultural prompt framing | 0.314 | 3.87 | p < 0.001 |
| L4 | Few-shot cultural exemplars | 0.346 | 4.72 | p < 0.001 |
| L5 | Few-shot + prompt-level repulsion | 0.442 | 6.96 | p < 0.001 |
| L6 | Full pipeline + DPP selection | 0.520 | 9.61 | p < 0.001 |

*Results: Mistral-7B-Instruct-v0.2, 15 prompts, K=30.*

**L0–L1 are noise.** Temperature doesn't help — it changes how randomly the model speaks, not what it says.

**L3+ works immediately.** The moment you add cultural framing to the prompt, diversity triples. Stacking few-shot exemplars (L4), cross-response repulsion (L5), and DPP subset selection (L6) pushes diversity to 4.8× the baseline.

## Key Findings

1. **The Cliff**: Weight-level and sampling-level interventions (temperature, LoRA adapters) produce zero statistically significant diversity improvement. Prompt-level cultural steering produces immediate, large gains.

2. **In-Context Learning > Fine-tuning**: Three diverse human-written examples in the prompt outperform cultural LoRA adapters specifically designed for diversity. No training needed.

3. **Combined Pipeline**: Few-shot exemplars + cross-response repulsion + DPP achieves Vendi score of 9.61 (effectively 10 distinct responses out of 30), up from 1.91 at baseline.

## Setup

### Prerequisites
- Python 3.9+
- A [Fireworks AI](https://fireworks.ai) API key (free tier gives $1 credit — enough for multiple full runs)

### Installation

```bash
git clone https://github.com/Graviton19/Hivemind-Ladder.git
cd hivemind-ladder
pip install -r requirements.txt
```

### API Key

Get your key from [fireworks.ai](https://fireworks.ai) → Dashboard → API Keys, then:

```bash
# Mac / Linux
export FIREWORKS_API_KEY="fw-your-key-here"

# Windows (PowerShell)
$env:FIREWORKS_API_KEY="fw-your-key-here"
```

## Usage

### Quick Test (recommended first)

```bash
python -m src.run_experiment --prompts 2 --k 5
```

Runs 2 prompts with K=5 responses per level. Takes ~5 minutes, costs < $0.01. Verify everything works before committing to a full run.

### Full Experiment

```bash
python -m src.run_experiment
```

Runs all 15 prompts with K=30 responses across 6 levels. Takes ~2–4 hours (depending on rate limits), costs ~$0.55.

### Run Specific Levels Only

```bash
python -m src.run_experiment --levels L0 L4 L6
```

### Use a Different Model

```bash
# Llama 3.3 70B (~$2.50 for full run)
python -m src.run_experiment --model accounts/fireworks/models/llama-v3p3-70b-instruct

```

### Analyze Results

```bash
python -m src.analyze --results results/experiment_TIMESTAMP.json
```

Generates paper-ready figures (ladder bar chart, Pareto frontier, per-prompt heatmap) and runs statistical tests.

### All CLI Options

| Flag | Description | Default |
|------|-------------|---------|
| `--prompts N` | Number of prompts to use (1–15) | 15 |
| `--k N` | Responses per level per prompt | 30 |
| `--levels L0 L4 ...` | Which levels to run | all |
| `--model ID` | Fireworks model ID | Llama-3.3-70B-Instruct |
| `--rpm N` | Max requests per minute | 20 (auto-adapts) |
| `--output-dir DIR` | Output directory | results/ |

## Project Structure

```
hivemind-ladder/
├── src/
│   ├── __init__.py          # Package marker (required, intentionally empty)
│   ├── __main__.py          # Entry point for python -m src
│   ├── config.py            # All experiment settings
│   ├── prompts.py           # 15 prompts + 75 cultural exemplars
│   ├── api_client.py        # Fireworks client with adaptive rate limiting
│   ├── ladder.py            # All 6 intervention levels
│   ├── metrics.py           # SemDiv, Vendi score, LexDiv, Quality
│   ├── run_experiment.py    # Main experiment runner
│   └── analyze.py           # Plotting + statistical tests
├── requirements.txt
├── README.md
└── .gitignore
```

## How Each Level Works

**L0 — Naive**: Generate K responses with identical prompt and default sampling. This is the Hivemind baseline.

**L1 — Temperature Sweep**: Vary temperature from 0.5 to 1.3 across K generations. Tests whether sampling randomness alone breaks mode collapse. (It doesn't — temperature preserves the logit ordering, so the model's preferred answer stays preferred.)

**L3 — Cultural Prompt Framing**: Cycle through 5 cultural frames ("Responding from the perspective of East Asian Confucian values..."). No adapter weights, just prompt text. This is where the cliff occurs.

**L4 — Few-Shot Cultural Exemplars**: Include 3 randomly-sampled human-written examples from different cultures directly in the prompt. Each generation sees a different random subset. In-context learning is the strongest prompting-level intervention.

**L5 — Few-Shot + Repulsion**: Same as L4, plus each response after the first includes summaries of all previous responses with instructions to be different. Forces the model away from already-covered perspectives.

**L6 — Full Pipeline + DPP**: Over-generate 2K candidates using L5, then select the K most diverse-and-high-quality subset using a Determinantal Point Process. The DPP maximizes the volume of the quality-weighted embedding parallelepiped a mathematical guarantee on diversity.

> **Note on L2 and token-level repulsion**: L2 (cultural LoRA adapters) and token-level n-gram repulsion require local GPU access and are implemented in our [Colab notebooks](). The API-based codebase uses prompt-level repulsion as the equivalent for L5.

## Cost Estimates

| Level | API Calls | Avg Input Tokens | Avg Output Tokens | Cost |
|-------|-----------|-----------------|-------------------|------|
| L0 | 450 | ~80 | ~200 | $0.11 |
| L1 | 450 | ~80 | ~200 | $0.11 |
| L3 | 450 | ~150 | ~200 | $0.14 |
| L4 | 450 | ~650 | ~200 | $0.34 |
| L5 | 450 | ~1,200 | ~200 | $0.57 |
| L6 | 900 | ~1,200 | ~200 | $1.13 |
| **Total** | **3,150** | | | **~$2.40** |

For Llama 3.3 70B (~$0.90/M tokens)→ **~$2.40** total.

## Rate Limiting

The API client uses **adaptive rate limiting** — it starts at 20 requests/minute and automatically adjusts:

- On a 429 error: halves the rate and waits before retrying
- After 50 consecutive successes: increases rate by 20%
- Minimum floor: 3 RPM (never drops below this)

You don't need to configure anything. If you're on Fireworks' free tier and hitting rate limits, the client will slow down and find the right speed automatically. All failed requests are retried up to 5 times with exponential backoff.

## Metrics

| Metric | What It Measures | Direction |
|--------|-----------------|-----------|
| **SemDiv** | 1 − mean pairwise cosine similarity of response embeddings | ↑ higher = more diverse |
| **Vendi** | Effective number of distinct responses (entropy of kernel eigenvalues) | ↑ higher = more diverse |
| **LexDiv** | Bigram type-token ratio across all responses | ↑ higher = more diverse |
| **Quality** | Mean cosine similarity to prompt embedding | ↑ higher = more on-topic |

Embeddings use `sentence-transformers/all-MiniLM-L6-v2`. Statistical significance is computed via paired t-tests (per-prompt pairing).


## Notebooks

| Notebook | Description | Runs on |
|----------|-------------|---------|
| [`Mitigating_Hivemind_with_adapters.ipynb`](Mitigating_Hivemind_with_adapters.ipynb) | Full ladder experiment on Mistral-7B with cultural LoRA adapters + token-level n-gram repulsion | GPU (Colab T4/A100) |
| [`llm_judge_creative_quality.ipynb`](llm_judge_creative_quality.ipynb) | LLM-as-Judge evaluation using GPT-OSS 120B via Ollama Cloud | CPU (API-based) |

### Mitigating_Hivemind_with_adapters.ipynb

The original ladder experiment running locally on **Mistral-7B-Instruct-v0.2** (4-bit quantized). This notebook includes two things the API-based codebase cannot do:

- **L2 (Cultural LoRA Adapters)**: Uses 5 cultural adapters from the [Modular Pluralism](https://arxiv.org/abs/2406.15951) paper (Feng et al., 2024) — `bunsenfeng/mistral-{africa,asia,europe,northamerica,southamerica}_culture`. These are LoRA adapters trained on culturally-grounded text from each region. Our results show they produce **no significant diversity improvement** when used alone (L2), which is a key negative finding.

- **Token-level n-gram repulsion (L5)**: Implements a `CrossResponseRepulsionProcessor` that directly modifies logits during generation. All bigrams, trigrams, and 4-grams from previous responses are banned — the model's probability for any banned continuation is reduced by ~150×. This is mechanistically enforced diversity, not a suggestion the model can ignore.

Requires a GPU with ≥16GB VRAM (Colab T4 works with 4-bit quantization). Runs all 7 levels (L0–L6) including adapter-based levels not available through the API.

### llm_judge_creative_quality.ipynb

Loads the experiment results JSON (from either the API codebase or the Mistral notebook) and runs **GPT-OSS 120B** (via Ollama Cloud) as an unbiased quality judge. Replaces the cosine-similarity quality metric — which is biased against diverse responses, with three judge-scored dimensions:

- **Coherence**: Is the response well-written and logical?
- **Depth**: Does it show genuine insight beyond surface platitudes?
- **Distinctiveness**: Does it offer a unique perspective or cultural viewpoint?

Also runs **set-level diversity scoring**: shows the judge 5 responses simultaneously and asks how many genuinely distinct viewpoints are represented. This directly validates that diversity gains are meaningful, not surface-level noise.

Requires an [Ollama API key](https://ollama.com) (free tier available). Runs on CPU, no GPU needed.

## References

- Jiang et al. (2025). [Artificial Hivemind: The Open-Ended Homogeneity of Language Models](https://arxiv.org/abs/2510.22954). NeurIPS 2025.
- Ruan et al. (2025). [G2: Guided Generation for Enhanced Output Diversity in LLMs](https://aclanthology.org/2025.emnlp-main.832/). EMNLP 2025.
- Tu et al. (2026). [PRISM: Pluralistic Reasoning via In-context Structure Modeling](https://arxiv.org/abs/2602.21317).
- Friedman & Dieng (2022). [The Vendi Score: A Diversity Evaluation Metric for Machine Learning](https://arxiv.org/abs/2210.02410).
- Feng et al.(2024). [Modular Pluralism: Pluralistic Alignment via Multi-LLM Collaboration](https://arxiv.org/abs/2406.15951). EMNLP 2024.

## License

MIT
