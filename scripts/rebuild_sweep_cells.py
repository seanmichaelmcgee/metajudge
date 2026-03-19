"""
Rebuild notebook cells to align with Kaggle's recommended multi-model workflow.

Architecture:
  Cell 0: Markdown header
  Cell 1: Imports & environment (+ model discovery)
  Cell 2: Response schema
  Cell 3: Embedded dataset & answer key
  Cell 4: Scoring & adjudication functions
  Cell 5: Task definition (per-item) + smoke test
  Cell 6: Batch evaluation (single model via evaluate() — official %choose target)
  Cell 7: Multi-model sweep via evaluate(llm=models) — uses SDK properly
  Cell 8: Detailed audit sweep (per-item sequential — optional, expensive)
  Cell 9: Cross-model diagnostics (works with Cell 7 or Cell 8 output)
  Cell 10: %choose
"""
import json

REPO = "/home/user/workspace/metajudge"
nb = json.load(open(f"{REPO}/notebooks/metajudge_submission.ipynb"))

# ============================================================
# Update Cell 1: Add model discovery
# ============================================================
cell1_src = ''.join(nb['cells'][1]['source'])
# Add model discovery at the end if not already there
if 'kbench.llms' not in cell1_src:
    cell1_src += """

# ── Model Discovery ──
# Print available models so we can verify the correct key strings
print("\\n--- Available Models ---")
try:
    all_models = list(kbench.llms.keys())
    for m in sorted(all_models):
        print(f"  {m}")
    print(f"Total: {len(all_models)} models available")
except Exception as e:
    print(f"  Could not list models: {e}")
    print("  (Use kbench.llms['provider/model-name'] to access specific models)")
"""
    nb['cells'][1]['source'] = [line + "\n" for line in cell1_src.split("\n")]
    nb['cells'][1]['source'][-1] = nb['cells'][1]['source'][-1].rstrip("\n")

# ============================================================
# Cell 7 — Multi-Model Sweep via evaluate() (SDK-aligned)
# ============================================================
cell7_evaluate = """# Cell 7 — Multi-Model Sweep via evaluate()
#
# Uses the Kaggle Benchmarks SDK evaluate() API with multiple models.
# This is the SDK-recommended approach for in-notebook multi-model runs.
#
# NOTE: The Kaggle-recommended approach for official leaderboard entries is:
#   1. Run Cell 6 (single model batch)
#   2. Save via %choose (Cell 10)
#   3. Use "Evaluate More Models" button on the Task Detail page
#
# Cell 7 is for development/validation — it runs all models in one go
# and captures headline scores. For per-item audit detail, use Cell 8.
#
# Model keys: verify via Cell 1 output (kbench.llms.keys())
# Update SWEEP_MODELS if the keys don't match.

SWEEP_MODELS = [
    "google/gemini-2.5-flash",
    "google/gemini-2.5-pro",
    "anthropic/claude-sonnet-4-20250514",
    "anthropic/claude-3-5-haiku-20241022",
    "deepseek/deepseek-v3",
]

# Step 1: Verify model availability
print("=== Model Availability ===")
verified_models = {}
for model_name in SWEEP_MODELS:
    try:
        m = kbench.llms[model_name]
        verified_models[model_name] = m
        print(f"  ✓ {model_name}")
    except KeyError:
        print(f"  ✗ {model_name} — not found in kbench.llms")
        print(f"    Check Cell 1 output for available model keys")

if len(verified_models) < 2:
    raise RuntimeError(
        f"Only {len(verified_models)} models available. "
        f"Need ≥2 for a meaningful sweep. "
        f"Update SWEEP_MODELS with keys from: list(kbench.llms.keys())"
    )

print(f"\\n{len(verified_models)}/{len(SWEEP_MODELS)} models verified.\\n")

# Step 2: Run evaluate() with all verified models
# The SDK handles multi-model execution when llm is a list
model_objects = list(verified_models.values())
model_names = list(verified_models.keys())

print("=== Running Multi-Model Evaluation ===")
print(f"Models: {len(model_objects)}")
print(f"Items per model: {len(dataset)}")
print(f"Total LLM calls: ~{len(model_objects) * len(dataset)}")
print()

with kbench.client.enable_cache():
    sweep_runs = metacog_calibration.evaluate(
        stop_condition=lambda runs: len(runs) == len(dataset) * len(model_objects),
        max_attempts=1,
        llm=model_objects,
        evaluation_data=dataset,
        n_jobs=3,
    )

sweep_df = sweep_runs.as_dataframe()
print(f"\\nSweep complete. Results dataframe: {sweep_df.shape}")
print(f"Columns: {list(sweep_df.columns)}")
print(sweep_df.head(10))

# Step 3: Extract per-model scores
# Note: the dataframe structure depends on SDK version.
# We'll inspect and adapt.
print("\\n=== Per-Model Results ===")
print(sweep_df.describe())
"""

# ============================================================
# Cell 8 — Detailed Audit Sweep (per-item sequential)
# ============================================================
cell8_audit = """# Cell 8 — Detailed Audit Sweep (Sequential Per-Item)
#
# This cell runs each model sequentially through all 100 items,
# capturing the FULL per-item audit trail:
#   model_answer, confidence, is_correct, brier_score, would_verify
#
# This is MORE EXPENSIVE than Cell 7 (same 500 calls, but sequential
# within each model). Use this when you need per-item diagnostics.
#
# Set RUN_AUDIT = True to execute. Default is False to avoid
# accidental quota burn.

RUN_AUDIT = False  # ← Set to True to run the full audit sweep

if not RUN_AUDIT:
    print("Audit sweep disabled. Set RUN_AUDIT = True in this cell to run.")
    print("This will make ~500 LLM calls and take ~10 minutes.")
    print("Use Cell 7 for quick multi-model headline scores instead.")
else:
    # Use same SWEEP_MODELS from Cell 7
    audit_models = {}
    for model_name in SWEEP_MODELS:
        try:
            audit_models[model_name] = kbench.llms[model_name]
        except KeyError:
            pass
    
    print(f"=== Audit Sweep: {len(audit_models)} models × {len(dataset)} items ===\\n")
    
    sweep_results = {}  # model_name → [per-item dicts]
    
    for model_name, model in audit_models.items():
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
                print(f"  [{row['example_id']}] {mark} conf={conf:.2f} "
                      f"score={score:.4f} → {resp.answer!r}")
                
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
        
        print(f"\\n  → {correct_count}/100 correct, headline={headline:.4f}")
        for bucket in ["easy", "medium", "hard", "deceptive", "adversarial"]:
            bucket_items = [r for r in model_items if r["difficulty"] == bucket]
            if bucket_items:
                b_correct = sum(1 for r in bucket_items if r["is_correct"])
                b_acc = b_correct / len(bucket_items)
                b_score = sum(r["brier_score"] for r in bucket_items) / len(bucket_items)
                b_conf = sum(r["confidence"] for r in bucket_items) / len(bucket_items)
                print(f"    {bucket:>12}: {b_correct}/{len(bucket_items)} "
                      f"({100*b_acc:.0f}%) score={b_score:.4f} "
                      f"conf={b_conf:.2f} gap={b_conf-b_acc:+.3f}")
        print()
    
    # Cross-model leaderboard
    print("\\n" + "="*70)
    print("CROSS-MODEL LEADERBOARD")
    print("="*70)
    for name in sorted(sweep_results.keys(),
                       key=lambda n: -sum(r["brier_score"] for r in sweep_results[n])/len(sweep_results[n])):
        items = sweep_results[name]
        headline = sum(r["brier_score"] for r in items) / len(items)
        correct = sum(1 for r in items if r["is_correct"])
        print(f"  {name:<45} {headline:.4f}  ({correct}/100)")
    
    print(f"\\nAudit sweep complete. Run Cell 9 for diagnostics.")
"""

# ============================================================
# Cell 9 — Cross-Model Diagnostics
# ============================================================
cell9_diagnostics = """# Cell 9 — Cross-Model Diagnostics & Discrimination Analysis
#
# Requires: sweep_results dict from Cell 8 (audit sweep)
# If Cell 8 was not run, this cell will report that and exit.

from collections import defaultdict

if 'sweep_results' not in dir() or not sweep_results:
    print("No audit sweep data found.")
    print("Run Cell 8 with RUN_AUDIT=True first, or use Cell 7 for quick headline scores.")
    print("Cell 7 uses evaluate() which is faster but doesn't capture per-item detail.")
else:
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
    
    bucket_accs = defaultdict(dict)
    for bucket in bucket_order:
        row_str = f"  {bucket:<14}"
        for model_name in models:
            items = [r for r in sweep_results[model_name] if r["difficulty"] == bucket]
            acc = sum(1 for r in items if r["is_correct"]) / len(items) if items else 0
            bucket_accs[bucket][model_name] = acc
            row_str += f"{100*acc:>17.1f}%"
        print(row_str)
    
    # ── 2. Item-Level Discrimination Map ──
    print(f"\\n{'='*80}")
    print("DISCRIMINATION MAP (items where models disagree)")
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
        if 0 < correct_count < n_models:
            disagreement_items.append({
                "example_id": eid,
                "difficulty": row["difficulty"],
                "gold": row["gold_answer"],
                "n_correct": correct_count,
                "detail": {m.split("/")[-1]: correctness[m] for m in models},
            })
    
    print(f"Discriminating items: {len(disagreement_items)}/{len(dataset)} "
          f"({100*len(disagreement_items)/len(dataset):.0f}%)")
    
    for item in sorted(disagreement_items, key=lambda x: x["n_correct"]):
        detail = " ".join(f"{m}:{'✓' if v else '✗'}" for m, v in item["detail"].items())
        print(f"  {item['example_id']} ({item['difficulty']:>12}) "
              f"gold={item['gold']!r:>20} [{item['n_correct']}/{n_models}] {detail}")
    
    # ── 3. Overconfidence Report ──
    print(f"\\n{'='*80}")
    print("OVERCONFIDENCE (wrong + conf > 0.80)")
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
    
    headlines = {m: sum(r["brier_score"] for r in sweep_results[m])/len(sweep_results[m])
                 for m in models}
    
    spread = max(headlines.values()) - min(headlines.values())
    c1 = spread >= 0.05
    print(f"  [{'✓' if c1 else '✗'}] C1: Brier spread ≥ 0.05 → {spread:.4f}")
    
    dec_below = sum(1 for m in models if bucket_accs["deceptive"][m] < 0.80)
    c2 = dec_below >= 3
    print(f"  [{'✓' if c2 else '✗'}] C2: Deceptive <80% on ≥3 → {dec_below}/{n_models}")
    
    adv_below = sum(1 for m in models if bucket_accs["adversarial"][m] < 0.70)
    c3 = adv_below >= 3
    print(f"  [{'✓' if c3 else '✗'}] C3: Adversarial <70% on ≥3 → {adv_below}/{n_models}")
    
    gap_items = set()
    for mn in models:
        for r in sweep_results[mn]:
            gap = abs(r["confidence"] - (1.0 if r["is_correct"] else 0.0))
            if gap > 0.20:
                gap_items.add(r["example_id"])
    c4 = len(gap_items) >= 10
    print(f"  [{'✓' if c4 else '✗'}] C4: ≥10 gap items → {len(gap_items)}")
    
    model_eces = {}
    for mn in models:
        items = sweep_results[mn]
        bins = defaultdict(list)
        for r in items:
            bins[min(int(r["confidence"] * 5), 4)].append(r)
        ece = sum(
            abs(sum(r["confidence"] for r in bi)/len(bi) - sum(1 for r in bi if r["is_correct"])/len(bi))
            * len(bi) / len(items)
            for bi in bins.values() if bi
        )
        model_eces[mn] = ece
    
    ece_range = max(model_eces.values()) - min(model_eces.values())
    c5 = ece_range >= 0.03
    print(f"  [{'✓' if c5 else '✗'}] C5: ECE range ≥ 0.03 → {ece_range:.4f}")
    
    total = sum([c1, c2, c3, c4, c5])
    verdict = "FREEZE ✓" if total >= 4 else "MARGINAL" if total >= 3 else "NEEDS WORK"
    print(f"\\n  VERDICT: {total}/5 → {verdict}")
    
    # ── 5. Audit CSV ──
    audit_rows = []
    for mn in models:
        short = mn.split("/")[-1]
        for r in sweep_results[mn]:
            audit_rows.append({"model": short, **{k: v for k, v in r.items() if k != "would_verify"}})
    
    audit_df = pd.DataFrame(audit_rows)
    print(f"\\nAudit CSV: {len(audit_df)} rows. Export with:")
    print(f"  audit_df.to_csv('metajudge_sweep_audit.csv', index=False)")
"""

# ============================================================
# Assemble notebook
# ============================================================

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

# Keep cells 0-6 (md, imports+discovery, schema, data, scoring, task, batch)
# Replace/add cells 7-10
choose_source = "%choose metacog_calibration_v1_batch"

nb["cells"] = nb["cells"][:7]  # Keep 0-6
nb["cells"].append(make_cell(cell7_evaluate))     # New Cell 7
nb["cells"].append(make_cell(cell8_audit))         # New Cell 8
nb["cells"].append(make_cell(cell9_diagnostics))   # New Cell 9
nb["cells"].append(make_cell(choose_source))       # Cell 10

# Save
with open(f"{REPO}/notebooks/metajudge_submission.ipynb", "w") as f:
    json.dump(nb, f, indent=1)

print("Notebook rebuilt. Cell structure:")
for i, cell in enumerate(nb["cells"]):
    src = "".join(cell["source"])
    first_line = src.split("\n")[0][:80]
    print(f"  Cell {i:2d}: {cell['cell_type']:8s} — {first_line}")

