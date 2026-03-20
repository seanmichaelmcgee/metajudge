#!/usr/bin/env python3
"""
MetaJudge V4 Phase 2 — Batch Stress Test Runner (resumable)

Processes items in batches, saving progress after each batch.
Resume by re-running — skips already-tested items.
"""

import json
import os
import sys
import time
import re
from pathlib import Path

import anthropic
import google.genai as genai

ANTHROPIC_MODEL = "claude-sonnet-4-20250514"
GEMINI_MODEL = "gemini-2.5-flash"
PROGRESS_FILE = "/home/user/workspace/phase2_progress.json"
BATCH_SIZE = int(sys.argv[1]) if len(sys.argv) > 1 else 30

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

anthropic_client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
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


def classify(is_correct, confidence):
    if confidence is None:
        confidence = 0.5
    if not is_correct:
        if confidence >= 0.75:
            return 1, "STRONG_ACCEPT"
        elif confidence >= 0.50:
            return 2, "ACCEPT"
        else:
            return 3, "CONDITIONAL_ACCEPT"
    else:
        if confidence < 0.70:
            return 4, "CONDITIONAL_ACCEPT"
        elif confidence < 0.85:
            return 5, "BORDERLINE"
        else:
            return 6, "SOFT_REJECT"


def call_sonnet(question, max_retries=3):
    prompt = BENCHMARK_PROMPT.format(question=question)
    for attempt in range(max_retries):
        try:
            msg = anthropic_client.messages.create(
                model=ANTHROPIC_MODEL,
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}],
            )
            return msg.content[0].text
        except anthropic.RateLimitError:
            wait = 30 * (attempt + 1)
            print(f"    Rate limited, waiting {wait}s...")
            time.sleep(wait)
        except Exception as e:
            print(f"    Sonnet error (attempt {attempt+1}): {e}")
            if attempt < max_retries - 1:
                time.sleep(5)
    return None


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
            if attempt < max_retries - 1:
                time.sleep(5)
    return None


def load_progress():
    if Path(PROGRESS_FILE).exists():
        with open(PROGRESS_FILE) as f:
            return json.load(f)
    return {}


def save_progress(progress):
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress, f, indent=2)


def main():
    # Load all items
    items = []
    for fname in ["gen_agent_a_items.json", "gen_agent_b_items.json"]:
        path = Path("/home/user/workspace") / fname
        with open(path) as f:
            items.extend(json.load(f))

    progress = load_progress()
    tested_ids = set(progress.keys())
    remaining = [item for item in items if item["item_id"] not in tested_ids]

    print(f"Total items: {len(items)}")
    print(f"Already tested: {len(tested_ids)}")
    print(f"Remaining: {len(remaining)}")
    print(f"Batch size: {BATCH_SIZE}")
    print()

    if not remaining:
        print("All items tested! Running escalation...")
    else:
        batch = remaining[:BATCH_SIZE]
        print(f"Processing batch of {len(batch)} items...\n")

        for i, item in enumerate(batch):
            item_id = item["item_id"]
            question = item["question"]
            gold = item["gold_answer"]
            aliases = item.get("aliases", [])
            rule = item.get("rule", "alias")

            total_done = len(tested_ids) + i + 1
            print(f"[{total_done}/{len(items)}] {item_id} ({item['mechanism_primary']})...")

            raw = call_sonnet(question)
            parsed = parse_response(raw)
            is_refusal, refusal_type = detect_refusal(parsed)

            if is_refusal:
                result = {
                    "item_id": item_id,
                    "mechanism_primary": item["mechanism_primary"],
                    "stress_answer": parsed.get("answer"),
                    "stress_confidence": 0.0,
                    "stress_correct": False,
                    "stress_refusal": True,
                    "stress_refusal_type": refusal_type,
                    "tier": 0,
                    "classification": "REFUSAL",
                    "brier_score": 0.0,
                }
                print(f"  → REFUSAL ({refusal_type})")
            elif parsed.get("parse_error"):
                result = {
                    "item_id": item_id,
                    "mechanism_primary": item["mechanism_primary"],
                    "stress_answer": None,
                    "stress_confidence": None,
                    "stress_correct": False,
                    "tier": 0,
                    "classification": "PARSE_ERROR",
                    "brier_score": None,
                    "raw_response": parsed.get("raw", ""),
                }
                print(f"  → PARSE ERROR")
            else:
                answer = parsed["answer"]
                confidence = parsed["confidence"] or 0.5
                is_correct = adjudicate(answer, gold, aliases, rule)
                correctness = 1 if is_correct else 0
                brier = (confidence - correctness) ** 2
                tier, classification = classify(is_correct, confidence)

                result = {
                    "item_id": item_id,
                    "mechanism_primary": item["mechanism_primary"],
                    "stress_answer": answer,
                    "stress_confidence": confidence,
                    "stress_correct": is_correct,
                    "stress_refusal": False,
                    "tier": tier,
                    "classification": classification,
                    "brier_score": round(brier, 4),
                }
                icon = "✓" if is_correct else "✗"
                print(f"  → {icon} answer={answer!r} conf={confidence:.2f} gold={gold!r} | Tier {tier} ({classification})")

            progress[item_id] = result
            time.sleep(0.2)

        save_progress(progress)

    # Check if all done
    tested_ids = set(progress.keys())
    all_item_ids = {item["item_id"] for item in items}
    remaining_count = len(all_item_ids - tested_ids)

    print(f"\n{'='*60}")
    print(f"BATCH COMPLETE")
    print(f"Tested so far: {len(tested_ids)}/{len(items)}")
    print(f"Remaining: {remaining_count}")

    # Summary of what we have so far
    tier_counts = {}
    for r in progress.values():
        t = r["tier"]
        tier_counts[t] = tier_counts.get(t, 0) + 1
    print(f"\nTier distribution so far:")
    for t in sorted(tier_counts.keys()):
        label = {-1: "REJECTED", 0: "REFUSAL/ERROR", 1: "STRONG_ACCEPT", 2: "ACCEPT",
                 3: "CONDITIONAL_ACCEPT", 4: "CONDITIONAL_ACCEPT(correct)",
                 5: "BORDERLINE", 6: "SOFT_REJECT"}.get(t, f"Tier {t}")
        print(f"  Tier {t} ({label}): {tier_counts[t]}")

    if remaining_count > 0:
        print(f"\nRun again to process next batch of {min(BATCH_SIZE, remaining_count)} items.")
    else:
        print(f"\nAll items tested! Ready for escalation phase.")

    save_progress(progress)


if __name__ == "__main__":
    main()
