import os
import json
import time
import random
import argparse
import logging
import numpy as np
from datetime import datetime

from .config import Config
from .api_client import FireworksClient
from .metrics import MetricsComputer, METRIC_NAMES, METRIC_DIRS
from .ladder import LEVELS
from .prompts import PROMPTS

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def run_experiment(config: Config, prompt_count: int = None, level_filter: list = None):
    random.seed(config.seed)
    np.random.seed(config.seed)

    prompts = PROMPTS[:prompt_count] if prompt_count else PROMPTS
    levels = {k: v for k, v in LEVELS.items() if not level_filter or k in level_filter}

    logger.info(f"Model: {config.model_display_name}")
    logger.info(f"Prompts: {len(prompts)}")
    logger.info(f"Levels: {list(levels.keys())}")
    logger.info(f"K: {config.K}")

    total_runs = len(prompts) * len(levels)
    total_calls = sum(
        config.K if name != "L6" else config.M
        for name in levels
    ) * len(prompts)
    logger.info(f"Total runs: {total_runs} | Est. API calls: {total_calls}")

    client = FireworksClient(config)
    metrics = MetricsComputer(config.embed_model_id)

    all_responses = {}
    all_metrics = {}
    done = 0

    os.makedirs(config.output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    responses_path = os.path.join(config.output_dir, f"responses_{timestamp}.json")

    def _save_responses():
        entries = []
        for p, levels_map in all_responses.items():
            for lvl, resps in levels_map.items():
                entries.append({
                    "prompt": p,
                    "level": lvl,
                    "responses": resps,
                })
        with open(responses_path, "w") as f:
            json.dump(entries, f, indent=2)

    for prompt in prompts:
        all_responses[prompt] = {}
        all_metrics[prompt] = {}

        for level_name, (level_label, level_fn) in levels.items():
            done += 1
            logger.info(f"[{done}/{total_runs}] {level_label} | \"{prompt[:45]}...\"")

            t0 = time.time()
            try:
                kwargs = {}
                if level_name == "L5":
                    kwargs["max_previous"] = config.repulsion_max_previous
                elif level_name == "L6":
                    kwargs["metrics"] = metrics
                    kwargs["overgen_ratio"] = config.dpp_overgen_ratio
                    kwargs["quality_weight"] = config.dpp_quality_weight
                    kwargs["max_previous"] = config.repulsion_max_previous

                responses = level_fn(client, prompt, config.K, **kwargs)

                elapsed = time.time() - t0
                logger.info(f"  → {len(responses)} responses in {elapsed:.0f}s")

                m = metrics.compute_all(responses, prompt)
                logger.info(
                    f"  → SemDiv={m['SemDiv']:.3f} Vendi={m['Vendi']:.2f} "
                    f"LexDiv={m['LexDiv']:.3f} Quality={m['Quality']:.3f}"
                )

                all_responses[prompt][level_name] = responses
                all_metrics[prompt][level_name] = m

            except Exception as e:
                logger.error(f"  FAILED: {e}")
                all_responses[prompt][level_name] = []
                all_metrics[prompt][level_name] = {m: 0.0 for m in METRIC_NAMES}

            _save_responses()
            logger.info(f"  → Responses saved to: {responses_path}")

    agg = {}
    for level_name in levels:
        agg[level_name] = {}
        for m in METRIC_NAMES:
            vals = [
                all_metrics[p][level_name][m]
                for p in prompts
                if level_name in all_metrics[p]
                and all_metrics[p][level_name][m] != 0.0
            ]
            if vals:
                agg[level_name][m] = {
                    "mean": float(np.mean(vals)),
                    "se": float(np.std(vals) / np.sqrt(len(vals))),
                    "values": [float(v) for v in vals],
                }
            else:
                agg[level_name][m] = {"mean": 0.0, "se": 0.0, "values": []}

    _print_results_table(agg, levels, len(prompts), config.K)


    out_path = os.path.join(config.output_dir, f"experiment_{timestamp}.json")

    output = {
        "config": {
            "model": config.model_id,
            "model_display_name": config.model_display_name,
            "K": config.K,
            "seed": config.seed,
            "n_prompts": len(prompts),
            "prompts": prompts,
            "levels": list(levels.keys()),
            "timestamp": timestamp,
        },
        "api_stats": client.get_stats(),
        "aggregated_metrics": agg,
        "per_prompt_metrics": {
            p: {l: all_metrics[p].get(l, {}) for l in levels}
            for p in prompts
        },
        "responses": all_responses,
    }

    with open(out_path, "w") as f:
        json.dump(output, f, indent=2, default=float)

    logger.info(f"\nResults saved to:   {out_path}")
    logger.info(f"Responses saved to: {responses_path}")
    client.print_stats()

    return output


def _print_results_table(agg, levels, n_prompts, k):
    col = 16
    header = f"{'Level':<26}" + "".join(
        f"{m+' '+d:>{col}}" for m, d in zip(METRIC_NAMES, METRIC_DIRS)
    )
    div = "═" * len(header)

    print(f"\n{div}")
    print(f"Hivemind Ladder Results ({n_prompts} prompts × K={k})")
    print(f"{div}")
    print(header)
    print("─" * len(header))

    for level_name, (level_label, _) in levels.items():
        label = f"{level_name}: {level_label}"
        row = f"{label:<26}"
        for m in METRIC_NAMES:
            mean = agg[level_name][m]["mean"]
            se = agg[level_name][m]["se"]
            row += f"{mean:.3f}±{se:.3f}".rjust(col)
        print(row)

    print(div)

    if "L0" in agg:
        print(f"\nΔ vs L0 (Naive):")
        for level_name, (level_label, _) in levels.items():
            if level_name == "L0":
                continue
            label = f"{level_name}: {level_label}"
            row = f"{label:<26}"
            for m in METRIC_NAMES:
                delta = agg[level_name][m]["mean"] - agg["L0"][m]["mean"]
                row += f"{delta:>+.3f}".rjust(col)
            print(row)


def main():
    parser = argparse.ArgumentParser(description="Run Hivemind Ladder experiment")
    parser.add_argument("--prompts", type=int, default=None,
                        help="Number of prompts to use (default: all 15)")
    parser.add_argument("--k", type=int, default=None,
                        help="Responses per level per prompt (default: 30)")
    parser.add_argument("--levels", nargs="+", default=None,
                        help="Which levels to run (e.g., L0 L4 L6)")
    parser.add_argument("--model", type=str, default=None,
                        help="Fireworks model ID override")
    parser.add_argument("--rpm", type=int, default=None,
                        help="Max requests per minute (default: 90)")
    parser.add_argument("--output-dir", type=str, default=None,
                        help="Output directory (default: results)")
    args = parser.parse_args()

    config = Config()
    if args.k:
        config.K = args.k
    if args.model:
        config.model_id = args.model
        config.model_display_name = args.model.split("/")[-1]
    if args.rpm:
        config.max_requests_per_minute = args.rpm
    if args.output_dir:
        config.output_dir = args.output_dir

    run_experiment(
        config,
        prompt_count=args.prompts,
        level_filter=args.levels,
    )


if __name__ == "__main__":
    main()
