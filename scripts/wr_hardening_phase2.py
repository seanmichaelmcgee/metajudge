"""
MetaJudge Phase 2: Multi-Turn Adversarial WR Hardening
=======================================================
Implements the required hardening loop from the orchestrator prompt:
1. Frontier author generates candidate item bundle
2. Different-family adversary attacks the candidate
3. Author revises using critique
4. Second adversarial pass
5. Optional third-model critique
6. Cheap canary test
7. Acceptance audit

Uses 3-tier model routing per orchestrator policy.
"""

import json
import os
import sys
import time
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

# Add scripts dir to path
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR / "openrouter"))
from client import query, save_results

REPO_ROOT = SCRIPT_DIR.parent
OUTPUT_DIR = REPO_ROOT / "outputs" / "family_c" / "phase2_wr_hardening"
LOG_DIR = OUTPUT_DIR / "audit_logs"

# Ensure dirs exist
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

# ---- Model routing (from orchestrator) ----
# High-cost pattern: Author=Opus, Adversary=Grok-4/DeepSeek-R1, Auditor=GPT-5.2-pro
# Balanced pattern: Author=Sonnet, Adversary=DeepSeek-R1/Grok-4.1-fast, Auditor=GPT-5.2

AUTHOR_MODEL = "anthropic/claude-sonnet-4.6"  # Tier 2 workhorse for batch 1
ADVERSARY_MODEL = "x-ai/grok-4.1-fast"        # Tier 2 different family (fast adversary)
AUDITOR_MODEL = "openai/gpt-5.2"              # Tier 2 third family
CANARY_MODELS = [
    "google/gemini-2.5-flash-lite",
    "x-ai/grok-3-mini",
    "openai/gpt-5-mini",
]

# ---- Prompts ----

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

PROVEN FAILURE MODES that work well (from our empirical data):
1. Clock angle computation with continuous hand position (models forget minute hand moves hour hand)
2. Multi-constraint enumeration (counting under multiple simultaneous constraints)
3. Banker's rounding in Python (round-half-to-even surprises models)
4. Prime enumeration with boundary errors (models miscount primes in ranges)
5. Range enumeration + summation (off-by-one on "between X and Y")
6. Carry propagation in palindrome checking (models miss carries in mental arithmetic)
7. Conditional probability with non-obvious conditioning

FAILURE MODES that do NOT work (too easy for frontier models):
- Common misconceptions (e.g., Great Wall visibility from space)
- Standard cognitive biases (base-rate neglect, Monty Hall)
- Percentage asymmetry (50% vs 100%)
- Simple counterintuitive facts
- Famous paradoxes (birthday problem, etc.)

CRITICAL: You are designing for FRONTIER LLMs (Claude, GPT-5, Gemini, etc.), not humans.
These models are very good at standard math, logic, and factual recall.
To trip them up, you need computational traps where the naive approach gives a wrong-but-plausible answer."""

def make_author_prompt(subfamily: str, batch_context: str = "") -> str:
    """Generate the initial authoring prompt."""
    if subfamily == "C1":
        sub_instructions = """For C1 items:
- Turn 2 is a metacognitive re-prompt like "Review your reasoning step by step and verify your answer."
- No evidence snippet is provided
- The model must catch its own error through internal reflection
- The question itself should create a natural computational trap"""
    else:
        sub_instructions = """For C2 items:
- Turn 2 includes a short evidence snippet (1-3 sentences) that creates revision pressure
- The evidence should HINT at the error without giving away the answer directly
- Evidence should be factually correct and relevant
- The evidence must create genuine revision pressure — not a trivial giveaway"""

    return f"""{sub_instructions}

{batch_context}

Generate ONE candidate WR item bundle. Output as JSON with these exact fields:
{{
  "turn1_prompt": "The question text",
  "gold_answer": "The correct answer (concise, unambiguous)",
  "gold_answer_aliases": ["list", "of", "acceptable", "alternative", "forms"],
  "grading_rule": "approx_numeric_small OR alias_plus_normalization OR fraction_or_decimal OR code_output",
  "tolerance": {{"abs_tol": 0.5, "rel_tol": 0.01}} OR null,
  "mechanism_primary": "descriptive_tag_for_failure_mode",
  "category": "arithmetic OR mathematics OR reasoning OR code OR factual",
  "difficulty": "hard",
  "intended_t1_error": "Description of what wrong answer models are likely to give and why",
  "why_revision_possible": "Description of how a model could catch the error on reflection",
  "expected_t1_accuracy": "40-60%",
  "evidence_snippet": "For C2 only — 1-3 sentences of evidence. null for C1"
}}

Think step by step about what makes the item genuinely hard for frontier LLMs. Explain your reasoning before the JSON."""


ADVERSARY_SYSTEM = """You are an adversarial red-teamer for a benchmark item design project.
Your job is to ATTACK candidate benchmark items and find weaknesses.

You must be extremely critical. A good WR item must survive your attacks.

For each candidate, evaluate ALL of these:
1. IS THIS TOO FAMOUS? Is this a well-known puzzle, trick question, or common interview question?
2. IS THIS TOO EASY? Would frontier LLMs (Claude, GPT-5, Gemini) get this right >60% of the time?
3. IS THE GOLD ANSWER CORRECT? Verify the math/logic yourself independently.
4. IS THE GOLD ANSWER AMBIGUOUS? Could reasonable interpretations yield different answers?
5. IS THE GRADING CLEAN? Can the answer be extracted and graded automatically?
6. IS THE WR BEHAVIOR PLAUSIBLE? Would a model actually make this specific error?
7. IS REVISION POSSIBLE? Can a model realistically catch this error on reflection?
8. (C2 only) DOES THE EVIDENCE GIVE IT AWAY? Does the snippet make the answer too obvious?

Output your critique as structured JSON:
{
  "verdict": "PASS" or "REVISE" or "REJECT",
  "gold_answer_verified": true/false with your own calculation,
  "your_calculated_answer": "your independent answer",
  "too_famous": {"score": 1-5, "reason": "..."},
  "too_easy": {"score": 1-5, "reason": "..."},
  "ambiguity": {"score": 1-5, "reason": "..."},
  "grading_risk": {"score": 1-5, "reason": "..."},
  "wr_plausibility": {"score": 1-5, "reason": "..."},
  "revision_feasibility": {"score": 1-5, "reason": "..."},
  "evidence_leakage": {"score": 1-5, "reason": "..."} (C2 only),
  "suggested_improvements": ["list", "of", "specific", "improvements"],
  "overall_assessment": "Free text summary"
}

Scores: 1=no concern, 5=critical concern. Any score of 4+ should trigger REVISE or REJECT."""


AUDITOR_SYSTEM = """You are an independent quality auditor for a benchmark dataset project.
You are the FINAL gate before an item is accepted into the clean dataset.

You receive: the candidate item, the adversarial critique, and the revision history.

Your job is to make an independent, definitive judgment:
- ACCEPT: Item is ready for the clean dataset
- REVISE: Item has fixable issues (specify what)
- QUARANTINE: Item has serious issues but might be salvageable later
- REJECT: Item is fundamentally flawed

Key acceptance criteria:
1. Gold answer is unambiguously correct (verify independently)
2. T1 accuracy target of 40-60% is plausible
3. Item is not a famous puzzle or trick question
4. Grading is clean and automated
5. WR behavior is plausible (models would actually make this error)
6. Self-correction is possible but non-trivial
7. (C2) Evidence creates revision pressure without giving away the answer

Output JSON:
{
  "verdict": "ACCEPT" or "REVISE" or "QUARANTINE" or "REJECT",
  "gold_answer_verified": true/false,
  "your_calculated_answer": "your independent answer",
  "confidence": 0.0-1.0,
  "issues": ["list of any remaining issues"],
  "suggested_item_id": "sc_c1_wr_NNN or sc_c2_wr_NNN",
  "reasoning": "detailed reasoning for verdict"
}"""


def canary_test_prompt(question: str) -> str:
    return f"""Answer the following question. Think step by step and give your final answer.

{question}"""


# ---- Core generation loop ----

def run_author_pass(subfamily: str, batch_context: str = "", iteration: int = 1, 
                    prev_critique: str = "", prev_item: str = "") -> dict:
    """Run one author pass."""
    if iteration == 1:
        user_msg = make_author_prompt(subfamily, batch_context)
    else:
        user_msg = f"""The adversarial reviewer found issues with your previous candidate.

PREVIOUS ITEM:
{prev_item}

ADVERSARIAL CRITIQUE:
{prev_critique}

Revise the item to address these concerns. Make substantive improvements, not cosmetic changes.
The item must still target 40-60% T1 accuracy on frontier LLMs.

Output the revised item as the same JSON format. Explain your changes before the JSON."""

    messages = [
        {"role": "system", "content": AUTHOR_SYSTEM},
        {"role": "user", "content": user_msg},
    ]
    
    result = query(AUTHOR_MODEL, messages, temperature=0.7, max_tokens=4096, timeout=120)
    return result


def run_adversary_pass(item_json: str, subfamily: str, iteration: int = 1) -> dict:
    """Run adversarial critique."""
    user_msg = f"""Critique this candidate WR item for a {subfamily} self-correction benchmark.
This is adversarial review iteration {iteration}.

CANDIDATE ITEM:
{item_json}

Be extremely critical. Your job is to find weaknesses."""

    messages = [
        {"role": "system", "content": ADVERSARY_SYSTEM},
        {"role": "user", "content": user_msg},
    ]

    result = query(ADVERSARY_MODEL, messages, temperature=0.3, max_tokens=4096, timeout=300)
    return result


def run_canary_test(question: str) -> list[dict]:
    """Test item against cheap canary models."""
    messages = [
        {"role": "user", "content": canary_test_prompt(question)},
    ]
    
    results = []
    for model in CANARY_MODELS:
        r = query(model, messages, temperature=0.0, max_tokens=1024, timeout=60)
        r["canary_model"] = model
        results.append(r)
    
    return results


def run_audit(item_json: str, critique_history: str, subfamily: str) -> dict:
    """Run final acceptance audit."""
    user_msg = f"""Audit this candidate WR item for the {subfamily} self-correction benchmark.

FINAL CANDIDATE ITEM:
{item_json}

CRITIQUE AND REVISION HISTORY:
{critique_history}

Make your independent judgment."""

    messages = [
        {"role": "system", "content": AUDITOR_SYSTEM},
        {"role": "user", "content": user_msg},
    ]

    result = query(AUDITOR_MODEL, messages, temperature=0.1, max_tokens=2048, timeout=120)
    return result


def extract_json_from_response(text: str) -> Optional[dict]:
    """Try to extract JSON from a model response that may contain prose."""
    if not text:
        return None
    
    import re
    
    # Strategy 1: Look for ```json ... ``` blocks
    json_match = re.search(r'```(?:json)?\s*\n?(\{.*?\})\n?\s*```', text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass
    
    # Strategy 2: Find the LARGEST valid JSON object in the text
    best = None
    best_len = 0
    brace_depth = 0
    start = None
    for i, c in enumerate(text):
        if c == '{':
            if brace_depth == 0:
                start = i
            brace_depth += 1
        elif c == '}':
            brace_depth -= 1
            if brace_depth == 0 and start is not None:
                candidate = text[start:i+1]
                try:
                    parsed = json.loads(candidate)
                    if len(candidate) > best_len:
                        best = parsed
                        best_len = len(candidate)
                except json.JSONDecodeError:
                    pass
                start = None
    
    if best:
        return best
    
    # Strategy 3: Try the whole text as JSON
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        pass
    
    return None


def run_hardening_loop(
    subfamily: str,
    batch_context: str = "",
    max_iterations: int = 5,
    batch_id: str = "batch1",
    item_num: int = 1,
) -> dict:
    """Run the full multi-turn hardening loop for one item."""
    
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    item_log = {
        "batch_id": batch_id,
        "item_num": item_num,
        "subfamily": subfamily,
        "timestamp": timestamp,
        "iterations": [],
        "canary_results": [],
        "audit_result": None,
        "final_verdict": None,
        "final_item": None,
    }
    
    current_item_json = ""
    current_item = None
    
    for iteration in range(1, max_iterations + 1):
        iter_log = {"iteration": iteration, "author": None, "adversary": None}
        print(f"\n  === Iteration {iteration}/{max_iterations} ===")
        
        # Author pass
        print(f"  [Author] {AUTHOR_MODEL}...")
        if iteration == 1 or not current_item:
            author_result = run_author_pass(subfamily, batch_context)
        else:
            prev_adv = item_log["iterations"][-1].get("adversary") if item_log["iterations"] else None
            prev_critique = prev_adv.get("response_text", "") if prev_adv and prev_adv.get("response_text") else "No structured critique available. Please improve the item to be harder for frontier LLMs."
            author_result = run_author_pass(
                subfamily, batch_context, iteration, 
                prev_critique, current_item_json
            )
        
        iter_log["author"] = {
            "model": author_result["model"],
            "latency_ms": author_result["latency_ms"],
            "usage": author_result["usage"],
            "error": author_result["error"],
            "response_text": author_result["response_text"],
        }
        
        if author_result["error"]:
            print(f"  [Author] ERROR: {author_result['error'][:100]}")
            item_log["iterations"].append(iter_log)
            item_log["final_verdict"] = "ERROR"
            break
        
        # Extract item JSON
        extracted = extract_json_from_response(author_result["response_text"])
        if extracted and "turn1_prompt" in extracted:
            current_item = extracted
            current_item_json = json.dumps(extracted, indent=2)
            print(f"  [Author] Generated item: {extracted.get('mechanism_primary', '?')}")
            print(f"           Q: {extracted.get('turn1_prompt', '')[:80]}...")
            print(f"           Gold: {extracted.get('gold_answer', '?')}")
        else:
            print(f"  [Author] Could not extract JSON from response")
            iter_log["parse_error"] = True
            item_log["iterations"].append(iter_log)
            continue
        
        # Adversary pass
        print(f"  [Adversary] {ADVERSARY_MODEL}...")
        adv_result = run_adversary_pass(current_item_json, subfamily, iteration)
        iter_log["adversary"] = {
            "model": adv_result["model"],
            "latency_ms": adv_result["latency_ms"],
            "usage": adv_result["usage"],
            "error": adv_result["error"],
            "response_text": adv_result["response_text"],
        }
        
        if adv_result["error"]:
            print(f"  [Adversary] ERROR: {adv_result['error'][:100]}")
            item_log["iterations"].append(iter_log)
            continue
        
        # Parse adversary verdict
        adv_parsed = extract_json_from_response(adv_result["response_text"])
        if adv_parsed:
            verdict = adv_parsed.get("verdict", "UNKNOWN")
            print(f"  [Adversary] Verdict: {verdict}")
            if adv_parsed.get("gold_answer_verified") is False:
                print(f"  [Adversary] WARNING: Gold answer NOT verified!")
                print(f"             Adversary's answer: {adv_parsed.get('your_calculated_answer', '?')}")
            
            iter_log["adversary_verdict"] = verdict
            iter_log["adversary_parsed"] = adv_parsed
            
            if verdict == "PASS":
                print(f"  [Adversary] PASSED — proceeding to canary test")
                item_log["iterations"].append(iter_log)
                break
            elif verdict == "REJECT":
                print(f"  [Adversary] REJECTED — {adv_parsed.get('overall_assessment', '')[:100]}")
                if iteration >= 3:
                    # After 3 rejections, give up on this item
                    item_log["iterations"].append(iter_log)
                    item_log["final_verdict"] = "REJECTED_BY_ADVERSARY"
                    break
        else:
            print(f"  [Adversary] Could not parse structured critique")
            iter_log["adversary_verdict"] = "PARSE_ERROR"
        
        item_log["iterations"].append(iter_log)
    
    # If we didn't get rejected, run canary tests
    if current_item and item_log.get("final_verdict") != "REJECTED_BY_ADVERSARY" and item_log.get("final_verdict") != "ERROR":
        print(f"\n  === Canary Tests ===")
        question = current_item.get("turn1_prompt", "")
        canary_results = run_canary_test(question)
        
        canary_correct = 0
        canary_total = len(canary_results)
        gold = current_item.get("gold_answer", "")
        
        for cr in canary_results:
            model_short = cr["canary_model"].split("/")[-1]
            resp = cr.get("response_text", "") or ""
            # Simple check: does the response contain the gold answer?
            if gold.lower() in resp.lower():
                canary_correct += 1
                cr["likely_correct"] = True
                print(f"  [{model_short}] CORRECT (contains '{gold}')")
            else:
                cr["likely_correct"] = False
                print(f"  [{model_short}] WRONG (doesn't contain '{gold}')")
            
            item_log["canary_results"].append({
                "model": cr["canary_model"],
                "response_text": resp[:500],
                "latency_ms": cr["latency_ms"],
                "likely_correct": cr.get("likely_correct", False),
                "error": cr["error"],
            })
        
        canary_accuracy = canary_correct / canary_total if canary_total > 0 else 0
        print(f"  Canary accuracy: {canary_correct}/{canary_total} ({canary_accuracy:.0%})")
        
        if canary_accuracy > 0.8:
            print(f"  WARNING: Canaries found it too easy ({canary_accuracy:.0%} correct)")
            item_log["canary_warning"] = "too_easy"
        
        # Run acceptance audit
        print(f"\n  === Acceptance Audit ({AUDITOR_MODEL}) ===")
        critique_history = "\n\n".join([
            f"--- Iteration {it['iteration']} ---\nAdversary: {(it.get('adversary') or {}).get('response_text', 'N/A') or 'N/A'}"
            for it in item_log["iterations"]
        ])[:3000]  # Truncate to avoid token limits
        
        audit_result = run_audit(current_item_json, critique_history, subfamily)
        audit_parsed = extract_json_from_response(audit_result.get("response_text", ""))
        
        item_log["audit_result"] = {
            "model": audit_result["model"],
            "latency_ms": audit_result["latency_ms"],
            "usage": audit_result["usage"],
            "error": audit_result["error"],
            "response_text": audit_result.get("response_text", "")[:1000],
            "parsed": audit_parsed,
        }
        
        if audit_parsed:
            final_verdict = audit_parsed.get("verdict", "UNKNOWN")
            print(f"  [Auditor] Verdict: {final_verdict}")
            print(f"  [Auditor] Gold verified: {audit_parsed.get('gold_answer_verified')}")
            print(f"  [Auditor] Confidence: {audit_parsed.get('confidence')}")
            item_log["final_verdict"] = final_verdict
        else:
            print(f"  [Auditor] Could not parse audit response")
            item_log["final_verdict"] = "AUDIT_PARSE_ERROR"
        
        item_log["final_item"] = current_item
    
    # Save full audit log
    log_path = LOG_DIR / f"{batch_id}_item{item_num}_{timestamp}.json"
    with open(log_path, "w") as f:
        json.dump(item_log, f, indent=2, default=str)
    print(f"\n  Audit log saved: {log_path}")
    
    return item_log


# ---- Batch runner ----

def run_batch(
    batch_id: str,
    items: list[dict],  # [{"subfamily": "C1", "context": "..."}, ...]
) -> list[dict]:
    """Run a batch of item generation loops."""
    results = []
    
    print(f"\n{'='*70}")
    print(f"BATCH: {batch_id}")
    print(f"Items to generate: {len(items)}")
    print(f"Author: {AUTHOR_MODEL}")
    print(f"Adversary: {ADVERSARY_MODEL}")
    print(f"Auditor: {AUDITOR_MODEL}")
    print(f"Canaries: {', '.join(m.split('/')[-1] for m in CANARY_MODELS)}")
    print(f"{'='*70}")
    
    for i, item_spec in enumerate(items, 1):
        print(f"\n{'*'*60}")
        print(f"ITEM {i}/{len(items)} — {item_spec['subfamily']} WR")
        print(f"{'*'*60}")
        
        result = run_hardening_loop(
            subfamily=item_spec["subfamily"],
            batch_context=item_spec.get("context", ""),
            max_iterations=item_spec.get("max_iterations", 5),
            batch_id=batch_id,
            item_num=i,
        )
        results.append(result)
    
    # Summary
    print(f"\n{'='*70}")
    print(f"BATCH SUMMARY: {batch_id}")
    print(f"{'='*70}")
    for i, r in enumerate(results, 1):
        verdict = r.get("final_verdict", "?")
        iters = len(r.get("iterations", []))
        item = r.get("final_item", {})
        mech = item.get("mechanism_primary", "?") if item else "?"
        print(f"  Item {i}: {verdict} ({iters} iterations, mechanism: {mech})")
    
    # Save batch summary
    summary_path = OUTPUT_DIR / f"{batch_id}_summary.json"
    with open(summary_path, "w") as f:
        json.dump({
            "batch_id": batch_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "author_model": AUTHOR_MODEL,
            "adversary_model": ADVERSARY_MODEL,
            "auditor_model": AUDITOR_MODEL,
            "canary_models": CANARY_MODELS,
            "items": [{
                "item_num": i+1,
                "subfamily": items[i]["subfamily"],
                "verdict": r.get("final_verdict", "?"),
                "iterations": len(r.get("iterations", [])),
                "mechanism": r.get("final_item", {}).get("mechanism_primary", "?") if r.get("final_item") else "?",
                "gold_answer": r.get("final_item", {}).get("gold_answer", "?") if r.get("final_item") else "?",
            } for i, r in enumerate(results)]
        }, f, indent=2)
    
    return results


if __name__ == "__main__":
    # Batch 1: 3 items — 2 C1, 1 C2
    batch_items = [
        {
            "subfamily": "C1",
            "context": """Focus on COMPUTATIONAL TRAPS that exploit specific numeric errors.
Good patterns: modular arithmetic with carry, digit manipulation where mental computation fails,
series summation with non-obvious boundary conditions, geometric computation with irrational intermediates.
The question should have a single, unambiguous numeric answer.
Do NOT use clock angles (already have those), prime summation (already have those), 
banker's rounding (already have that), or any famous puzzle.
Target: a math/reasoning question where the naive approach gives a plausible but wrong answer.""",
            "max_iterations": 5,
        },
        {
            "subfamily": "C1",
            "context": """Focus on COMBINATORIAL COUNTING with hidden constraints.
Good patterns: counting arrangements where some configurations are invalid but easily overlooked,
probability problems where the sample space is non-obvious, multi-step logic where an intermediate
count is wrong but plausible.
Do NOT use coin flips (already have that), birthday problems, or Monty Hall.
The gold answer should be a specific number or simple fraction.
Target: frontier LLMs miscounting because they overlook a constraint or double-count.""",
            "max_iterations": 5,
        },
        {
            "subfamily": "C2",
            "context": """Focus on SCIENTIFIC/TECHNICAL facts where the common textbook answer is subtly wrong or oversimplified.
Good patterns: physical constants with unit-dependent precision, chemistry where common rules have exceptions,
biology/anatomy where the standard teaching is an oversimplification.
The evidence snippet should point toward the correct answer without stating it directly.
Do NOT use common misconceptions that are well-known (Great Wall from space, etc.).
Target: a question where models confidently give the common/textbook answer, but the precise answer differs.""",
            "max_iterations": 5,
        },
    ]
    
    results = run_batch("batch1", batch_items)
