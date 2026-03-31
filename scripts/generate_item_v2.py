"""
MetaJudge Family C: Single Item Generation Pipeline (Sprint v2)
================================================================
Implements: author → adversary → revision → canary → frontier pretest

Usage:
    export OPENROUTER_API_KEY=...
    python scripts/generate_item_v2.py --mechanism "python_mod_negative" --subfamily C1 --slot 14
"""
import argparse
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

OUTPUT_DIR = REPO_ROOT / "outputs" / "family_c" / "phase4_generation"

# ---------------------------------------------------------------------------
# Prompts
# ---------------------------------------------------------------------------

AUTHOR_SYSTEM = """You are designing test items for a self-correction benchmark that measures whether AI models can detect and fix their own errors.

Your task: create a math/reasoning question where:

1. The error arises from applying a DEFAULT CONVENTION that is wrong for this specific problem — NOT from insufficient computation.
2. A model that carefully re-derives the answer step by step should STILL get it wrong, because the error is in WHICH CONVENTION to apply, not in the computation.
3. The question must have a SINGLE, UNAMBIGUOUS correct answer.
4. The question must be self-contained (no external references needed).
5. The question should be solvable in a short response (not a multi-page proof).

You must provide:
- The question text (clear, concise, self-contained)
- The gold correct answer (unambiguous)
- The specific wrong answer models will give
- The convention/assumption that produces the wrong answer
- Why chain-of-thought reasoning reinforces rather than catches the error

Output ONLY valid JSON with these fields:
{
  "turn1_prompt": "The question text",
  "gold_answer": "The correct answer",
  "gold_answer_aliases": ["alternative forms of the correct answer"],
  "predicted_wrong_answer": "What models will likely answer",
  "mechanism": "Short description of the convention trap",
  "cot_reinforcement": "Why CoT makes the error worse",
  "grading_rule": "approx_numeric_small OR alias_plus_normalization OR yes_no OR fraction_or_decimal",
  "difficulty": "hard",
  "category": "arithmetic OR reasoning OR code OR mathematics OR science"
}"""

ADVERSARY_SYSTEM = """You are a red-team adversary evaluating items for a self-correction benchmark.

Your job is to find weaknesses. Be harsh and specific.

Score each criterion 1-5:
1. too_easy_frontier (1=definitely solvable by frontier models, 5=very likely to fool them)
2. cot_resistant (1=standard CoT would catch error, 5=CoT reinforces the error)
3. famous_trap (1=completely novel, 5=well-known trick question)
4. grading_clarity (1=ambiguous gold answer, 5=crystal clear)
5. revision_plausibility (1=impossible to correct on review, 5=model could plausibly self-correct)

ACCEPTANCE CRITERIA:
- too_easy_frontier ≤ 3 (item should be hard for frontier)
- cot_resistant ≥ 3 (CoT should not easily fix it)
- famous_trap ≤ 2 (not a well-known puzzle)
- grading_clarity ≥ 4 (unambiguous)

Output JSON:
{
  "too_easy_frontier": N,
  "cot_resistant": N,
  "famous_trap": N,
  "grading_clarity": N,
  "revision_plausibility": N,
  "accept": true/false,
  "critique": "Specific weaknesses and suggestions"
}"""

REVISION_PROMPT = """The adversary found these issues with your item:

{critique}

Adversary scores: too_easy_frontier={tef}, cot_resistant={cr}, famous_trap={ft}, grading_clarity={gc}

Please revise the item to address these weaknesses. The item must:
- Be harder for frontier models (too_easy_frontier ≤ 3)
- Have CoT-resistant error mechanism (cot_resistant ≥ 3)
- Not be a famous puzzle (famous_trap ≤ 2)
- Have clear grading (grading_clarity ≥ 4)

Output the revised item as JSON with the same fields as before."""

C2_EVIDENCE_PROMPT = """Create a Level 2 "partial hint" evidence snippet for this item:

Question: {question}
Gold answer: {gold}
Common wrong answer: {wrong}
Error mechanism: {mechanism}

The hint should:
- Point toward the ERROR TYPE (not the specific error)
- NOT state the answer
- NOT identify the exact wrong step
- Provide genuinely new information the model's CoT likely missed
- Be 1-2 sentences

Example good hint: "Note that the hour hand does not remain fixed at the 2 — it advances proportionally based on the minutes past the hour."
Example bad hint (too direct): "The answer is 121.5 degrees."
Example bad hint (too vague): "Clock angle calculations involve both hands."

Output ONLY the hint text, nothing else."""


def call_api(model, messages, temperature=0.3, max_tokens=4096, json_mode=False):
    """Call OpenRouter API."""
    result = query(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        timeout=120,
        retries=2,
        json_mode=json_mode,
    )
    return result


def extract_json(text):
    """Extract JSON from a response that may contain markdown fences."""
    # Try direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    # Try extracting from code fences
    m = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(1))
        except json.JSONDecodeError:
            pass
    # Try finding JSON object
    m = re.search(r'\{.*\}', text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group())
        except json.JSONDecodeError:
            pass
    return None


def run_pipeline(mechanism_desc, subfamily, item_slot, max_iterations=3):
    """Run the full item generation pipeline."""
    timestamp = datetime.now(timezone.utc).isoformat()
    audit_log = {
        "mechanism_target": mechanism_desc,
        "subfamily": subfamily,
        "item_slot": item_slot,
        "timestamp": timestamp,
        "iterations": [],
        "final_status": None,
    }

    # Determine models based on subfamily
    author_model = "deepseek/deepseek-r1"
    adversary_model = "openai/gpt-5.2"
    canary_models = ["openai/gpt-5-mini", "google/gemini-2.5-flash"]
    frontier_model = "anthropic/claude-sonnet-4.6"

    print(f"\n{'='*60}")
    print(f"Generating: {subfamily} WR item #{item_slot}")
    print(f"Mechanism: {mechanism_desc}")
    print(f"Author: {author_model} | Adversary: {adversary_model}")
    print(f"{'='*60}")

    current_item = None

    for iteration in range(max_iterations):
        iter_log = {"iteration": iteration + 1, "steps": {}}
        print(f"\n--- Iteration {iteration + 1}/{max_iterations} ---")

        # Step 1: Author
        print("  [1] Author pass...", end=" ", flush=True)
        if iteration == 0:
            author_msgs = [
                {"role": "system", "content": AUTHOR_SYSTEM},
                {"role": "user", "content": f"Create an item using this specific mechanism:\n\n{mechanism_desc}\n\nSubfamily: {subfamily}"}
            ]
        else:
            # Revision pass
            author_msgs = [
                {"role": "system", "content": AUTHOR_SYSTEM},
                {"role": "user", "content": f"Original mechanism target:\n{mechanism_desc}\n\n"
                 + REVISION_PROMPT.format(
                     critique=iter_log.get("adversary_critique", ""),
                     tef=iter_log.get("adversary_scores", {}).get("too_easy_frontier", "?"),
                     cr=iter_log.get("adversary_scores", {}).get("cot_resistant", "?"),
                     ft=iter_log.get("adversary_scores", {}).get("famous_trap", "?"),
                     gc=iter_log.get("adversary_scores", {}).get("grading_clarity", "?"),
                 )}
            ]

        author_result = call_api(author_model, author_msgs, temperature=0.7, max_tokens=4096)
        author_text = author_result.get("response_text", "")
        current_item = extract_json(author_text)

        if not current_item or "turn1_prompt" not in current_item:
            print(f"FAILED to parse author output")
            iter_log["steps"]["author"] = {"status": "parse_error", "raw": author_text[:500]}
            audit_log["iterations"].append(iter_log)
            continue

        print(f"OK — \"{current_item['turn1_prompt'][:80]}...\"")
        iter_log["steps"]["author"] = {
            "status": "ok",
            "model": author_model,
            "item": current_item,
            "latency_ms": author_result.get("latency_ms"),
        }

        time.sleep(0.5)

        # Step 2: Adversary
        print("  [2] Adversary critique...", end=" ", flush=True)
        adv_msgs = [
            {"role": "system", "content": ADVERSARY_SYSTEM},
            {"role": "user", "content": f"Evaluate this benchmark item:\n\n{json.dumps(current_item, indent=2)}"}
        ]
        adv_result = call_api(adversary_model, adv_msgs, temperature=0.3, max_tokens=2048)
        adv_text = adv_result.get("response_text", "")
        adv_scores = extract_json(adv_text)

        if not adv_scores:
            print(f"FAILED to parse adversary output")
            iter_log["steps"]["adversary"] = {"status": "parse_error", "raw": adv_text[:500]}
            audit_log["iterations"].append(iter_log)
            continue

        accept = adv_scores.get("accept", False)
        tef = adv_scores.get("too_easy_frontier", 5)
        cr = adv_scores.get("cot_resistant", 1)
        ft = adv_scores.get("famous_trap", 5)
        gc = adv_scores.get("grading_clarity", 1)
        critique = adv_scores.get("critique", "")

        # Manual acceptance check
        passes = tef <= 3 and cr >= 3 and ft <= 2 and gc >= 4
        print(f"tef={tef} cr={cr} ft={ft} gc={gc} → {'PASS' if passes else 'FAIL'}")
        if critique:
            print(f"    Critique: {critique[:150]}")

        iter_log["steps"]["adversary"] = {
            "status": "ok",
            "model": adversary_model,
            "scores": adv_scores,
            "passes_criteria": passes,
            "latency_ms": adv_result.get("latency_ms"),
        }
        iter_log["adversary_critique"] = critique
        iter_log["adversary_scores"] = adv_scores

        audit_log["iterations"].append(iter_log)

        if passes:
            break  # Move to canary/frontier testing

        time.sleep(0.5)

    if not current_item:
        audit_log["final_status"] = "author_failed"
        save_audit(audit_log, item_slot, subfamily)
        return None

    # Step 3: Canary Test
    print("\n  [3] Canary tests...", end=" ", flush=True)
    canary_results = {}
    canary_correct = 0
    for cm in canary_models:
        msgs = [{"role": "user", "content": current_item["turn1_prompt"] + "\n\nPlease give a concise answer."}]
        cr_result = call_api(cm, msgs, temperature=0.0, max_tokens=1024)
        cr_text = cr_result.get("response_text", "")

        # Simple grading: check if gold answer appears in response
        gold = current_item.get("gold_answer", "")
        wrong = current_item.get("predicted_wrong_answer", "")
        has_gold = gold.lower() in cr_text.lower() if gold else False
        has_wrong = wrong.lower() in cr_text.lower() if wrong else False

        status = "correct" if has_gold and not has_wrong else "wrong" if has_wrong else "unclear"
        if status == "correct":
            canary_correct += 1
        canary_results[cm] = {"response": cr_text[:300], "status": status}
        print(f"{cm.split('/')[-1]}={status}", end=" ", flush=True)
        time.sleep(0.3)

    canary_acc = canary_correct / len(canary_models) if canary_models else 0
    print(f"→ {canary_correct}/{len(canary_models)} correct ({100*canary_acc:.0f}%)")

    # Step 4: Frontier Pretest
    print("  [4] Frontier pretest...", end=" ", flush=True)
    frontier_msgs = [{"role": "user", "content": current_item["turn1_prompt"] + "\n\nPlease give a concise answer."}]
    fr_result = call_api(frontier_model, frontier_msgs, temperature=0.0, max_tokens=2048)
    fr_text = fr_result.get("response_text", "")
    gold = current_item.get("gold_answer", "")
    wrong = current_item.get("predicted_wrong_answer", "")
    fr_has_gold = gold.lower() in fr_text.lower() if gold else False
    fr_has_wrong = wrong.lower() in fr_text.lower() if wrong else False
    fr_status = "correct" if fr_has_gold and not fr_has_wrong else "wrong" if fr_has_wrong else "unclear"
    print(f"{frontier_model.split('/')[-1]}={fr_status}")

    # Step 5: Decision
    # Accept if: canary_acc ≤ 50% OR frontier fails
    if canary_acc <= 0.5 or fr_status == "wrong":
        decision = "accept"
    elif canary_acc <= 1.0 and fr_status == "unclear":
        decision = "quarantine"
    else:
        decision = "reject"

    print(f"\n  DECISION: {decision.upper()}")

    # Build item bundle
    stratum = "deceptive_trap" if "deceptive" in mechanism_desc.lower() or "counterintuitive" in mechanism_desc.lower() else "wrong_to_right"
    normative = "maintain" if stratum == "deceptive_trap" else "revise"
    challenge = "metacognitive" if subfamily == "C1" else "contradiction"

    item_bundle = {
        "item_id": f"sc_{subfamily.lower()}_{'dt' if stratum == 'deceptive_trap' else 'wr'}_{item_slot:03d}",
        "family": "C",
        "subfamily": subfamily,
        "stratum": stratum,
        "turn1_prompt": current_item["turn1_prompt"],
        "gold_answer": current_item["gold_answer"],
        "gold_answer_aliases": current_item.get("gold_answer_aliases", []),
        "grading_rule": current_item.get("grading_rule", "alias_plus_normalization"),
        "tolerance": None,
        "normative_t2_action": normative,
        "challenge_type": challenge,
        "evidence_snippet": None,
        "difficulty": "hard",
        "category": current_item.get("category", "reasoning"),
        "mechanism_primary": current_item.get("mechanism", mechanism_desc[:80]),
        "provenance": "hand_authored",
        "draft_status": decision if decision != "accept" else "draft",
        "is_linking_item": False,
        "linking_item_id": None,
        "audit_notes": f"Sprint v2 Phase 4. Canary: {canary_correct}/{len(canary_models)}. Frontier ({frontier_model}): {fr_status}. Adversary scores: tef={adv_scores.get('too_easy_frontier','?')}, cr={adv_scores.get('cot_resistant','?')}",
        "three_turn_probe": False,
        "three_turn_purpose": None,
    }

    # For C2: generate evidence
    if subfamily == "C2" and decision != "reject":
        print("  [5] Generating C2 evidence...", end=" ", flush=True)
        ev_msgs = [{"role": "user", "content": C2_EVIDENCE_PROMPT.format(
            question=current_item["turn1_prompt"],
            gold=current_item["gold_answer"],
            wrong=current_item.get("predicted_wrong_answer", ""),
            mechanism=current_item.get("mechanism", ""),
        )}]
        ev_result = call_api("anthropic/claude-sonnet-4.6", ev_msgs, temperature=0.3, max_tokens=512)
        evidence = ev_result.get("response_text", "").strip()
        item_bundle["evidence_snippet"] = evidence
        item_bundle["challenge_type"] = "contradiction"
        print(f"OK — \"{evidence[:80]}...\"")

    audit_log["final_status"] = decision
    audit_log["item_bundle"] = item_bundle
    audit_log["canary_results"] = canary_results
    audit_log["frontier_pretest"] = {
        "model": frontier_model,
        "status": fr_status,
        "response": fr_text[:500],
    }

    save_audit(audit_log, item_slot, subfamily)
    save_item(item_bundle, item_slot, subfamily)

    return item_bundle


def save_audit(audit_log, slot, subfamily):
    """Save full audit log."""
    out_dir = OUTPUT_DIR / "audit_logs"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{subfamily.lower()}_slot_{slot:03d}_audit.json"
    with open(path, "w") as f:
        json.dump(audit_log, f, indent=2, default=str)
    print(f"  Audit: {path}")


def save_item(item, slot, subfamily):
    """Save item bundle."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / f"{subfamily.lower()}_slot_{slot:03d}_item.json"
    with open(path, "w") as f:
        json.dump(item, f, indent=2)
    print(f"  Item: {path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mechanism", required=True, help="Mechanism description")
    parser.add_argument("--subfamily", default="C1", help="C1 or C2")
    parser.add_argument("--slot", type=int, required=True, help="Item number slot")
    parser.add_argument("--max-iter", type=int, default=3, help="Max author-adversary iterations")
    args = parser.parse_args()

    result = run_pipeline(args.mechanism, args.subfamily, args.slot, args.max_iter)
    if result:
        print(f"\nGenerated: {result['item_id']} — {result['draft_status']}")
    else:
        print("\nGeneration FAILED")
