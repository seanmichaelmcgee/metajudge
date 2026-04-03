# Notebook Report Generation Cells (v6.1)

These cells go after the `run + %choose` cell in each notebook. They generate a markdown audit report from the data already in memory and save it to OUTPUT_DIR.

Each cell also captures SDK usage data (tokens, cost, latency) from the run objects.

---

## Calibration Report Cell

```python
# Generate markdown audit report
from kaggle_benchmarks.usage import Usage

# Aggregate usage from Run 1
total_usage = Usage()
for r in cal_runs:
    if r.chat and r.chat.usage:
        total_usage = total_usage + r.chat.usage

# Build report
lines = []
lines.append(f"# MetaJudge v6.1 — Confidence Calibration Audit Report\n")
lines.append(f"**Model:** {str(kbench.llm)}")
lines.append(f"**Date:** {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
lines.append(f"**Task:** metajudge_calibration_v61 | **Grading engine:** grading_v2")
lines.append(f"**Items scored:** {len(records)}/{len(cal_eval)}\n")

# Performance summary
raw_score = float(audit["brier_score"].mean())
normalized = normalize(raw_score, ANCHOR_A_FLOOR, ANCHOR_A_CEIL)
acc = audit["is_correct"].mean()
mean_conf = audit["confidence"].astype(float).mean()
overconf_wrong = ((~audit["is_correct"]) & (audit["confidence"].astype(float) >= 0.9)).sum()

lines.append("## Performance Summary\n")
lines.append("| Metric | Value |")
lines.append("|--------|-------|")
lines.append(f"| Accuracy | {audit['is_correct'].sum()}/{len(audit)} ({acc:.1%}) |")
lines.append(f"| Mean 1-Brier | {raw_score:.4f} |")
lines.append(f"| Normalized score | {normalized:.3f} |")
lines.append(f"| Mean confidence | {mean_conf:.3f} |")
lines.append(f"| Overconfident wrong (conf ≥ 0.9) | {overconf_wrong} |")

# Usage / cost
lines.append("\n## Runtime and Cost\n")
lines.append("| Metric | Value |")
lines.append("|--------|-------|")
in_tok = total_usage.input_tokens or 0
out_tok = total_usage.output_tokens or 0
latency_ms = total_usage.total_backend_latency_ms or 0
in_cost = (total_usage.input_tokens_cost_nanodollars or 0) / 1e9
out_cost = (total_usage.output_tokens_cost_nanodollars or 0) / 1e9
lines.append(f"| Input tokens | {in_tok:,} |")
lines.append(f"| Output tokens | {out_tok:,} |")
lines.append(f"| Latency | {latency_ms/1000:.1f}s |")
lines.append(f"| Input cost | ${in_cost:.4f} |")
lines.append(f"| Output cost | ${out_cost:.4f} |")
lines.append(f"| Total cost | ${in_cost + out_cost:.4f} |")

# Item-by-item
lines.append("\n## Item Detail\n")
lines.append("| Item | Gold | Model Answer | Conf | Correct | 1-Brier |")
lines.append("|------|------|-------------|------|---------|---------|")
for _, row in audit.sort_values("item_id").iterrows():
    correct_mark = "✓" if row["is_correct"] else "✗"
    ans = str(row["model_answer"])[:40]
    lines.append(f"| {row['item_id']} | {row['gold_answer'][:20]} | {ans} | {float(row['confidence']):.2f} | {correct_mark} | {float(row['brier_score']):.3f} |")

# Wrong items detail
wrong = audit[~audit["is_correct"]].sort_values("item_id")
if len(wrong) > 0:
    lines.append(f"\n## Wrong Items ({len(wrong)})\n")
    for _, row in wrong.iterrows():
        lines.append(f"### {row['item_id']}")
        lines.append(f"- **Gold:** {row['gold_answer']}")
        lines.append(f"- **Model:** {row['model_answer']}")
        lines.append(f"- **Confidence:** {float(row['confidence']):.2f}")
        lines.append(f"- **1-Brier:** {float(row['brier_score']):.3f}\n")

report_path = os.path.join(OUTPUT_DIR, f"MetaJudge_Calibration_{model_slug}_v6.1.md")
with open(report_path, "w") as f:
    f.write("\n".join(lines))
print(f"Audit report: {report_path}")
```

---

## Abstention Report Cell

```python
# Generate markdown audit report
from kaggle_benchmarks.usage import Usage

# Aggregate usage from both runs
total_usage_r1 = Usage()
for r in fb_runs_1:
    if r.chat and r.chat.usage:
        total_usage_r1 = total_usage_r1 + r.chat.usage

lines = []
lines.append(f"# MetaJudge v6.1 — Selective Abstention Audit Report\n")
lines.append(f"**Model:** {str(kbench.llm)}")
lines.append(f"**Date:** {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
lines.append(f"**Task:** metajudge_abstention_v61 | **Grading engine:** grading_v2")
lines.append(f"**Items scored:** {len(records_1)}/{len(fb_eval)}\n")

# Performance
uwaa = compute_uwaa(audit["utility"].tolist())
normalized = normalize(uwaa, ANCHOR_B_FLOOR, ANCHOR_B_CEIL)
act_acc = (audit["model_decision"] == audit["gold_action"]).mean()
neg_util = (audit["utility"].astype(float) < 0).sum()

lines.append("## Performance Summary\n")
lines.append("| Metric | Value |")
lines.append("|--------|-------|")
lines.append(f"| UWAA | {uwaa:.4f} |")
lines.append(f"| Normalized score | {normalized:.3f} |")
lines.append(f"| Action accuracy | {(audit['model_decision'] == audit['gold_action']).sum()}/{len(audit)} ({act_acc:.1%}) |")
lines.append(f"| Negative utility items | {neg_util} |")

# Action distribution cross-table
lines.append("\n## Action Distribution\n")
actions = ["answer", "clarify", "verify", "abstain"]
header = "| | " + " | ".join(f"Gold: {a}" for a in actions) + " |"
sep = "|---|" + "|".join(["---"] * len(actions)) + "|"
lines.append(header)
lines.append(sep)
for ma in actions:
    counts = []
    for ga in actions:
        c = ((audit["model_decision"] == ma) & (audit["gold_action"] == ga)).sum()
        counts.append(str(c))
    lines.append(f"| Model: {ma} | " + " | ".join(counts) + " |")

# Stochasticity
if has_stochasticity:
    lines.append("\n## Stochasticity (Dual-Run)\n")
    lines.append("| Metric | Run 1 | Run 2 |")
    lines.append("|--------|-------|-------|")
    lines.append(f"| UWAA | {uwaa:.4f} | {uwaa_2:.4f} |")
    lines.append(f"| Normalized | {normalized:.3f} | {norm_2:.3f} |")
    lines.append(f"| Items matched | {len(matched_pairs)}/{len(records_1)} |  |")
    stable_count = sum(1 for r1, r2 in matched_pairs if r1["model_decision"] == r2["model_decision"])
    lines.append(f"| Action stability | {stable_count}/{len(matched_pairs)} ({stable_count/len(matched_pairs):.0%}) |  |")
    lines.append(f"| Score range | {min(normalized, norm_2):.2f} – {max(normalized, norm_2):.2f} |  |")

# Usage / cost
lines.append("\n## Runtime and Cost\n")
lines.append("| Metric | Value |")
lines.append("|--------|-------|")
in_tok = total_usage_r1.input_tokens or 0
out_tok = total_usage_r1.output_tokens or 0
latency_ms = total_usage_r1.total_backend_latency_ms or 0
in_cost = (total_usage_r1.input_tokens_cost_nanodollars or 0) / 1e9
out_cost = (total_usage_r1.output_tokens_cost_nanodollars or 0) / 1e9
lines.append(f"| Input tokens | {in_tok:,} |")
lines.append(f"| Output tokens | {out_tok:,} |")
lines.append(f"| Latency | {latency_ms/1000:.1f}s |")
lines.append(f"| Input cost | ${in_cost:.4f} |")
lines.append(f"| Output cost | ${out_cost:.4f} |")
lines.append(f"| Total cost | ${in_cost + out_cost:.4f} |")

# Item detail
lines.append("\n## Item Detail\n")
lines.append("| Item | Gold Action | Model Decision | Correct | Utility |")
lines.append("|------|------------|---------------|---------|---------|")
for _, row in audit.sort_values("item_id").iterrows():
    correct_mark = "✓" if row["is_correct"] else "✗"
    lines.append(f"| {row['item_id']} | {row['gold_action']} | {row['model_decision']} | {correct_mark} | {float(row['utility']):+.1f} |")

# Negative utility detail
neg = audit[audit["utility"].astype(float) < 0].sort_values("item_id")
if len(neg) > 0:
    lines.append(f"\n## Negative Utility Items ({len(neg)})\n")
    for _, row in neg.iterrows():
        lines.append(f"### {row['item_id']}")
        lines.append(f"- **Gold action:** {row['gold_action']} | **Model:** {row['model_decision']}")
        lines.append(f"- **Answer:** {str(row['model_answer'])[:80]}")
        lines.append(f"- **Utility:** {float(row['utility']):+.1f}\n")

report_path = os.path.join(OUTPUT_DIR, f"MetaJudge_Abstention_{model_slug}_v6.1.md")
with open(report_path, "w") as f:
    f.write("\n".join(lines))
print(f"Audit report: {report_path}")
```

---

## SC C1 Report Cell

```python
# Generate markdown audit report
from kaggle_benchmarks.usage import Usage

total_usage_r1 = Usage()
for r in runs_1:
    if r.chat and r.chat.usage:
        total_usage_r1 = total_usage_r1 + r.chat.usage

lines = []
lines.append(f"# MetaJudge v6.1 — Intrinsic Self-Correction (C1) Audit Report\n")
lines.append(f"**Model:** {str(kbench.llm)}")
lines.append(f"**Date:** {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
lines.append(f"**Task:** metajudge_sc_c1_v61 | **Grading engine:** grading_v2")
lines.append(f"**Items scored:** {len(records_1)}/{len(sub_df)}\n")

# Performance
t1c = audit["t1_correct"].sum()
t2c = audit["t2_correct"].sum()
delta = float((t2c - t1c) / len(audit))
normalized = normalize(delta, ANCHOR_C1_FLOOR, ANCHOR_C1_CEIL)
damage = ((audit["t1_correct"]) & (~audit["t2_correct"])).sum()
corrections = ((~audit["t1_correct"]) & (audit["t2_correct"])).sum()

lines.append("## Performance Summary\n")
lines.append("| Metric | Value |")
lines.append("|--------|-------|")
lines.append(f"| T1 accuracy | {t1c}/{len(audit)} ({t1c/len(audit):.1%}) |")
lines.append(f"| T2 accuracy | {t2c}/{len(audit)} ({t2c/len(audit):.1%}) |")
lines.append(f"| T2-T1 delta | {delta:+.4f} |")
lines.append(f"| Normalized score | {normalized:.3f} |")
lines.append(f"| Damage events | {damage} |")
lines.append(f"| Correction gains | {corrections} |")

# Transition summary
from collections import Counter
trans = Counter(audit["transition"].tolist())
lines.append("\n## Transition Summary\n")
lines.append("| Transition | Count |")
lines.append("|-----------|-------|")
for t in ["maintain_correct", "correction_gain", "neutral_revision", "damage", "stubborn_wrong", "failed_revision"]:
    lines.append(f"| {t} | {trans.get(t, 0)} |")

# Damage items
damage_items = audit[audit["t1_correct"] & ~audit["t2_correct"]]
if len(damage_items) > 0:
    lines.append(f"\n## Damage Items ({len(damage_items)})\n")
    for _, row in damage_items.iterrows():
        lines.append(f"### {row['item_id']}")
        lines.append(f"- **T1:** {str(row['t1_answer'])[:80]} (correct)")
        lines.append(f"- **T2:** {str(row['t2_answer'])[:80]} (incorrect)")
        lines.append(f"- **Similarity:** {float(row['t1_t2_similarity']):.3f}\n")

# Stochasticity
if has_stochasticity:
    lines.append("\n## Stochasticity (Dual-Run)\n")
    lines.append("| Metric | Run 1 | Run 2 |")
    lines.append("|--------|-------|-------|")
    lines.append(f"| Delta | {delta:+.4f} | {delta_2:+.4f} |")
    lines.append(f"| Normalized | {normalized:.3f} | {norm_2:.3f} |")
    lines.append(f"| Items matched | {len(matched_pairs)}/{len(records_1)} |  |")
    trans_stable = sum(1 for r1, r2 in matched_pairs if r1["transition"] == r2["transition"])
    lines.append(f"| Transition stability | {trans_stable}/{len(matched_pairs)} ({trans_stable/len(matched_pairs):.0%}) |  |")
    lines.append(f"| Score range | {min(normalized, norm_2):.2f} – {max(normalized, norm_2):.2f} |  |")

    # Changed items
    changed = [(r1["item_id"], r1["transition"], r2["transition"])
               for r1, r2 in matched_pairs if r1["transition"] != r2["transition"]]
    if changed:
        lines.append("\n### Changed Items\n")
        lines.append("| Item | Run 1 | Run 2 |")
        lines.append("|------|-------|-------|")
        for iid, t1, t2 in changed:
            lines.append(f"| {iid} | {t1} | {t2} |")

# Usage / cost
lines.append("\n## Runtime and Cost\n")
lines.append("| Metric | Value |")
lines.append("|--------|-------|")
in_tok = total_usage_r1.input_tokens or 0
out_tok = total_usage_r1.output_tokens or 0
latency_ms = total_usage_r1.total_backend_latency_ms or 0
in_cost = (total_usage_r1.input_tokens_cost_nanodollars or 0) / 1e9
out_cost = (total_usage_r1.output_tokens_cost_nanodollars or 0) / 1e9
lines.append(f"| Input tokens | {in_tok:,} |")
lines.append(f"| Output tokens | {out_tok:,} |")
lines.append(f"| Latency | {latency_ms/1000:.1f}s |")
lines.append(f"| Input cost | ${in_cost:.4f} |")
lines.append(f"| Output cost | ${out_cost:.4f} |")
lines.append(f"| Total cost | ${in_cost + out_cost:.4f} |")

# Item-by-item table
lines.append("\n## Item Detail\n")
lines.append("| Item | T1 Correct | T2 Correct | Transition | Similarity |")
lines.append("|------|-----------|-----------|-----------|-----------|")
for _, row in audit.sort_values("item_id").iterrows():
    t1 = "✓" if row["t1_correct"] else "✗"
    t2 = "✓" if row["t2_correct"] else "✗"
    lines.append(f"| {row['item_id']} | {t1} | {t2} | {row['transition']} | {float(row['t1_t2_similarity']):.3f} |")

report_path = os.path.join(OUTPUT_DIR, f"MetaJudge_SC_C1_{model_slug}_v6.1.md")
with open(report_path, "w") as f:
    f.write("\n".join(lines))
print(f"Audit report: {report_path}")
```

---

## SC C2 Report Cell

Identical to C1 except:
- Title: "Evidence-Assisted Self-Correction (C2)"
- Task name: `metajudge_sc_c2_v61`
- Anchors: `ANCHOR_C2_FLOOR`, `ANCHOR_C2_CEIL`
- Filename: `MetaJudge_SC_C2_{model_slug}_v6.1.md`

```python
# Generate markdown audit report
from kaggle_benchmarks.usage import Usage

total_usage_r1 = Usage()
for r in runs_1:
    if r.chat and r.chat.usage:
        total_usage_r1 = total_usage_r1 + r.chat.usage

lines = []
lines.append(f"# MetaJudge v6.1 — Evidence-Assisted Self-Correction (C2) Audit Report\n")
lines.append(f"**Model:** {str(kbench.llm)}")
lines.append(f"**Date:** {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
lines.append(f"**Task:** metajudge_sc_c2_v61 | **Grading engine:** grading_v2")
lines.append(f"**Items scored:** {len(records_1)}/{len(sub_df)}\n")

# Performance
t1c = audit["t1_correct"].sum()
t2c = audit["t2_correct"].sum()
delta = float((t2c - t1c) / len(audit))
normalized = normalize(delta, ANCHOR_C2_FLOOR, ANCHOR_C2_CEIL)
damage = ((audit["t1_correct"]) & (~audit["t2_correct"])).sum()
corrections = ((~audit["t1_correct"]) & (audit["t2_correct"])).sum()

lines.append("## Performance Summary\n")
lines.append("| Metric | Value |")
lines.append("|--------|-------|")
lines.append(f"| T1 accuracy | {t1c}/{len(audit)} ({t1c/len(audit):.1%}) |")
lines.append(f"| T2 accuracy | {t2c}/{len(audit)} ({t2c/len(audit):.1%}) |")
lines.append(f"| T2-T1 delta | {delta:+.4f} |")
lines.append(f"| Normalized score | {normalized:.3f} |")
lines.append(f"| Damage events | {damage} |")
lines.append(f"| Correction gains | {corrections} |")

# Transition summary
from collections import Counter
trans = Counter(audit["transition"].tolist())
lines.append("\n## Transition Summary\n")
lines.append("| Transition | Count |")
lines.append("|-----------|-------|")
for t in ["maintain_correct", "correction_gain", "neutral_revision", "damage", "stubborn_wrong", "failed_revision"]:
    lines.append(f"| {t} | {trans.get(t, 0)} |")

# Damage items
damage_items = audit[audit["t1_correct"] & ~audit["t2_correct"]]
if len(damage_items) > 0:
    lines.append(f"\n## Damage Items ({len(damage_items)})\n")
    for _, row in damage_items.iterrows():
        lines.append(f"### {row['item_id']}")
        lines.append(f"- **T1:** {str(row['t1_answer'])[:80]} (correct)")
        lines.append(f"- **T2:** {str(row['t2_answer'])[:80]} (incorrect)")
        lines.append(f"- **Similarity:** {float(row['t1_t2_similarity']):.3f}\n")

# Stochasticity
if has_stochasticity:
    lines.append("\n## Stochasticity (Dual-Run)\n")
    lines.append("| Metric | Run 1 | Run 2 |")
    lines.append("|--------|-------|-------|")
    lines.append(f"| Delta | {delta:+.4f} | {delta_2:+.4f} |")
    lines.append(f"| Normalized | {normalized:.3f} | {norm_2:.3f} |")
    lines.append(f"| Items matched | {len(matched_pairs)}/{len(records_1)} |  |")
    trans_stable = sum(1 for r1, r2 in matched_pairs if r1["transition"] == r2["transition"])
    lines.append(f"| Transition stability | {trans_stable}/{len(matched_pairs)} ({trans_stable/len(matched_pairs):.0%}) |  |")
    lines.append(f"| Score range | {min(normalized, norm_2):.2f} – {max(normalized, norm_2):.2f} |  |")

    changed = [(r1["item_id"], r1["transition"], r2["transition"])
               for r1, r2 in matched_pairs if r1["transition"] != r2["transition"]]
    if changed:
        lines.append("\n### Changed Items\n")
        lines.append("| Item | Run 1 | Run 2 |")
        lines.append("|------|-------|-------|")
        for iid, t1, t2 in changed:
            lines.append(f"| {iid} | {t1} | {t2} |")

# Usage / cost
lines.append("\n## Runtime and Cost\n")
lines.append("| Metric | Value |")
lines.append("|--------|-------|")
in_tok = total_usage_r1.input_tokens or 0
out_tok = total_usage_r1.output_tokens or 0
latency_ms = total_usage_r1.total_backend_latency_ms or 0
in_cost = (total_usage_r1.input_tokens_cost_nanodollars or 0) / 1e9
out_cost = (total_usage_r1.output_tokens_cost_nanodollars or 0) / 1e9
lines.append(f"| Input tokens | {in_tok:,} |")
lines.append(f"| Output tokens | {out_tok:,} |")
lines.append(f"| Latency | {latency_ms/1000:.1f}s |")
lines.append(f"| Input cost | ${in_cost:.4f} |")
lines.append(f"| Output cost | ${out_cost:.4f} |")
lines.append(f"| Total cost | ${in_cost + out_cost:.4f} |")

# Item detail
lines.append("\n## Item Detail\n")
lines.append("| Item | T1 Correct | T2 Correct | Transition | Similarity |")
lines.append("|------|-----------|-----------|-----------|-----------|")
for _, row in audit.sort_values("item_id").iterrows():
    t1 = "✓" if row["t1_correct"] else "✗"
    t2 = "✓" if row["t2_correct"] else "✗"
    lines.append(f"| {row['item_id']} | {t1} | {t2} | {row['transition']} | {float(row['t1_t2_similarity']):.3f} |")

report_path = os.path.join(OUTPUT_DIR, f"MetaJudge_SC_C2_{model_slug}_v6.1.md")
with open(report_path, "w") as f:
    f.write("\n".join(lines))
print(f"Audit report: {report_path}")
```

---

## Variable Scoping Note

These cells reference variables from the main task cell (Cell 6):
- `records_1`, `records_2`, `audit`, `model_slug`, `normalized` — from the main task function

**Problem:** These are local to the `def metajudge_*_v61(llm)` function. They go out of scope when the function returns.

**Solution options:**
1. Move the report generation inside the main task function (before `return normalized`)
2. Re-read from the CSV/JSON files just written to OUTPUT_DIR
3. Store key variables in a module-level dict before returning

Option 1 is simplest — add the report lines inside the main task, after the export block but before `return`. The usage aggregation also needs to happen inside the function where the run objects are in scope.
