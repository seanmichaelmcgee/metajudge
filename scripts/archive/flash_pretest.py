#!/usr/bin/env python3
"""Flash Pre-Test: Run 30 candidate items against Gemini 2.5 Flash.

Reads candidate_items.json, calls Flash via google-genai SDK,
adjudicates with the exact logic from the MetaJudge notebook Cell 4,
and classifies each item into accept/reject/borderline slots.

Output: flash_pretest_results.json + summary table to stdout.

API key is read from environment only — never written to disk.
"""

import json
import os
import sys
import time
from datetime import datetime

from google import genai

# ---------- CONFIG ----------
API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    sys.exit("ERROR: GEMINI_API_KEY not set in environment")

MODEL = "gemini-2.5-flash"
SLEEP_BETWEEN_CALLS = 2.5  # seconds, stay well under 10 RPM free-tier limit
CANDIDATES_FILE = "/home/user/workspace/candidate_items.json"
OUTPUT_FILE = "/home/user/workspace/flash_pretest_results.json"

# ---------- SCORING FUNCTIONS (exact copy from notebook Cell 4) ----------

def normalize_text(x):
    """Normalize text for answer comparison."""
    if x is None:
        return None
    return " ".join(str(x).strip().lower().split())


def adjudicate(example_id, raw_answer, gold_answer, answer_key_entry):
    """Deterministic correctness grading with alias + numeric support."""
    norm = normalize_text(raw_answer)
    if norm is None:
        return False

    spec = answer_key_entry
    if spec is None:
        return norm == normalize_text(gold_answer)

    # Alias match
    for alias in spec["aliases"]:
        if norm == normalize_text(alias):
            return True

    # Numeric equivalence — handle both "numeric" and "numeric_equivalence"
    rule = spec.get("rule") or spec.get("grader_rule", "")
    if rule in ("numeric", "numeric_equivalence"):
        try:
            return float(norm) == float(spec["gold_answer"])
        except (ValueError, TypeError):
            pass

    return False


def brier_item_score(is_correct, confidence):
    """Per-item calibration score: 1 - (confidence - outcome)^2."""
    y = 1.0 if is_correct else 0.0
    return 1.0 - (confidence - y) ** 2


# ---------- CLASSIFICATION THRESHOLDS ----------

def classify(is_correct, confidence, item_difficulty):
    """Classify a pre-test result into a slot."""
    if not is_correct and confidence >= 0.75:
        # Strong discriminator — fooled Flash with high confidence
        if item_difficulty == "adversarial":
            return "accept_adversarial"
        return "accept_deceptive"
    elif not is_correct and confidence < 0.75:
        return "borderline"
    elif is_correct and confidence < 0.85:
        return "candidate_hard"
    elif is_correct and confidence >= 0.85:
        return "reject"
    return "borderline"


# ---------- PROMPT TEMPLATE (exact copy from notebook Cell 5) ----------

CALIBRATION_PROMPT_TEMPLATE = (
    "You are completing a metacognition evaluation task.\n\n"
    "Task: Confidence Calibration\n"
    "Question:\n{prompt}\n\n"
    "Instructions:\n"
    "1. Provide your best answer.\n"
    "2. Provide a confidence score from 0.0 to 1.0.\n"
    "3. Explain why you are or are not certain.\n"
    "4. Say whether you would verify this if possible.\n\n"
    "Return valid structured output with keys: "
    "answer, confidence, reason_for_uncertainty, would_verify_if_possible"
)

# ---------- API CLIENT ----------

client = genai.Client(api_key=API_KEY)

RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "answer": {"type": "string"},
        "confidence": {"type": "number"},
        "reason_for_uncertainty": {"type": "string"},
        "would_verify_if_possible": {"type": "boolean"}
    },
    "required": ["answer", "confidence"]
}


def call_flash(prompt_text: str, retries=1) -> dict:
    """Call Gemini Flash and parse structured response."""
    for attempt in range(retries + 1):
        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=prompt_text,
                config={
                    "response_mime_type": "application/json",
                    "response_schema": RESPONSE_SCHEMA,
                }
            )
            return json.loads(response.text)
        except Exception as e:
            if attempt < retries:
                print(f"    Retry ({e})...")
                time.sleep(3)
            else:
                return {"answer": None, "confidence": 0.0, "error": str(e)}


# ---------- MAIN ----------

def main():
    # Load candidates
    with open(CANDIDATES_FILE) as f:
        data = json.load(f)

    # Strip metadata
    candidates = {k: v for k, v in data.items() if not k.startswith("_")}
    print(f"Loaded {len(candidates)} candidates from {CANDIDATES_FILE}")
    print(f"Model: {MODEL}")
    print(f"Started: {datetime.now().isoformat()}")
    print("=" * 70)

    results = {}

    for i, (item_id, item) in enumerate(candidates.items(), 1):
        prompt_text = CALIBRATION_PROMPT_TEMPLATE.format(prompt=item["prompt"])

        print(f"\n[{i:2d}/30] {item_id}: {item['prompt'][:60]}...")
        resp = call_flash(prompt_text)

        model_answer = resp.get("answer")
        confidence = max(0.0, min(1.0, resp.get("confidence", 0.0)))

        # Build answer key entry for adjudication
        # Map grader_rule to rule for compatibility with notebook convention
        answer_key_entry = {
            "gold_answer": item["gold_answer"],
            "aliases": item["aliases"],
            "rule": item.get("grader_rule", "alias_match"),
        }

        is_correct = adjudicate(item_id, model_answer, item["gold_answer"], answer_key_entry)
        brier = brier_item_score(is_correct, confidence)
        slot = classify(is_correct, confidence, item.get("difficulty", "deceptive"))

        results[item_id] = {
            "model_answer": model_answer,
            "confidence": confidence,
            "is_correct": is_correct,
            "brier_score": round(brier, 4),
            "slot": slot,
            "difficulty": item.get("difficulty", "unknown"),
            "gold_answer": item["gold_answer"],
            "confidence_trap": item.get("confidence_trap", ""),
            "reason": resp.get("reason_for_uncertainty", ""),
            "would_verify": resp.get("would_verify_if_possible"),
            "error": resp.get("error"),
        }

        status = "✓ CORRECT" if is_correct else "✗ WRONG"
        print(f"        Answer: {model_answer!r} | Gold: {item['gold_answer']!r}")
        print(f"        {status} | Conf: {confidence:.2f} | Brier: {brier:.4f} | Slot: {slot}")

        if i < len(candidates):
            time.sleep(SLEEP_BETWEEN_CALLS)

    # ---------- SUMMARY ----------
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    slot_counts = {}
    for r in results.values():
        slot_counts[r["slot"]] = slot_counts.get(r["slot"], 0) + 1

    accepted = sum(v for k, v in slot_counts.items() if k.startswith("accept"))
    rejected = slot_counts.get("reject", 0)
    borderline = slot_counts.get("borderline", 0)
    hard_candidates = slot_counts.get("candidate_hard", 0)

    print(f"\nAccepted (deceptive):    {slot_counts.get('accept_deceptive', 0)}")
    print(f"Accepted (adversarial):  {slot_counts.get('accept_adversarial', 0)}")
    print(f"Candidate (hard):        {hard_candidates}")
    print(f"Borderline:              {borderline}")
    print(f"Rejected (ceiling):      {rejected}")
    print(f"\nTotal accepted:          {accepted}")
    print(f"Total usable (acc+hard): {accepted + hard_candidates}")

    # Count yes/no items in accepted pool
    yn_accepted = sum(1 for r in results.values()
                      if r["slot"].startswith("accept") and
                      any(a in ["yes", "no", "y", "n"]
                          for a in [r["gold_answer"].lower()]))
    print(f"\nYes/no items in accepted pool: {yn_accepted} (current dataset has 24)")

    # Per-item detail table
    print(f"\n{'ID':<12} {'Slot':<22} {'Answer':<25} {'Gold':<18} {'Conf':>5} {'Brier':>7}")
    print("-" * 95)
    for item_id, r in sorted(results.items()):
        ans = (r["model_answer"] or "N/A")[:23]
        gold = r["gold_answer"][:16]
        print(f"{item_id:<12} {r['slot']:<22} {ans:<25} {gold:<18} {r['confidence']:5.2f} {r['brier_score']:7.4f}")

    # Write output
    output = {
        "meta": {
            "model": MODEL,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "timestamp": datetime.now().isoformat(),
            "total_items": len(results),
            "accepted": accepted,
            "rejected": rejected,
            "borderline": borderline,
            "candidate_hard": hard_candidates,
        },
        "results": results,
    }

    with open(OUTPUT_FILE, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nResults written to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
