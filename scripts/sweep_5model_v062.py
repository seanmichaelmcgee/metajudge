"""
MetaJudge Family C: 5-Model Narrative Sweep (v0.6.2)
=====================================================
Runs the self-correction protocol (T1 → T2) for all clean Family C items
across specified models via OpenRouter.

C1 items: T2 = metacognitive re-prompt (no evidence)
C2 items: T2 = evidence snippet + re-prompt

Usage:
    export OPENROUTER_API_KEY=...
    python scripts/sweep_5model_v062.py
"""

import csv
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.openrouter.client import query

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
MODELS = [
    "deepseek/deepseek-chat",
    "x-ai/grok-3-mini",
    "openai/gpt-4.1",
]

TEMPERATURE = 0.3
MAX_TOKENS = 400
INTER_CALL_DELAY = 1.0  # seconds between API calls

OUTPUT_DIR = REPO_ROOT / "outputs" / "family_c"

# ---------------------------------------------------------------------------
# T2 prompts
# ---------------------------------------------------------------------------
C1_T2_PROMPT = (
    "Please reconsider your answer carefully. Take a moment to verify your "
    "reasoning step by step. What is your final answer?"
)

C2_T2_TEMPLATE = (
    "Here is some additional information:\n\n{evidence}\n\n"
    "Given this additional information, please reconsider. What is your final answer?"
)

# ---------------------------------------------------------------------------
# Grading functions
# ---------------------------------------------------------------------------

WORD_NUMBERS = {
    'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4,
    'five': 5, 'six': 6, 'seven': 7, 'eight': 8, 'nine': 9,
    'ten': 10, 'eleven': 11, 'twelve': 12,
}


def strip_markdown(text: str) -> str:
    """Remove markdown formatting."""
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    text = re.sub(r'__(.+?)__', r'\1', text)
    text = re.sub(r'_(.+?)_', r'\1', text)
    return text


def extract_first_number(text: str) -> float | None:
    """Extract the first number from text, handling commas, negatives,
    word-numbers (zero-twelve), and LaTeX \\frac{a}{b}."""
    text = strip_markdown(text)

    # Check for word numbers first
    text_lower = text.lower()
    for word, val in WORD_NUMBERS.items():
        if re.search(r'\b' + word + r'\b', text_lower):
            return float(val)

    # Check for LaTeX \frac{a}{b} (including \boxed{\frac{a}{b}})
    m = re.search(r'\\frac\{(\d+)\}\{(\d+)\}', text)
    if m:
        return float(m.group(1)) / float(m.group(2))

    # Handle commas in numbers: "1,081" → "1081"
    text = re.sub(r'(\d),(\d)', r'\1\2', text)
    m = re.search(r'-?\d+\.?\d*', text)
    if m:
        try:
            return float(m.group())
        except ValueError:
            return None
    return None


def extract_final_answer_number(text: str, gold_num: float) -> float | None:
    """Extract number from 'final answer' patterns, or best-match number.

    Prioritizes 'final answer' patterns over first-number extraction.
    """
    clean = strip_markdown(text)

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
                return float(num_str)
            except ValueError:
                pass

    # Priority 2: last number in bold/emphasis
    bold_nums = re.findall(r'\*\*(-?\d[\d,]*\.?\d*)\*\*', text)
    if bold_nums:
        try:
            return float(bold_nums[-1].replace(',', ''))
        except ValueError:
            pass

    # Priority 3: extract all numbers and pick best match
    # Handle commas in numbers
    all_text = re.sub(r'(\d),(\d)', r'\1\2', clean)
    matches = re.finditer(r'-?\d+\.?\d*', all_text)
    all_nums = []
    for m in matches:
        try:
            all_nums.append(float(m.group()))
        except ValueError:
            pass

    if not all_nums:
        return None

    # If gold is in the list, return it
    for n in all_nums:
        if abs(n - gold_num) < 0.001:
            return n

    # Return the last number (most likely the conclusion)
    return all_nums[-1]


def grade_alias_plus_normalization(response: str, gold: str, aliases: list[str]) -> bool:
    """Check if any alias appears in the response (case-insensitive)."""
    resp_lower = response.lower().strip()
    candidates = [gold] + (aliases or [])
    for ans in candidates:
        ans_lower = ans.lower().strip()
        if ans_lower in resp_lower:
            return True
    # Also check numeric equivalence if gold is numeric
    try:
        gold_num = float(gold.replace(",", ""))
        resp_num = extract_first_number(response)
        if resp_num is not None and abs(resp_num - gold_num) < 0.01:
            return True
    except (ValueError, TypeError):
        pass
    return False


def grade_approx_numeric_small(response: str, gold: str, tolerance: dict | None) -> bool:
    """Extract number using final-answer heuristics and check within tolerance."""
    try:
        gold_num = float(gold.replace(",", ""))
    except (ValueError, TypeError):
        return False

    abs_tol = 0.5
    rel_tol = 0.01
    if tolerance:
        abs_tol = tolerance.get("abs_tol", abs_tol)
        rel_tol = tolerance.get("rel_tol", rel_tol)

    # Primary path: extract_final_answer_number (prioritizes final answer patterns)
    resp_num = extract_final_answer_number(response, gold_num)
    if resp_num is not None:
        if abs(resp_num - gold_num) <= abs_tol:
            return True
        if gold_num != 0 and abs(resp_num - gold_num) / abs(gold_num) <= rel_tol:
            return True

    # Fallback: extract_first_number (word numbers, LaTeX, etc.)
    resp_num = extract_first_number(response)
    if resp_num is not None:
        if abs(resp_num - gold_num) <= abs_tol:
            return True
        if gold_num != 0 and abs(resp_num - gold_num) / abs(gold_num) <= rel_tol:
            return True

    return False


def grade_code_output(response: str, gold: str, aliases: list[str]) -> bool:
    """For code output, check exact match or alias match in response."""
    return grade_alias_plus_normalization(response, gold, aliases)


def grade_fraction_or_decimal(response: str, gold: str, aliases: list[str]) -> bool:
    """Check fraction or decimal equivalence, including LaTeX \\frac{}{}."""
    # First try alias matching
    if grade_alias_plus_normalization(response, gold, aliases):
        return True
    # Try numeric equivalence via final-answer extraction
    try:
        gold_num = float(gold.replace(",", ""))
        resp_num = extract_final_answer_number(response, gold_num)
        if resp_num is not None and abs(resp_num - gold_num) < 0.01:
            return True
        # Fallback to extract_first_number (handles LaTeX \frac)
        resp_num = extract_first_number(response)
        if resp_num is not None and abs(resp_num - gold_num) < 0.01:
            return True
    except (ValueError, TypeError):
        pass
    # Also check LaTeX fractions explicitly
    m = re.search(r'\\frac\{(\d+)\}\{(\d+)\}', response)
    if m:
        try:
            gold_num = float(gold.replace(",", ""))
            frac_val = float(m.group(1)) / float(m.group(2))
            if abs(frac_val - gold_num) < 0.01:
                return True
        except (ValueError, TypeError, ZeroDivisionError):
            pass
    return False


def grade_yes_no(response: str, gold: str) -> bool:
    """Check if response contains the correct yes/no."""
    resp_lower = response.lower().strip()
    gold_lower = gold.lower().strip()
    if gold_lower in ("yes", "no"):
        # Check that the response contains the right answer
        has_yes = "yes" in resp_lower
        has_no = "no" in resp_lower
        if gold_lower == "yes":
            return has_yes
        else:
            return has_no and not has_yes
    return False


def grade_item(response: str, item: dict) -> bool:
    """Grade a response against an item's correct answer."""
    rule = item["grading_rule"]
    gold = item["gold_answer"]
    aliases = item.get("gold_answer_aliases", [])
    tolerance = item.get("tolerance")

    if rule == "alias_plus_normalization":
        return grade_alias_plus_normalization(response, gold, aliases)
    elif rule == "approx_numeric_small":
        return grade_approx_numeric_small(response, gold, tolerance)
    elif rule == "code_output":
        return grade_code_output(response, gold, aliases)
    elif rule == "fraction_or_decimal":
        return grade_fraction_or_decimal(response, gold, aliases)
    elif rule == "yes_no":
        return grade_yes_no(response, gold)
    else:
        # Fallback: alias matching
        return grade_alias_plus_normalization(response, gold, aliases)


def classify_transition(t1_correct: bool, t2_correct: bool) -> str:
    """Classify the T1→T2 transition."""
    if not t1_correct and t2_correct:
        return "wrong_to_right"
    elif t1_correct and t2_correct:
        return "right_to_right"
    elif t1_correct and not t2_correct:
        return "right_to_wrong"
    else:
        return "wrong_to_wrong"


# ---------------------------------------------------------------------------
# Loading items
# ---------------------------------------------------------------------------

def load_clean_items() -> list[dict]:
    """Load all clean Family C items from C1 and C2 candidate JSONs."""
    c1_path = REPO_ROOT / "data" / "family_c" / "family_c_c1_candidates.json"
    c2_path = REPO_ROOT / "data" / "family_c" / "family_c_c2_candidates.json"

    items = []
    for path in [c1_path, c2_path]:
        with open(path) as f:
            raw = json.load(f)
        clean = [i for i in raw if i.get("draft_status") == "clean"]
        items.extend(clean)

    return items


# ---------------------------------------------------------------------------
# API calling
# ---------------------------------------------------------------------------

def call_model(model: str, messages: list[dict]) -> dict:
    """Call model via OpenRouter client. Returns the client result dict."""
    return query(
        model=model,
        messages=messages,
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
        timeout=90,
        retries=2,
        json_mode=False,
    )


def run_item(model: str, item: dict) -> dict:
    """Run the self-correction protocol for one item on one model."""
    subfamily = item["subfamily"]
    question = item["turn1_prompt"]

    # T1: ask the question
    t1_messages = [
        {"role": "user", "content": question + "\n\nPlease give a concise answer."}
    ]
    t1_result = call_model(model, t1_messages)
    t1_response = t1_result.get("response_text") or ""
    t1_error = t1_result.get("error")

    time.sleep(INTER_CALL_DELAY)

    # T2: re-prompt
    if subfamily == "C1":
        t2_user_msg = C1_T2_PROMPT
    else:  # C2
        evidence = item.get("evidence_snippet", "")
        t2_user_msg = C2_T2_TEMPLATE.format(evidence=evidence)

    t2_messages = [
        {"role": "user", "content": question + "\n\nPlease give a concise answer."},
        {"role": "assistant", "content": t1_response},
        {"role": "user", "content": t2_user_msg},
    ]
    t2_result = call_model(model, t2_messages)
    t2_response = t2_result.get("response_text") or ""
    t2_error = t2_result.get("error")

    # Grade
    t1_correct = grade_item(t1_response, item) if t1_response else False
    t2_correct = grade_item(t2_response, item) if t2_response else False
    transition = classify_transition(t1_correct, t2_correct)

    return {
        "item_id": item["item_id"],
        "family": item["family"],
        "subfamily": item["subfamily"],
        "stratum": item["stratum"],
        "category": item.get("category", ""),
        "grading_rule": item["grading_rule"],
        "gold_answer": item["gold_answer"],
        "model": model,
        "t1_response": t1_response,
        "t1_correct": t1_correct,
        "t1_error": t1_error,
        "t1_latency_ms": t1_result.get("latency_ms"),
        "t2_response": t2_response,
        "t2_correct": t2_correct,
        "t2_error": t2_error,
        "t2_latency_ms": t2_result.get("latency_ms"),
        "transition": transition,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def save_jsonl(results: list[dict], path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        for r in results:
            f.write(json.dumps(r, default=str) + "\n")


def save_summary_csv(results: list[dict], path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "item_id", "subfamily", "stratum", "t1_answer", "t1_correct",
        "t2_answer", "t2_correct", "transition",
    ]
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in results:
            writer.writerow({
                "item_id": r["item_id"],
                "subfamily": r["subfamily"],
                "stratum": r["stratum"],
                "t1_answer": (r["t1_response"] or "")[:200],
                "t1_correct": r["t1_correct"],
                "t2_answer": (r["t2_response"] or "")[:200],
                "t2_correct": r["t2_correct"],
                "transition": r["transition"],
            })


def model_slug(model: str) -> str:
    return model.replace("/", "-").replace(".", "")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run_sweep():
    items = load_clean_items()
    print(f"Loaded {len(items)} clean items (C1 + C2)")

    for model in MODELS:
        slug = model_slug(model)
        print(f"\n{'='*60}")
        print(f"Model: {model}  ({len(items)} items, {len(items)*2} API calls)")
        print(f"{'='*60}")

        results = []
        errors = 0
        for i, item in enumerate(items):
            print(f"  [{i+1}/{len(items)}] {item['item_id']} ...", end=" ", flush=True)
            try:
                r = run_item(model, item)
                results.append(r)
                status = r["transition"]
                if r["t1_error"] or r["t2_error"]:
                    errors += 1
                    status += " (API error)"
                print(status)
            except Exception as e:
                print(f"EXCEPTION: {e}")
                errors += 1

            time.sleep(INTER_CALL_DELAY)

        # Save outputs
        jsonl_path = OUTPUT_DIR / f"sweep_raw_{slug}.jsonl"
        csv_path = OUTPUT_DIR / f"sweep_summary_{slug}.csv"
        save_jsonl(results, jsonl_path)
        save_summary_csv(results, csv_path)

        # Print summary
        transitions = {}
        for r in results:
            t = r["transition"]
            transitions[t] = transitions.get(t, 0) + 1

        print(f"\n  Results for {model}:")
        print(f"    Items: {len(results)}, Errors: {errors}")
        print(f"    Transitions: {transitions}")
        print(f"    Saved: {jsonl_path}")
        print(f"    Saved: {csv_path}")

    print(f"\n{'='*60}")
    print("Sweep complete!")


if __name__ == "__main__":
    run_sweep()
