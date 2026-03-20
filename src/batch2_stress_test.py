#!/usr/bin/env python3
"""
MetaJudge — Batch 2 Stress Test Pipeline

Runs all Batch 2 items through Sonnet, then escalates Tier 6 through Flash.
Saves progress to batch2_sonnet_progress.json and batch2_escalation_progress.json.
"""

import json
import os
import sys
import time
import re
from pathlib import Path

import anthropic
import google.genai as genai

SONNET_MODEL = "claude-sonnet-4-20250514"
FLASH_MODEL = "gemini-2.5-flash"
ITEMS_A = "/home/user/workspace/batch2_agent_a_items.json"
ITEMS_B = "/home/user/workspace/batch2_agent_b_items.json"
SONNET_PROGRESS = "/home/user/workspace/batch2_sonnet_progress.json"
ESCALATION_PROGRESS = "/home/user/workspace/batch2_escalation_progress.json"
BATCH_SIZE = int(sys.argv[2]) if len(sys.argv) > 2 else 25

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
            m_clean = model_norm.replace(",", "").replace("$", "").replace("%", "").replace("°", "").replace("c", "").replace("f", "").strip()
            g_clean = gold_norm.replace(",", "").replace("$", "").replace("%", "").replace("°", "").replace("c", "").replace("f", "").strip()
            m_val = float(m_clean)
            g_val = float(g_clean)
            if abs(m_val - g_val) < max(0.01, abs(g_val) * 0.005):
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
                model=SONNET_MODEL, max_tokens=1024,
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
                model=FLASH_MODEL, contents=prompt,
            )
            return resp.text
        except Exception as e:
            print(f"    Flash error (attempt {attempt+1}): {e}")
            if "429" in str(e) or "quota" in str(e).lower():
                wait = 30 * (attempt + 1)
                time.sleep(wait)
            elif attempt < max_retries - 1:
                time.sleep(5)
    return None


def load_json(path):
    if Path(path).exists():
        with open(path) as f:
            return json.load(f)
    return {}


def save_json(data, path):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def run_sonnet_phase(items, progress):
    tested_ids = set(progress.keys())
    remaining = [item for item in items if item["item_id"] not in tested_ids]
    
    print(f"\n=== SONNET STRESS TEST ===")
    print(f"Total: {len(items)}, Done: {len(tested_ids)}, Remaining: {len(remaining)}")
    
    batch = remaining[:BATCH_SIZE]
    if not batch:
        print("All items tested with Sonnet!")
        return progress, True
    
    print(f"Processing batch of {len(batch)}...\n")
    
    for i, item in enumerate(batch):
        iid = item["item_id"]
        total = len(tested_ids) + i + 1
        print(f"[{total}/{len(items)}] {iid} ({item['mechanism_primary']})...")
        
        raw = call_sonnet(item["question"])
        parsed = parse_response(raw)
        is_refusal, refusal_type = detect_refusal(parsed)
        
        if is_refusal or parsed.get("parse_error"):
            result = {
                "item_id": iid, "mechanism_primary": item["mechanism_primary"],
                "stress_answer": parsed.get("answer"), "stress_confidence": 0.0,
                "stress_correct": False, "stress_refusal": True,
                "tier": 0, "classification": "REFUSAL", "brier_score": 0.0,
            }
            print(f"  → REFUSAL")
        else:
            answer = parsed["answer"]
            confidence = parsed["confidence"] or 0.5
            is_correct = adjudicate(answer, item["gold_answer"], item.get("aliases", []), item.get("rule", "alias"))
            correctness = 1 if is_correct else 0
            brier = round((confidence - correctness) ** 2, 4)
            tier, classification = classify(is_correct, confidence)
            
            result = {
                "item_id": iid, "mechanism_primary": item["mechanism_primary"],
                "stress_answer": answer, "stress_confidence": confidence,
                "stress_correct": is_correct, "stress_refusal": False,
                "tier": tier, "classification": classification, "brier_score": brier,
            }
            icon = "✓" if is_correct else "✗"
            print(f"  → {icon} ans={answer!r} conf={confidence:.2f} gold={item['gold_answer']!r} | T{tier} ({classification})")
        
        progress[iid] = result
        time.sleep(0.3)
    
    save_json(progress, SONNET_PROGRESS)
    
    tested_ids = set(progress.keys())
    all_done = len([i for i in items if i["item_id"] not in tested_ids]) == 0
    
    tier_counts = {}
    for r in progress.values():
        t = r["tier"]
        tier_counts[t] = tier_counts.get(t, 0) + 1
    print(f"\nSonnet progress: {len(tested_ids)}/{len(items)}")
    for t in sorted(tier_counts.keys()):
        print(f"  Tier {t}: {tier_counts[t]}")
    
    return progress, all_done


def run_escalation_phase(items, sonnet_progress, escalation):
    items_by_id = {item["item_id"]: item for item in items}
    
    tier6_ids = sorted([iid for iid, r in sonnet_progress.items() if r.get("tier") == 6])
    already_done = set(escalation.keys())
    remaining = [iid for iid in tier6_ids if iid not in already_done]
    
    print(f"\n=== FLASH ESCALATION ===")
    print(f"Tier 6 items: {len(tier6_ids)}, Done: {len(already_done)}, Remaining: {len(remaining)}")
    
    batch = remaining[:BATCH_SIZE]
    if not batch:
        print("All Tier 6 items escalated!")
        return escalation, True
    
    print(f"Processing batch of {len(batch)}...\n")
    
    for i, iid in enumerate(batch):
        item = items_by_id.get(iid)
        if not item:
            continue
        
        total = len(already_done) + i + 1
        print(f"[{total}/{len(tier6_ids)}] {iid} ({item['mechanism_primary']})...")
        
        raw = call_flash(item["question"])
        parsed = parse_response(raw)
        is_refusal, _ = detect_refusal(parsed)
        
        if is_refusal or parsed.get("parse_error"):
            decision = "KEEP_BORDERLINE"
            print(f"  → Flash REFUSAL/ERROR → KEEP")
            escalation[iid] = {
                "item_id": iid, "flash_answer": None, "flash_confidence": 0.0,
                "flash_correct": False, "escalation_decision": decision,
            }
        else:
            answer = parsed["answer"]
            confidence = parsed["confidence"] or 0.5
            is_correct = adjudicate(answer, item["gold_answer"], item.get("aliases", []), item.get("rule", "alias"))
            
            if is_correct and confidence >= 0.85:
                decision = "REJECT"
                print(f"  → Flash ✓ conf={confidence:.2f} → REJECT")
            else:
                decision = "KEEP_BORDERLINE"
                icon = "✓" if is_correct else "✗"
                print(f"  → Flash {icon} ans={answer!r} conf={confidence:.2f} → KEEP")
            
            escalation[iid] = {
                "item_id": iid, "flash_answer": answer, "flash_confidence": confidence,
                "flash_correct": is_correct, "escalation_decision": decision,
            }
        
        time.sleep(0.3)
    
    save_json(escalation, ESCALATION_PROGRESS)
    
    already_done = set(escalation.keys())
    all_done = len([iid for iid in tier6_ids if iid not in already_done]) == 0
    
    reject = sum(1 for r in escalation.values() if r["escalation_decision"] == "REJECT")
    keep = sum(1 for r in escalation.values() if r["escalation_decision"] == "KEEP_BORDERLINE")
    print(f"\nEscalation progress: {len(already_done)}/{len(tier6_ids)}")
    print(f"  REJECT: {reject}, KEEP: {keep}")
    
    return escalation, all_done


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "sonnet"
    
    # Load items
    items = []
    for fname in [ITEMS_A, ITEMS_B]:
        with open(fname) as f:
            items.extend(json.load(f))
    
    print(f"Batch 2 items loaded: {len(items)}")
    
    if mode == "sonnet":
        progress = load_json(SONNET_PROGRESS)
        progress, all_done = run_sonnet_phase(items, progress)
        if not all_done:
            print(f"\nRun again to continue Sonnet testing.")
        else:
            print(f"\nSonnet phase complete! Run with 'escalate' to start escalation.")
    
    elif mode == "escalate":
        sonnet_progress = load_json(SONNET_PROGRESS)
        escalation = load_json(ESCALATION_PROGRESS)
        escalation, all_done = run_escalation_phase(items, sonnet_progress, escalation)
        if not all_done:
            print(f"\nRun again to continue escalation.")
        else:
            print(f"\nEscalation complete!")


if __name__ == "__main__":
    main()
