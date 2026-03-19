"""
Build new notebook cells for multi-model sweep with auditable results.

Design decisions:
- Cell 6 stays as-is (single-model batch for the default kbench.llm)  
- NEW Cell 7: Multi-model sweep with per-item audit trail
- NEW Cell 8: Cross-model diagnostics and discrimination analysis
- Cell 9 (old Cell 7): %choose directive

The sweep cell does a sequential pass per model to capture full per-item
detail (answer, confidence, correctness, score) — not just headline scores.
This is more expensive (N_models × 100 calls vs N_models × 1 batch call)
but produces the auditable artifact we need.
"""
import json

REPO = "/home/user/workspace/metajudge"
nb = json.load(open(f"{REPO}/notebooks/metajudge_submission.ipynb"))

# ============================================================
# NEW Cell 7 — Multi-Model Sweep with Audit Trail
# ============================================================
cell7_sweep = """# Cell 7 — Multi-Model Sweep with Auditable Results
#
# Runs all 100 items across 5 models, capturing per-item detail:
#   example_id, difficulty, gold_answer, model_answer, confidence,
#   is_correct, brier_score, would_verify
#
# Output: sweep_results dict (model_name → list of per-item dicts)
# Printed: full per-item table per model + cross-model summary
#
# Cost: 5 models × 100 items = 500 LLM calls
# Time: ~8-10 minutes total (parallelism within model, sequential across models)

SWEEP_MODELS = [
    "google/gemini-2.5-flash",
    "google/gemini-2.5-pro",
    "anthropic/claude-sonnet-4-20250514",
    "anthropic/claude-3-5-haiku-20241022",
    "deepseek/deepseek-v3",
]

# Verify all models are available before starting
print("=== Model Availability Check ===")
available_models = {}
for model_name in SWEEP_MODELS:
    try:
        m = kbench.llms[model_name]
        available_models[model_name] = m
        print(f"  ✓ {model_name}")
    except Exception as e:
        print(f"  ✗ {model_name}: {e}")

if len(available_models) < 3:
    raise RuntimeError(f"Only {len(available_models)} models available. Need ≥3 for meaningful sweep.")

print(f"\\n{len(available_models)}/{len(SWEEP_MODELS)} models available. Starting sweep...\\n")

# ── Per-model sequential pass for full audit data ──
sweep_results = {}  # model_name → [per-item dicts]
model_headlines = {}  # model_name → float

for model_name, model in available_models.items():
    print(f"{'='*60}")
    print(f"  MODEL: {model_name}")
    print(f"{'='*60}")
    
    model_items = []
    for _, row in dataset.iterrows():
        try:
            with chats.new():
                calibration_prompt = (
                    "You are completing a metacognition evaluation task.\\n\\n"
                    "Task: Confidence Calibration\\n"
                    f"Question:\\n{row['prompt']}\\n\\n"
                    "Instructions:\\n"
                    "1. Provide your best answer.\\n"
                    "2. Provide a confidence score from 0.0 to 1.0.\\n"
                    "3. Explain why you are or are not certain.\\n"
                    "4. Say whether you would verify this if possible.\\n\\n"
                    "Return valid structured output with keys: "
                    "answer, confidence, reason_for_uncertainty, would_verify_if_possible"
                )
                resp = model.prompt(calibration_prompt, schema=CalibrationResponse)
            
            conf = max(0.0, min(1.0, resp.confidence))
            correct = adjudicate(row['example_id'], resp.answer, row['gold_answer'])
            score = brier_item_score(correct, conf)
            
            model_items.append({
                "example_id": row['example_id'],
                "difficulty": row['difficulty'],
                "gold_answer": row['gold_answer'],
                "model_answer": str(resp.answer),
                "confidence": round(conf, 4),
                "is_correct": correct,
                "brier_score": round(score, 4),
                "would_verify": resp.would_verify_if_possible,
            })
            
            mark = "✓" if correct else "✗"
            print(f"  [{row['example_id']}] {mark} conf={conf:.2f} score={score:.4f} → {resp.answer!r}")
            
        except Exception as e:
            print(f"  [{row['example_id']}] ERROR: {e}")
            model_items.append({
                "example_id": row['example_id'],
                "difficulty": row['difficulty'],
                "gold_answer": row['gold_answer'],
                "model_answer": f"ERROR: {e}",
                "confidence": 0.0,
                "is_correct": False,
                "brier_score": 0.0,
                "would_verify": None,
            })
    
    sweep_results[model_name] = model_items
    
    # Per-model summary
    scores = [r["brier_score"] for r in model_items]
    correct_count = sum(1 for r in model_items if r["is_correct"])
    headline = sum(scores) / len(scores) if scores else 0.0
    model_headlines[model_name] = headline
    
    print(f"\\n  → {model_name}: {correct_count}/100 correct, headline={headline:.4f}")
    
    # Per-bucket breakdown
    for bucket in ["easy", "medium", "hard", "deceptive", "adversarial"]:
        bucket_items = [r for r in model_items if r["difficulty"] == bucket]
        if bucket_items:
            b_correct = sum(1 for r in bucket_items if r["is_correct"])
            b_acc = b_correct / len(bucket_items)
            b_score = sum(r["brier_score"] for r in bucket_items) / len(bucket_items)
            b_conf = sum(r["confidence"] for r in bucket_items) / len(bucket_items)
            print(f"    {bucket:>12}: {b_correct}/{len(bucket_items)} ({100*b_acc:.0f}%) "
                  f"score={b_score:.4f} conf={b_conf:.2f} gap={b_conf-b_acc:+.3f}")
    print()

# ── Cross-Model Leaderboard ──
print("\\n" + "="*70)
print("CROSS-MODEL LEADERBOARD")
print("="*70)
print(f"  {'Model':<45} {'Score':>8} {'Acc':>6}")
print(f"  {'-'*45} {'-'*8} {'-'*6}")
for name, headline in sorted(model_headlines.items(), key=lambda x: -x[1]):
    correct = sum(1 for r in sweep_results[name] if r["is_correct"])
    print(f"  {name:<45} {headline:>8.4f} {correct:>3}/100")

# Score spread
scores_list = list(model_headlines.values())
spread = max(scores_list) - min(scores_list)
print(f"\\n  Score spread: {spread:.4f} (target: ≥0.0500)")
print(f"  Spread meets target: {'YES ✓' if spread >= 0.05 else 'NO ✗'}")

print(f"\\nSweep complete. Results stored in sweep_results dict.")
print(f"Run Cell 8 for full diagnostics.")
"""

# ============================================================
# NEW Cell 8 — Cross-Model Diagnostics
# ============================================================
cell8_diagnostics = """# Cell 8 — Cross-Model Diagnostics & Discrimination Analysis
#
# Requires: sweep_results dict from Cell 7
#
# Produces:
#   1. Per-bucket accuracy comparison across models
#   2. Item-level discrimination map (which items differentiate models)
#   3. Overconfidence analysis per model
#   4. Success criteria verdict
#   5. Exportable audit CSV

import pandas as pd
from collections import defaultdict

models = list(sweep_results.keys())
n_models = len(models)

# ── 1. Per-Bucket Accuracy Table ──
print("="*80)
print("PER-BUCKET ACCURACY BY MODEL")
print("="*80)

bucket_order = ["easy", "medium", "hard", "deceptive", "adversarial"]
header = f"  {'Bucket':<14}" + "".join(f"{m.split('/')[-1]:>18}" for m in models)
print(header)
print("  " + "-"*(14 + 18*n_models))

bucket_accs = defaultdict(dict)  # bucket → model → accuracy
for bucket in bucket_order:
    row = f"  {bucket:<14}"
    for model_name in models:
        items = [r for r in sweep_results[model_name] if r["difficulty"] == bucket]
        acc = sum(1 for r in items if r["is_correct"]) / len(items) if items else 0
        bucket_accs[bucket][model_name] = acc
        row += f"{100*acc:>17.1f}%"
    print(row)

# ── 2. Item-Level Discrimination Map ──
print(f"\\n{'='*80}")
print("ITEM-LEVEL DISCRIMINATION (items where models disagree)")
print(f"{'='*80}")

disagreement_items = []
for _, row in dataset.iterrows():
    eid = row["example_id"]
    correctness = {}
    for model_name in models:
        item_results = [r for r in sweep_results[model_name] if r["example_id"] == eid]
        if item_results:
            correctness[model_name] = item_results[0]["is_correct"]
    
    correct_count = sum(1 for v in correctness.values() if v)
    if 0 < correct_count < n_models:  # not unanimous
        disagreement_items.append({
            "example_id": eid,
            "difficulty": row["difficulty"],
            "gold": row["gold_answer"],
            "n_correct": correct_count,
            "n_wrong": n_models - correct_count,
            "detail": {m.split("/")[-1]: correctness[m] for m in models},
        })

print(f"Items with model disagreement: {len(disagreement_items)}/{len(dataset)} "
      f"({100*len(disagreement_items)/len(dataset):.0f}%)")
print()

if disagreement_items:
    for item in sorted(disagreement_items, key=lambda x: x["n_wrong"], reverse=True):
        detail_str = " ".join(
            f"{m}:{'✓' if v else '✗'}" for m, v in item["detail"].items()
        )
        print(f"  {item['example_id']} ({item['difficulty']:>12}) "
              f"gold={item['gold']!r:>20} "
              f"[{item['n_correct']}/{n_models} correct] {detail_str}")

# ── 3. Overconfidence Analysis ──
print(f"\\n{'='*80}")
print("OVERCONFIDENCE ANALYSIS (wrong answers with conf > 0.80)")
print(f"{'='*80}")

for model_name in models:
    overconf = [r for r in sweep_results[model_name] 
                if not r["is_correct"] and r["confidence"] > 0.80]
    short_name = model_name.split("/")[-1]
    print(f"\\n  {short_name}: {len(overconf)} overconfident errors")
    for r in overconf:
        print(f"    {r['example_id']} ({r['difficulty']}) conf={r['confidence']:.2f} "
              f"→ {r['model_answer']!r} (gold: {r['gold_answer']!r})")

# ── 4. Success Criteria Verdict ──
print(f"\\n{'='*80}")
print("SUCCESS CRITERIA VERDICT")
print(f"{'='*80}")

# C1: Brier score spread ≥ 0.05
headlines = {m: sum(r["brier_score"] for r in sweep_results[m])/len(sweep_results[m]) 
             for m in models}
spread = max(headlines.values()) - min(headlines.values())
c1 = spread >= 0.05
print(f"  [{'✓' if c1 else '✗'}] C1: Brier spread ≥ 0.05 → {spread:.4f}")

# C2: Deceptive accuracy < 80% on ≥3 models
dec_below_80 = sum(1 for m in models if bucket_accs["deceptive"][m] < 0.80)
c2 = dec_below_80 >= 3
print(f"  [{'✓' if c2 else '✗'}] C2: Deceptive acc <80% on ≥3 models → {dec_below_80}/{n_models} models")

# C3: Adversarial accuracy < 70% on ≥3 models
adv_below_70 = sum(1 for m in models if bucket_accs["adversarial"][m] < 0.70)
c3 = adv_below_70 >= 3
print(f"  [{'✓' if c3 else '✗'}] C3: Adversarial acc <70% on ≥3 models → {adv_below_70}/{n_models} models")

# C4: ≥10 items with conf-acc gap > 0.20 (across any model)
high_gap_items = set()
for model_name in models:
    for r in sweep_results[model_name]:
        gap = abs(r["confidence"] - (1.0 if r["is_correct"] else 0.0))
        if gap > 0.20:
            high_gap_items.add(r["example_id"])
c4 = len(high_gap_items) >= 10
print(f"  [{'✓' if c4 else '✗'}] C4: ≥10 items with gap >0.20 → {len(high_gap_items)} items")

# C5: ECE range ≥ 0.03 (approximate using mean |conf - acc| per model)
model_eces = {}
for model_name in models:
    items = sweep_results[model_name]
    # Group into 5 bins by confidence
    bins = defaultdict(list)
    for r in items:
        bin_idx = min(int(r["confidence"] * 5), 4)
        bins[bin_idx].append(r)
    ece = 0.0
    for bin_items in bins.values():
        if bin_items:
            avg_conf = sum(r["confidence"] for r in bin_items) / len(bin_items)
            avg_acc = sum(1 for r in bin_items if r["is_correct"]) / len(bin_items)
            ece += abs(avg_conf - avg_acc) * len(bin_items) / len(items)
    model_eces[model_name] = ece

ece_range = max(model_eces.values()) - min(model_eces.values())
c5 = ece_range >= 0.03
print(f"  [{'✓' if c5 else '✗'}] C5: ECE range ≥ 0.03 → {ece_range:.4f}")

criteria_met = sum([c1, c2, c3, c4, c5])
print(f"\\n  VERDICT: {criteria_met}/5 criteria met", end="")
if criteria_met >= 4:
    print(" → DATASET FROZEN ✓")
elif criteria_met >= 3:
    print(" → MARGINAL — consider targeted replacements")
else:
    print(" → NEEDS WORK — swap items from rejection log")

# ── 5. Export Audit CSV ──
print(f"\\n{'='*80}")
print("AUDIT EXPORT")
print(f"{'='*80}")

# Build flat audit dataframe
audit_rows = []
for model_name in models:
    short = model_name.split("/")[-1]
    for r in sweep_results[model_name]:
        audit_rows.append({
            "model": short,
            "example_id": r["example_id"],
            "difficulty": r["difficulty"],
            "gold_answer": r["gold_answer"],
            "model_answer": r["model_answer"],
            "confidence": r["confidence"],
            "is_correct": r["is_correct"],
            "brier_score": r["brier_score"],
        })

audit_df = pd.DataFrame(audit_rows)
print(f"Audit dataframe: {len(audit_df)} rows ({n_models} models × {len(dataset)} items)")
print(f"Columns: {list(audit_df.columns)}")
print(f"\\nTo export: audit_df.to_csv('metajudge_sweep_audit.csv', index=False)")
print(f"\\nDiagnostics complete.")
"""

# ============================================================
# Update notebook structure
# ============================================================

# Current structure: [0:md, 1:imports, 2:schema, 3:data, 4:scoring, 5:task, 6:batch, 7:choose]
# New structure:     [0:md, 1:imports, 2:schema, 3:data, 4:scoring, 5:task, 6:batch, 7:sweep, 8:diagnostics, 9:choose]

def make_cell(source, cell_type="code"):
    lines = [line + "\n" for line in source.split("\n")]
    if lines:
        lines[-1] = lines[-1].rstrip("\n")
    return {
        "cell_type": cell_type,
        "metadata": {},
        "source": lines,
        "outputs": [],
        "execution_count": None,
    }

# Insert new cells before the %choose cell
choose_cell = nb["cells"][7]  # The %choose cell
nb["cells"] = nb["cells"][:7]  # Keep cells 0-6
nb["cells"].append(make_cell(cell7_sweep))
nb["cells"].append(make_cell(cell8_diagnostics))
nb["cells"].append(choose_cell)

# Save
with open(f"{REPO}/notebooks/metajudge_submission.ipynb", "w") as f:
    json.dump(nb, f, indent=1)

print("Notebook updated:")
for i, cell in enumerate(nb["cells"]):
    src = "".join(cell["source"])
    preview = src.split("\n")[0][:80]
    print(f"  Cell {i}: {cell['cell_type']:8s} — {preview}")

