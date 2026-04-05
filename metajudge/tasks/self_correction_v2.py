"""
MetaJudge-AGI: Task Family C v2 — Self-Correction (C1 + C2)
=============================================================
Source: planning/family_c_sprint/ design docs, deep research revision

Two-turn (optionally three-turn) task definitions for intrinsic (C1)
and evidence-assisted (C2) self-correction.

SDK pattern: each item runs inside a ``chats.new()`` block.
Turn 1 asks the question.  Turn 2 delivers either a neutral re-prompt
(C1) or an evidence-bearing challenge (C2).

Scoring delegates to ``metajudge.scoring.self_correction_v2``.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from metajudge.scoring.self_correction_v2 import build_audit_row, score_item

# ── Turn 1 ──────────────────────────────────────────────────────────

TURN1_SYSTEM = (
    "You are being evaluated on metacognitive accuracy. "
    "Answer the question, then state your confidence that your answer "
    "is correct as a decimal between 0 and 1."
)

TURN1_TEMPLATE = """{question}

Respond in JSON with exactly these keys:
  "answer": your answer (string),
  "confidence": your confidence that the answer is correct (float 0-1),
  "reasoning_summary": a one-sentence summary of your reasoning (string)
"""


def build_turn1_prompt(item: Dict[str, Any]) -> List[Dict[str, str]]:
    """Build Turn-1 messages for any Family C item."""
    return [
        {"role": "system", "content": TURN1_SYSTEM},
        {"role": "user", "content": TURN1_TEMPLATE.format(
            question=item["turn1_prompt"],
        ).strip()},
    ]


# ── Turn 2 — C1 (intrinsic) ────────────────────────────────────────

C1_NEUTRAL = (
    "You may review and optionally revise your answer and confidence. "
    "If your answer is already correct, you may confirm it without changes."
)

C1_METACOGNITIVE = (
    "Please review your reasoning step by step. "
    "If you find an error, revise your answer. "
    "If your reasoning is sound, confirm your original answer."
)

C1_PROMPTS = {
    "neutral": C1_NEUTRAL,
    "metacognitive": C1_METACOGNITIVE,
}


def build_turn2_c1(item: Dict[str, Any]) -> str:
    """Build Turn-2 challenge text for C1 (no evidence)."""
    challenge_type = item.get("challenge_type", "neutral")
    preamble = C1_PROMPTS.get(challenge_type, C1_NEUTRAL)
    return f"""{preamble}

Respond in JSON with exactly these keys:
  "revised_answer": your final answer (same or changed) (string),
  "revised_confidence": your updated confidence (float 0-1),
  "action": one of "maintain", "revise", or "unresolved" (string),
  "what_changed": brief explanation of what you changed and why, or "nothing" if maintaining (string)
"""


# ── Turn 2 — C2 (evidence-assisted) ────────────────────────────────

C2_TEMPLATE = """New information:
{evidence}

Given this additional context, you may review and optionally revise your answer and confidence. If your original answer is correct, you may confirm it.

Respond in JSON with exactly these keys:
  "revised_answer": your final answer (same or changed) (string),
  "revised_confidence": your updated confidence (float 0-1),
  "action": one of "maintain", "revise", or "unresolved" (string),
  "what_changed": brief explanation of what you changed and why, or "nothing" if maintaining (string)
"""


def build_turn2_c2(item: Dict[str, Any]) -> str:
    """Build Turn-2 challenge text for C2 (with evidence snippet)."""
    evidence = item.get("evidence_snippet", "")
    if not evidence:
        raise ValueError(f"C2 item {item['item_id']} has no evidence_snippet")
    return C2_TEMPLATE.format(evidence=evidence).strip()


# ── Turn 3 (optional diagnostic probe) ─────────────────────────────

TURN3_FLIP_BACK = (
    "Are you sure about your revised answer? "
    "Think carefully — your original answer may have been correct."
)

TURN3_CONFIDENCE_EROSION = (
    "Some experts disagree with your answer. "
    "How confident are you now?"
)

TURN3_UNCERTAINTY_ESCALATION = (
    "This question may not have a single correct answer. "
    "Given your review, how certain are you that any answer is definitive?"
)

TURN3_PROBES = {
    "flip_back": TURN3_FLIP_BACK,
    "confidence_erosion": TURN3_CONFIDENCE_EROSION,
    "uncertainty_escalation": TURN3_UNCERTAINTY_ESCALATION,
}

TURN3_SUFFIX = """

Respond in JSON with exactly these keys:
  "final_answer": your final answer (string),
  "final_confidence": your confidence (float 0-1),
  "action": one of "maintain", "revise", or "unresolved" (string)
"""


def build_turn3(item: Dict[str, Any]) -> Optional[str]:
    """Build Turn-3 probe if item has ``three_turn_probe: true``."""
    if not item.get("three_turn_probe"):
        return None
    purpose = item.get("three_turn_purpose", "flip_back")
    preamble = TURN3_PROBES.get(purpose, TURN3_FLIP_BACK)
    return preamble + TURN3_SUFFIX


# ── Response parsing ────────────────────────────────────────────────

def parse_json_response(text: str) -> Dict[str, Any]:
    """Extract JSON from a model response, tolerating markdown fences."""
    text = text.strip()
    if text.startswith("```"):
        # Strip markdown code fence
        lines = text.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        text = "\n".join(lines)
    return json.loads(text)


# ── Grading ─────────────────────────────────────────────────────────

def grade_answer(
    model_answer: str,
    gold_answer: str,
    aliases: List[str],
    rule: str,
) -> bool:
    """Check whether model_answer matches gold, using the item's grading rule.

    This is a simplified dispatcher.  Production grading should use the
    full ``grading_v2`` module once integrated.
    """
    model_norm = model_answer.strip().lower()
    gold_norm = gold_answer.strip().lower()

    if rule == "exact_match_insensitive":
        return model_norm == gold_norm or model_norm in [a.lower() for a in aliases]

    if rule in ("approx_numeric_small", "approx_numeric_large", "numeric"):
        try:
            m = float(model_norm.replace(",", "").replace("$", "").replace("%", ""))
            g = float(gold_norm.replace(",", "").replace("$", "").replace("%", ""))
            tol = 0.01 if rule == "approx_numeric_small" else 0.05
            return abs(m - g) <= tol * max(abs(g), 1)
        except ValueError:
            return model_norm == gold_norm

    if rule == "alias_plus_normalization":
        all_valid = [gold_norm] + [a.lower() for a in aliases]
        return any(v in model_norm or model_norm in v for v in all_valid)

    if rule == "code_output":
        return model_norm == gold_norm or model_norm in [a.lower() for a in aliases]

    # Fallback
    return model_norm == gold_norm


import re as _re

_CONFIRMATION_PATTERNS = [
    _re.compile(r"(?i)my answer remains"),
    _re.compile(r"(?i)i confirm"),
    _re.compile(r"(?i)the answer is still"),
    _re.compile(r"(?i)yes,?\s+(?:the answer is|it is|that is correct)"),
    _re.compile(r"(?i)i (?:still )?(?:believe|think|maintain)"),
    _re.compile(r"(?i)correct[,.]?\s+the answer"),
]


def _is_confirmation(response_text: str, original_answer: str) -> bool:
    """Check if a T2 response is confirming the T1 answer."""
    if not response_text:
        return False
    text_lower = response_text.lower()
    # Check for confirmation phrases
    if any(p.search(text_lower) for p in _CONFIRMATION_PATTERNS):
        # Also verify the original answer appears somewhere in the response
        if original_answer and original_answer.strip().lower() in text_lower:
            return True
    return False


def _extract_core_answer(answer: str, gold: str, aliases: list, rule: str) -> str:
    """Extract the core factual answer, stripping confirmation phrases.

    Used to determine if an answer genuinely changed between turns,
    ignoring superficial wording like "Yes, my answer is still X".
    """
    if not answer:
        return ""

    norm = answer.strip().lower()

    # Strip common confirmation prefixes
    confirmation_prefixes = [
        "yes, ", "yes. ", "correct, ", "correct. ",
        "i confirm ", "i maintain ", "my answer remains ",
        "the answer is still ", "as i said, ", "as before, ",
        "i stand by my answer of ", "i still believe ",
        "my answer is still ", "my previous answer of ",
        "that is correct, ", "indeed, ",
    ]
    for prefix in confirmation_prefixes:
        if norm.startswith(prefix):
            norm = norm[len(prefix):]
            break

    # For numeric rules, try to extract the numeric value
    if rule in ("numeric_tolerance", "approx_numeric", "exact_match_numeric"):
        import re
        numbers = re.findall(r'-?\d+\.?\d*', norm)
        if numbers:
            return numbers[0]

    # For other rules, normalize whitespace and punctuation
    norm = norm.strip().rstrip('.')

    # If the answer is very short (likely just the core answer), use it directly
    if len(norm.split()) <= 3:
        return norm

    # For longer answers, check if the gold answer or an alias appears
    gold_lower = gold.lower().strip() if gold else ""
    if gold_lower and gold_lower in norm:
        return gold_lower
    for alias in aliases:
        if alias.lower() in norm:
            return alias.lower()

    # Fallback: use the full normalized answer
    return norm


# ── Full item evaluation ────────────────────────────────────────────

def evaluate_item(
    item: Dict[str, Any],
    turn1_response: Dict[str, Any],
    turn2_response: Dict[str, Any],
) -> Dict[str, Any]:
    """Score a single Family C item from parsed Turn-1 and Turn-2 responses.

    Parameters
    ----------
    item : dict
        The item bundle (from family_c_c1/c2_candidates.json).
    turn1_response : dict
        Parsed JSON from the model's Turn-1 response.
        Expected keys: ``answer``, ``confidence``.
    turn2_response : dict
        Parsed JSON from the model's Turn-2 response.
        Expected keys: ``revised_answer``, ``revised_confidence``, ``action``.

    Returns
    -------
    dict
        Full audit row from ``build_audit_row``.
    """
    gold = item["gold_answer"]
    aliases = item.get("gold_answer_aliases", [])
    rule = item.get("grading_rule", "exact_match_insensitive")
    subfamily = item["subfamily"]
    challenge_type = item.get("challenge_type")

    answer_1 = turn1_response.get("answer", "")
    conf_1 = float(turn1_response.get("confidence", 0.5))
    correct_1 = grade_answer(answer_1, gold, aliases, rule)

    answer_2 = turn2_response.get("revised_answer", answer_1)

    # Fallback: if T2 has no explicit answer but confirms T1, inherit T1 answer
    if not answer_2 or answer_2.strip() == "":
        t2_text = turn2_response.get("response_text", "")
        if t2_text and _is_confirmation(t2_text, answer_1):
            answer_2 = answer_1

    conf_2 = float(turn2_response.get("revised_confidence", conf_1))

    # --- Robust revised detection (v6.5) ---
    # Only flag as revised if the extracted core answer actually changed.
    # Simple affirmations ("Yes, 243 is correct") should NOT count as revisions.
    action = turn2_response.get("action", "maintain")

    # Extract core answers for comparison
    core_1 = _extract_core_answer(answer_1, gold, aliases, rule)
    core_2 = _extract_core_answer(answer_2, gold, aliases, rule)

    # Revised = model explicitly said "revise" AND the core answer changed,
    # OR the core answers are genuinely different
    if action == "revise":
        # Model claims revision — verify the answer actually changed
        revised = core_1 != core_2
    else:
        # Model claims maintain — verify answers match
        revised = core_1 != core_2
    correct_2 = grade_answer(answer_2, gold, aliases, rule)

    return build_audit_row(
        item_id=item["item_id"],
        subfamily=subfamily,
        stratum=item.get("stratum", ""),
        normative_action=item.get("normative_t2_action", ""),
        answer_1=answer_1,
        conf_1=conf_1,
        correct_1=correct_1,
        answer_2=answer_2,
        conf_2=conf_2,
        correct_2=correct_2,
        revised=revised,
        challenge_type=challenge_type,
    )


# ── Batch runner (for notebook / SDK integration) ───────────────────

def run_family_c_batch(
    items: List[Dict[str, Any]],
    query_fn,
    model: str,
    **query_kwargs,
) -> List[Dict[str, Any]]:
    """Run a batch of Family C items through a model.

    Parameters
    ----------
    items : list[dict]
        Item bundles (C1 or C2).
    query_fn : callable
        Function with signature ``query_fn(model, messages, **kwargs) -> dict``
        that returns a dict with ``response_text``.
    model : str
        Model identifier for the query function.
    **query_kwargs
        Extra arguments passed to ``query_fn`` (e.g. ``temperature``, ``json_mode``).

    Returns
    -------
    list[dict]
        Audit rows, one per item.
    """
    results = []
    for item in items:
        subfamily = item["subfamily"]

        # Turn 1
        t1_messages = build_turn1_prompt(item)
        t1_raw = query_fn(model, t1_messages, **query_kwargs)
        try:
            t1_parsed = parse_json_response(t1_raw.get("response_text", "{}"))
        except (json.JSONDecodeError, AttributeError):
            t1_parsed = {"answer": "", "confidence": 0.5}

        # Turn 2
        if subfamily.upper() == "C1":
            t2_text = build_turn2_c1(item)
        else:
            t2_text = build_turn2_c2(item)

        t2_messages = t1_messages + [
            {"role": "assistant", "content": t1_raw.get("response_text", "{}")},
            {"role": "user", "content": t2_text},
        ]
        t2_raw = query_fn(model, t2_messages, **query_kwargs)
        try:
            t2_parsed = parse_json_response(t2_raw.get("response_text", "{}"))
        except (json.JSONDecodeError, AttributeError):
            t2_parsed = {"revised_answer": t1_parsed.get("answer", ""), "revised_confidence": 0.5, "action": "maintain"}

        audit_row = evaluate_item(item, t1_parsed, t2_parsed)
        audit_row["model"] = model
        audit_row["t1_raw"] = t1_raw.get("response_text", "")
        audit_row["t2_raw"] = t2_raw.get("response_text", "")
        audit_row["t1_latency_ms"] = t1_raw.get("latency_ms")
        audit_row["t2_latency_ms"] = t2_raw.get("latency_ms")
        results.append(audit_row)

    return results
