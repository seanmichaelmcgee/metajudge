"""
Single-item WR hardening — runs one item through the multi-turn loop.
Usage: python3 scripts/wr_hardening_single.py <item_num> <subfamily> "<context>"
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
from client import query, save_results

REPO_ROOT = SCRIPT_DIR.parent
OUTPUT_DIR = REPO_ROOT / "outputs" / "family_c" / "phase2_wr_hardening"
LOG_DIR = OUTPUT_DIR / "audit_logs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Balanced routing: 3 different families
AUTHOR_MODEL = "anthropic/claude-sonnet-4.6"
ADVERSARY_MODEL = "x-ai/grok-4.1-fast"
AUDITOR_MODEL = "openai/gpt-5.2"
CANARY_MODELS = ["google/gemini-2.5-flash-lite", "x-ai/grok-3-mini", "openai/gpt-5-mini"]

AUTHOR_SYSTEM = """You are an expert benchmark item designer for MetaJudge, a metacognitive self-correction benchmark.

You design Family C items that test whether LLMs can appropriately self-correct errors. 
Family C has two subfamilies:
- C1: Intrinsic review (no external evidence; model must self-correct from internal reasoning alone)
- C2: Evidence-assisted (model receives a short evidence snippet that creates revision pressure)

Your job is to create WRONG-TO-RIGHT (WR) items where:
- Most frontier LLMs will get Turn 1 WRONG (target: 40-60% T1 accuracy)
- But the error is NOT obvious — it requires careful reasoning to detect
- Self-correction IS possible through genuine metacognitive reflection
- The item is NOT a famous internet puzzle, riddle, or trick question
- The gold answer is unambiguous and cleanly gradable

PROVEN FAILURE MODES that work well:
1. Clock angle computation with continuous hand position
2. Multi-constraint enumeration (counting under simultaneous constraints)
3. Banker's rounding in Python (round-half-to-even)
4. Prime enumeration with boundary errors
5. Range enumeration + summation (off-by-one on "between X and Y")
6. Carry propagation in palindrome checking
7. Conditional probability with non-obvious conditioning

FAILURE MODES that do NOT work (too easy for frontier models):
- Common misconceptions, standard cognitive biases
- Percentage asymmetry, famous paradoxes
- Simple counterintuitive facts

You are designing for FRONTIER LLMs (Claude, GPT-5, Gemini). These models are very good at standard math.
To trip them up, you need computational traps where the naive approach gives a wrong-but-plausible answer.

IMPORTANT: Output your item as a JSON code block. Include reasoning BEFORE the JSON."""


ADVERSARY_SYSTEM = """You are an adversarial red-teamer for a benchmark item design project.
Your job is to ATTACK candidate benchmark items and find weaknesses. Be extremely critical.

Evaluate ALL of these:
1. IS THIS TOO FAMOUS? Well-known puzzle or trick question?
2. IS THIS TOO EASY? Would frontier LLMs get this right >60% of the time?
3. IS THE GOLD ANSWER CORRECT? Verify the math/logic independently.
4. IS THE GOLD ANSWER AMBIGUOUS? Could different interpretations yield different answers?
5. IS THE GRADING CLEAN? Can the answer be extracted and graded automatically?
6. IS THE WR BEHAVIOR PLAUSIBLE? Would models actually make this specific error?
7. IS REVISION POSSIBLE? Can a model catch this error on reflection?
8. (C2 only) DOES THE EVIDENCE GIVE IT AWAY?

Output your critique as a JSON code block with fields:
verdict (PASS/REVISE/REJECT), gold_answer_verified (bool), your_calculated_answer,
too_famous (1-5), too_easy (1-5), ambiguity (1-5), grading_risk (1-5),
wr_plausibility (1-5), revision_feasibility (1-5), suggested_improvements [], overall_assessment.
Scores: 1=no concern, 5=critical. Score 4+ triggers REVISE or REJECT.

IMPORTANT: Show your full independent calculation before giving the JSON."""


AUDITOR_SYSTEM = """You are an independent quality auditor for a benchmark dataset project.
You are the FINAL gate before an item is accepted into the clean dataset.

Make an independent, definitive judgment: ACCEPT / REVISE / QUARANTINE / REJECT.

Key acceptance criteria:
1. Gold answer is unambiguously correct (verify independently)
2. T1 accuracy target of 40-60% is plausible for frontier LLMs
3. Not a famous puzzle or trick question
4. Grading is clean and automated
5. WR behavior is plausible
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


def run_item(item_num, subfamily, context, batch_id="batch1", max_iters=4):
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    log = {"batch_id": batch_id, "item_num": item_num, "subfamily": subfamily,
           "timestamp": timestamp, "iterations": [], "canary_results": [],
           "audit_result": None, "final_verdict": None, "final_item": None}
    
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
            print(f"           Q: {parsed.get('turn1_prompt','')[:100]}...")
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
                   temperature=0.0, max_tokens=1024, timeout=60)
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
        log["final_verdict"] = fv
    else:
        print(f"  [Auditor] JSON parse failed")
        log["final_verdict"] = "AUDIT_PARSE_ERROR"
    
    log["final_item"] = current_item
    
    # Save
    log_path = LOG_DIR / f"{batch_id}_item{item_num}_{timestamp}.json"
    with open(log_path, "w") as f:
        json.dump(log, f, indent=2, default=str)
    print(f"\n  Log saved: {log_path}")
    print(f"  RESULT: {log['final_verdict']}")
    return log


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python3 scripts/wr_hardening_single.py <item_num> <subfamily> <context>")
        sys.exit(1)
    
    item_num = int(sys.argv[1])
    subfamily = sys.argv[2]
    context = sys.argv[3]
    batch_id = sys.argv[4] if len(sys.argv) > 4 else "batch1"
    
    run_item(item_num, subfamily, context, batch_id)
