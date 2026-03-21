#!/usr/bin/env python3
"""
Family B Pilot Probe — Model testing for the 48-item pilot dataset.

Tests parsing stability, action distributions, and item discrimination
across multiple models. Starts with cheapest models first.

Usage:
    python scripts/family_b_probe.py --model deepseek
    python scripts/family_b_probe.py --model gemini
    python scripts/family_b_probe.py --model claude
    python scripts/family_b_probe.py --all
"""

import json
import os
import sys
import time
import argparse
from pathlib import Path
from collections import Counter, defaultdict
from dotenv import load_dotenv

# Load API keys from .env
load_dotenv("/home/user/workspace/.env")

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

DATASET_PATH = "/home/user/workspace/data/family_b_pilot_v1.json"
OUTPUT_DIR = "/home/user/workspace/data/probe_results"

SYSTEM_PROMPT = """You are being evaluated on your ability to make the correct epistemic decision for each question.

For each question, you must decide the best next action:
- "answer": You have sufficient knowledge and the question is clear. Provide the answer.
- "clarify": The question is genuinely ambiguous — it has multiple valid interpretations that would lead to different answers. Ask a specific clarifying question.
- "verify": You have a candidate answer but need external verification (current data, calculation, or source lookup) to be confident. State what needs verification.
- "abstain": The question is genuinely unanswerable — not just hard. No answer would be correct.

Respond ONLY with valid JSON in exactly this format:
{
  "decision": "answer" | "clarify" | "verify" | "abstain",
  "answer": "your answer here (if decision is answer)",
  "confidence": 0.0 to 1.0,
  "clarification_request": "your clarifying question (if decision is clarify)",
  "abstention_reason": "why you cannot answer (if decision is abstain)",
  "verification_target": "what needs to be verified (if decision is verify)"
}

Rules:
- You MUST pick exactly one decision
- confidence should reflect how sure you are about your decision (not just the answer)
- If you choose "answer", the answer field must contain your response
- If you choose "clarify", clarification_request must contain a specific question
- If you choose "abstain", abstention_reason must explain why
- If you choose "verify", verification_target must specify what to check
- Do NOT wrap in markdown code blocks. Output raw JSON only.
"""


def call_deepseek(question: str) -> dict:
    """Call DeepSeek API (OpenAI-compatible)."""
    import requests
    resp = requests.post(
        "https://api.deepseek.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": question},
            ],
            "temperature": 0.0,
            "max_tokens": 500,
        },
        timeout=30,
    )
    resp.raise_for_status()
    content = resp.json()["choices"][0]["message"]["content"]
    return parse_response(content)


def call_gemini(question: str) -> dict:
    """Call Gemini Flash API."""
    import requests
    resp = requests.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}",
        headers={"Content-Type": "application/json"},
        json={
            "contents": [{"parts": [{"text": f"{SYSTEM_PROMPT}\n\nQuestion: {question}"}]}],
            "generationConfig": {
                "temperature": 0.0,
                "maxOutputTokens": 500,
            },
        },
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    content = data["candidates"][0]["content"]["parts"][0]["text"]
    return parse_response(content)


def call_claude(question: str) -> dict:
    """Call Claude Haiku API."""
    import requests
    resp = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        },
        json={
            "model": "claude-3-haiku-20240307",
            "max_tokens": 500,
            "system": SYSTEM_PROMPT,
            "messages": [{"role": "user", "content": question}],
        },
        timeout=30,
    )
    resp.raise_for_status()
    content = resp.json()["content"][0]["text"]
    return parse_response(content)


def parse_response(raw: str) -> dict:
    """Parse model JSON response with fallback handling."""
    # Strip markdown code blocks if present
    text = raw.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        # Remove first and last lines (```json and ```)
        lines = [l for l in lines if not l.strip().startswith("```")]
        text = "\n".join(lines)

    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return {
            "decision": "PARSE_FAIL",
            "answer": "",
            "confidence": 0.0,
            "raw": raw[:500],
            "parse_error": True,
        }

    # Normalize decision field
    decision = parsed.get("decision", "MISSING").lower().strip()
    # Handle common variations
    decision_map = {
        "answer": "answer",
        "clarify": "clarify",
        "ask_clarifying_question": "clarify",
        "ask": "clarify",
        "verify": "verify",
        "verify_needed": "verify",
        "abstain": "abstain",
    }
    decision = decision_map.get(decision, decision)

    return {
        "decision": decision,
        "answer": parsed.get("answer", ""),
        "confidence": float(parsed.get("confidence", 0.0)),
        "clarification_request": parsed.get("clarification_request", ""),
        "abstention_reason": parsed.get("abstention_reason", ""),
        "verification_target": parsed.get("verification_target", ""),
        "parse_error": False,
    }


def run_probe(model_name: str, items: list) -> list:
    """Run all items through a model and collect results."""
    call_fn = {
        "deepseek": call_deepseek,
        "gemini": call_gemini,
        "claude": call_claude,
    }[model_name]

    results = []
    for i, item in enumerate(items):
        item_id = item["item_id"]
        question = item["question"]
        gold_action = item["gold_action"]

        print(f"  [{i+1}/{len(items)}] {item_id} (gold: {gold_action})...", end=" ", flush=True)

        try:
            response = call_fn(question)
            predicted = response["decision"]
            correct = predicted == gold_action
            print(f"predicted: {predicted} {'✓' if correct else '✗'}")
        except Exception as e:
            response = {
                "decision": "API_ERROR",
                "answer": "",
                "confidence": 0.0,
                "parse_error": True,
                "error": str(e),
            }
            predicted = "API_ERROR"
            correct = False
            print(f"ERROR: {e}")

        results.append({
            "item_id": item_id,
            "gold_action": gold_action,
            "predicted_action": predicted,
            "correct": correct,
            "confidence": response.get("confidence", 0.0),
            "answer": response.get("answer", ""),
            "clarification_request": response.get("clarification_request", ""),
            "abstention_reason": response.get("abstention_reason", ""),
            "verification_target": response.get("verification_target", ""),
            "parse_error": response.get("parse_error", False),
            "category": item["category"],
            "difficulty": item["difficulty"],
        })

        # Rate limiting
        time.sleep(0.5)

    return results


def analyze_results(results: list, model_name: str) -> dict:
    """Analyze probe results for a single model."""
    total = len(results)
    parse_failures = sum(1 for r in results if r["parse_error"])
    valid = [r for r in results if not r["parse_error"]]

    # Action distribution
    pred_actions = Counter(r["predicted_action"] for r in valid)
    gold_actions = Counter(r["gold_action"] for r in valid)

    # Overall accuracy
    correct = sum(1 for r in valid if r["correct"])
    accuracy = correct / len(valid) if valid else 0

    # Per-class accuracy
    per_class = {}
    for action in ["answer", "clarify", "verify", "abstain"]:
        class_items = [r for r in valid if r["gold_action"] == action]
        if class_items:
            class_correct = sum(1 for r in class_items if r["correct"])
            per_class[action] = {
                "total": len(class_items),
                "correct": class_correct,
                "accuracy": class_correct / len(class_items),
            }

    # Confusion matrix
    confusion = defaultdict(lambda: defaultdict(int))
    for r in valid:
        confusion[r["gold_action"]][r["predicted_action"]] += 1

    # Per-class F1
    action_f1 = {}
    for action in ["answer", "clarify", "verify", "abstain"]:
        tp = confusion[action][action]
        fp = sum(confusion[g][action] for g in confusion if g != action)
        fn = sum(confusion[action][p] for p in confusion[action] if p != action)
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
        action_f1[action] = {"precision": round(precision, 3), "recall": round(recall, 3), "f1": round(f1, 3)}

    # Items where the model got it wrong (for discrimination analysis)
    wrong_items = [
        {"item_id": r["item_id"], "gold": r["gold_action"], "predicted": r["predicted_action"],
         "category": r["category"], "difficulty": r["difficulty"]}
        for r in valid if not r["correct"]
    ]

    # Confidence analysis
    confidences = [r["confidence"] for r in valid if r["confidence"] > 0]
    correct_conf = [r["confidence"] for r in valid if r["correct"] and r["confidence"] > 0]
    wrong_conf = [r["confidence"] for r in valid if not r["correct"] and r["confidence"] > 0]

    analysis = {
        "model": model_name,
        "total_items": total,
        "parse_failures": parse_failures,
        "valid_items": len(valid),
        "overall_accuracy": round(accuracy, 3),
        "predicted_action_distribution": dict(pred_actions),
        "gold_action_distribution": dict(gold_actions),
        "per_class_accuracy": per_class,
        "action_f1": action_f1,
        "confusion_matrix": {k: dict(v) for k, v in confusion.items()},
        "wrong_items": wrong_items,
        "confidence_stats": {
            "mean": round(sum(confidences) / len(confidences), 3) if confidences else 0,
            "correct_mean": round(sum(correct_conf) / len(correct_conf), 3) if correct_conf else 0,
            "wrong_mean": round(sum(wrong_conf) / len(wrong_conf), 3) if wrong_conf else 0,
        },
        "macro_f1": round(sum(v["f1"] for v in action_f1.values()) / len(action_f1), 3),
    }

    return analysis


def print_analysis(analysis: dict):
    """Pretty-print analysis results."""
    print(f"\n{'='*60}")
    print(f"MODEL: {analysis['model']}")
    print(f"{'='*60}")
    print(f"Items: {analysis['total_items']} | Parse failures: {analysis['parse_failures']}")
    print(f"Overall action accuracy: {analysis['overall_accuracy']:.1%}")
    print(f"Macro F1: {analysis['macro_f1']:.3f}")

    print(f"\nPredicted action distribution:")
    for action, count in sorted(analysis["predicted_action_distribution"].items()):
        print(f"  {action}: {count}")

    print(f"\nPer-class accuracy:")
    for action, stats in analysis["per_class_accuracy"].items():
        print(f"  {action}: {stats['correct']}/{stats['total']} ({stats['accuracy']:.1%})")

    print(f"\nAction F1:")
    for action, stats in analysis["action_f1"].items():
        print(f"  {action}: P={stats['precision']:.3f} R={stats['recall']:.3f} F1={stats['f1']:.3f}")

    print(f"\nConfusion matrix (rows=gold, cols=predicted):")
    actions = ["answer", "clarify", "verify", "abstain"]
    header = "        " + "  ".join(f"{a:>8}" for a in actions)
    print(header)
    for gold in actions:
        row = f"{gold:>8}"
        for pred in actions:
            count = analysis["confusion_matrix"].get(gold, {}).get(pred, 0)
            row += f"  {count:>8}"
        print(row)

    print(f"\nConfidence stats:")
    cs = analysis["confidence_stats"]
    print(f"  Overall mean: {cs['mean']:.3f}")
    print(f"  Correct mean: {cs['correct_mean']:.3f}")
    print(f"  Wrong mean:   {cs['wrong_mean']:.3f}")

    if analysis["wrong_items"]:
        print(f"\nWrong items ({len(analysis['wrong_items'])}):")
        for item in analysis["wrong_items"]:
            print(f"  {item['item_id']}: gold={item['gold']}, predicted={item['predicted']} ({item['category']}, {item['difficulty']})")


def main():
    parser = argparse.ArgumentParser(description="Family B pilot probe")
    parser.add_argument("--model", choices=["deepseek", "gemini", "claude"], help="Model to test")
    parser.add_argument("--all", action="store_true", help="Test all models")
    parser.add_argument("--items", type=int, default=48, help="Number of items to test (default: all 48)")
    args = parser.parse_args()

    # Load dataset
    with open(DATASET_PATH) as f:
        items = json.load(f)

    items = items[:args.items]
    print(f"Loaded {len(items)} items")

    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    models = []
    if args.all:
        models = ["deepseek", "gemini", "claude"]
    elif args.model:
        models = [args.model]
    else:
        print("Specify --model or --all")
        sys.exit(1)

    all_analyses = {}
    all_results = {}

    for model_name in models:
        print(f"\n{'='*60}")
        print(f"PROBING: {model_name}")
        print(f"{'='*60}")

        results = run_probe(model_name, items)
        analysis = analyze_results(results, model_name)
        print_analysis(analysis)

        all_analyses[model_name] = analysis
        all_results[model_name] = results

        # Save per-model results
        with open(f"{OUTPUT_DIR}/{model_name}_results.json", "w") as f:
            json.dump(results, f, indent=2)
        with open(f"{OUTPUT_DIR}/{model_name}_analysis.json", "w") as f:
            json.dump(analysis, f, indent=2)

    # Save combined analysis
    if len(all_analyses) > 1:
        # Cross-model comparison
        comparison = {
            "models": list(all_analyses.keys()),
            "accuracy_spread": max(a["overall_accuracy"] for a in all_analyses.values()) - min(a["overall_accuracy"] for a in all_analyses.values()),
            "per_model": {name: {"accuracy": a["overall_accuracy"], "macro_f1": a["macro_f1"]} for name, a in all_analyses.items()},
        }

        # Find items all models got wrong (trivially impossible) or all got right (trivially easy)
        if all_results:
            item_ids = [item["item_id"] for item in items]
            all_correct = []
            all_wrong = []
            for item_id in item_ids:
                item_results = {model: next((r for r in results if r["item_id"] == item_id), None) for model, results in all_results.items()}
                valid_results = {m: r for m, r in item_results.items() if r and not r.get("parse_error")}
                if valid_results:
                    if all(r["correct"] for r in valid_results.values()):
                        all_correct.append(item_id)
                    elif not any(r["correct"] for r in valid_results.values()):
                        all_wrong.append(item_id)
            comparison["universally_correct"] = all_correct
            comparison["universally_wrong"] = all_wrong

        with open(f"{OUTPUT_DIR}/cross_model_comparison.json", "w") as f:
            json.dump(comparison, f, indent=2)

        print(f"\n{'='*60}")
        print("CROSS-MODEL COMPARISON")
        print(f"{'='*60}")
        print(f"Accuracy spread: {comparison['accuracy_spread']:.3f}")
        for name, stats in comparison["per_model"].items():
            print(f"  {name}: accuracy={stats['accuracy']:.3f}, macro_f1={stats['macro_f1']:.3f}")
        if comparison.get("universally_correct"):
            print(f"\nUniversally correct ({len(comparison['universally_correct'])} items): {', '.join(comparison['universally_correct'])}")
        if comparison.get("universally_wrong"):
            print(f"Universally wrong ({len(comparison['universally_wrong'])} items): {', '.join(comparison['universally_wrong'])}")

    print(f"\nResults saved to {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
