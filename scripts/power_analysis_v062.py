"""
Family C Statistical Power Analysis
====================================
MetaJudge-AGI v0.6.2 — hardening/family-c-v0.6.2 branch

Evaluates whether the current 45-item clean set supports defensible
statistical claims about model self-correction behavior.

Outputs: outputs/family_c/power_analysis_v062.md

Key questions:
  1. SC rate CI widths given tiny wrong-on-T1 denominators (4-9)
  2. Whether T2-T1 accuracy delta is a more powerful headline metric
  3. McNemar-style pairwise distinguishability
  4. Minimum item counts for defensible claims
  5. Rescaling compression analysis — does the current [-.55, .30] range
     compress score distinctions?

Usage: python3 scripts/power_analysis_v062.py
"""

import csv
import math
import os
import sys
from collections import Counter
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
from scipy import stats

REPO_ROOT = Path(__file__).resolve().parent.parent
SWEEP_CSV = REPO_ROOT / "outputs" / "family_c" / "sweep_cross_model_v062.csv"
OUTPUT_MD = REPO_ROOT / "outputs" / "family_c" / "power_analysis_v062.md"

# Add metajudge to path for scoring imports
sys.path.insert(0, str(REPO_ROOT))
from metajudge.scoring.self_correction_v2 import (
    _C1_BASE, _C2_BASE, _RAW_MIN, _RAW_MAX, _CONF_ADJ_MIN, _CONF_ADJ_MAX, _rescale,
)


# ── Data loading ─────────────────────────────────────────────

def load_sweep() -> Tuple[List[dict], List[str]]:
    """Load cross-model sweep CSV."""
    with open(SWEEP_CSV) as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    models = ["deepseek", "grok", "gpt41", "claude"]  # exclude gemini (truncation)
    return rows, models


def extract_transitions(rows: List[dict], model: str) -> Dict[str, int]:
    """Count transition types for a model."""
    col = f"{model}_transition"
    return dict(Counter(r[col] for r in rows))


# ── 1. Binomial CI for SC rate ───────────────────────────────

def wilson_ci(k: int, n: int, alpha: float = 0.05) -> Tuple[float, float]:
    """Wilson score interval for binomial proportion."""
    if n == 0:
        return (0.0, 1.0)
    z = stats.norm.ppf(1 - alpha / 2)
    p_hat = k / n
    denom = 1 + z**2 / n
    center = (p_hat + z**2 / (2 * n)) / denom
    spread = z * math.sqrt(p_hat * (1 - p_hat) / n + z**2 / (4 * n**2)) / denom
    return (max(0, center - spread), min(1, center + spread))


def sc_rate_analysis(rows: List[dict], models: List[str]) -> str:
    """Analyze SC rate CI widths."""
    lines = []
    lines.append("## 1. Self-Correction Rate Confidence Intervals\n")
    lines.append("SC rate = W→R / (total wrong on T1). Wilson 95% CIs.\n")
    lines.append("| Model | Wrong T1 | W→R | SC Rate | 95% CI | CI Width |")
    lines.append("|-------|----------|-----|---------|--------|----------|")

    for model in models:
        trans = extract_transitions(rows, model)
        t1_wrong = trans.get("WR", 0) + trans.get("WW", 0)
        wr = trans.get("WR", 0)
        rate = wr / t1_wrong if t1_wrong > 0 else float("nan")
        lo, hi = wilson_ci(wr, t1_wrong)
        width = hi - lo
        lines.append(
            f"| {model:10s} | {t1_wrong:2d} | {wr} | {rate:.1%} | "
            f"[{lo:.1%}, {hi:.1%}] | {width:.1%} |"
        )

    lines.append("")
    lines.append("**Interpretation:** CI widths of 40-70% make pairwise SC rate ")
    lines.append("comparisons statistically indefensible with current item counts. ")
    lines.append("Claude's 50% SC rate (2/4) has a CI of [~15%, ~85%] — it overlaps ")
    lines.append("with every other model.\n")
    return "\n".join(lines)


# ── 2. T2-T1 accuracy delta ────────────────────────────────

def t2_t1_delta_analysis(rows: List[dict], models: List[str]) -> str:
    """T2-T1 delta uses all 45 items — much more powerful."""
    lines = []
    lines.append("## 2. T2-T1 Accuracy Delta (Recommended Headline Metric)\n")
    lines.append("T2-T1 delta = (T2 accuracy) - (T1 accuracy), computed over all 45 items.")
    lines.append("This uses the full item set, not just wrong-on-T1 items.\n")
    lines.append("| Model | T1 Acc | T2 Acc | Delta (pp) | 95% CI (bootstrap) | Significant? |")
    lines.append("|-------|--------|--------|------------|--------------------|--------------| ")

    n_items = len(rows)
    rng = np.random.default_rng(42)

    for model in models:
        col = f"{model}_transition"
        t1_correct = np.array([1 if r[col] in ("RR", "RW") else 0 for r in rows])
        t2_correct = np.array([1 if r[col] in ("RR", "WR") else 0 for r in rows])
        deltas_per_item = t2_correct - t1_correct  # -1, 0, or +1 per item

        t1_acc = t1_correct.mean()
        t2_acc = t2_correct.mean()
        observed_delta = t2_acc - t1_acc

        # Bootstrap CI for the delta
        n_boot = 10000
        boot_deltas = np.empty(n_boot)
        for b in range(n_boot):
            idx = rng.integers(0, n_items, size=n_items)
            boot_deltas[b] = deltas_per_item[idx].mean()

        ci_lo = np.percentile(boot_deltas, 2.5)
        ci_hi = np.percentile(boot_deltas, 97.5)
        sig = "Yes" if (ci_lo > 0 or ci_hi < 0) else "No"

        lines.append(
            f"| {model:10s} | {t1_acc:.1%} | {t2_acc:.1%} | "
            f"{observed_delta * 100:+.1f} | [{ci_lo * 100:+.1f}, {ci_hi * 100:+.1f}] | {sig} |"
        )

    lines.append("")
    lines.append("**Interpretation:** T2-T1 delta uses all 45 items as paired observations, ")
    lines.append("giving much tighter CIs than SC rate. However, for models with small deltas ")
    lines.append("(0-2pp), the CI will still cross zero. The strongest signal is DeepSeek's ")
    lines.append("+8.9pp improvement — this is the most defensible claim in the dataset.\n")
    return "\n".join(lines)


# ── 3. McNemar pairwise tests ──────────────────────────────

def mcnemar_analysis(rows: List[dict], models: List[str]) -> str:
    """McNemar test for pairwise T2 accuracy differences."""
    lines = []
    lines.append("## 3. McNemar Pairwise Comparisons (T2 Accuracy)\n")
    lines.append("McNemar's test for paired binary data: are two models' T2 accuracy ")
    lines.append("profiles significantly different on the same 45 items?\n")
    lines.append("| Pair | Discordant | p-value | Significant (α=0.05)? |")
    lines.append("|------|------------|---------|----------------------|")

    for i in range(len(models)):
        for j in range(i + 1, len(models)):
            m1, m2 = models[i], models[j]
            col1 = f"{m1}_transition"
            col2 = f"{m2}_transition"

            # T2 correct
            t2_1 = [r[col1] in ("RR", "WR") for r in rows]
            t2_2 = [r[col2] in ("RR", "WR") for r in rows]

            # Discordant pairs
            b = sum(1 for a, bb in zip(t2_1, t2_2) if a and not bb)  # m1 right, m2 wrong
            c = sum(1 for a, bb in zip(t2_1, t2_2) if not a and bb)  # m1 wrong, m2 right

            n_disc = b + c
            if n_disc == 0:
                p_val = 1.0
            else:
                # McNemar exact (binomial test)
                p_val = stats.binomtest(min(b, c), n_disc, 0.5).pvalue if n_disc > 0 else 1.0

            sig = "Yes" if p_val < 0.05 else "No"
            lines.append(
                f"| {m1} vs {m2} | {n_disc} ({b}:{c}) | {p_val:.3f} | {sig} |"
            )

    lines.append("")
    lines.append("**Interpretation:** With 45 items and high T2 accuracy (88-93%), ")
    lines.append("discordant pairs are rare. Most comparisons will be non-significant. ")
    lines.append("The most distinguishable pair is likely Claude vs others (highest T2).\n")
    return "\n".join(lines)


# ── 4. Minimum item count analysis ─────────────────────────

def minimum_items_analysis() -> str:
    """How many items are needed for various CI widths on SC rate?"""
    lines = []
    lines.append("## 4. Minimum Item Count for Defensible SC Rate Claims\n")
    lines.append("Assuming a true SC rate of ~35% (mid-range of observed rates), ")
    lines.append("how many wrong-on-T1 items are needed for a given CI width?\n")
    lines.append("| Wrong-on-T1 items | Wilson CI width | Can distinguish 35% from 0%? |")
    lines.append("|-------------------|-----------------|------------------------------|")

    true_rate = 0.35
    for n in [4, 5, 7, 9, 15, 20, 30, 50]:
        k = round(true_rate * n)
        lo, hi = wilson_ci(k, n)
        width = hi - lo
        can_distinguish = lo > 0.0
        lines.append(
            f"| {n:2d} | {width:.1%} | {'Yes' if can_distinguish else 'No'} |"
        )

    lines.append("")
    lines.append("To get wrong-on-T1 items ≥ 15, with models at 80-90% T1 accuracy, ")
    lines.append("you'd need a total item count of:\n")
    lines.append("| T1 Accuracy | Items needed for 15 wrong-on-T1 |")
    lines.append("|-------------|--------------------------------|")
    for t1_acc in [0.80, 0.85, 0.90]:
        needed = math.ceil(15 / (1 - t1_acc))
        lines.append(f"| {t1_acc:.0%} | {needed} |")

    lines.append("")
    lines.append("**Conclusion:** At current T1 accuracies, you need 75-150 total items ")
    lines.append("to get enough wrong-on-T1 trials for defensible SC rate comparisons. ")
    lines.append("With 45 items, the recommendation is to lead with T2-T1 delta as the ")
    lines.append("headline metric and report SC rates as exploratory/descriptive.\n")
    return "\n".join(lines)


# ── 5. Rescaling compression analysis ──────────────────────

def rescaling_analysis() -> str:
    """Analyze whether the [-0.55, 0.30] rescaling compresses distinctions."""
    lines = []
    lines.append("## 5. Rescaling Compression Analysis\n")
    lines.append("The scoring maps raw scores from [-0.55, 0.30] to [0, 1]. ")
    lines.append("Since the raw range is only 0.85 units wide but many outcomes ")
    lines.append("land above 0.30 (the nominal max), there is significant top-clamping.\n")

    lines.append("### Raw scores and scaled equivalents (C1, neutral confidence adj)\n")
    lines.append("| Transition | Base | +Typical Adj | Raw | Scaled | Clamped? |")
    lines.append("|------------|------|-------------|-----|--------|----------|")

    typical_adj = {
        "correction_gain": 0.03,     # stable conf on correction
        "maintain_correct": 0.05,    # slight conf rise
        "neutral_revision": 0.05,    # stable
        "damage": -0.15,             # worst case
        "stubborn_wrong": 0.0,       # neutral
        "failed_revision": 0.0,      # neutral
    }

    for trans in ["maintain_correct", "correction_gain", "neutral_revision",
                  "stubborn_wrong", "failed_revision", "damage"]:
        base = _C1_BASE[trans]
        adj = typical_adj[trans]
        raw = base + adj
        scaled = _rescale(raw)
        clamped = raw > _RAW_MAX or raw < _RAW_MIN
        lines.append(
            f"| {trans:20s} | {base:+.2f} | {adj:+.2f} | {raw:+.2f} | "
            f"{scaled:.3f} | {'YES' if clamped else 'no'} |"
        )

    # Count how many transitions clamp
    clamped_count = sum(
        1 for t in typical_adj
        if _C1_BASE[t] + typical_adj[t] > _RAW_MAX
        or _C1_BASE[t] + typical_adj[t] < _RAW_MIN
    )

    lines.append("")
    lines.append(f"**{clamped_count}/6 transitions clamp** under typical conditions. ")
    lines.append("This means maintain_correct, correction_gain (best case), and ")
    lines.append("neutral_revision all score 1.0. The effective discrimination range ")
    lines.append("collapses to a 3-way distinction:\n")
    lines.append("- **1.0** — correct outcome (maintain, correction, neutral revision)")
    lines.append("- **~0.75-0.88** — wrong but not damaging (stubborn, failed revision)")
    lines.append("- **0.0-0.18** — damage\n")
    lines.append("This compression means Family C's scaled_score effectively measures ")
    lines.append("a single thing: **did the model damage a correct answer?** ")
    lines.append("All non-damage outcomes land in a narrow band near 1.0.\n")

    lines.append("### Implication for discrimination\n")
    lines.append("With most models showing 0-1 damage events out of 45 items, the ")
    lines.append("headline scaled_score will be ≥0.95 for all models. Model differences ")
    lines.append("will be driven almost entirely by the stubborn_wrong vs correction_gain ")
    lines.append("distinction, which is only a ~0.12 gap in scaled space. To see this ")
    lines.append("distinction, **report raw transition matrices alongside scaled scores.**\n")
    return "\n".join(lines)


# ── 6. Recommendation summary ─────────────────────────────

def recommendations(rows: List[dict], models: List[str]) -> str:
    lines = []
    lines.append("## 6. Recommendations\n")

    lines.append("### What to lead with (defensible at n=45)")
    lines.append("1. **T2-T1 accuracy delta** — uses all 45 paired observations, ")
    lines.append("   tight CIs, captures the core finding that metacognitive prompting ")
    lines.append("   produces net benefit for 3/4 non-rigid models.")
    lines.append("2. **Raw transition matrices** — the most informative output. ")
    lines.append("   Report R→R, W→R, R→W, W→W counts per model.")
    lines.append("3. **Behavioral profile taxonomy** — qualitative: Claude (self-corrects, ")
    lines.append("   minimal damage), DeepSeek (strong self-corrector), GPT-4.1 (moderate), ")
    lines.append("   Grok (rigid). This doesn't need p-values.\n")

    lines.append("### What to report as exploratory (underpowered at n=45)")
    lines.append("1. **SC rates** — report with Wilson CIs and explicit caveat about ")
    lines.append("   small denominators (4-9 wrong-on-T1 items).")
    lines.append("2. **Damage rates** — only 1 genuine damage event across 4×45=180 trials. ")
    lines.append("   Cannot make any statistical claim about damage rates.\n")

    lines.append("### What to fix before benchmark promotion")
    lines.append("1. **Rescaling compression** — the current [-0.55, 0.30] range clamps ")
    lines.append("   3/6 transitions to 1.0, destroying discrimination in scaled_score. ")
    lines.append("   Consider widening _RAW_MAX to 0.65 (= maintain_correct base) so that ")
    lines.append("   only the best outcomes clamp, not all non-damage outcomes.")
    lines.append("2. **Item count** — 75-150 items needed for SC rate CIs to be defensible. ")
    lines.append("   The WR hardening pipeline needs a strategy pivot (current approach ")
    lines.append("   generates 0/12 accepted items at frontier difficulty).")
    lines.append("3. **Weaker model panel** — running the 45 items against weaker models ")
    lines.append("   (the team's pending work) will increase wrong-on-T1 counts and provide ")
    lines.append("   the statistical power the current panel lacks.\n")
    return "\n".join(lines)


# ── Main ───────────────────────────────────────────────────

def main():
    rows, models = load_sweep()

    sections = [
        f"# Family C Power Analysis — v0.6.2\n",
        f"**Date:** {__import__('datetime').date.today()}",
        f"**Branch:** `hardening/family-c-v0.6.2`",
        f"**Items:** {len(rows)} clean, 4 reliable models (Gemini excluded — truncation)\n",
        "---\n",
        sc_rate_analysis(rows, models),
        t2_t1_delta_analysis(rows, models),
        mcnemar_analysis(rows, models),
        minimum_items_analysis(),
        rescaling_analysis(),
        recommendations(rows, models),
    ]

    report = "\n".join(sections)
    OUTPUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_MD.write_text(report)
    print(report)
    print(f"\n[Saved to {OUTPUT_MD}]")


if __name__ == "__main__":
    main()
