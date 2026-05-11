import os
import json
import argparse
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

from .metrics import METRIC_NAMES, METRIC_DIRS


LEVEL_LABELS = {
    "L0": "L0: Naive",
    "L1": "L1: Temperature",
    "L3": "L3: Cultural prompt",
    "L4": "L4: Few-shot",
    "L5": "L5: Few-shot+repulsion",
    "L6": "L6: Full pipeline",
}

COLORS = {
    "L0": "#BDBDBD",
    "L1": "#90A4AE",
    "L3": "#AED581",
    "L4": "#4FC3F7",
    "L5": "#FFB74D",
    "L6": "#E53935",
}


def load_results(path: str) -> dict:
    with open(path) as f:
        return json.load(f)


def plot_ladder(data: dict, output_dir: str):
    agg = data["aggregated_metrics"]
    levels = [l for l in ["L0", "L1", "L3", "L4", "L5", "L6"] if l in agg]

    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    for ax, metric, title in zip(
        axes,
        ["SemDiv", "Vendi", "LexDiv"],
        ["Semantic Diversity ↑", "Vendi Score ↑", "Lexical Diversity ↑"],
    ):
        means = [agg[l][metric]["mean"] for l in levels]
        ses = [agg[l][metric]["se"] for l in levels]
        colors = [COLORS.get(l, "#999") for l in levels]

        bars = ax.bar(
            range(len(levels)), means, color=colors,
            yerr=ses, capsize=4, width=0.6,
            edgecolor="white", linewidth=0.5,
        )
        if "L6" in levels:
            idx = levels.index("L6")
            bars[idx].set_edgecolor("#B71C1C")
            bars[idx].set_linewidth(2)

        ax.set_xticks(range(len(levels)))
        ax.set_xticklabels(
            [LEVEL_LABELS.get(l, l) for l in levels],
            rotation=35, ha="right", fontsize=8,
        )
        ax.set_title(title, fontsize=12)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        if "L1" in levels and "L3" in levels:
            cliff_x = (levels.index("L1") + levels.index("L3")) / 2
            ax.axvline(cliff_x, color="red", linestyle="--", alpha=0.4, linewidth=1.5)
            ax.text(cliff_x, max(means) * 0.95, "  CLIFF",
                    color="red", fontsize=8, alpha=0.6, va="top")

    n_prompts = data["config"]["n_prompts"]
    k = data["config"]["K"]
    model = data["config"].get("model_display_name", "")
    plt.suptitle(
        f"Breaking the Hivemind: Ladder of Interventions\n"
        f"({model}, {n_prompts} prompts, K={k})",
        fontsize=13, y=1.03,
    )
    plt.tight_layout()

    path = os.path.join(output_dir, "fig1_ladder.png")
    plt.savefig(path, dpi=200, bbox_inches="tight")
    plt.close()
    print(f"Saved: {path}")


def plot_pareto(data: dict, output_dir: str):
    agg = data["aggregated_metrics"]
    levels = [l for l in ["L0", "L1", "L3", "L4", "L5", "L6"] if l in agg]

    fig, ax = plt.subplots(figsize=(8, 6))
    for level in levels:
        x = agg[level]["SemDiv"]["mean"]
        y = agg[level]["Quality"]["mean"]
        color = COLORS.get(level, "#999")
        is_l6 = level == "L6"

        ax.scatter(
            x, y, c=color, s=150, zorder=3,
            edgecolors="black" if is_l6 else color,
            linewidth=2 if is_l6 else 0,
        )
        ax.annotate(
            LEVEL_LABELS.get(level, level), (x, y),
            textcoords="offset points", xytext=(8, 5), fontsize=9,
        )

    ax.set_xlabel("Semantic Diversity ↑", fontsize=11)
    ax.set_ylabel("Quality (Prompt Relevance) ↑", fontsize=11)
    ax.set_title("Quality-Diversity Trade-off", fontsize=12)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    plt.tight_layout()
    path = os.path.join(output_dir, "fig2_pareto.png")
    plt.savefig(path, dpi=200, bbox_inches="tight")
    plt.close()
    print(f"Saved: {path}")


def plot_per_prompt(data: dict, output_dir: str):
    per_prompt = data["per_prompt_metrics"]
    prompts = data["config"]["prompts"]
    levels = [l for l in ["L0", "L1", "L3", "L4", "L5", "L6"]
              if any(l in per_prompt[p] for p in prompts)]

    matrix = []
    for p in prompts:
        row = []
        for l in levels:
            val = per_prompt.get(p, {}).get(l, {}).get("SemDiv", 0)
            row.append(float(val))
        matrix.append(row)

    matrix = np.array(matrix)
    short_prompts = [p[:35] + "..." if len(p) > 35 else p for p in prompts]

    fig, ax = plt.subplots(figsize=(10, 8))
    im = ax.imshow(matrix, cmap="RdYlGn", aspect="auto", vmin=0, vmax=0.6)

    ax.set_xticks(range(len(levels)))
    ax.set_xticklabels([LEVEL_LABELS.get(l, l) for l in levels],
                       rotation=35, ha="right", fontsize=9)
    ax.set_yticks(range(len(prompts)))
    ax.set_yticklabels(short_prompts, fontsize=8)
    ax.set_title("Semantic Diversity by Prompt × Level", fontsize=12)

    for i in range(len(prompts)):
        for j in range(len(levels)):
            ax.text(j, i, f"{matrix[i, j]:.2f}",
                    ha="center", va="center", fontsize=7,
                    color="white" if matrix[i, j] < 0.2 else "black")

    plt.colorbar(im, ax=ax, label="SemDiv", shrink=0.8)
    plt.tight_layout()

    path = os.path.join(output_dir, "fig3_per_prompt.png")
    plt.savefig(path, dpi=200, bbox_inches="tight")
    plt.close()
    print(f"Saved: {path}")


def run_statistical_tests(data: dict):
    per_prompt = data["per_prompt_metrics"]
    prompts = data["config"]["prompts"]
    levels = [l for l in ["L1", "L3", "L4", "L5", "L6"]
              if any(l in per_prompt[p] for p in prompts)]

    print(f"\nPaired t-tests vs L0 (Naive):\n")
    print(f"{'Level':<26}" + "".join(f"{m:>14}" for m in METRIC_NAMES))
    print("─" * (26 + 14 * len(METRIC_NAMES)))

    for level in levels:
        label = LEVEL_LABELS.get(level, level)
        row = f"{label:<26}"
        for m in METRIC_NAMES:
            base = [float(per_prompt[p].get("L0", {}).get(m, 0)) for p in prompts]
            cond = [float(per_prompt[p].get(level, {}).get(m, 0)) for p in prompts]

            if len(base) >= 3 and any(b != c for b, c in zip(base, cond)):
                _, pval = stats.ttest_rel(cond, base)
                stars = "***" if pval < .001 else "**" if pval < .01 else "*" if pval < .05 else "ns"
                row += f"{pval:.3f}{stars}".rjust(14)
            else:
                row += "n/a".rjust(14)
        print(row)


def print_qualitative(data: dict, n_prompts: int = 2, n_responses: int = 3):
    responses = data["responses"]
    prompts = data["config"]["prompts"][:n_prompts]
    show_levels = ["L0", "L4", "L6"]

    for prompt in prompts:
        print(f"\n{'='*70}")
        print(f"Prompt: \"{prompt}\"")
        print(f"{'='*70}")
        for level in show_levels:
            if level not in responses.get(prompt, {}):
                continue
            label = LEVEL_LABELS.get(level, level)
            print(f"\n  --- {label} ---")
            for i, r in enumerate(responses[prompt][level][:n_responses]):
                display = r[:180].replace("\n", " ")
                if len(r) > 180:
                    display += "..."
                print(f"  [{i+1}] {display}")


def main():
    parser = argparse.ArgumentParser(description="Analyze experiment results")
    parser.add_argument("--results", type=str, required=True,
                        help="Path to experiment JSON file")
    parser.add_argument("--output-dir", type=str, default=None,
                        help="Output dir for figures (default: same as results)")
    args = parser.parse_args()

    data = load_results(args.results)
    output_dir = args.output_dir or os.path.dirname(args.results) or "results"
    os.makedirs(output_dir, exist_ok=True)

    config = data["config"]
    print(f"Model: {config.get('model_display_name', config.get('model', '?'))}")
    print(f"Prompts: {config['n_prompts']}, K: {config['K']}")
    print(f"Levels: {config['levels']}")

    if "api_stats" in data:
        s = data["api_stats"]
        print(f"API: {s['total_requests']} calls, ${s['estimated_cost_usd']:.4f}")

    plot_ladder(data, output_dir)
    plot_pareto(data, output_dir)
    plot_per_prompt(data, output_dir)
    run_statistical_tests(data)
    print_qualitative(data)


if __name__ == "__main__":
    main()
