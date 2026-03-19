"""Analyze Gemini 2.5 Flash results from the V2 100-item sweep."""
import json, csv

REPO = "/home/user/workspace/metajudge"

# Load dataset for difficulty labels
with open(f"{REPO}/data/calibration.csv") as f:
    rows = {r["example_id"]: r for r in csv.DictReader(f)}

# Parse the output manually from the user's paste
# Format: [cal_NNN] answer='X', conf=Y, correct=True/False, score=Z
results = []
raw = """cal_001,65,1.00,False,0.0000
cal_002,10,1.00,True,1.0000
cal_003,365,1.00,True,1.0000
cal_004,8,1.00,True,1.0000
cal_005,7,1.00,True,1.0000
cal_006,H2O,1.00,True,1.0000
cal_007,24,1.00,True,1.0000
cal_008,Paris,1.00,True,1.0000
cal_009,5,1.00,True,1.0000
cal_010,144,1.00,True,1.0000
cal_011,19,0.90,True,0.9900
cal_012,1912,1.00,True,1.0000
cal_013,Jupiter,1.00,True,1.0000
cal_014,George Orwell,1.00,True,1.0000
cal_015,Vatican City,1.00,True,1.0000
cal_016,Hydrogen,1.00,True,1.0000
cal_017,Yen,1.00,True,1.0000
cal_018,7,1.00,True,1.0000
cal_019,China,1.00,True,1.0000
cal_020,300000,1.00,True,1.0000
cal_021,Carbon Dioxide,1.00,True,1.0000
cal_022,11,1.00,True,1.0000
cal_023,Mandarin,0.98,True,0.9996
cal_024,Diamond,1.00,True,1.0000
cal_025,8,1.00,True,1.0000
cal_026,Mount Everest,1.00,True,1.0000
cal_027,27,0.95,True,0.9975
cal_028,Immanuel Kant,1.00,True,1.0000
cal_029,Na,1.00,True,1.0000
cal_030,55,1.00,True,1.0000
cal_031,88,1.00,True,1.0000
cal_032,Liver,1.00,True,1.0000
cal_033,1991,1.00,True,1.0000
cal_034,Iron,1.00,True,1.0000
cal_035,6,1.00,True,1.0000
cal_036,Equilateral,1.00,True,1.0000
cal_037,Mount Chimborazo,0.95,True,0.9975
cal_038,27,0.90,True,0.9900
cal_039,10,0.95,True,0.9975
cal_040,9,0.95,True,0.9975
cal_041,16,0.95,True,0.9975
cal_042,52,1.00,True,1.0000
cal_043,65536,1.00,True,1.0000
cal_044,12,1.00,True,1.0000
cal_045,720,1.00,True,1.0000
cal_046,940000000,0.95,True,0.9975
cal_047,1,0.90,True,0.9900
cal_048,8,0.99,True,0.9999
cal_049,128,1.00,True,1.0000
cal_050,8,1.00,True,1.0000
cal_051,5280,1.00,True,1.0000
cal_052,7,1.00,True,1.0000
cal_053,10080,1.00,True,1.0000
cal_054,880,1.00,True,1.0000
cal_055,101,1.00,True,1.0000
cal_056,2444,1.00,True,1.0000
cal_057,540,0.98,True,0.9996
cal_058,21,0.95,True,0.9975
cal_059,8,0.95,True,0.9975
cal_060,10,1.00,True,1.0000
cal_061,15,0.95,True,0.9975
cal_062,72,1.00,True,1.0000
cal_063,26,0.90,True,0.9900
cal_064,6561,1.00,True,1.0000
cal_065,11,0.90,False,0.1900
cal_066,144,1.00,True,1.0000
cal_067,Nintendo,1.00,True,1.0000
cal_068,71,0.95,True,0.9975
cal_069,Nitrogen,1.00,True,1.0000
cal_070,Wellington,1.00,True,1.0000
cal_071,no,0.95,True,0.9975
cal_072,no,0.99,True,0.9999
cal_073,Fruit,1.00,True,1.0000
cal_074,Atlantic Ocean,0.90,True,0.9900
cal_075,Lithium,1.00,True,1.0000
cal_076,Mauna Kea,0.95,True,0.9975
cal_077,Canada,0.95,True,0.9975
cal_078,116,1.00,True,1.0000
cal_079,Hydrogen,1.00,True,1.0000
cal_080,no,1.00,True,1.0000
cal_081,Yes,1.00,True,1.0000
cal_082,no,0.95,True,0.9975
cal_083,no,0.95,True,0.9975
cal_084,Yes,0.85,False,0.2775
cal_085,no,1.00,True,1.0000
cal_086,No,1.00,True,1.0000
cal_087,no,0.98,True,0.9996
cal_088,United States,0.90,False,0.1900
cal_089,no,0.95,True,0.9975
cal_090,no,1.00,True,1.0000
cal_091,yes,1.00,True,1.0000
cal_092,no,0.95,True,0.9975
cal_093,no,0.98,True,0.9996
cal_094,yes,1.00,True,1.0000
cal_095,Yes,1.00,True,1.0000
cal_096,Brazil,1.00,True,1.0000
cal_097,0,0.99,True,0.9999
cal_098,no,0.99,True,0.9999
cal_099,no,0.99,True,0.9999
cal_100,no,0.99,True,0.9999"""

for line in raw.strip().split("\n"):
    parts = line.split(",")
    eid = parts[0]
    answer = ",".join(parts[1:-3]) if len(parts) > 4 else parts[1]
    conf = float(parts[-3])
    correct = parts[-2] == "True"
    score = float(parts[-1])
    difficulty = rows[eid]["difficulty"]
    results.append({
        "example_id": eid,
        "answer": answer,
        "confidence": conf,
        "correct": correct,
        "score": score,
        "difficulty": difficulty,
    })

# ============================================================
# Analysis
# ============================================================

print("=" * 60)
print("GEMINI 2.5 FLASH — V2 100-ITEM SWEEP ANALYSIS")
print("=" * 60)

# Overall
total = len(results)
correct_count = sum(1 for r in results if r["correct"])
mean_score = sum(r["score"] for r in results) / total
print(f"\nOverall: {correct_count}/{total} correct ({100*correct_count/total:.1f}%)")
print(f"Mean 1-Brier: {mean_score:.4f}")

# By difficulty bucket
print(f"\n{'Bucket':<14} {'N':>3} {'Correct':>7} {'Acc%':>6} {'Mean Score':>10} {'Mean Conf':>9} {'Conf-Acc Gap':>12}")
print("-" * 65)
buckets = ["easy", "medium", "hard", "deceptive", "adversarial"]
bucket_stats = {}
for bucket in buckets:
    items = [r for r in results if r["difficulty"] == bucket]
    n = len(items)
    corr = sum(1 for r in items if r["correct"])
    acc = corr / n if n else 0
    mean_s = sum(r["score"] for r in items) / n if n else 0
    mean_conf = sum(r["confidence"] for r in items) / n if n else 0
    gap = mean_conf - acc
    bucket_stats[bucket] = {"n": n, "correct": corr, "accuracy": acc, "mean_score": mean_s, "mean_conf": mean_conf, "gap": gap}
    print(f"{bucket:<14} {n:>3} {corr:>4}/{n:<3} {100*acc:>5.1f}% {mean_s:>10.4f} {mean_conf:>9.2f} {gap:>+11.3f}")

# Wrong items detail
print(f"\n{'='*60}")
print("WRONG ITEMS (where signal lives)")
print(f"{'='*60}")
wrong = [r for r in results if not r["correct"]]
for r in wrong:
    gold = rows[r["example_id"]]["gold_answer"]
    prompt_preview = rows[r["example_id"]]["prompt"][:70]
    print(f"  {r['example_id']} ({r['difficulty']}) conf={r['confidence']:.2f} → '{r['answer']}' (gold: '{gold}')")
    print(f"    {prompt_preview}...")
    brier = (r["confidence"] - 0)**2  # wrong answer Brier
    print(f"    Brier penalty: {brier:.4f} | Conf-Acc gap: {r['confidence']:+.2f}")

# Overconfidence analysis
print(f"\n{'='*60}")
print("OVERCONFIDENCE ANALYSIS")
print(f"{'='*60}")
overconf = [r for r in results if not r["correct"] and r["confidence"] > 0.80]
print(f"Items wrong with conf > 0.80: {len(overconf)}")
for r in overconf:
    print(f"  {r['example_id']} ({r['difficulty']}): conf={r['confidence']:.2f}, answer='{r['answer']}'")

# Items with conf < 1.0 (where model showed uncertainty)
uncertain = [r for r in results if r["confidence"] < 1.0]
print(f"\nItems with conf < 1.0: {len(uncertain)}")
uncertain_correct = [r for r in uncertain if r["correct"]]
uncertain_wrong = [r for r in uncertain if not r["correct"]]
print(f"  Of which correct: {len(uncertain_correct)}")
print(f"  Of which wrong: {len(uncertain_wrong)}")

# Check success criteria
print(f"\n{'='*60}")
print("SUCCESS CRITERIA CHECK (single model — partial)")
print(f"{'='*60}")
dec_acc = bucket_stats["deceptive"]["accuracy"]
adv_acc = bucket_stats["adversarial"]["accuracy"]
conf_acc_gaps = [abs(r["confidence"] - (1 if r["correct"] else 0)) for r in results if abs(r["confidence"] - (1 if r["correct"] else 0)) > 0.20]
print(f"Deceptive accuracy: {100*dec_acc:.1f}% (target: <80% on 3+ models) → {'SIGNAL' if dec_acc < 0.80 else 'CEILING'}")
print(f"Adversarial accuracy: {100*adv_acc:.1f}% (target: <70% on 3+ models) → {'SIGNAL' if adv_acc < 0.70 else 'CEILING'}")
print(f"Items with conf-acc gap > 0.20: {len(conf_acc_gaps)} (target: ≥10) → {'PASS' if len(conf_acc_gaps) >= 10 else 'FAIL'}")

# Smoke test anomaly
print(f"\n{'='*60}")
print("SMOKE TEST ANOMALY")
print(f"{'='*60}")
print("Cell 5 (single item): cal_001 answer='65', correct=False")
print("Cell 6 (batch): cal_001 answer='3', correct=True")
print("NOTE: cal_001 appears to have different answers between single and batch runs.")
print("The Cell 5 smoke test returned '65' which was marked False — but 65 IS the gold answer for cal_001.")
print("This suggests a grading bug in the smoke test, or the dataset wasn't loaded correctly in Cell 5.")

