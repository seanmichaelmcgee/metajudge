"""
Analyze sweep_v2 results across all models.
Produces: transition matrices, accuracy deltas, B0 comparison,
confidence dynamics, edit-distance distributions.
"""
import json
import sys
from collections import defaultdict, Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = REPO_ROOT / "outputs" / "family_c" / "sweep_v2"


def load_all_results():
    """Load all JSONL result files."""
    results = []
    for jf in sorted(OUTPUT_DIR.glob("*.jsonl")):
        with open(jf) as f:
            for line in f:
                if line.strip():
                    results.append(json.loads(line))
    return results


def model_short(model: str) -> str:
    """Shorten model names for display."""
    mapping = {
        "anthropic/claude-sonnet-4.6": "sonnet-4.6",
        "openai/gpt-5.2": "gpt-5.2",
        "deepseek/deepseek-r1": "ds-r1",
        "google/gemini-2.5-flash": "gem-flash",
        "openai/gpt-5-mini": "gpt-5-mini",
    }
    return mapping.get(model, model.split("/")[-1])


def analyze(results):
    """Full analysis suite."""
    # Group by model
    by_model = defaultdict(list)
    for r in results:
        by_model[r["model"]].append(r)

    lines = []
    lines.append("# Sprint v2 Validation Sweep Analysis")
    lines.append(f"**Total trials:** {len(results)} ({len(by_model)} models × items)\n")

    # ==========================================
    # 1. Headline: T1, T2 accuracy + delta
    # ==========================================
    lines.append("## 1. Accuracy Summary\n")
    lines.append("| Model | Items | T1 Acc | T2 Acc | Δ(T2-T1) | T1 Err | T2 Err |")
    lines.append("|-------|-------|--------|--------|----------|--------|--------|")

    for model in sorted(by_model.keys()):
        rows = by_model[model]
        n = len(rows)
        t1c = sum(1 for r in rows if r.get("t1_correct"))
        t2c = sum(1 for r in rows if r.get("t2_correct"))
        t1e = sum(1 for r in rows if r.get("t1_error"))
        t2e = sum(1 for r in rows if r.get("t2_error"))
        t1a = t1c / n if n else 0
        t2a = t2c / n if n else 0
        delta = t2a - t1a
        sign = "+" if delta >= 0 else ""
        lines.append(
            f"| {model_short(model)} | {n} | {100*t1a:.1f}% | {100*t2a:.1f}% "
            f"| {sign}{100*delta:.1f}% | {t1e} | {t2e} |"
        )
    lines.append("")

    # ==========================================
    # 2. Transition matrices
    # ==========================================
    lines.append("## 2. Transition Matrices\n")
    for model in sorted(by_model.keys()):
        rows = by_model[model]
        trans = Counter(r["transition"] for r in rows)
        lines.append(f"**{model_short(model)}:**")
        lines.append("| Transition | Count | % |")
        lines.append("|-----------|-------|---|")
        for t in ["right_to_right", "wrong_to_right", "right_to_wrong", "wrong_to_wrong"]:
            c = trans.get(t, 0)
            pct = 100 * c / len(rows) if rows else 0
            lines.append(f"| {t} | {c} | {pct:.1f}% |")
        lines.append("")

    # ==========================================
    # 3. B0 Baseline Analysis
    # ==========================================
    lines.append("## 3. B0 Re-answering Baseline\n")
    b0_rows = [r for r in results if r.get("b0_correct") is not None]
    if b0_rows:
        lines.append(f"B0 ran on {len(b0_rows)} trials (diagnostic subset × models)\n")
        lines.append("| Model | B0 Items | T1 Acc | T2 Acc | B0 Acc | C1−B0 | Systematic Err |")
        lines.append("|-------|----------|--------|--------|--------|-------|---------------|")
        for model in sorted(by_model.keys()):
            b0_model = [r for r in b0_rows if r["model"] == model]
            if not b0_model:
                continue
            n = len(b0_model)
            t1c = sum(1 for r in b0_model if r.get("t1_correct"))
            t2c = sum(1 for r in b0_model if r.get("t2_correct"))
            b0c = sum(1 for r in b0_model if r.get("b0_correct"))
            # Systematic errors: T1 wrong AND B0 wrong (same error reproduced)
            systematic = sum(1 for r in b0_model
                           if not r.get("t1_correct") and not r.get("b0_correct"))
            t1a = t1c / n
            t2a = t2c / n
            b0a = b0c / n
            c1_b0 = t2a - b0a
            sign = "+" if c1_b0 >= 0 else ""
            lines.append(
                f"| {model_short(model)} | {n} | {100*t1a:.1f}% | {100*t2a:.1f}% "
                f"| {100*b0a:.1f}% | {sign}{100*c1_b0:.1f}% | {systematic}/{n} |"
            )
        lines.append("")
    else:
        lines.append("No B0 data found.\n")

    # ==========================================
    # 4. Confidence Dynamics
    # ==========================================
    lines.append("## 4. Confidence Dynamics\n")
    lines.append("| Model | T1 Conf (mean) | T2 Conf (mean) | Δ Conf | Parse Rate |")
    lines.append("|-------|---------------|---------------|--------|-----------|")
    for model in sorted(by_model.keys()):
        rows = by_model[model]
        t1_confs = [r["t1_confidence"] for r in rows if r.get("t1_confidence") is not None]
        t2_confs = [r["t2_confidence"] for r in rows if r.get("t2_confidence") is not None]
        t1_mean = sum(t1_confs) / len(t1_confs) if t1_confs else float("nan")
        t2_mean = sum(t2_confs) / len(t2_confs) if t2_confs else float("nan")
        delta = t2_mean - t1_mean if t1_confs and t2_confs else float("nan")
        parse_rate = len(t1_confs) / len(rows) if rows else 0
        sign = "+" if delta >= 0 else ""
        lines.append(
            f"| {model_short(model)} | {100*t1_mean:.1f}% | {100*t2_mean:.1f}% "
            f"| {sign}{100*delta:.1f}% | {100*parse_rate:.0f}% |"
        )
    lines.append("")

    # ==========================================
    # 5. Edit Distance Analysis
    # ==========================================
    lines.append("## 5. Edit Distance (T1↔T2 Similarity)\n")
    lines.append("| Model | Mean Sim | No Change (>0.9) | Targeted (0.4-0.9) | Rewrite (<0.4) |")
    lines.append("|-------|---------|-----------------|-------------------|---------------|")
    for model in sorted(by_model.keys()):
        rows = by_model[model]
        sims = [r["t1_t2_similarity"] for r in rows if r.get("t1_t2_similarity") is not None]
        if not sims:
            continue
        mean_sim = sum(sims) / len(sims)
        no_change = sum(1 for s in sims if s > 0.9)
        targeted = sum(1 for s in sims if 0.4 <= s <= 0.9)
        rewrite = sum(1 for s in sims if s < 0.4)
        lines.append(
            f"| {model_short(model)} | {mean_sim:.3f} | {no_change} ({100*no_change/len(sims):.0f}%) "
            f"| {targeted} ({100*targeted/len(sims):.0f}%) | {rewrite} ({100*rewrite/len(sims):.0f}%) |"
        )
    lines.append("")

    # ==========================================
    # 6. C1 Prompt Type Distribution
    # ==========================================
    lines.append("## 6. C1 Prompt Selection\n")
    c1_rows = [r for r in results if r.get("subfamily") == "C1"]
    if c1_rows:
        lines.append("| Model | Primary (>500ch) | Fallback (≤500ch) |")
        lines.append("|-------|-----------------|------------------|")
        for model in sorted(by_model.keys()):
            c1_m = [r for r in c1_rows if r["model"] == model]
            primary = sum(1 for r in c1_m if r.get("c1_prompt_type") == "primary")
            fallback = sum(1 for r in c1_m if r.get("c1_prompt_type") == "fallback")
            lines.append(f"| {model_short(model)} | {primary} | {fallback} |")
        lines.append("")

    # ==========================================
    # 7. Per-item difficulty (cross-model)
    # ==========================================
    lines.append("## 7. Item Difficulty Profile\n")
    lines.append("Items with T1 accuracy < 100% across models (potential WR differentiators):\n")
    lines.append("| Item | Subfamily | Stratum | T1 Acc (across models) | T2 Acc | W→R |")
    lines.append("|------|-----------|---------|----------------------|--------|-----|")

    by_item = defaultdict(list)
    for r in results:
        by_item[r["item_id"]].append(r)

    interesting = []
    for item_id, rows in sorted(by_item.items()):
        t1c = sum(1 for r in rows if r.get("t1_correct"))
        t2c = sum(1 for r in rows if r.get("t2_correct"))
        wr = sum(1 for r in rows if r["transition"] == "wrong_to_right")
        t1a = t1c / len(rows)
        if t1a < 1.0:
            interesting.append((item_id, rows[0]["subfamily"], rows[0]["stratum"],
                              t1a, t2c / len(rows), wr))

    interesting.sort(key=lambda x: x[3])  # sort by T1 accuracy
    for item_id, sub, strat, t1a, t2a, wr in interesting:
        lines.append(f"| {item_id} | {sub} | {strat} | {100*t1a:.0f}% | {100*t2a:.0f}% | {wr} |")
    lines.append("")

    # ==========================================
    # 8. Gradeability check
    # ==========================================
    lines.append("## 8. Gradeability Gate\n")
    total = len(results)
    gradeable = sum(1 for r in results if r.get("t1_response") and r.get("t2_response")
                    and not r.get("t1_error") and not r.get("t2_error"))
    pct = 100 * gradeable / total if total else 0
    lines.append(f"Gradeable output: {gradeable}/{total} ({pct:.1f}%)")
    gate = "PASS" if pct >= 90 else "FAIL"
    lines.append(f"Gate (≥90%): **{gate}**\n")

    return "\n".join(lines)


if __name__ == "__main__":
    results = load_all_results()
    if not results:
        print("No results found in", OUTPUT_DIR)
        sys.exit(1)

    report = analyze(results)

    # Save report
    report_path = OUTPUT_DIR / "sweep_v2_analysis.md"
    with open(report_path, "w") as f:
        f.write(report)
    print(report)
    print(f"\nReport saved to: {report_path}")

    # Also save to workspace for easy access
    workspace_path = Path("/home/user/workspace/sweep_v2_analysis.md")
    with open(workspace_path, "w") as f:
        f.write(report)
