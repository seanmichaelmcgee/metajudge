#!/usr/bin/env python3
"""
MetaJudge — Batch 3 Multi-Model Runner

Tests Batch 3 survivors against: Gemini Pro, DeepSeek V3.1, Claude Haiku.
Sonnet results already exist from the stress test.

Usage:
  python batch2_multimodel_runner.py gemini_pro
  python batch2_multimodel_runner.py deepseek
  python batch2_multimodel_runner.py haiku
"""

import json
import os
import sys
import time
import re
import requests
from pathlib import Path

import anthropic
import google.genai as genai

# Batch 3 items and results
ITEMS_A = "/home/user/workspace/batch3_agent_a_items.json"
ITEMS_B = "/home/user/workspace/batch3_agent_b_items.json"
SURVIVORS_FILE = "/home/user/workspace/combined_survivors.json"
RESULTS_FILE = "/home/user/workspace/batch3_multimodel_results.json"

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


def call_deepseek(question, max_retries=3):
    prompt = BENCHMARK_PROMPT.format(question=question)
    api_key = os.environ.get("DEEPSEEK_API_KEY", "")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1024,
    }
    for attempt in range(max_retries):
        try:
            resp = requests.post("https://api.deepseek.com/chat/completions",
                                 headers=headers, json=payload, timeout=120)
            if resp.status_code == 200:
                data = resp.json()
                return data["choices"][0]["message"]["content"]
            elif resp.status_code == 429:
                wait = 30 * (attempt + 1)
                print(f"    Rate limited (429), waiting {wait}s...")
                time.sleep(wait)
            else:
                print(f"    DeepSeek error ({resp.status_code}): {resp.text[:200]}")
                if attempt < max_retries - 1:
                    time.sleep(5)
        except Exception as e:
            print(f"    DeepSeek error (attempt {attempt+1}): {e}")
            if attempt < max_retries - 1:
                time.sleep(5)
    return None


def call_haiku(question, max_retries=3):
    prompt = BENCHMARK_PROMPT.format(question=question)
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))
    for attempt in range(max_retries):
        try:
            msg = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}],
            )
            return msg.content[0].text
        except anthropic.RateLimitError:
            wait = 30 * (attempt + 1)
            print(f"    Rate limited, waiting {wait}s...")
            time.sleep(wait)
        except Exception as e:
            print(f"    Haiku error (attempt {attempt+1}): {e}")
            if attempt < max_retries - 1:
                time.sleep(5)
    return None


def call_gemini_pro(question, max_retries=3):
    prompt = BENCHMARK_PROMPT.format(question=question)
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY", ""))
    for attempt in range(max_retries):
        try:
            resp = client.models.generate_content(
                model="gemini-2.5-pro",
                contents=prompt,
            )
            return resp.text
        except Exception as e:
            print(f"    Gemini Pro error (attempt {attempt+1}): {e}")
            if "429" in str(e) or "quota" in str(e).lower():
                wait = 60 * (attempt + 1)
                print(f"    Rate limited, waiting {wait}s...")
                time.sleep(wait)
            elif attempt < max_retries - 1:
                time.sleep(10)
    return None


MODEL_CONFIG = {
    "deepseek": {"fn": call_deepseek, "label": "DeepSeek V3.1", "delay": 1.0},
    "haiku": {"fn": call_haiku, "label": "Claude Haiku 4.5", "delay": 0.5},
    "gemini_pro": {"fn": call_gemini_pro, "label": "Gemini 2.5 Pro", "delay": 1.0},
}


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in MODEL_CONFIG:
        print(f"Usage: python batch2_multimodel_runner.py [{' | '.join(MODEL_CONFIG.keys())}]")
        sys.exit(1)

    model_key = sys.argv[1]
    config = MODEL_CONFIG[model_key]
    call_fn = config["fn"]
    model_label = config["label"]
    delay = config["delay"]

    # Load all Batch 3 items for question lookup
    items_by_id = {}
    for fname in [ITEMS_A, ITEMS_B]:
        with open(fname) as f:
            for item in json.load(f):
                items_by_id[item["item_id"]] = item

    # Get Batch 3 survivor IDs from combined_survivors.json
    with open(SURVIVORS_FILE) as f:
        all_survivors = json.load(f)
    
    batch2_survivors = [s for s in all_survivors if s.get("batch") == 3]
    survivor_ids = [s["item_id"] for s in batch2_survivors]
    
    print(f"Batch 3 survivors: {len(survivor_ids)}")

    # Load existing results
    results = {}
    if Path(RESULTS_FILE).exists():
        with open(RESULTS_FILE) as f:
            results = json.load(f)

    # Check what's already done
    already_done = set()
    for item_id in survivor_ids:
        if item_id in results and model_key in results[item_id]:
            already_done.add(item_id)

    remaining = [iid for iid in survivor_ids if iid not in already_done]

    print(f"Model: {model_label} ({model_key})")
    print(f"Already done: {len(already_done)}")
    print(f"Remaining: {len(remaining)}")
    print()

    for i, item_id in enumerate(remaining):
        item = items_by_id.get(item_id)
        if not item:
            print(f"  WARNING: {item_id} not found in items, skipping")
            continue

        question = item["question"]
        gold = item["gold_answer"]
        aliases = item.get("aliases", [])
        rule = item.get("rule", "alias")

        print(f"[{i+1}/{len(remaining)}] {item_id} ({item['mechanism_primary']})...")

        raw = call_fn(question)
        parsed = parse_response(raw)
        is_refusal, refusal_type = detect_refusal(parsed)

        if is_refusal:
            answer = parsed.get("answer")
            confidence = 0.0
            is_correct = False
            brier = 0.0
            print(f"  → REFUSAL ({refusal_type})")
        elif parsed.get("parse_error"):
            answer = None
            confidence = 0.0
            is_correct = False
            brier = 0.0
            print(f"  → PARSE ERROR: {parsed.get('raw', '')[:100]}")
        else:
            answer = parsed["answer"]
            confidence = parsed["confidence"] or 0.5
            is_correct = adjudicate(answer, gold, aliases, rule)
            correctness = 1 if is_correct else 0
            brier = round((confidence - correctness) ** 2, 4)
            icon = "✓" if is_correct else "✗"
            print(f"  → {icon} answer={answer!r} conf={confidence:.2f} gold={gold!r} brier={brier:.4f}")

        if item_id not in results:
            results[item_id] = {}

        results[item_id][model_key] = {
            "model": model_label,
            "answer": answer,
            "confidence": confidence,
            "correct": is_correct,
            "refusal": is_refusal if not parsed.get("parse_error") else False,
            "brier_score": brier,
        }

        with open(RESULTS_FILE, "w") as f:
            json.dump(results, f, indent=2)

        time.sleep(delay)

    print(f"\n{'='*60}")
    print(f"{model_label} testing complete!")

    correct = sum(1 for iid in survivor_ids
                  if results.get(iid, {}).get(model_key, {}).get("correct", False))
    print(f"Accuracy: {correct}/{len(survivor_ids)} ({100*correct/len(survivor_ids):.1f}%)")


if __name__ == "__main__":
    main()
