"""
Single-item WR hardening v2 — with FRONTIER PRE-TEST GATE.

Key changes from v1:
1. Frontier pre-test: After canary + audit, runs the question through 2 frontier
   models. Item is REJECTED if both frontier models get T1 correct.
2. Updated AUTHOR_SYSTEM with research-informed failure modes.
3. Higher max_tokens for all calls (4096 for frontier, prevents truncation).
4. Uses frozen v2 grader for frontier pre-test grading.
5. Saves comprehensive audit log.

Usage: python3 scripts/wr_hardening_single_v2.py <item_num> <subfamily> "<context>" [batch_id]
"""

import json
import os
import sys
import time
import re
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR / "openrouter"))
sys.path.insert(0, str(SCRIPT_DIR))
from client import query
from regrade_sweep_v062 import grade_item_v2

REPO_ROOT = SCRIPT_DIR.parent
OUTPUT_DIR = REPO_ROOT / "outputs" / "family_c" / "phase2_wr_hardening"
LOG_DIR = OUTPUT_DIR / "audit_logs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

# ── Model routing ──────────────────────────────────────────
# Author, Adversary, Auditor: 3 different model families (Tier 2)
AUTHOR_MODEL = "anthropic/claude-sonnet-4.6"
ADVERSARY_MODEL = "x-ai/grok-4.1-fast"
AUDITOR_MODEL = "openai/gpt-5.2"

# Canaries: Tier 1 cheap models
CANARY_MODELS = ["google/gemini-2.5-flash-lite", "x-ai/grok-3-mini", "openai/gpt-5-mini"]

# Frontier pre-test: 2 strong reasoning models from different families
FRONTIER_PRETEST_MODELS = [
    "openai/gpt-5.2",
    "deepseek/deepseek-r1",
]

# ── System prompts ─────────────────────────────────────────

AUTHOR_SYSTEM = """You are an expert benchmark item designer for MetaJudge, a metacognitive self-correction benchmark.

You design Family C items that test whether LLMs can appropriately self-correct errors. 
Family C has two subfamilies:
- C1: Intrinsic review (no external evidence; model must self-correct from internal reasoning alone)
- C2: Evidence-assisted (model receives a short evidence snippet that creates revision pressure)

Your job is to create WRONG-TO-RIGHT (WR) items where:
- Most FRONTIER LLMs will get Turn 1 WRONG (target: 40-60% T1 accuracy on GPT-5, Claude Opus, DeepSeek-R1)
- But the error is NOT obvious — it requires careful reasoning to detect
- Self-correction IS possible through genuine metacognitive reflection
- The item is NOT a famous internet puzzle, riddle, or trick question
- The gold answer is unambiguous and cleanly gradable

CRITICAL: These items must fool FRONTIER REASONING MODELS, not just cheap models. Frontier models
are excellent at standard math, well-known misconceptions, and textbook combinatorics. You need
computational traps where the naive systematic approach produces a wrong-but-plausible answer.

PROVEN FAILURE MODES (items scoring 40-60% on frontier models):
1. Banker's rounding in Python (round-half-to-even) — models assume round-half-up
2. Clock angle with continuous second-hand position — models forget the hour hand moves continuously
3. Prime enumeration boundary — models include/exclude boundary primes inconsistently
4. Multi-constraint enumeration with hidden constraint counts — models enumerate wrong subset

RESEARCH-INFORMED FAILURE MODES TO EXPLOIT (from academic literature):
5. Compositional reasoning: Compose 2 individually easy steps where the composed problem is hard
   (LLMs solve each sub-problem but fail when chained — Hosseini et al. 2024, Zhao et al. 2024)
6. Multi-digit arithmetic with middle-digit errors — models pattern-match rather than compute
7. Counting under constraints: enumerate items satisfying simultaneous conditions where the
   "obvious" systematic approach misses edge cases or double-counts
8. Convention traps: problems where a plausible-but-wrong convention leads to a different answer
   (e.g., inclusive vs exclusive ranges, 0-indexed vs 1-indexed, "between" ambiguity)
9. Modular arithmetic with non-obvious carries or wrapping
10. Sequence/pattern problems where the "obvious" pattern has an exception at a specific index
11. Problems requiring exact decimal arithmetic where floating-point intuition misleads
12. State-space enumeration where symmetry-based shortcuts overcount or undercount

FAILURE MODES THAT DO NOT WORK (too easy for frontier models):
- Common misconceptions, standard cognitive biases
- Percentage asymmetry, famous paradoxes (Monty Hall, birthday, etc.)
- Simple counterintuitive facts
- Standard combinatorics (stars-and-bars, basic inclusion-exclusion)
- Well-known chemistry/physics facts
- Simple digit reversal counting
- Standard algebra that reduces to one equation

DESIGN PRINCIPLES:
- The problem should look routine enough that models dive in confidently
- The trap should be in a specific computational step, not in understanding the problem
- There should be a single, unambiguous gold answer
- The wrong answer that models give should be PREDICTABLE (off by 1, off by a specific factor, etc.)
- The problem should be self-contained (no external knowledge beyond basic math/CS)

IMPORTANT: Output your item as a JSON code block with these fields:
  item_id, family, subfamily, stratum, turn1_prompt, gold_answer, gold_answer_aliases,
  grading_rule, normative_t2_action, challenge_type, evidence_snippet (C2 only),
  difficulty, category, mechanism_primary, provenance, draft_status, is_linking_item,
  linking_item_id, audit_notes, three_turn_probe, three_turn_purpose

Include detailed reasoning BEFORE the JSON explaining:
1. What the trap mechanism is
2. What wrong answer models will likely give and why
3. Why the gold answer is correct (show your work)
4. Why self-correction is feasible"""


ADVERSARY_SYSTEM = """You are an adversarial red-teamer for a benchmark item design project.
Your job is to ATTACK candidate benchmark items and find weaknesses. Be extremely critical.

IMPORTANT CONTEXT: Prior items that passed canary tests (cheap model difficulty) ALL failed
frontier validation — they were trivially easy for GPT-5.2, Claude Opus, DeepSeek-R1.
Your job is to be HARDER than those frontier models. If a frontier reasoning model would
solve this with high-quality chain-of-thought reasoning, it should FAIL your review.

Evaluate ALL of these:
1. IS THIS TOO FAMOUS? Well-known puzzle or trick question?
2. IS THIS TOO EASY FOR FRONTIER MODELS? Think like GPT-5.2 with chain-of-thought. Would it
   systematically solve this? Standard algebra, combinatorics, and well-known facts are TOO EASY.
3. IS THE GOLD ANSWER CORRECT? Verify the math/logic independently. Show all work.
4. IS THE GOLD ANSWER AMBIGUOUS? Could different interpretations yield different answers?
5. IS THE GRADING CLEAN? Can the answer be extracted and graded automatically?
6. IS THE WR BEHAVIOR PLAUSIBLE? Would frontier models actually make this specific error?
7. IS REVISION POSSIBLE? Can a model catch this error on reflection?
8. (C2 only) DOES THE EVIDENCE GIVE IT AWAY?

Output your critique as a JSON code block with fields:
verdict (PASS/REVISE/REJECT), gold_answer_verified (bool), your_calculated_answer,
too_famous (1-5), too_easy_frontier (1-5), ambiguity (1-5), grading_risk (1-5),
wr_plausibility (1-5), revision_feasibility (1-5), suggested_improvements [], overall_assessment.
Scores: 1=no concern, 5=critical. too_easy_frontier score 4+ triggers REVISE or REJECT.

IMPORTANT: Show your full independent calculation before giving the JSON."""


AUDITOR_SYSTEM = """You are an independent quality auditor for a benchmark dataset project.
You are the FINAL gate before an item goes to frontier pre-test.

Make an independent, definitive judgment: ACCEPT / REVISE / QUARANTINE / REJECT.

Key acceptance criteria:
1. Gold answer is unambiguously correct (verify independently)
2. T1 accuracy target of 40-60% is plausible for FRONTIER LLMs (GPT-5.2, Claude Opus, DeepSeek-R1)
   — NOT cheap models. Standard math, well-known facts, and textbook combinatorics are TOO EASY.
3. Not a famous puzzle or trick question
4. Grading is clean and automated
5. WR behavior is plausible for frontier reasoning models
6. Self-correction is possible but non-trivial

Output JSON with: verdict, gold_answer_verified (bool), your_calculated_answer,
confidence (0-1), issues [], reasoning.

IMPORTANT: Show your full independent calculation before giving the JSON."""


def extract_json(text):
    if not text:
        return None
    # Try ```json blocks
    m = re.search(r'```(?:json)?\s*\n?(\{.*?\})\n?\s*```', text, re.DOTALL)
    if m:
        try: return json.loads(m.group(1))
        except: pass
    # Find largest valid JSON object
    best, best_len = None, 0
    depth, start = 0, None
    for i, c in enumerate(text):
        if c == '{':
            if depth == 0: start = i
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0 and start is not None:
                try:
                    p = json.loads(text[start:i+1])
                    if len(text[start:i+1]) > best_len:
                        best, best_len = p, len(text[start:i+1])
                except: pass
                start = None
    return best



def normalize_latex_for_grading(text):
    """Pre-process response text to convert LaTeX fractions to plain text for grading.
    This prevents false negatives where models answer correctly in LaTeX format."""
    if not text:
        return text
    # Convert \frac{a}{b} -> a/b
    text = re.sub(r'\\frac\{([^}]+)\}\{([^}]+)\}', r'\1/\2', text)
    # Remove \boxed{...} wrapper
    text = re.sub(r'\\boxed\{([^}]+)\}', r'\1', text)
    # Remove remaining LaTeX math delimiters
    text = text.replace('\\(', '').replace('\\)', '')
    text = text.replace('\\[', '').replace('\\]', '')
    text = text.replace('$', '')
    return text


def frontier_pretest(item, log):
    """Run frontier pre-test: 2 frontier models must NOT both get T1 correct."""
    question = item.get("turn1_prompt", "")
    gold = item.get("gold_answer", "")
    grading_rule = item.get("grading_rule", "")
    aliases = item.get("gold_answer_aliases", [])

    grade_data = {
        "grading_rule": grading_rule,
        "gold_answer": gold,
        "gold_answer_aliases": aliases,
        "tolerance": item.get("tolerance"),
    }

    results = []
    correct_count = 0

    print(f"\n  === Frontier Pre-Test ===")
    for model in FRONTIER_PRETEST_MODELS:
        model_short = model.split("/")[-1]
        print(f"  [{model_short}] running T1...")

        r = query(model,
                  [{"role": "user", "content": f"Answer this question. Think step by step, showing all work.\n\n{question}"}],
                  temperature=0.0, max_tokens=4096, timeout=180)

        resp = r.get("response_text", "") or ""
        normalized_resp = normalize_latex_for_grading(resp)
        is_correct = grade_item_v2(normalized_resp, grade_data) if resp else False
        if is_correct:
            correct_count += 1

        print(f"  [{model_short}] {'CORRECT' if is_correct else 'WRONG'} ({r.get('latency_ms', 0)}ms)")
        print(f"  [{model_short}] excerpt: {resp[-300:].replace(chr(10), ' ')[:200]}")

        results.append({
            "model": model,
            "model_short": model_short,
            "t1_correct": is_correct,
            "response_text": resp[:1500],
            "latency_ms": r.get("latency_ms"),
            "error": r.get("error"),
        })

    log["frontier_pretest"] = results
    frontier_acc = correct_count / len(FRONTIER_PRETEST_MODELS)
    log["frontier_pretest_accuracy"] = frontier_acc

    # Gate: at least 1 frontier model must fail
    if correct_count == len(FRONTIER_PRETEST_MODELS):
        print(f"  FRONTIER GATE: FAIL — all {len(FRONTIER_PRETEST_MODELS)} frontier models correct")
        return False
    elif correct_count == 0:
        print(f"  FRONTIER GATE: PASS (strong) — 0/{len(FRONTIER_PRETEST_MODELS)} correct")
        return True
    else:
        print(f"  FRONTIER GATE: PASS — {correct_count}/{len(FRONTIER_PRETEST_MODELS)} correct ({frontier_acc:.0%})")
        return True


def run_item(item_num, subfamily, context, batch_id="batch2", max_iters=4):
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    log = {"batch_id": batch_id, "item_num": item_num, "subfamily": subfamily,
           "timestamp": timestamp, "iterations": [], "canary_results": [],
           "frontier_pretest": [], "audit_result": None,
           "final_verdict": None, "final_item": None}

    current_item = None
    current_json_str = ""

    for iteration in range(1, max_iters + 1):
        it = {"iteration": iteration, "author": None, "adversary": None}
        print(f"\n  === Iteration {iteration}/{max_iters} ===")

        # AUTHOR
        print(f"  [Author] {AUTHOR_MODEL}...")
        if iteration == 1 or not current_item:
            if subfamily == "C1":
                sub_note = "C1 item: Turn 2 is metacognitive re-prompt, no evidence snippet."
            else:
                sub_note = "C2 item: Turn 2 includes evidence snippet creating revision pressure."
            user_msg = f"{sub_note}\n\n{context}\n\nGenerate ONE candidate WR item bundle as JSON."
        else:
            prev_crit = (log["iterations"][-1].get("adversary") or {}).get("response_text", "Improve the item.") or "Improve the item."
            user_msg = f"PREVIOUS ITEM:\n{current_json_str}\n\nADVERSARIAL CRITIQUE:\n{prev_crit[:2000]}\n\nRevise the item to address these concerns. Output as JSON code block."

        ar = query(AUTHOR_MODEL, [{"role":"system","content":AUTHOR_SYSTEM},{"role":"user","content":user_msg}],
                   temperature=0.7, max_tokens=4096, timeout=120)
        it["author"] = {"model":ar["model"],"latency_ms":ar["latency_ms"],"usage":ar["usage"],
                        "error":ar["error"],"response_text":ar["response_text"]}

        if ar["error"]:
            print(f"  [Author] ERROR: {ar['error'][:100]}")
            log["iterations"].append(it)
            continue

        parsed = extract_json(ar["response_text"])
        if parsed and "turn1_prompt" in parsed:
            current_item = parsed
            current_json_str = json.dumps(parsed, indent=2)
            print(f"  [Author] Item: {parsed.get('mechanism_primary','?')}")
            print(f"           Q: {parsed.get('turn1_prompt','')[:120]}...")
            print(f"           Gold: {parsed.get('gold_answer','?')}")
        else:
            print(f"  [Author] JSON extraction failed")
            log["iterations"].append(it)
            continue

        # ADVERSARY
        print(f"  [Adversary] {ADVERSARY_MODEL}...")
        adv_msg = f"Critique this {subfamily} WR candidate (iteration {iteration}):\n\n{current_json_str}"
        avr = query(ADVERSARY_MODEL, [{"role":"system","content":ADVERSARY_SYSTEM},{"role":"user","content":adv_msg}],
                    temperature=0.3, max_tokens=4096, timeout=180)
        it["adversary"] = {"model":avr["model"],"latency_ms":avr["latency_ms"],"usage":avr["usage"],
                          "error":avr["error"],"response_text":avr["response_text"]}

        if avr["error"]:
            print(f"  [Adversary] ERROR: {avr['error'][:100]}")
            log["iterations"].append(it)
            continue

        adv_parsed = extract_json(avr["response_text"])
        if adv_parsed:
            verdict = adv_parsed.get("verdict","UNKNOWN")
            gold_ok = adv_parsed.get("gold_answer_verified", None)
            print(f"  [Adversary] Verdict: {verdict}, Gold verified: {gold_ok}")
            if gold_ok is False:
                their_ans = adv_parsed.get("your_calculated_answer","?")
                print(f"  [Adversary] THEIR answer: {their_ans}")
            it["adversary_verdict"] = verdict
            if verdict == "PASS":
                log["iterations"].append(it)
                break
            if verdict == "REJECT" and iteration >= 3:
                log["iterations"].append(it)
                log["final_verdict"] = "REJECTED_BY_ADVERSARY"
                break
        else:
            print(f"  [Adversary] JSON parse failed — treating as REVISE")

        log["iterations"].append(it)

    if not current_item or log.get("final_verdict") == "REJECTED_BY_ADVERSARY":
        log["final_verdict"] = log.get("final_verdict", "NO_ITEM_GENERATED")
        log_path = LOG_DIR / f"{batch_id}_item{item_num}_{timestamp}.json"
        with open(log_path, "w") as f:
            json.dump(log, f, indent=2, default=str)
        print(f"\n  RESULT: {log['final_verdict']}")
        return log

    # CANARY TESTS
    print(f"\n  === Canary Tests ===")
    question = current_item.get("turn1_prompt","")
    gold = str(current_item.get("gold_answer",""))
    correct = 0
    for model in CANARY_MODELS:
        cr = query(model, [{"role":"user","content":f"Answer this question. Think step by step.\n\n{question}"}],
                   temperature=0.0, max_tokens=2048, timeout=60)
        resp = (cr.get("response_text","") or "").lower()
        is_correct = gold.lower() in resp
        if is_correct: correct += 1
        mname = model.split("/")[-1]
        print(f"  [{mname}] {'CORRECT' if is_correct else 'WRONG'}")
        log["canary_results"].append({"model":model,"likely_correct":is_correct,
                                       "response_text":(cr.get("response_text","") or "")[:500],
                                       "error":cr["error"]})

    canary_acc = correct / len(CANARY_MODELS)
    print(f"  Canary accuracy: {correct}/{len(CANARY_MODELS)} ({canary_acc:.0%})")
    if canary_acc > 0.8:
        print(f"  WARNING: Too easy for canaries")
        log["canary_warning"] = "too_easy"

    # AUDIT
    print(f"\n  === Acceptance Audit ({AUDITOR_MODEL}) ===")
    hist = "\n".join([f"Iter {it['iteration']}: {(it.get('adversary') or {}).get('response_text','N/A') or 'N/A'}"
                      for it in log["iterations"]])[:2000]
    audit_msg = f"CANDIDATE:\n{current_json_str}\n\nCRITIQUE HISTORY:\n{hist}\n\nMake your independent judgment."
    aur = query(AUDITOR_MODEL, [{"role":"system","content":AUDITOR_SYSTEM},{"role":"user","content":audit_msg}],
                temperature=0.1, max_tokens=2048, timeout=120)

    audit_parsed = extract_json(aur.get("response_text",""))
    log["audit_result"] = {"model":aur["model"],"latency_ms":aur["latency_ms"],"usage":aur["usage"],
                           "error":aur["error"],"response_text":(aur.get("response_text","") or "")[:1500],
                           "parsed":audit_parsed}

    if audit_parsed:
        fv = audit_parsed.get("verdict","UNKNOWN")
        print(f"  [Auditor] Verdict: {fv}, Gold verified: {audit_parsed.get('gold_answer_verified')}")
        print(f"  [Auditor] Their answer: {audit_parsed.get('your_calculated_answer','?')}")
        print(f"  [Auditor] Confidence: {audit_parsed.get('confidence','?')}")

        if fv in ("QUARANTINE", "REJECT"):
            log["final_verdict"] = f"REJECTED_BY_AUDITOR_{fv}"
            log_path = LOG_DIR / f"{batch_id}_item{item_num}_{timestamp}.json"
            with open(log_path, "w") as f:
                json.dump(log, f, indent=2, default=str)
            print(f"\n  RESULT: {log['final_verdict']}")
            return log
    else:
        print(f"  [Auditor] JSON parse failed — proceeding to frontier pre-test")

    # ═══ FRONTIER PRE-TEST GATE (NEW in v2) ═══
    frontier_pass = frontier_pretest(current_item, log)

    if frontier_pass:
        log["final_verdict"] = "ACCEPTED_FRONTIER_PRETEST"
        log["final_item"] = current_item
        print(f"\n  ✓ FRONTIER PRE-TEST PASSED — item accepted for draft status")
    else:
        log["final_verdict"] = "REJECTED_FRONTIER_TOO_EASY"
        log["final_item"] = current_item
        print(f"\n  ✗ FRONTIER PRE-TEST FAILED — item too easy for frontier models")

    # Save log
    log_path = LOG_DIR / f"{batch_id}_item{item_num}_{timestamp}.json"
    with open(log_path, "w") as f:
        json.dump(log, f, indent=2, default=str)
    print(f"  Log saved: {log_path}")
    print(f"  RESULT: {log['final_verdict']}")
    return log


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python3 scripts/wr_hardening_single_v2.py <item_num> <subfamily> <context> [batch_id]")
        sys.exit(1)

    item_num = int(sys.argv[1])
    subfamily = sys.argv[2]
    context = sys.argv[3]
    batch_id = sys.argv[4] if len(sys.argv) > 4 else "batch2"

    run_item(item_num, subfamily, context, batch_id)
