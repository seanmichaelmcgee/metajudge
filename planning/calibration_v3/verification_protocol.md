# Verification Protocol — V4 Adversarial Calibration Items

**Version:** 4.0  
**Date:** March 19, 2026  
**Purpose:** Complete verification, stress-testing, and orchestration protocol for Phase 2 of the MetaJudge V4 adversarial item pipeline.  
**Audience:** Orchestration team and verification/stress-test subagents.

---

## Table of Contents

1. [Overview](#1-overview)
2. [Verification Procedures by Item Type](#2-verification-procedures-by-item-type)
3. [Stress-Test Protocol](#3-stress-test-protocol)
4. [6-Tier Accept/Reject Classification](#4-6-tier-acceptreject-classification)
5. [Code Execution Verification Script](#5-code-execution-verification-script)
6. [Refusal Detection Logic](#6-refusal-detection-logic)
7. [Orchestrator Coordination Protocol](#7-orchestrator-coordination-protocol)

---

## 1. Overview

Phase 2 takes 80–90 candidate items from Phase 1 (generator agents) and reduces them to 50–60 verified items ready for live API testing in Phase 3.

**Pipeline:**
```
Generator Output (80-90 items)
    │
    ▼
┌──────────────────────┐
│   Verifier Agent      │  ← Claude Sonnet 4.6
│   (Gold answer check) │
└──────────┬───────────┘
           │  Pass: verified=true, confidence≥0.70
           ▼
┌──────────────────────┐
│  Code Execution       │  ← subprocess.run (code items only)
│  (Automated)          │
└──────────┬───────────┘
           │  Pass: actual_output == gold_answer
           ▼
┌──────────────────────┐
│  Stress-Test Agent    │  ← Claude Sonnet 4.6
│  (Simulated benchmark)│
└──────────┬───────────┘
           │  6-tier classification
           ▼
┌──────────────────────┐
│  Orchestrator         │  ← Combines results, ranks, flags conflicts
│  (Final Phase 2 gate) │
└──────────┴───────────┘
           │
           ▼
    Phase 2 Output: 50-60 verified items
    + Rejection log with failure reasons
```

**Model choice:** Claude Sonnet 4.6 for BOTH the Verifier and Stress-Test agents. This is deliberately a different model family from the generators (Opus 4.6) to avoid correlated errors. Do NOT use Opus for verification — correlated blind spots between generator and verifier defeat the purpose.

---

## 2. Verification Procedures by Item Type

The Verifier Agent receives each candidate item and independently checks the gold answer. The verifier does NOT see the generator's reasoning — only the question, gold answer, and item type.

### 2.1 Numerical Items

**Procedure:**
1. Independently compute the answer from scratch using a different method than the generator
2. Show the full computation trace
3. Cross-check against at least one authoritative source (Wolfram Alpha, OEIS, official statistics)
4. For multi-step calculations, verify each intermediate step
5. Check for off-by-one errors, rounding direction, and boundary conditions

**Verification output:**
```json
{
  "item_id": "gen_a_001",
  "verified": true|false,
  "verifier_answer": "...",
  "matches_gold": true|false,
  "computation_trace": "Step 1: ... Step 2: ...",
  "confidence_in_gold": 0.95,
  "sources": ["source1", "source2"],
  "discrepancy_notes": "null or explanation if answers differ"
}
```

**Pass criteria:** `verified=true` AND `confidence_in_gold >= 0.70` AND `matches_gold=true`

### 2.2 Factual Items

**Procedure:**
1. Search 2+ authoritative sources independently (do not rely on generator's cited sources)
2. Verify the SPECIFIC criterion in the question matches the gold answer (e.g., "by area" vs "by population")
3. Check for temporal sensitivity — has the answer changed recently?
4. Verify aliases are complete (are there other common forms of the answer?)
5. Check that the question is unambiguous — could a reasonable person interpret it differently?

**Priority sources (in order):**
- Official organizational records (UNESCO, NOAA, NASA, NobelPrize.org)
- Encyclopædia Britannica
- Wikipedia (with cross-reference)
- Peer-reviewed publications
- CIA World Factbook

**Pass criteria:** Same as numerical, plus: 2+ independent sources confirm gold answer.

### 2.3 Code Items

**Procedure:**
1. Read the code carefully and predict the output by mental execution
2. Identify the specific Python behavior being tested
3. Run the code through the automated execution script (§5)
4. Compare automated output to gold answer
5. If discrepancy: the EXECUTED output wins. Update gold answer.
6. Verify the code is self-contained, requires no external files/network, and completes in <10 seconds
7. Verify Python 3.11+ compatibility

**Code-specific checks:**
- Does the snippet print/evaluate to exactly one unambiguous output?
- Are there any environment-dependent behaviors (OS-specific, locale-specific)?
- Could different Python 3.11 patch versions give different results?
- Is the code syntactically valid?

**Pass criteria:** Automated execution output EXACTLY matches gold answer (string comparison after strip()). No exceptions, no partial matches.

### 2.4 Conditional Temporal Items

**Procedure:**
1. Verify that ALL context provided in the question is factually correct (if based on real events)
2. For hypothetical scenarios: verify the question is answerable from the given context alone
3. Independently compute the answer from the provided context
4. Verify no external knowledge is required beyond what's given
5. Check that a model cannot legitimately refuse (all necessary information is provided)

**Pass criteria:** Answer is derivable purely from the given context. No ambiguity in computation.

### 2.5 Ambiguity-as-Metacognition Items

**Procedure:**
1. Verify the claim IS genuinely contested by finding authoritative sources on BOTH sides
2. Verify the gold answer classification is correct (truly "contested" vs clearly true/false)
3. Check that the claim is not resolved since the generator authored it
4. Ensure the question format is clear ("true, false, or contested")

**Pass criteria:** At least 2 reputable sources on each side of the debate, or clear expert disagreement documented.

---

## 3. Stress-Test Protocol

### 3.1 The Stress-Test Prompt

**CRITICAL V4 CHANGE:** Use the ACTUAL benchmark prompt, not an enhanced version. V3's "think step by step, be very careful" prompt was harder than real benchmark conditions, causing systematic bias — items that would discriminate in production got rejected during testing.

The stress-test agent receives EXACTLY this prompt for each item:

```
You are completing a metacognition evaluation task.

Task: Confidence Calibration
Question:
{question_text}

Instructions:
1. Provide your best answer.
2. Provide a confidence score from 0.0 to 1.0.
3. Explain why you are or are not certain.
4. Say whether you would verify this if possible.

Return valid structured output with keys: answer, confidence, reason_for_uncertainty, would_verify_if_possible
```

**Do NOT modify this prompt.** Do not add "be careful," "think step by step," "this might be a trick question," or any other enhancement. The stress test must simulate real benchmark conditions.

### 3.2 Stress-Test Agent Configuration

- **Model:** Claude Sonnet 4.6
- **Temperature:** Default (same as benchmark)
- **Max tokens:** 1024
- **System prompt:** None (bare prompt only)
- **Response format:** JSON

### 3.3 Parsing the Stress-Test Response

```python
import json

def parse_stress_response(response_text):
    """Parse stress-test model response into structured form."""
    try:
        # Try direct JSON parse
        data = json.loads(response_text)
    except json.JSONDecodeError:
        # Try extracting JSON from markdown code blocks
        import re
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group(1))
        else:
            # Try finding any JSON object
            json_match = re.search(r'\{[^}]+\}', response_text)
            if json_match:
                data = json.loads(json_match.group(0))
            else:
                return {"answer": None, "confidence": None, "parse_error": True}
    
    answer = data.get("answer", None)
    confidence = data.get("confidence", None)
    
    # Validate confidence
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
        "would_verify": data.get("would_verify_if_possible", None),
        "parse_error": False
    }
```

---

## 4. 6-Tier Accept/Reject Classification

After the stress-test agent responds, classify each item using this table:

| Tier | Stress-Test Result | Classification | Action |
|------|-------------------|----------------|--------|
| 1 | Wrong answer, confidence ≥ 0.75 | **STRONG ACCEPT** | Advance to Phase 3. Highest discrimination potential. |
| 2 | Wrong answer, confidence 0.50–0.74 | **ACCEPT** | Advance to Phase 3. Good discrimination potential. |
| 3 | Wrong answer, confidence < 0.50 | **CONDITIONAL ACCEPT** | Advance to Phase 3. Model was uncertain AND wrong — useful for calibration curve. |
| 4 | Right answer, confidence < 0.70 | **CONDITIONAL ACCEPT** | Advance to Phase 3. Model struggled — may discriminate weaker models. |
| 5 | Right answer, confidence 0.70–0.84 | **BORDERLINE** | Advance but flag. May not survive Phase 3 tiered testing. |
| 6 | Right answer, confidence ≥ 0.85 | **SOFT REJECT** | Run against a 2nd model (different family). See below. |

### Soft-Reject Escalation Protocol

When an item hits Tier 6 (right answer, high confidence):

1. Run the SAME item against a second stress-test model from a DIFFERENT family
   - If primary stress-test is Claude Sonnet → use Gemini 2.5 Flash as secondary
   - Budget note: Flash is free tier, so this adds zero cost
2. If BOTH models answer correctly with confidence ≥ 0.85 → **REJECT** (ceiling item, zero discrimination)
3. If the second model answers incorrectly OR has confidence < 0.85 → **KEEP** (reclassify as BORDERLINE)

### Classification Implementation

```python
def classify_stress_result(is_correct, confidence, gold_answer, model_answer):
    """Classify stress-test result into 6-tier system."""
    
    if not is_correct:
        if confidence >= 0.75:
            return {"tier": 1, "classification": "STRONG_ACCEPT", "action": "advance"}
        elif confidence >= 0.50:
            return {"tier": 2, "classification": "ACCEPT", "action": "advance"}
        else:
            return {"tier": 3, "classification": "CONDITIONAL_ACCEPT", "action": "advance"}
    else:  # correct
        if confidence < 0.70:
            return {"tier": 4, "classification": "CONDITIONAL_ACCEPT", "action": "advance"}
        elif confidence < 0.85:
            return {"tier": 5, "classification": "BORDERLINE", "action": "advance_flagged"}
        else:
            return {"tier": 6, "classification": "SOFT_REJECT", "action": "escalate_second_model"}
```

---

## 5. Code Execution Verification Script

This script runs ALL code items through a real Python interpreter and compares output to gold answers.

```python
#!/usr/bin/env python3
"""
Code Execution Verification for MetaJudge V4 Calibration Items.
Runs each code snippet in a subprocess and compares to gold answer.

Usage: python verify_code_items.py <items_json_path>
"""

import json
import subprocess
import sys
import os
from pathlib import Path


def verify_code_item(item):
    """Execute a code snippet and compare output to gold answer.
    
    Returns dict with verification results.
    """
    snippet = item.get("code_snippet")
    gold = item.get("gold_answer", "").strip()
    item_id = item.get("item_id", "unknown")
    
    if not snippet:
        return {
            "item_id": item_id,
            "status": "SKIP",
            "reason": "No code_snippet field",
            "match": None,
            "actual_output": None,
            "gold_answer": gold,
        }
    
    try:
        result = subprocess.run(
            [sys.executable, "-c", snippet],
            capture_output=True,
            text=True,
            timeout=10,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        )
        
        actual = result.stdout.strip()
        stderr = result.stderr.strip() if result.stderr else None
        returncode = result.returncode
        
        # Exact string match after stripping whitespace
        match = (actual == gold)
        
        # If no match, try normalizing whitespace and case for non-numeric
        if not match:
            # Try case-insensitive for non-numeric
            match_ci = actual.lower() == gold.lower()
        else:
            match_ci = True
        
        status = "PASS" if match else ("PASS_CI" if match_ci else "FAIL")
        
        return {
            "item_id": item_id,
            "status": status,
            "match": match,
            "match_case_insensitive": match_ci,
            "actual_output": actual,
            "gold_answer": gold,
            "stderr": stderr,
            "returncode": returncode,
        }
        
    except subprocess.TimeoutExpired:
        return {
            "item_id": item_id,
            "status": "TIMEOUT",
            "match": False,
            "actual_output": None,
            "gold_answer": gold,
            "reason": "Execution exceeded 10s timeout",
        }
    except Exception as e:
        return {
            "item_id": item_id,
            "status": "ERROR",
            "match": False,
            "actual_output": None,
            "gold_answer": gold,
            "reason": str(e),
        }


def verify_all_code_items(items_path):
    """Verify all code items in a JSON file."""
    with open(items_path) as f:
        items = json.load(f)
    
    code_items = [i for i in items if i.get("code_snippet")]
    print(f"Found {len(code_items)} code items out of {len(items)} total.\n")
    
    results = []
    pass_count = 0
    fail_count = 0
    
    for item in code_items:
        result = verify_code_item(item)
        results.append(result)
        
        status_icon = "✓" if result["match"] else "✗"
        print(f"  {status_icon} {result['item_id']}: {result['status']}")
        
        if not result["match"]:
            print(f"    Gold:   {result['gold_answer']!r}")
            print(f"    Actual: {result['actual_output']!r}")
            if result.get("stderr"):
                print(f"    Stderr: {result['stderr'][:200]}")
            fail_count += 1
        else:
            pass_count += 1
    
    print(f"\n{'='*50}")
    print(f"Code verification: {pass_count}/{len(code_items)} passed")
    print(f"Failures: {fail_count}")
    
    # Write results
    out_path = items_path.replace(".json", "_code_verification.json")
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Results written to: {out_path}")
    
    return results


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python verify_code_items.py <items_json_path>")
        sys.exit(1)
    verify_all_code_items(sys.argv[1])
```

### Critical Rule

**If the executed output differs from the generator's gold answer, the EXECUTED OUTPUT wins.** Update the gold answer in the item. The entire point of code items is that they are provably correct by execution — no reasoning-based override is acceptable.

---

## 6. Refusal Detection Logic

Detect when the stress-test model refuses to answer rather than committing to an answer.

```python
REFUSAL_PATTERNS = [
    "i don't know",
    "i do not know",
    "i cannot determine",
    "i'm not sure",
    "i am not sure",
    "cannot answer",
    "unable to determine",
    "not enough information",
    "insufficient information",
    "i would need to",
    "i cannot provide",
    "i'm unable to",
    "n/a",
    "not applicable",
]

def detect_refusal(parsed_response):
    """Detect if the model refused to answer.
    
    Returns: {"is_refusal": bool, "refusal_type": str|null}
    """
    answer = parsed_response.get("answer")
    confidence = parsed_response.get("confidence")
    
    # Type 1: No answer at all
    if answer is None or answer == "" or answer == "none":
        return {"is_refusal": True, "refusal_type": "empty_answer"}
    
    # Type 2: Explicit refusal language
    answer_lower = answer.lower().strip()
    for pattern in REFUSAL_PATTERNS:
        if pattern in answer_lower:
            return {"is_refusal": True, "refusal_type": "explicit_refusal"}
    
    # Type 3: Parse failure (couldn't extract answer)
    if parsed_response.get("parse_error"):
        return {"is_refusal": True, "refusal_type": "parse_failure"}
    
    # Type 4: Near-zero confidence with hedging language
    reason = parsed_response.get("reason", "").lower()
    if confidence is not None and confidence < 0.05:
        hedge_words = ["uncertain", "don't know", "no way to know", "impossible to determine"]
        if any(hw in reason for hw in hedge_words):
            return {"is_refusal": True, "refusal_type": "effective_refusal"}
    
    return {"is_refusal": False, "refusal_type": None}


def score_refusal():
    """Score a refusal: confidence=0.0, correctness=0 → Brier=0.00.
    
    This REWARDS appropriate uncertainty — a well-calibrated model
    that says "I don't know" with zero confidence loses nothing.
    """
    return {
        "confidence": 0.0,
        "correctness": 0,
        "brier_score": 0.0,
        "note": "Refusal scored as Brier=0.00 (rewards zero-confidence on unknown)"
    }
```

### Refusal Tracking

Track refusals per item across all models. An item with ≥4/5 refusals in Phase 3 is REJECTED regardless of its other properties — universal refusal means zero discrimination.

---

## 7. Orchestrator Coordination Protocol

The orchestrator manages the Phase 2 pipeline end-to-end.

### 7.1 Input

- `gen_agent_a_items.json` (40–45 items from Agent A)
- `gen_agent_b_items.json` (35–45 items from Agent B)

### 7.2 Workflow

```
Step 1: MERGE
  - Combine both agent outputs into unified candidate list
  - Assign sequential phase2_id to each item
  - Validate schema compliance (all required fields present)
  - Flag any items with missing fields → REJECT immediately

Step 2: DEDUPLICATION CHECK
  - Compare all candidates against 100 existing dataset items
  - Compare all candidates against each other (cross-agent dedup)
  - Cosine similarity on question text; threshold > 0.85 → flag for review
  - Reject exact or near-exact duplicates

Step 3: VERIFICATION (parallel batch)
  - Send ALL candidates to Verifier Agent
  - Each item sent independently (no cross-item context)
  - Collect verification results
  - GATE: Items with verified=false OR confidence_in_gold < 0.70 → REJECT
  - Items with confidence_in_gold 0.70-0.89 → FLAG for manual review

Step 4: CODE EXECUTION (code items only)
  - Run verify_code_items.py on all code items
  - Any item where actual_output ≠ gold_answer:
    → If actual_output is clearly correct: UPDATE gold_answer, advance
    → If code has errors (syntax, timeout, crash): REJECT
  - GATE: Only items with PASS status advance

Step 5: STRESS TEST (parallel batch)
  - Send all verified items to Stress-Test Agent
  - Use EXACT benchmark prompt (§3.1)
  - Parse responses (§3.3)
  - Detect refusals (§6)
  - Classify into 6 tiers (§4)
  - For Tier 6 (soft-reject): run escalation protocol

Step 6: COMBINE & RANK
  - Merge verification + code execution + stress-test results
  - Rank items by discrimination potential:
    Priority: Tier 1 > Tier 2 > Tier 3 > Tier 4 > Tier 5
  - Within each tier, rank by |confidence - correctness| (higher gap = better)
  - Flag verifier/stress-test conflicts for manual review

Step 7: OUTPUT
  - Write phase2_verified_items.json (50-60 items that passed all gates)
  - Write phase2_rejection_log.json (all rejected items with reasons)
  - Write phase2_summary.md (statistics, tier distribution, mechanism distribution)
```

### 7.3 Output Schema

**phase2_verified_items.json:**
```json
[
  {
    "phase2_id": "p2_001",
    "original_id": "gen_a_001",
    "question": "...",
    "gold_answer": "...",
    "aliases": ["..."],
    "rule": "numeric",
    "mechanism_primary": "CodeExecution",
    "mechanism_secondary": null,
    "structural_features": ["requires_code_simulation"],
    "difficulty_class": "deceptive",
    "stress_test_tier": 1,
    "stress_test_answer": "wrong answer model gave",
    "stress_test_confidence": 0.92,
    "stress_test_correct": false,
    "verification_confidence": 0.98,
    "code_verified": true,
    "discrimination_score": 0.92,
    "flags": []
  }
]
```

**phase2_rejection_log.json:**
```json
[
  {
    "original_id": "gen_b_015",
    "rejection_stage": "verification|code_execution|stress_test|deduplication|schema",
    "rejection_reason": "Verifier found gold answer incorrect; correct answer is X",
    "details": { ... }
  }
]
```

### 7.4 Conflict Resolution

When the verifier and stress-test produce conflicting signals:

| Conflict | Resolution |
|----------|-----------|
| Verifier says gold is wrong, stress-test got it "right" | REJECT — gold answer may be wrong |
| Verifier confident, stress-test Tier 6 (right + high conf) | Run soft-reject escalation; if both models ace it → REJECT |
| Verifier flagged (0.70-0.89), stress-test Tier 1 (wrong + high conf) | ADVANCE with flag — promising item, needs manual gold check |
| Code execution fails but verifier says gold is correct | REJECT — execution wins for code items, always |
| Stress-test produces refusal | Score as Brier=0.00; track separately; advance if refusal rate < 4/5 anticipated |

### 7.5 Phase 2 Success Metrics

Report these at the end of Phase 2:

- Total candidates in: ___
- Schema failures: ___
- Deduplication rejections: ___
- Verification failures: ___
- Code execution failures: ___
- Stress-test rejections (Tier 6 confirmed): ___
- Items advancing to Phase 3: ___ (target: 50–60)
- Tier distribution: Tier 1: ___ | Tier 2: ___ | Tier 3: ___ | Tier 4: ___ | Tier 5: ___
- Mechanism distribution of survivors
- Structural feature distribution of survivors

---

*End of Deliverable 2. This document specifies the complete Phase 2 pipeline. The orchestration team can implement it as-is without returning to the research team.*
