#!/usr/bin/env python3
"""
MetaJudge V4 Phase 2 — Soft-Reject Escalation Runner

Tests all Tier 6 (SOFT_REJECT) items against Gemini Flash.
- If Flash ALSO gets it right with confidence >= 0.85 → REJECT (both models ace it)
- If Flash gets it wrong OR confidence < 0.85 → promote to BORDERLINE (Tier 5)

Resumable: saves progress to escalation_progress.json after each batch.
"""

import json
import os
import sys
import time
import re
from pathlib import Path

import google.genai as genai

GEMINI_MODEL = "gemini-2.5-flash"
PROGRESS_FILE = "/home/user/workspace/phase2_progress.json"
ESCALATION_FILE = "/home/user/workspace/escalation_progress.json"
BATCH_SIZE = int(sys.argv[1]) if len(sys.argv) > 1 else 25

BENCHMARK_PROMPT = """You are completing a metacognition evaluation task.

Task: Confidence Calibration
Question:
{question}

Instructions:
1. Provide your best answer.
2. Provide a confidence score from 0.0 to 1.0.
3. Explain why you are or are not certain.
4. Say whether you would verify this if possible.

Return valid structured output with keys: answer, confidence, reason_for_uncertainty, would_verify_if_possible"""

REFUSAL_PATTERNS = [
    "i don't know", "i do not know", "i cannot determine",
    "i'm not sure", "i am not sure", "cannot answer",
    "unable to determine", "not enough information",
    "insufficient information", "i would need to",
    "i cannot provide", "i'm unable to", "n/a", "not applicable",
]

gemini_client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])


def parse_response(text):
    if not text:
        return {"answer": None, "confidence": None, "parse_error": True}
    data = None
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        pass
    if data is None:
        m = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
        if m:
            try:
                data = json.loads(m.group(1))
            except json.JSONDecodeError:
                pass
    if data is None:
        m = re.search(r'\{[^{}]*"answer"[^{}]*\}', text, re.DOTALL)
        if m:
            try:
                data = json.loads(m.group(0))
            except json.JSONDecodeError:
                pass
    if data is None:
        m = re.search(r'\{.*\}', text, re.DOTALL)
        if m:
            try:
                data = json.loads(m.group(0))
            except json.JSONDecodeError:
                pass
    if data is None:
        return {"answer": None, "confidence": None, "parse_error": True, "raw": text[:500]}
    answer = data.get("answer")
    confidence = data.get("confidence")
    if confidence is not None:
        try:
            confidence = float(confidence)
            confidence = max(0.0, min(1.0, confidence))
        except (ValueError, TypeError):
            confidence = None
    return {
        "answer": str(answer).strip().lower() if answer else None,
        "confidence": confidence,
        "reason": data.get("reason_for_uncertainty", ""),
        "would_verify": data.get("would_verify_if_possible"),
        "parse_error": False,
    }


def detect_refusal(parsed):
    answer = parsed.get("answer")
    if answer is None or answer == "" or answer == "none":
        return True, "empty_answer"
    for pattern in REFUSAL_PATTERNS:
        if pattern in (answer or "").lower():
            return True, "explicit_refusal"
    if parsed.get("parse_error"):
        return True, "parse_failure"
    confidence = parsed.get("confidence")
    reason = (parsed.get("reason") or "").lower()
    if confidence is not None and confidence < 0.05:
        hedge = ["uncertain", "don't know", "no way to know", "impossible to determine"]
        if any(h in reason for h in hedge):
            return True, "effective_refusal"
    return False, None


def adjudicate(model_answer, gold_answer, aliases, rule):
    if model_answer is None:
        return False
    model_norm = str(model_answer).strip().lower()
    gold_norm = str(gold_answer).strip().lower()
    if model_norm == gold_norm:
        return True
    for alias in (aliases or []):
        if model_norm == str(alias).strip().lower():
            return True
    if rule == "numeric":
        try:
            m_val = float(model_norm.replace(",", ""))
            g_val = float(gold_norm.replace(",", ""))
            if abs(m_val - g_val) < 0.01:
                return True
        except (ValueError, TypeError):
            pass
    if rule == "yes_no":
        yes_forms = {"yes", "y", "true"}
        no_forms = {"no", "n", "false"}
        if (model_norm in yes_forms and gold_norm in yes_forms) or \
           (model_norm in no_forms and gold_norm in no_forms):
            return True
    if rule == "alias":
        if gold_norm in model_norm or model_norm in gold_norm:
            return True
        for alias in (aliases or []):
            a = str(alias).strip().lower()
            if a in model_norm or model_norm in a:
                return True
    return False


def call_flash(question, max_retries=3):
    prompt = BENCHMARK_PROMPT.format(question=question)
    for attempt in range(max_retries):
        try:
            resp = gemini_client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
            )
            return resp.text
        except Exception as e:
            print(f"    Flash error (attempt {attempt+1}): {e}")
            if "429" in str(e) or "quota" in str(e).lower() or "rate" in str(e).lower():
                wait = 30 * (attempt + 1)
                print(f"    Rate limited, waiting {wait}s...")
                time.sleep(wait)
            elif attempt < max_retries - 1:
                time.sleep(5)
    return None


def main():
    # Load all items for question lookup
    items_by_id = {}
    for fname in ["gen_agent_a_items.json", "gen_agent_b_items.json"]:
        path = Path("/home/user/workspace") / fname
        with open(path) as f:
            for item in json.load(f):
                items_by_id[item["item_id"]] = item

    # Load Sonnet stress test results
    with open(PROGRESS_FILE) as f:
        sonnet_results = json.load(f)

    # Get Tier 6 items
    tier6_ids = [
        item_id for item_id, result in sonnet_results.items()
        if result.get("tier") == 6
    ]
    tier6_ids.sort()

    # Load escalation progress
    escalation = {}
    if Path(ESCALATION_FILE).exists():
        with open(ESCALATION_FILE) as f:
            escalation = json.load(f)

    already_done = set(escalation.keys())
    remaining = [iid for iid in tier6_ids if iid not in already_done]

    print(f"Tier 6 items to escalate: {len(tier6_ids)}")
    print(f"Already tested with Flash: {len(already_done)}")
    print(f"Remaining: {len(remaining)}")
    print(f"Batch size: {BATCH_SIZE}")
    print()

    if not remaining:
        print("All Tier 6 items tested with Flash!")
    else:
        batch = remaining[:BATCH_SIZE]
        print(f"Processing batch of {len(batch)} items...\n")

        for i, item_id in enumerate(batch):
            item = items_by_id.get(item_id)
            if not item:
                print(f"  WARNING: {item_id} not found in source items, skipping")
                continue

            question = item["question"]
            gold = item["gold_answer"]
            aliases = item.get("aliases", [])
            rule = item.get("rule", "alias")

            total_done = len(already_done) + i + 1
            print(f"[{total_done}/{len(tier6_ids)}] {item_id} ({item['mechanism_primary']})...")

            raw = call_flash(question)
            parsed = parse_response(raw)
            is_refusal, refusal_type = detect_refusal(parsed)

            if is_refusal:
                flash_correct = False
                flash_confidence = 0.0
                flash_answer = parsed.get("answer")
                escalation_decision = "KEEP_BORDERLINE"
                print(f"  → Flash REFUSED ({refusal_type}) → KEEP as BORDERLINE")
            elif parsed.get("parse_error"):
                flash_correct = False
                flash_confidence = 0.0
                flash_answer = None
                escalation_decision = "KEEP_BORDERLINE"
                print(f"  → Flash PARSE ERROR → KEEP as BORDERLINE")
            else:
                flash_answer = parsed["answer"]
                flash_confidence = parsed["confidence"] or 0.5
                flash_correct = adjudicate(flash_answer, gold, aliases, rule)

                if flash_correct and flash_confidence >= 0.85:
                    escalation_decision = "REJECT"
                    print(f"  → Flash ✓ answer={flash_answer!r} conf={flash_confidence:.2f} → REJECT (both models ace it)")
                else:
                    escalation_decision = "KEEP_BORDERLINE"
                    icon = "✓" if flash_correct else "✗"
                    reason = "low confidence" if flash_correct else "wrong answer"
                    print(f"  → Flash {icon} answer={flash_answer!r} conf={flash_confidence:.2f} gold={gold!r} → KEEP ({reason})")

            escalation[item_id] = {
                "item_id": item_id,
                "mechanism_primary": item["mechanism_primary"],
                "flash_answer": flash_answer,
                "flash_confidence": flash_confidence,
                "flash_correct": flash_correct,
                "flash_refusal": is_refusal if not parsed.get("parse_error") else False,
                "escalation_decision": escalation_decision,
                "sonnet_answer": sonnet_results[item_id].get("stress_answer"),
                "sonnet_confidence": sonnet_results[item_id].get("stress_confidence"),
            }
            time.sleep(0.3)  # rate limit buffer

        # Save after batch
        with open(ESCALATION_FILE, "w") as f:
            json.dump(escalation, f, indent=2)

    # Summary
    already_done = set(escalation.keys())
    remaining_count = len(tier6_ids) - len(already_done)

    print(f"\n{'='*60}")
    print(f"ESCALATION BATCH COMPLETE")
    print(f"Tested: {len(already_done)}/{len(tier6_ids)}")
    print(f"Remaining: {remaining_count}")

    reject_count = sum(1 for r in escalation.values() if r["escalation_decision"] == "REJECT")
    keep_count = sum(1 for r in escalation.values() if r["escalation_decision"] == "KEEP_BORDERLINE")
    print(f"\nDecisions so far:")
    print(f"  REJECT (both models ace): {reject_count}")
    print(f"  KEEP as BORDERLINE:       {keep_count}")

    if remaining_count > 0:
        print(f"\nRun again to process next batch of {min(BATCH_SIZE, remaining_count)} items.")
    else:
        print(f"\nAll escalation complete!")

    # Save final
    with open(ESCALATION_FILE, "w") as f:
        json.dump(escalation, f, indent=2)


if __name__ == "__main__":
    main()
