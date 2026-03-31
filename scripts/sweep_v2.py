"""
MetaJudge Family C: Sweep v2 — Redesigned Protocol
====================================================
Sprint v2 implementation of the self-correction protocol with:
  - C1: third-person detect-only (primary) / "Wait" fallback (short T1)
  - C2: reviewer's note framing
  - B0: independent re-answering baseline (diagnostic subset)
  - Confidence elicitation (ANSWER: | CONFIDENCE: format)
  - Edit-distance computation (t1↔t2, t1↔b0)
  - Per-condition temperature control

Usage:
    export OPENROUTER_API_KEY=...
    python scripts/sweep_v2.py              # Full sweep
    python scripts/sweep_v2.py --smoke-test # Quick 3-item validation
"""

import csv
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.openrouter.client import query

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
MODELS = [
    "anthropic/claude-sonnet-4.6",
    "openai/gpt-5.2",
    "deepseek/deepseek-r1",
    "google/gemini-2.5-flash",
    "openai/gpt-5-mini",
]

# Temperature settings per condition
TEMP_T1 = 0.0       # Turn 1: deterministic
TEMP_C1 = 0.0       # C1 condition: deterministic (no stochastic noise)
TEMP_C2 = 0.3       # C2 condition: slight stochasticity for evidence integration
TEMP_B0 = 0.0       # B0 baseline: deterministic (must match T1 for fair comparison)

MAX_TOKENS = 4096   # Increased — reasoning models need more tokens
INTER_CALL_DELAY = 0.5

OUTPUT_DIR = REPO_ROOT / "outputs" / "family_c"

# ---------------------------------------------------------------------------
# T1 prompt suffix
# ---------------------------------------------------------------------------
T1_SUFFIX = (
    "\n\nPlease give a concise answer, then rate your confidence from 0 to 100."
    "\nFormat: ANSWER: [your answer] | CONFIDENCE: [0-100]"
)

# ---------------------------------------------------------------------------
# T2 prompts — C1 (primary + fallback)
# ---------------------------------------------------------------------------
C1_T2_PRIMARY = """A colleague submitted the following analysis for review.

As an independent reviewer, evaluate this analysis WITHOUT re-solving the problem from scratch. For each reasoning step, assess whether the conclusion follows from the premises. Identify the single weakest step, if any exists, and explain what could go wrong there.

Then provide your verdict:
- If you found an error: state the corrected answer
- If the analysis is sound: confirm the original answer
- If you are uncertain: state what additional information would be needed

ANSWER: [your answer] | CONFIDENCE: [0-100]"""

C1_T2_FALLBACK = """Wait — before confirming, let me reconsider.

Review your previous answer carefully. What is the most likely type of error, if any? If you find an error, provide the corrected answer. If you find no error, confirm your answer.

ANSWER: [your answer] | CONFIDENCE: [0-100]"""

# ---------------------------------------------------------------------------
# T2 prompt — C2 (reviewer's note framing)
# ---------------------------------------------------------------------------
C2_T2_TEMPLATE = """Here is a reviewer's note on your analysis:

{evidence}

Consider this feedback carefully. If it reveals an error in your reasoning, provide the corrected answer. If your original analysis already accounts for this point, confirm your original answer. If you are now uncertain, state what remains unclear.

ANSWER: [your answer] | CONFIDENCE: [0-100]"""

# ---------------------------------------------------------------------------
# B0 diagnostic subset (15 WR items)
# ---------------------------------------------------------------------------
B0_DIAGNOSTIC_IDS = {
    # C1 WR items (9 clean)
    "sc_c1_wr_001", "sc_c1_wr_002", "sc_c1_wr_004",
    "sc_c1_wr_006", "sc_c1_wr_007", "sc_c1_wr_008",
    "sc_c1_wr_009", "sc_c1_wr_010", "sc_c1_wr_011",
    # C2 WR items (first 6 of 7 to reach 15)
    "sc_c2_wr_001", "sc_c2_wr_006", "sc_c2_wr_007",
    "sc_c2_wr_008", "sc_c2_wr_009", "sc_c2_wr_010",
}

# ---------------------------------------------------------------------------
# Confidence parsing
# ---------------------------------------------------------------------------

def parse_answer_confidence(text: str) -> tuple[str, float | None]:
    """Extract answer and confidence from structured response.

    Returns (answer_text, confidence_normalized) where confidence is in [0,1] or None.
    """
    confidence = None
    answer = text  # fallback: full text

    # Try structured format: ANSWER: ... | CONFIDENCE: ...
    m = re.search(r'ANSWER:\s*(.+?)\s*\|\s*CONFIDENCE:\s*(\d+)', text, re.IGNORECASE)
    if m:
        answer = m.group(1).strip()
        confidence = float(m.group(2)) / 100.0
        return answer, confidence

    # Try just CONFIDENCE: N at end
    m = re.search(r'CONFIDENCE:\s*(\d+)', text, re.IGNORECASE)
    if m:
        confidence = float(m.group(1)) / 100.0

    # Try just ANSWER: at end
    m = re.search(r'ANSWER:\s*(.+?)(?:\s*$|\s*\|)', text, re.IGNORECASE)
    if m:
        answer = m.group(1).strip()

    return answer, confidence


# ---------------------------------------------------------------------------
# Edit-distance computation
# ---------------------------------------------------------------------------

def compute_edit_similarity(t1: str, t2: str) -> float:
    """Ratio of unchanged content. 1.0 = identical, 0.0 = completely different."""
    return SequenceMatcher(None, t1.lower(), t2.lower()).ratio()


# ---------------------------------------------------------------------------
# Grading functions (copied from sweep_5model_v062.py)
# ---------------------------------------------------------------------------

def extract_first_number(text: str) -> float | None:
    """Extract the first number from text, handling commas and negatives."""
    text = text.replace(",", "")
    m = re.search(r'-?\d+\.?\d*', text)
    if m:
        try:
            return float(m.group())
        except ValueError:
            return None
    return None


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
    """Extract first number and check within tolerance."""
    try:
        gold_num = float(gold.replace(",", ""))
    except (ValueError, TypeError):
        return False

    resp_num = extract_first_number(response)
    if resp_num is None:
        return False

    abs_tol = 0.5
    rel_tol = 0.01
    if tolerance:
        abs_tol = tolerance.get("abs_tol", abs_tol)
        rel_tol = tolerance.get("rel_tol", rel_tol)

    if abs(resp_num - gold_num) <= abs_tol:
        return True
    if gold_num != 0 and abs(resp_num - gold_num) / abs(gold_num) <= rel_tol:
        return True
    return False


def grade_code_output(response: str, gold: str, aliases: list[str]) -> bool:
    """For code output, check exact match or alias match in response."""
    return grade_alias_plus_normalization(response, gold, aliases)


def grade_fraction_or_decimal(response: str, gold: str, aliases: list[str]) -> bool:
    """Check fraction or decimal equivalence."""
    if grade_alias_plus_normalization(response, gold, aliases):
        return True
    try:
        gold_num = float(gold.replace(",", ""))
        resp_num = extract_first_number(response)
        if resp_num is not None and abs(resp_num - gold_num) < 0.01:
            return True
    except (ValueError, TypeError):
        pass
    return False


def grade_yes_no(response: str, gold: str) -> bool:
    """Check if response contains the correct yes/no."""
    resp_lower = response.lower().strip()
    gold_lower = gold.lower().strip()
    if gold_lower in ("yes", "no"):
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
    """Classify the T1->T2 transition."""
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

def call_model(model: str, messages: list[dict], temperature: float = TEMP_T1) -> dict:
    """Call model via OpenRouter client. Returns the client result dict."""
    return query(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=MAX_TOKENS,
        timeout=120,  # increased for reasoning models
        retries=2,
        json_mode=False,
    )


# ---------------------------------------------------------------------------
# Core protocol: run one item
# ---------------------------------------------------------------------------

def run_item(model: str, item: dict, run_b0: bool = False) -> dict:
    """Run the self-correction protocol for one item on one model.

    Protocol:
      T1: initial answer with confidence elicitation
      T2: C1 (third-person/fallback) or C2 (reviewer's note) re-prompt
      B0: (optional) independent re-answering baseline
    """
    subfamily = item["subfamily"]
    question = item["turn1_prompt"]

    # --- T1: ask the question ---
    t1_messages = [
        {"role": "user", "content": question + T1_SUFFIX}
    ]
    t1_result = call_model(model, t1_messages, temperature=TEMP_T1)
    t1_response = t1_result.get("response_text") or ""
    t1_error = t1_result.get("error")
    t1_answer, t1_confidence = parse_answer_confidence(t1_response)
    t1_correct = grade_item(t1_answer, item) if t1_answer else False

    time.sleep(INTER_CALL_DELAY)

    # --- T2: re-prompt (C1 or C2) ---
    c1_prompt_type = None
    if subfamily == "C1":
        if len(t1_response) > 500:
            t2_user_msg = C1_T2_PRIMARY
            c1_prompt_type = "primary"
        else:
            t2_user_msg = C1_T2_FALLBACK
            c1_prompt_type = "fallback"
        t2_temp = TEMP_C1
    else:  # C2
        evidence = item.get("evidence_snippet", "")
        t2_user_msg = C2_T2_TEMPLATE.format(evidence=evidence)
        t2_temp = TEMP_C2

    t2_messages = [
        {"role": "user", "content": question + T1_SUFFIX},
        {"role": "assistant", "content": t1_response},
        {"role": "user", "content": t2_user_msg},
    ]
    t2_result = call_model(model, t2_messages, temperature=t2_temp)
    t2_response = t2_result.get("response_text") or ""
    t2_error = t2_result.get("error")
    t2_answer, t2_confidence = parse_answer_confidence(t2_response)
    t2_correct = grade_item(t2_answer, item) if t2_answer else False

    # Transition and edit similarity
    transition = classify_transition(t1_correct, t2_correct)
    t1_t2_similarity = compute_edit_similarity(t1_response, t2_response)

    # --- B0: independent re-answering baseline (optional) ---
    b0_response = None
    b0_answer = None
    b0_confidence = None
    b0_correct = None
    b0_error = None
    b0_latency = None
    t1_b0_similarity = None
    b0_transition = None

    if run_b0:
        time.sleep(INTER_CALL_DELAY)
        b0_messages = [
            {"role": "user", "content": question + T1_SUFFIX}  # identical to T1 prompt
        ]
        b0_result = call_model(model, b0_messages, temperature=TEMP_B0)
        b0_response = b0_result.get("response_text") or ""
        b0_error = b0_result.get("error")
        b0_latency = b0_result.get("latency_ms")
        b0_answer, b0_confidence = parse_answer_confidence(b0_response)
        b0_correct = grade_item(b0_answer, item) if b0_answer else False
        t1_b0_similarity = compute_edit_similarity(t1_response, b0_response)
        b0_transition = classify_transition(t1_correct, b0_correct)

    return {
        "item_id": item["item_id"],
        "family": item["family"],
        "subfamily": item["subfamily"],
        "stratum": item["stratum"],
        "category": item.get("category", ""),
        "grading_rule": item["grading_rule"],
        "gold_answer": item["gold_answer"],
        "model": model,
        # T1
        "t1_response": t1_response,
        "t1_answer_parsed": t1_answer,
        "t1_correct": t1_correct,
        "t1_confidence": t1_confidence,
        "t1_error": t1_error,
        "t1_latency_ms": t1_result.get("latency_ms"),
        # T2
        "t2_response": t2_response,
        "t2_answer_parsed": t2_answer,
        "t2_correct": t2_correct,
        "t2_confidence": t2_confidence,
        "t2_error": t2_error,
        "t2_latency_ms": t2_result.get("latency_ms"),
        # Transition & similarity
        "transition": transition,
        "t1_t2_similarity": t1_t2_similarity,
        "c1_prompt_type": c1_prompt_type,
        # B0 fields (None if not run)
        "b0_response": b0_response,
        "b0_answer_parsed": b0_answer,
        "b0_confidence": b0_confidence,
        "b0_correct": b0_correct,
        "b0_error": b0_error,
        "b0_latency_ms": b0_latency,
        "t1_b0_similarity": t1_b0_similarity,
        "b0_transition": b0_transition,
        # Metadata
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
        "item_id", "subfamily", "stratum", "model",
        "t1_correct", "t1_confidence", "t2_correct", "t2_confidence", "transition",
        "t1_t2_similarity", "c1_prompt_type",
        "b0_correct", "b0_confidence",
    ]
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for r in results:
            writer.writerow({
                "item_id": r["item_id"],
                "subfamily": r["subfamily"],
                "stratum": r["stratum"],
                "model": r["model"],
                "t1_correct": r["t1_correct"],
                "t1_confidence": r.get("t1_confidence"),
                "t2_correct": r["t2_correct"],
                "t2_confidence": r.get("t2_confidence"),
                "transition": r["transition"],
                "t1_t2_similarity": r.get("t1_t2_similarity"),
                "c1_prompt_type": r.get("c1_prompt_type"),
                "b0_correct": r.get("b0_correct"),
                "b0_confidence": r.get("b0_confidence"),
            })


def model_slug(model: str) -> str:
    return model.replace("/", "-").replace(".", "")


# ---------------------------------------------------------------------------
# Smoke test
# ---------------------------------------------------------------------------

def run_smoke_test():
    """Quick validation: 3 items x 1 model."""
    items = load_clean_items()
    # Pick one C1 WR, one C2 WR, one RR
    smoke_items = []
    for item in items:
        if item["item_id"] == "sc_c1_wr_001":
            smoke_items.append(item)
        elif item["item_id"] == "sc_c2_wr_001":
            smoke_items.append(item)
        elif item["item_id"] == "sc_c1_rr_001":
            smoke_items.append(item)

    model = "openai/gpt-5-mini"
    print(f"Smoke test: {len(smoke_items)} items x {model}")

    results = []
    for item in smoke_items:
        run_b0 = item["item_id"] in B0_DIAGNOSTIC_IDS
        r = run_item(model, item, run_b0=run_b0)
        results.append(r)
        # Print key fields for validation
        print(f"\n  {r['item_id']}:")
        print(f"    T1: correct={r['t1_correct']}, conf={r.get('t1_confidence')}")
        print(f"    T2: correct={r['t2_correct']}, conf={r.get('t2_confidence')}")
        print(f"    Transition: {r['transition']}")
        sim = r.get("t1_t2_similarity")
        print(f"    Edit similarity: {sim:.3f}" if sim is not None else "    Edit similarity: N/A")
        if r.get("c1_prompt_type"):
            print(f"    C1 prompt type: {r['c1_prompt_type']}")
        if r.get("b0_response") is not None:
            print(f"    B0: correct={r['b0_correct']}, conf={r.get('b0_confidence')}")
            b0_sim = r.get("t1_b0_similarity")
            print(f"    B0 edit similarity: {b0_sim:.3f}" if b0_sim is not None else "    B0 edit similarity: N/A")

    # Save smoke test output (repo JSONL)
    out_path = OUTPUT_DIR / "smoke_test_v2.jsonl"
    save_jsonl(results, out_path)
    print(f"\nSmoke test JSONL saved: {out_path}")

    # Save to workspace (external copy)
    workspace_path = Path("/home/user/workspace/phase2_smoke_results.json")
    with open(workspace_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"Smoke test JSON saved: {workspace_path}")

    return results


# ---------------------------------------------------------------------------
# Full sweep
# ---------------------------------------------------------------------------

def run_sweep():
    items = load_clean_items()
    print(f"Loaded {len(items)} clean items (C1 + C2)")

    for model in MODELS:
        slug = model_slug(model)
        # Count B0 items for this run
        b0_count = sum(1 for i in items if i["item_id"] in B0_DIAGNOSTIC_IDS)
        api_calls = len(items) * 2 + b0_count
        print(f"\n{'='*60}")
        print(f"Model: {model}  ({len(items)} items, {api_calls} API calls)")
        print(f"{'='*60}")

        results = []
        errors = 0
        for i, item in enumerate(items):
            print(f"  [{i+1}/{len(items)}] {item['item_id']} ...", end=" ", flush=True)
            try:
                run_b0 = item["item_id"] in B0_DIAGNOSTIC_IDS
                r = run_item(model, item, run_b0=run_b0)
                results.append(r)
                status = r["transition"]
                if r["t1_error"] or r["t2_error"]:
                    errors += 1
                    status += " (API error)"
                if run_b0:
                    status += " [+B0]"
                print(status)
            except Exception as e:
                print(f"EXCEPTION: {e}")
                errors += 1

            time.sleep(INTER_CALL_DELAY)

        # Save outputs
        jsonl_path = OUTPUT_DIR / f"sweep_v2_raw_{slug}.jsonl"
        csv_path = OUTPUT_DIR / f"sweep_v2_summary_{slug}.csv"
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
    print("Sweep v2 complete!")


if __name__ == "__main__":
    if "--smoke-test" in sys.argv:
        run_smoke_test()
    else:
        run_sweep()
