"""
MetaJudge-AGI: Task Family C — Self-Correction (V2 Protocol)
=============================================================
Source: planning/family_c_sprint/21_family_c_design_review_v2.md

Two-turn evaluation of metacognitive self-correction ability.
  C1: intrinsic review (third-person + fallback prompts)
  C2: evidence-assisted review (reviewer's note with evidence snippet)
  B0: baseline re-answering (separate chat, no review context)

This module provides prompt templates, answer/confidence parsing,
and scoring helpers. The actual @kbench.task definitions live in
the notebooks (they need the live SDK context).
"""

from __future__ import annotations

import re
from difflib import SequenceMatcher
from typing import Any, Dict, Optional, Tuple

from metajudge.scoring.self_correction_v2 import (
    build_audit_row,
    classify_transition,
    score_item,
)

# ---------------------------------------------------------------------------
# Prompt templates
# ---------------------------------------------------------------------------

T1_SUFFIX = (
    "\n\nPlease give a concise answer, then rate your confidence from 0 to 100."
    "\nFormat: ANSWER: [your answer] | CONFIDENCE: [0-100]"
)

C1_T2_PRIMARY = """A colleague submitted the following analysis for review.

As an independent reviewer, evaluate this analysis WITHOUT re-solving the problem from scratch. For each reasoning step, assess whether the conclusion follows from the premises. Identify the single weakest step, if any exists, and explain what could go wrong there.

Then provide your verdict:
- If you found an error: state the corrected answer
- If the analysis is sound: confirm the original answer
- If you are uncertain: state what additional information would be needed

ANSWER: [your answer] | CONFIDENCE: [0-100]"""

C1_T2_FALLBACK = """Wait — before confirming, let me reconsider.

Review your previous answer carefully. What is the most likely type of error, if any? If you find an error, provide the corrected answer. If you find no error, confirm your answer.

ANSWER: [your answer] | CONFIDENCE: [0-100]"""

C2_T2_TEMPLATE = """Here is a reviewer's note on your analysis:

{evidence}

Consider this feedback carefully. If it reveals an error in your reasoning, provide the corrected answer. If your original analysis already accounts for this point, confirm your original answer. If you are now uncertain, state what remains unclear.

ANSWER: [your answer] | CONFIDENCE: [0-100]"""

# Threshold for choosing C1 primary vs fallback prompt.
C1_PRIMARY_MIN_LENGTH = 500


# ---------------------------------------------------------------------------
# Answer + confidence parsing
# ---------------------------------------------------------------------------

def parse_answer_confidence(text: str) -> Tuple[str, Optional[float]]:
    """Extract answer and confidence from free-form response.

    Looks for ``ANSWER: <text> | CONFIDENCE: <0-100>`` pattern.
    Falls back to partial extraction or full text as answer.

    Returns (answer_text, confidence_0_to_1_or_None).
    """
    confidence = None
    answer = text  # fallback: full text

    # Try structured format: ANSWER: ... | CONFIDENCE: ...
    m = re.search(r'ANSWER:\s*(.+?)\s*\|\s*CONFIDENCE:\s*(\d+)', text, re.IGNORECASE)
    if m:
        answer = m.group(1).strip()
        confidence = float(m.group(2)) / 100.0
        return answer, confidence

    # Try just CONFIDENCE: N
    m = re.search(r'CONFIDENCE:\s*(\d+)', text, re.IGNORECASE)
    if m:
        confidence = float(m.group(1)) / 100.0

    # Try just ANSWER: ...
    m = re.search(r'ANSWER:\s*(.+?)(?:\s*$|\s*\|)', text, re.IGNORECASE)
    if m:
        answer = m.group(1).strip()

    return answer, confidence


# ---------------------------------------------------------------------------
# Confirmation-without-restatement detection
# ---------------------------------------------------------------------------

_CONFIRMATION_PHRASES = [
    "my original answer remains",
    "my original answer is confirmed",
    "my original answer stands",
    "my original analysis already accounts",
    "my original analysis is confirmed",
    "i confirm my previous answer",
    "i confirm the original answer",
    "the analysis is sound",
    "no error found",
    "no error in the previous",
    "original answer remains correct",
    "answer is confirmed",
    "i have found no error",
    "confirm my answer",
    "the information in the reviewer",
    "upon review, the most likely source of error",
    "after careful review, i confirm",
    "the previous answer is confirmed",
    "i confirm the previous answer",
]


def is_confirmation_without_restatement(t2_answer: str, gold_answer: str) -> bool:
    """Detect if T2 answer is a confirmation that doesn't restate the answer.

    Returns True when the T2 parsed answer matches a confirmation phrase
    pattern AND does not contain the gold answer text. In this case, the
    model intended to confirm T1 but the ANSWER: tag was missing or the
    extraction captured the explanation rather than a concise answer.
    """
    t2_lower = t2_answer.lower()
    gold_lower = gold_answer.lower().strip()

    # If the gold answer is present in the text, grading can handle it
    if gold_lower in t2_lower:
        return False

    # Only flag if the answer is long (>40 chars) — short answers are
    # unlikely to be verbose confirmations
    if len(t2_answer) <= 40:
        return False

    return any(phrase in t2_lower for phrase in _CONFIRMATION_PHRASES)


def resolve_t2_answer(
    t2_answer: str,
    t1_answer: str,
    gold_answer: str,
) -> str:
    """Return the effective T2 answer for grading.

    If T2 is a confirmation-without-restatement, inherit T1's parsed answer
    (since the model intended to confirm it). Otherwise return T2 as-is.
    """
    if is_confirmation_without_restatement(t2_answer, gold_answer):
        return t1_answer
    return t2_answer


# ---------------------------------------------------------------------------
# Edit-distance computation
# ---------------------------------------------------------------------------

def compute_edit_similarity(t1: str, t2: str) -> float:
    """Ratio of unchanged content. 1.0 = identical, 0.0 = completely different."""
    return SequenceMatcher(None, t1.lower(), t2.lower()).ratio()


# ---------------------------------------------------------------------------
# Scoring helper (wraps the scoring module for notebook convenience)
# ---------------------------------------------------------------------------

def score_family_c_item(
    item_id: str,
    subfamily: str,
    stratum: str,
    normative_t2_action: str,
    t1_answer: str,
    t1_confidence: Optional[float],
    t1_correct: bool,
    t2_answer: str,
    t2_confidence: Optional[float],
    t2_correct: bool,
    challenge_type: Optional[str] = None,
    t1_text: str = "",
    t2_text: str = "",
) -> Dict[str, Any]:
    """Score a Family C item and return a complete audit row.

    Handles None confidence by defaulting to 0.5.
    """
    conf_1 = t1_confidence if t1_confidence is not None else 0.5
    conf_2 = t2_confidence if t2_confidence is not None else 0.5
    revised = t1_answer.strip().lower() != t2_answer.strip().lower()

    row = build_audit_row(
        item_id=item_id,
        subfamily=subfamily,
        stratum=stratum,
        normative_action=normative_t2_action,
        answer_1=t1_answer,
        conf_1=conf_1,
        correct_1=t1_correct,
        answer_2=t2_answer,
        conf_2=conf_2,
        correct_2=t2_correct,
        revised=revised,
        challenge_type=challenge_type,
    )

    # Add edit similarity if full text available
    if t1_text and t2_text:
        row["t1_t2_similarity"] = round(compute_edit_similarity(t1_text, t2_text), 4)

    return row
