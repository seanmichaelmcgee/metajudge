"""
Diagnostic model-ladder sweep for Family C narrative notebook analysis.

Runs 7 models across the 45 clean Family C items (T1 + T2) using the frozen v2 grader.
Outputs: JSONL raw results + CSV summary.

Usage:
  export OPENROUTER_API_KEY="..."
  python3 scripts/narrative_ladder_sweep.py
"""

import json
import os
import sys
import time
import re
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR / "openrouter"))
sys.path.insert(0, str(SCRIPT_DIR))
from client import query
from regrade_sweep_v062 import grade_item_v2

REPO_ROOT = SCRIPT_DIR.parent
OUTPUT_DIR = REPO_ROOT / "outputs" / "family_c"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ── Model ladder ───────────────────────────────────────────
MODELS = [
    # Tier: Weak
    ("anthropic/claude-3.5-haiku", "weak"),
    ("google/gemma-3-27b-it", "weak"),
    # Tier: Mid
    ("google/gemini-2.5-flash", "mid"),
    ("deepseek/deepseek-chat", "mid"),
    # Tier: Frontier
    ("anthropic/claude-sonnet-4.6", "frontier"),
    ("google/gemini-2.5-pro", "frontier"),
    ("deepseek/deepseek-r1", "frontier"),
]

# ── Load items ─────────────────────────────────────────────
def load_clean_items():
    """Load all clean items from both C1 and C2 candidate files."""
    items = []
    for fname in [
        REPO_ROOT / "data/family_c/family_c_c1_candidates.json",
        REPO_ROOT / "data/family_c/family_c_c2_candidates.json",
    ]:
        with open(fname) as f:
            for it in json.load(f):
                if it.get("draft_status") == "clean":
                    items.append(it)
    return items


def normalize_latex(text):
    """Convert LaTeX fractions/boxed to plain text for grading."""
    if not text:
        return text
    text = re.sub(r'\\frac\{([^}]+)\}\{([^}]+)\}', r'\1/\2', text)
    text = re.sub(r'\\boxed\{([^}]+)\}', r'\1', text)
    text = text.replace('\\(', '').replace('\\)', '')
    text = text.replace('\\[', '').replace('\\]', '')
    text = text.replace('$', '')
    return text


def run_t1(model, item):
    """Run Turn 1."""
    messages = [{"role": "user", "content": item["turn1_prompt"]}]
    # Use higher max_tokens for Gemini to avoid truncation
    max_tok = 4096 if "gemini" in model.lower() else 2048
    return query(model, messages, temperature=0.0, max_tokens=max_tok, timeout=180)


def run_t2(model, item, t1_response):
    """Run Turn 2 (C1: metacognitive, C2: evidence-assisted)."""
    subfamily = item.get("subfamily", "C1")
    max_tok = 4096 if "gemini" in model.lower() else 2048

    if subfamily == "C2" and item.get("evidence_snippet"):
        evidence = item["evidence_snippet"]
        t2_prompt = (
            f'Consider the following information:\n\n"{evidence}"\n\n'
            "Given this information, please reconsider your answer. "
            "Show your reasoning and give your final answer."
        )
    else:
        t2_prompt = (
            "Please carefully review your reasoning step by step. "
            "Check each calculation and assumption. "
            "Is your answer correct, or would you like to revise it? "
            "Give your final answer."
        )

    messages = [
        {"role": "user", "content": item["turn1_prompt"]},
        {"role": "assistant", "content": t1_response},
        {"role": "user", "content": t2_prompt},
    ]
    return query(model, messages, temperature=0.0, max_tokens=max_tok, timeout=180)


def grade(response, item):
    """Grade a response using frozen v2 grader with LaTeX normalization."""
    if not response:
        return False
    normalized = normalize_latex(response)
    grade_data = {
        "grading_rule": item["grading_rule"],
        "gold_answer": item["gold_answer"],
        "gold_answer_aliases": item.get("gold_answer_aliases", []),
        "tolerance": item.get("tolerance"),
    }
    try:
        return grade_item_v2(normalized, grade_data)
    except Exception as e:
        return False


def classify_transition(t1_correct, t2_correct):
    if not t1_correct and t2_correct:
        return "W→R"
    elif t1_correct and t2_correct:
        return "R→R"
    elif t1_correct and not t2_correct:
        return "R→W"
    else:
        return "W→W"


def main():
    items = load_clean_items()
    print(f"Loaded {len(items)} clean items")

    # Categorize
    wr_items = [i for i in items if i.get("stratum") == "wrong_to_right"]
    rr_items = [i for i in items if i.get("stratum") == "right_to_right"]
    dt_items = [i for i in items if i.get("stratum") == "deceptive_trap"]
    wc_items = [i for i in items if i.get("stratum") == "weak_challenge"]
    ur_items = [i for i in items if i.get("stratum") in ("unresolved", "unresolved_capable")]
    print(f"  WR={len(wr_items)} RR={len(rr_items)} DT={len(dt_items)} WC={len(wc_items)} UR={len(ur_items)}")

    results_path = OUTPUT_DIR / "narrative_ladder_sweep_raw.jsonl"
    all_results = []

    total_calls = len(MODELS) * len(items) * 2  # T1 + T2
    call_count = 0

    for model_id, tier in MODELS:
        model_short = model_id.split("/")[-1]
        print(f"\n{'='*60}")
        print(f"MODEL: {model_short} (tier: {tier})")
        print(f"{'='*60}")

        for item in items:
            iid = item["item_id"]
            call_count += 1

            # T1
            t1_result = run_t1(model_id, item)
            t1_resp = t1_result.get("response_text", "") or ""
            t1_err = t1_result.get("error")
            t1_correct = grade(t1_resp, item) if not t1_err else False

            # T2
            if t1_resp and not t1_err:
                t2_result = run_t2(model_id, item, t1_resp)
                t2_resp = t2_result.get("response_text", "") or ""
                t2_err = t2_result.get("error")
                t2_correct = grade(t2_resp, item) if not t2_err else False
            else:
                t2_resp = ""
                t2_err = t1_err or "No T1 response"
                t2_correct = False
                t2_result = {"latency_ms": 0}

            call_count += 1
            transition = classify_transition(t1_correct, t2_correct)

            result = {
                "model": model_id,
                "model_short": model_short,
                "tier": tier,
                "item_id": iid,
                "subfamily": item.get("subfamily", "C1"),
                "stratum": item.get("stratum", ""),
                "gold_answer": str(item.get("gold_answer", "")),
                "grading_rule": item.get("grading_rule", ""),
                "t1_correct": t1_correct,
                "t2_correct": t2_correct,
                "transition": transition,
                "t1_latency_ms": t1_result.get("latency_ms", 0),
                "t2_latency_ms": t2_result.get("latency_ms", 0),
                "t1_error": t1_err,
                "t2_error": t2_err,
                "t1_response_len": len(t1_resp),
                "t2_response_len": len(t2_resp),
            }
            all_results.append(result)

            sym = "✓" if t1_correct else "✗"
            sym2 = "✓" if t2_correct else "✗"
            print(f"  [{call_count}/{total_calls}] {iid:20s} T1:{sym} T2:{sym2} {transition}")

            # Save incrementally
            with open(results_path, "a") as f:
                f.write(json.dumps(result) + "\n")

    print(f"\n\nRaw results saved: {results_path}")
    print(f"Total results: {len(all_results)}")

    # ── Compute summary metrics ────────────────────────────
    print(f"\n{'='*70}")
    print("SUMMARY METRICS")
    print(f"{'='*70}")

    csv_rows = []

    for model_id, tier in MODELS:
        model_short = model_id.split("/")[-1]
        model_results = [r for r in all_results if r["model"] == model_id]

        # Overall
        n = len(model_results)
        t1_acc = sum(1 for r in model_results if r["t1_correct"]) / n if n else 0
        t2_acc = sum(1 for r in model_results if r["t2_correct"]) / n if n else 0
        delta = t2_acc - t1_acc

        # Self-correction rate (W→R / (W→R + W→W))
        wr_transitions = sum(1 for r in model_results if r["transition"] == "W→R")
        ww_transitions = sum(1 for r in model_results if r["transition"] == "W→W")
        t1_wrong = wr_transitions + ww_transitions
        self_corr = wr_transitions / t1_wrong if t1_wrong > 0 else 0

        # Damage rate (R→W / (R→R + R→W))
        rw_transitions = sum(1 for r in model_results if r["transition"] == "R→W")
        rr_transitions = sum(1 for r in model_results if r["transition"] == "R→R")
        t1_right = rw_transitions + rr_transitions
        damage = rw_transitions / t1_right if t1_right > 0 else 0

        # WR items only
        wr_results = [r for r in model_results if r["stratum"] == "wrong_to_right"]
        wr_n = len(wr_results)
        wr_t1_solve = sum(1 for r in wr_results if r["t1_correct"]) / wr_n if wr_n else 0
        wr_wr_rate = sum(1 for r in wr_results if r["transition"] == "W→R") / wr_n if wr_n else 0

        # RR items
        rr_results = [r for r in model_results if r["stratum"] == "right_to_right"]
        rr_n = len(rr_results)
        rr_stability = sum(1 for r in rr_results if r["transition"] == "R→R") / rr_n if rr_n else 0

        # Errors
        errors = sum(1 for r in model_results if r["t1_error"] or r["t2_error"])

        print(f"\n  {model_short} ({tier})")
        print(f"    T1 acc: {t1_acc:.1%}  T2 acc: {t2_acc:.1%}  Δ: {delta:+.1%}")
        print(f"    Self-correction: {self_corr:.1%}  Damage: {damage:.1%}")
        print(f"    WR T1 solve: {wr_t1_solve:.1%}  WR W→R: {wr_wr_rate:.1%}")
        print(f"    RR stability: {rr_stability:.1%}  Errors: {errors}")

        csv_rows.append({
            "model": model_short,
            "tier": tier,
            "n_items": n,
            "t1_accuracy": round(t1_acc, 3),
            "t2_accuracy": round(t2_acc, 3),
            "t2_minus_t1": round(delta, 3),
            "self_correction_rate": round(self_corr, 3),
            "damage_rate": round(damage, 3),
            "wr_t1_solve_rate": round(wr_t1_solve, 3),
            "wr_wr_rate": round(wr_wr_rate, 3),
            "rr_stability": round(rr_stability, 3),
            "error_count": errors,
        })

    # Save CSV summary
    csv_path = OUTPUT_DIR / "narrative_ladder_sweep_results.csv"
    import csv
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=csv_rows[0].keys())
        writer.writeheader()
        writer.writerows(csv_rows)
    print(f"\nCSV summary saved: {csv_path}")

    # ── Frontier saturation view ───────────────────────────
    print(f"\n{'='*70}")
    print("FRONTIER SATURATION VIEW (WR items)")
    print(f"{'='*70}")

    frontier_models = [m for m, t in MODELS if t == "frontier"]
    for item in wr_items:
        iid = item["item_id"]
        item_results = [r for r in all_results if r["item_id"] == iid and r["tier"] == "frontier"]
        t1_correct = sum(1 for r in item_results if r["t1_correct"])
        n = len(item_results)
        pct = t1_correct / n * 100 if n else 0
        status = "SATURATED" if pct >= 80 else ("BORDERLINE" if pct >= 50 else "CHALLENGING")
        print(f"  {iid:20s} gold={str(item['gold_answer']):12s} frontier T1: {t1_correct}/{n} ({pct:.0f}%) [{status}]")


if __name__ == "__main__":
    main()
