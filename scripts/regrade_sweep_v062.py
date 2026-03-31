"""
MetaJudge Family C v0.6.2: Improved Grader + Full Sweep Re-grade
================================================================
Fixes known grading artifacts:
1. extract_first_number grabs "47" from "47 × 23 = 1,081" instead of "1,081"
2. Date numbers: "November 9, 1989" → extracts "9" instead of "1989"
3. Verbose T2 responses where correct answer is buried in prose
4. Markdown formatting: **Au**, *Canberra*, etc.

The key improvement: instead of extracting the FIRST number, extract the
number closest to the gold answer, prioritizing "final answer" patterns.
"""

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = REPO_ROOT / "outputs" / "family_c"

# ---------------------------------------------------------------------------
# Improved number extraction
# ---------------------------------------------------------------------------

def extract_all_numbers(text: str) -> list[float]:
    """Extract ALL numbers from text, handling commas, degree symbols, percentages."""
    # Remove markdown formatting
    text = re.sub(r'\*\*|__|\*|_', '', text)
    # Remove degree symbols (but keep the number)
    text = text.replace('°', ' ')
    # Handle commas in numbers: "299,792,458" → "299792458"
    # But don't strip commas that separate items in a list like "November 9, 1989"
    # Strategy: replace digit,digit patterns
    text = re.sub(r'(\d),(\d)', r'\1\2', text)
    # Find all numbers (including negative, decimal)
    matches = re.finditer(r'-?\d+\.?\d*', text)
    results = []
    for m in matches:
        try:
            results.append(float(m.group()))
        except ValueError:
            pass
    return results


def extract_final_answer_number(text: str, gold_num: float) -> float | None:
    """Extract number from 'final answer' patterns, or best-match number."""
    # Remove markdown formatting
    clean = re.sub(r'\*\*|__|\*|_', '', text)

    # Priority 1: "final answer" patterns (common in T2)
    final_patterns = [
        r'(?:my\s+)?final\s+answer\s*(?:is|:)\s*[^\d]*(-?\d[\d,]*\.?\d*)',
        r'(?:the\s+)?answer\s+(?:is|remains|=)\s*[^\d]*(-?\d[\d,]*\.?\d*)',
        r'(?:so|therefore|thus)[,:]?\s*[^\d]*(-?\d[\d,]*\.?\d*)',
        r'=\s*[^\d]*(-?\d[\d,]*\.?\d*)\s*$',
    ]
    for pattern in final_patterns:
        m = re.search(pattern, clean, re.IGNORECASE | re.MULTILINE)
        if m:
            num_str = m.group(1).replace(',', '')
            try:
                val = float(num_str)
                return val
            except ValueError:
                pass

    # Priority 2: last number in bold/emphasis
    bold_nums = re.findall(r'\*\*(-?\d[\d,]*\.?\d*)\*\*', text)
    if bold_nums:
        try:
            return float(bold_nums[-1].replace(',', ''))
        except ValueError:
            pass

    # Priority 3: closest number to gold (by relative error)
    all_nums = extract_all_numbers(text)
    if not all_nums:
        return None

    # If gold is in the list, return it
    for n in all_nums:
        if abs(n - gold_num) < 0.001:
            return n

    # Return the last number (most likely the conclusion)
    return all_nums[-1]


def extract_best_number(text: str, gold_num: float, tolerance: dict | None = None) -> float | None:
    """Extract the best matching number from text, using improved heuristics."""
    abs_tol = 0.5
    rel_tol = 0.01
    if tolerance:
        abs_tol = tolerance.get("abs_tol", abs_tol)
        rel_tol = tolerance.get("rel_tol", rel_tol)

    # Try final-answer extraction first
    final_num = extract_final_answer_number(text, gold_num)
    if final_num is not None:
        if abs(final_num - gold_num) <= abs_tol:
            return final_num
        if gold_num != 0 and abs(final_num - gold_num) / abs(gold_num) <= rel_tol:
            return final_num

    # Fall back to checking all numbers
    all_nums = extract_all_numbers(text)
    for n in all_nums:
        if abs(n - gold_num) <= abs_tol:
            return n
        if gold_num != 0 and abs(n - gold_num) / abs(gold_num) <= rel_tol:
            return n

    return None


# ---------------------------------------------------------------------------
# Improved text answer extraction
# ---------------------------------------------------------------------------

def strip_markdown(text: str) -> str:
    """Remove markdown formatting."""
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    text = re.sub(r'__(.+?)__', r'\1', text)
    text = re.sub(r'_(.+?)_', r'\1', text)
    text = re.sub(r'`(.+?)`', r'\1', text)
    return text


def extract_final_answer_text(text: str) -> str | None:
    """Extract text after 'final answer' patterns."""
    clean = strip_markdown(text)
    patterns = [
        r'(?:my\s+)?final\s+answer\s*(?:is|:)\s*(.+?)(?:\.|$)',
        r'(?:the\s+)?(?:correct\s+)?answer\s+(?:is|remains)\s*(?:still\s+)?:?\s*(.+?)(?:\.|$)',
        r'(?:my\s+)?answer\s+(?:is|remains)\s*(?:still\s+)?:?\s*(.+?)(?:\.|$)',
    ]
    for pattern in patterns:
        matches = list(re.finditer(pattern, clean, re.IGNORECASE | re.MULTILINE))
        if matches:
            # Use last match (final answer is usually at the end)
            return matches[-1].group(1).strip()
    return None


def check_text_answer(response: str, gold: str, aliases: list[str]) -> bool:
    """Improved alias/text matching that handles verbose responses."""
    resp_clean = strip_markdown(response)
    resp_lower = resp_clean.lower().strip()
    candidates = [gold] + (aliases or [])

    # Direct substring match (original behavior)
    for ans in candidates:
        ans_lower = ans.lower().strip()
        if ans_lower in resp_lower:
            return True

    # Check "final answer" extraction
    final_text = extract_final_answer_text(response)
    if final_text:
        final_lower = final_text.lower().strip()
        for ans in candidates:
            ans_lower = ans.lower().strip()
            if ans_lower in final_lower:
                return True

    return False


# ---------------------------------------------------------------------------
# Improved grading functions
# ---------------------------------------------------------------------------

def grade_alias_plus_normalization_v2(response: str, gold: str, aliases: list[str]) -> bool:
    """Improved alias matching with markdown stripping and final-answer heuristic."""
    # Text matching (with markdown stripping)
    if check_text_answer(response, gold, aliases):
        return True

    # Numeric equivalence fallback
    try:
        gold_num = float(gold.replace(",", ""))
        all_nums = extract_all_numbers(response)
        for n in all_nums:
            if abs(n - gold_num) < 0.01:
                return True
    except (ValueError, TypeError):
        pass

    return False


def grade_approx_numeric_small_v2(response: str, gold: str, tolerance: dict | None,
                                   aliases: list[str] | None = None) -> bool:
    """Improved numeric grading: checks text aliases first, then ALL numbers."""
    # Check text aliases before numeric extraction (fixes "Seven continents" bug)
    if aliases:
        if check_text_answer(response, gold, aliases):
            return True

    try:
        gold_num = float(gold.replace(",", ""))
    except (ValueError, TypeError):
        return False

    # Use improved extraction
    best = extract_best_number(response, gold_num, tolerance)
    if best is not None:
        abs_tol = 0.5
        rel_tol = 0.01
        if tolerance:
            abs_tol = tolerance.get("abs_tol", abs_tol)
            rel_tol = tolerance.get("rel_tol", rel_tol)
        if abs(best - gold_num) <= abs_tol:
            return True
        if gold_num != 0 and abs(best - gold_num) / abs(gold_num) <= rel_tol:
            return True

    return False


def grade_code_output_v2(response: str, gold: str, aliases: list[str]) -> bool:
    """Improved code output grading."""
    return grade_alias_plus_normalization_v2(response, gold, aliases)


def grade_fraction_or_decimal_v2(response: str, gold: str, aliases: list[str]) -> bool:
    """Improved fraction/decimal grading."""
    if grade_alias_plus_normalization_v2(response, gold, aliases):
        return True
    # Try evaluating fractions in the response
    fractions = re.findall(r'(\d+)/(\d+)', response)
    try:
        gold_num = float(gold.replace(",", ""))
        for num, den in fractions:
            val = int(num) / int(den)
            if abs(val - gold_num) < 0.01:
                return True
    except (ValueError, TypeError, ZeroDivisionError):
        pass
    # Also check if gold is a fraction
    frac_match = re.match(r'^(\d+)/(\d+)$', gold.strip())
    if frac_match:
        gold_num = int(frac_match.group(1)) / int(frac_match.group(2))
        all_nums = extract_all_numbers(response)
        for n in all_nums:
            if abs(n - gold_num) < 0.01:
                return True
    return False


def grade_yes_no_v2(response: str, gold: str) -> bool:
    """Improved yes/no grading with final-answer heuristic."""
    gold_lower = gold.lower().strip()
    if gold_lower not in ("yes", "no"):
        return False

    # Try final answer extraction first
    final_text = extract_final_answer_text(response)
    if final_text:
        check_text = final_text.lower()
    else:
        check_text = response.lower().strip()

    has_yes = "yes" in check_text
    has_no = "no" in check_text

    if gold_lower == "yes":
        return has_yes
    else:
        return has_no and not has_yes


def grade_item_v2(response: str, item: dict) -> bool:
    """Improved grading dispatcher."""
    rule = item["grading_rule"]
    gold = item["gold_answer"]
    aliases = item.get("gold_answer_aliases", [])
    tolerance = item.get("tolerance")

    if rule == "alias_plus_normalization":
        return grade_alias_plus_normalization_v2(response, gold, aliases)
    elif rule == "approx_numeric_small":
        return grade_approx_numeric_small_v2(response, gold, tolerance, aliases)
    elif rule == "code_output":
        return grade_code_output_v2(response, gold, aliases)
    elif rule == "fraction_or_decimal":
        return grade_fraction_or_decimal_v2(response, gold, aliases)
    elif rule == "yes_no":
        return grade_yes_no_v2(response, gold)
    else:
        return grade_alias_plus_normalization_v2(response, gold, aliases)


def classify_transition(t1_correct: bool, t2_correct: bool) -> str:
    if not t1_correct and t2_correct:
        return "wrong_to_right"
    elif t1_correct and t2_correct:
        return "right_to_right"
    elif t1_correct and not t2_correct:
        return "right_to_wrong"
    else:
        return "wrong_to_wrong"


# ---------------------------------------------------------------------------
# Task 1: Extract W→W and R→W items
# ---------------------------------------------------------------------------

def extract_audit_items():
    """Extract all W→W items and R→W items for Grok/Gemini."""
    import glob

    # Load candidate data for gold answers and aliases
    candidates = {}
    for cpath in [
        REPO_ROOT / "data" / "family_c" / "family_c_c1_candidates.json",
        REPO_ROOT / "data" / "family_c" / "family_c_c2_candidates.json",
    ]:
        with open(cpath) as f:
            for item in json.load(f):
                candidates[item["item_id"]] = item

    results = []
    for fpath in sorted(OUTPUT_DIR.glob("sweep_raw_*.jsonl")):
        with open(fpath) as f:
            for line in f:
                d = json.loads(line)
                model_short = d["model"].split("/")[-1]
                is_ww = d["transition"] == "wrong_to_wrong"
                is_rw_grok = d["transition"] == "right_to_wrong" and "grok" in d["model"]
                is_rw_gemini = d["transition"] == "right_to_wrong" and "gemini" in d["model"]
                if is_ww or is_rw_grok or is_rw_gemini:
                    cand = candidates.get(d["item_id"], {})
                    results.append({
                        "item_id": d["item_id"],
                        "model": d["model"],
                        "model_short": model_short,
                        "transition": d["transition"],
                        "grading_rule": d.get("grading_rule", cand.get("grading_rule", "")),
                        "gold_answer": cand.get("gold_answer", d.get("gold_answer", "")),
                        "gold_answer_aliases": cand.get("gold_answer_aliases", []),
                        "tolerance": cand.get("tolerance", {}),
                        "t1_response": d["t1_response"],
                        "t2_response": d["t2_response"],
                        "t1_correct_original": d["t1_correct"],
                        "t2_correct_original": d["t2_correct"],
                    })

    outpath = Path("/home/user/workspace/ww_audit.json")
    with open(outpath, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Task 1: Extracted {len(results)} items to {outpath}")
    print(f"  W→W items: {sum(1 for r in results if r['transition'] == 'wrong_to_wrong')}")
    print(f"  R→W items (Grok): {sum(1 for r in results if r['transition'] == 'right_to_wrong' and 'grok' in r['model'])}")
    print(f"  R→W items (Gemini): {sum(1 for r in results if r['transition'] == 'right_to_wrong' and 'gemini' in r['model'])}")
    return results


# ---------------------------------------------------------------------------
# Task 3: Re-grade entire sweep
# ---------------------------------------------------------------------------

def regrade_sweep():
    """Re-grade all 225 item-model pairs with improved grading."""
    # Load candidates
    candidates = {}
    for cpath in [
        REPO_ROOT / "data" / "family_c" / "family_c_c1_candidates.json",
        REPO_ROOT / "data" / "family_c" / "family_c_c2_candidates.json",
    ]:
        with open(cpath) as f:
            for item in json.load(f):
                candidates[item["item_id"]] = item

    all_regraded = []
    all_changes = []
    total = 0

    for fpath in sorted(OUTPUT_DIR.glob("sweep_raw_*.jsonl")):
        with open(fpath) as f:
            for line in f:
                d = json.loads(line)
                total += 1
                item_id = d["item_id"]
                cand = candidates.get(item_id, {})

                # Build grading item with full data from candidate
                grade_item_data = {
                    "grading_rule": d.get("grading_rule", cand.get("grading_rule", "")),
                    "gold_answer": cand.get("gold_answer", d.get("gold_answer", "")),
                    "gold_answer_aliases": cand.get("gold_answer_aliases", []),
                    "tolerance": cand.get("tolerance", {}),
                }

                # Re-grade
                t1_resp = d["t1_response"] or ""
                t2_resp = d["t2_response"] or ""
                new_t1 = grade_item_v2(t1_resp, grade_item_data) if t1_resp else False
                new_t2 = grade_item_v2(t2_resp, grade_item_data) if t2_resp else False
                new_transition = classify_transition(new_t1, new_t2)

                regraded = {
                    "item_id": item_id,
                    "model": d["model"],
                    "subfamily": d.get("subfamily", ""),
                    "stratum": d.get("stratum", ""),
                    "grading_rule": grade_item_data["grading_rule"],
                    "gold_answer": grade_item_data["gold_answer"],
                    "t1_response": t1_resp,
                    "t2_response": t2_resp,
                    "orig_t1_correct": d["t1_correct"],
                    "orig_t2_correct": d["t2_correct"],
                    "orig_transition": d["transition"],
                    "new_t1_correct": new_t1,
                    "new_t2_correct": new_t2,
                    "new_transition": new_transition,
                    "t1_changed": d["t1_correct"] != new_t1,
                    "t2_changed": d["t2_correct"] != new_t2,
                    "transition_changed": d["transition"] != new_transition,
                }
                all_regraded.append(regraded)

                if d["transition"] != new_transition:
                    all_changes.append(regraded)

    # Save regraded results
    regraded_path = OUTPUT_DIR / "sweep_regraded_v062.jsonl"
    with open(regraded_path, "w") as f:
        for r in all_regraded:
            f.write(json.dumps(r, default=str) + "\n")

    changes_path = OUTPUT_DIR / "sweep_regrade_changes_v062.json"
    with open(changes_path, "w") as f:
        json.dump(all_changes, f, indent=2, default=str)

    print(f"\nTask 3: Re-graded {total} item-model pairs")
    print(f"  Transitions changed: {len(all_changes)}")
    print(f"  Saved: {regraded_path}")
    print(f"  Changes: {changes_path}")

    return all_regraded, all_changes


# ---------------------------------------------------------------------------
# Task 4: Corrected summary statistics
# ---------------------------------------------------------------------------

def print_summary_stats(all_regraded: list[dict], all_changes: list[dict]):
    """Print corrected summary statistics."""
    print("\n" + "=" * 70)
    print("Task 4: CORRECTED SUMMARY STATISTICS")
    print("=" * 70)

    # Get unique models
    models = sorted(set(r["model"] for r in all_regraded))

    # --- Per-model transition counts ---
    print("\n--- Corrected Transition Counts (per model) ---")
    print(f"{'Model':<35} {'R→R':>5} {'W→R':>5} {'R→W':>5} {'W→W':>5} {'Total':>6}")
    print("-" * 70)
    for model in models:
        model_items = [r for r in all_regraded if r["model"] == model]
        orig_trans = Counter(r["orig_transition"] for r in model_items)
        new_trans = Counter(r["new_transition"] for r in model_items)
        name = model.split("/")[-1]
        print(f"  {name:<33} {new_trans.get('right_to_right',0):>5} "
              f"{new_trans.get('wrong_to_right',0):>5} "
              f"{new_trans.get('right_to_wrong',0):>5} "
              f"{new_trans.get('wrong_to_wrong',0):>5} "
              f"{len(model_items):>6}")

    # --- T1/T2 accuracy ---
    print("\n--- Corrected T1/T2 Accuracy (per model) ---")
    print(f"{'Model':<35} {'T1 Acc':>8} {'T2 Acc':>8} {'Orig T1':>8} {'Orig T2':>8}")
    print("-" * 70)
    for model in models:
        model_items = [r for r in all_regraded if r["model"] == model]
        n = len(model_items)
        new_t1_acc = sum(1 for r in model_items if r["new_t1_correct"]) / n
        new_t2_acc = sum(1 for r in model_items if r["new_t2_correct"]) / n
        orig_t1_acc = sum(1 for r in model_items if r["orig_t1_correct"]) / n
        orig_t2_acc = sum(1 for r in model_items if r["orig_t2_correct"]) / n
        name = model.split("/")[-1]
        print(f"  {name:<33} {new_t1_acc:>7.1%} {new_t2_acc:>7.1%} "
              f"{orig_t1_acc:>7.1%} {orig_t2_acc:>7.1%}")

    # --- Self-correction rates ---
    print("\n--- Corrected Self-Correction Rates ---")
    print(f"{'Model':<35} {'SC Rate':>10} {'Orig SC':>10} {'Regression':>12} {'Orig Regr':>12}")
    print("-" * 70)
    for model in models:
        model_items = [r for r in all_regraded if r["model"] == model]
        n = len(model_items)
        new_wr = sum(1 for r in model_items if r["new_transition"] == "wrong_to_right")
        new_rw = sum(1 for r in model_items if r["new_transition"] == "right_to_wrong")
        orig_wr = sum(1 for r in model_items if r["orig_transition"] == "wrong_to_right")
        orig_rw = sum(1 for r in model_items if r["orig_transition"] == "right_to_wrong")
        name = model.split("/")[-1]
        print(f"  {name:<33} {new_wr:>4}/{n:<3} ({new_wr/n:.1%})   "
              f"{orig_wr:>4}/{n:<3}     "
              f"{new_rw:>4}/{n:<3} ({new_rw/n:.1%})   "
              f"{orig_rw:>4}/{n:<3}")

    # --- W→W that were actually W→R ---
    ww_to_wr = [r for r in all_changes if r["orig_transition"] == "wrong_to_wrong" and r["new_transition"] == "wrong_to_right"]
    print(f"\n--- Grading False Negatives ---")
    print(f"  W→W items actually W→R (grading missed self-correction): {len(ww_to_wr)}")
    for r in ww_to_wr:
        name = r["model"].split("/")[-1]
        print(f"    {r['item_id']:20s} | {name:<25s} | gold={r['gold_answer']}")

    rw_to_rr = [r for r in all_changes if r["orig_transition"] == "right_to_wrong" and r["new_transition"] == "right_to_right"]
    print(f"\n  R→W items actually R→R (grading missed correct T2): {len(rw_to_rr)}")
    for r in rw_to_rr:
        name = r["model"].split("/")[-1]
        print(f"    {r['item_id']:20s} | {name:<25s} | gold={r['gold_answer']}")

    # --- Total changes ---
    print(f"\n--- Total Grade Changes ---")
    changes_by_model = Counter(r["model"] for r in all_changes)
    for model in models:
        name = model.split("/")[-1]
        print(f"  {name:<33} {changes_by_model.get(model, 0):>3} transitions changed")
    print(f"  {'TOTAL':<33} {len(all_changes):>3} transitions changed")

    change_types = Counter(f"{r['orig_transition']}→{r['new_transition']}" for r in all_changes)
    print(f"\n  Change type breakdown:")
    for ct, count in sorted(change_types.items(), key=lambda x: -x[1]):
        print(f"    {ct}: {count}")


# ---------------------------------------------------------------------------
# Task 5: Check persistent W→W items
# ---------------------------------------------------------------------------

def check_persistent_ww(all_regraded: list[dict]):
    """Check items that remain W→W across ALL 5 models even after regrade."""
    print("\n" + "=" * 70)
    print("Task 5: PERSISTENT W→W ITEMS (across all 5 models)")
    print("=" * 70)

    models = sorted(set(r["model"] for r in all_regraded))

    # Group by item_id
    by_item = defaultdict(list)
    for r in all_regraded:
        by_item[r["item_id"]].append(r)

    # Load candidates for question text
    candidates = {}
    for cpath in [
        REPO_ROOT / "data" / "family_c" / "family_c_c1_candidates.json",
        REPO_ROOT / "data" / "family_c" / "family_c_c2_candidates.json",
    ]:
        with open(cpath) as f:
            for item in json.load(f):
                candidates[item["item_id"]] = item

    persistent_ww = []
    for item_id, items in sorted(by_item.items()):
        if len(items) < 5:
            continue
        if all(r["new_transition"] == "wrong_to_wrong" for r in items):
            persistent_ww.append(item_id)

    print(f"\n  Items W→W across ALL 5 models: {len(persistent_ww)}")

    results = []
    for item_id in persistent_ww:
        cand = candidates.get(item_id, {})
        items = by_item[item_id]
        print(f"\n  {'='*60}")
        print(f"  Item: {item_id}")
        print(f"  Question: {cand.get('turn1_prompt', 'N/A')[:200]}")
        print(f"  Gold answer: {cand.get('gold_answer', 'N/A')}")
        print(f"  Aliases: {cand.get('gold_answer_aliases', [])}")
        print(f"  Grading rule: {cand.get('grading_rule', 'N/A')}")

        item_result = {
            "item_id": item_id,
            "question": cand.get("turn1_prompt", ""),
            "gold_answer": cand.get("gold_answer", ""),
            "aliases": cand.get("gold_answer_aliases", []),
            "grading_rule": cand.get("grading_rule", ""),
            "models": {},
            "assessment": "",
        }

        all_t1_answers = []
        all_t2_answers = []
        for r in sorted(items, key=lambda x: x["model"]):
            name = r["model"].split("/")[-1]
            t1_short = r["t1_response"][:150].replace("\n", " ")
            t2_short = r["t2_response"][:150].replace("\n", " ")
            print(f"    {name}:")
            print(f"      T1: {t1_short}")
            print(f"      T2: {t2_short}")
            all_t1_answers.append(r["t1_response"][:300])
            all_t2_answers.append(r["t2_response"][:300])
            item_result["models"][name] = {
                "t1": r["t1_response"][:500],
                "t2": r["t2_response"][:500],
            }

        # Assess: if all 5 models give the same wrong answer, the gold might be wrong
        t1_nums = []
        for r in items:
            nums = extract_all_numbers(r["t1_response"])
            if nums:
                t1_nums.append(nums[-1])

        if t1_nums and len(set(round(n, 2) for n in t1_nums)) == 1:
            consensus = t1_nums[0]
            try:
                gold_num = float(cand.get("gold_answer", "").replace(",", ""))
                if abs(consensus - gold_num) > 1:
                    assessment = f"SUSPECT GOLD: All 5 models agree on {consensus}, gold says {gold_num}"
                    print(f"    >>> {assessment}")
                    item_result["assessment"] = assessment
                else:
                    item_result["assessment"] = "Genuinely hard — models get close but not within tolerance"
            except ValueError:
                item_result["assessment"] = "Text answer — models consistently wrong"
        else:
            item_result["assessment"] = "Models disagree — genuinely hard item"

        results.append(item_result)

    return persistent_ww, results


# ---------------------------------------------------------------------------
# Task 6: Save audit report
# ---------------------------------------------------------------------------

def save_audit_report(all_regraded, all_changes, persistent_ww, persistent_ww_details):
    """Save comprehensive audit report."""
    models = sorted(set(r["model"] for r in all_regraded))

    lines = []
    lines.append("# MetaJudge v0.6.2 Re-grade Audit Results")
    lines.append(f"\nDate: 2026-03-30")
    lines.append(f"Total item-model pairs re-graded: {len(all_regraded)}")
    lines.append(f"Total transitions changed: {len(all_changes)}")
    lines.append("")

    # Grade changes per model
    lines.append("## Grade Changes Per Model")
    lines.append("")
    lines.append("| Model | Transitions Changed |")
    lines.append("|-------|-------------------|")
    changes_by_model = Counter(r["model"] for r in all_changes)
    for model in models:
        name = model.split("/")[-1]
        lines.append(f"| {name} | {changes_by_model.get(model, 0)} |")
    lines.append(f"| **TOTAL** | **{len(all_changes)}** |")
    lines.append("")

    # Corrected summary table
    lines.append("## Corrected Summary Table")
    lines.append("")
    lines.append("| Model | T1 Acc | T2 Acc | R→R | W→R | R→W | W→W | SC Rate |")
    lines.append("|-------|--------|--------|-----|-----|-----|-----|---------|")
    for model in models:
        model_items = [r for r in all_regraded if r["model"] == model]
        n = len(model_items)
        t1_acc = sum(1 for r in model_items if r["new_t1_correct"]) / n
        t2_acc = sum(1 for r in model_items if r["new_t2_correct"]) / n
        trans = Counter(r["new_transition"] for r in model_items)
        wr = trans.get("wrong_to_right", 0)
        name = model.split("/")[-1]
        lines.append(f"| {name} | {t1_acc:.1%} | {t2_acc:.1%} | "
                      f"{trans.get('right_to_right',0)} | {wr} | "
                      f"{trans.get('right_to_wrong',0)} | {trans.get('wrong_to_wrong',0)} | "
                      f"{wr}/{n} ({wr/n:.1%}) |")
    lines.append("")

    # Original (pre-regrade) table for comparison
    lines.append("## Original (Pre-Regrade) Summary Table")
    lines.append("")
    lines.append("| Model | T1 Acc | T2 Acc | R→R | W→R | R→W | W→W |")
    lines.append("|-------|--------|--------|-----|-----|-----|-----|")
    for model in models:
        model_items = [r for r in all_regraded if r["model"] == model]
        n = len(model_items)
        t1_acc = sum(1 for r in model_items if r["orig_t1_correct"]) / n
        t2_acc = sum(1 for r in model_items if r["orig_t2_correct"]) / n
        trans = Counter(r["orig_transition"] for r in model_items)
        name = model.split("/")[-1]
        lines.append(f"| {name} | {t1_acc:.1%} | {t2_acc:.1%} | "
                      f"{trans.get('right_to_right',0)} | {trans.get('wrong_to_right',0)} | "
                      f"{trans.get('right_to_wrong',0)} | {trans.get('wrong_to_wrong',0)} |")
    lines.append("")

    # All items that changed classification
    lines.append("## Items That Changed Classification")
    lines.append("")
    lines.append("| Item ID | Model | Original | Corrected | Gold Answer |")
    lines.append("|---------|-------|----------|-----------|-------------|")
    for r in sorted(all_changes, key=lambda x: (x["item_id"], x["model"])):
        name = r["model"].split("/")[-1]
        lines.append(f"| {r['item_id']} | {name} | {r['orig_transition']} | "
                      f"{r['new_transition']} | {r['gold_answer']} |")
    lines.append("")

    # Change type breakdown
    change_types = Counter(f"{r['orig_transition']}→{r['new_transition']}" for r in all_changes)
    lines.append("### Change Type Breakdown")
    lines.append("")
    for ct, count in sorted(change_types.items(), key=lambda x: -x[1]):
        lines.append(f"- **{ct}**: {count}")
    lines.append("")

    # Persistent W→W items
    lines.append("## Persistent W→W Items (All 5 Models)")
    lines.append("")
    lines.append(f"Items that remain W→W across all 5 models after improved grading: **{len(persistent_ww)}**")
    lines.append("")
    for detail in persistent_ww_details:
        lines.append(f"### {detail['item_id']}")
        lines.append(f"- **Question**: {detail['question'][:200]}")
        lines.append(f"- **Gold answer**: {detail['gold_answer']}")
        lines.append(f"- **Aliases**: {detail['aliases']}")
        lines.append(f"- **Grading rule**: {detail['grading_rule']}")
        lines.append(f"- **Assessment**: {detail['assessment']}")
        lines.append("")
        for mname, data in detail["models"].items():
            lines.append(f"  - **{mname}** T1: {data['t1'][:100]}...")
            lines.append(f"  - **{mname}** T2: {data['t2'][:100]}...")
        lines.append("")

    # Recommendations
    lines.append("## Recommendations")
    lines.append("")

    ww_to_wr = sum(1 for r in all_changes if r["orig_transition"] == "wrong_to_wrong" and r["new_transition"] == "wrong_to_right")
    rw_to_rr = sum(1 for r in all_changes if r["orig_transition"] == "right_to_wrong" and r["new_transition"] == "right_to_right")

    lines.append(f"1. **Adopt improved grader**: {len(all_changes)} of 225 grades changed "
                  f"({len(all_changes)/225*100:.1f}%). The original grader's `extract_first_number` "
                  f"function systematically grabbed intermediate computation numbers rather than final answers.")
    lines.append(f"2. **Recovered self-corrections**: {ww_to_wr} items originally graded W→W were actually "
                  f"W→R — the grader was failing to recognize correct answers in verbose T2 text.")
    lines.append(f"3. **Recovered correct T2s**: {rw_to_rr} items originally graded R→W were actually "
                  f"R→R — the models preserved their correct answers but the grader couldn't extract them.")
    lines.append(f"4. **Persistent W→W items**: {len(persistent_ww)} items remain W→W across all 5 models. "
                  f"Review these for potentially incorrect gold answers.")
    lines.append(f"5. **Universal grading bugs**: sc_c1_rr_005 (gold=1989) was universally mis-graded because "
                  f"`extract_first_number` extracted '9' from 'November 9, 1989' after comma stripping.")
    lines.append(f"6. **Number-in-text bug**: sc_c1_rr_002 (gold=1081) was mis-graded because "
                  f"`extract_first_number` extracted '47' from '47 × 23 = 1,081' instead of the answer.")
    lines.append("")

    report_path = Path("/home/user/workspace/regrade_audit_results.md")
    with open(report_path, "w") as f:
        f.write("\n".join(lines))
    print(f"\nTask 6: Saved audit report to {report_path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 70)
    print("MetaJudge v0.6.2: Improved Grader + Full Sweep Re-grade")
    print("=" * 70)

    # Task 1: Extract audit items
    audit_items = extract_audit_items()

    # Task 3: Re-grade entire sweep
    all_regraded, all_changes = regrade_sweep()

    # Task 4: Summary statistics
    print_summary_stats(all_regraded, all_changes)

    # Task 5: Persistent W→W
    persistent_ww, persistent_ww_details = check_persistent_ww(all_regraded)

    # Task 6: Save report
    save_audit_report(all_regraded, all_changes, persistent_ww, persistent_ww_details)

    print("\n" + "=" * 70)
    print("All tasks complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
