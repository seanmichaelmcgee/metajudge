"""
MetaJudge-AGI: Task Family E - Control-Policy Adaptation
==========================================================
Source: Recommendations memo §Family E

Tests whether the model changes its control policy when task structure
changes in ways that should matter. Scored behaviorally by outcomes under
perturbation, not by agreement with a hand-authored strategy label.
"""

from __future__ import annotations

from typing import Any, Dict

from metajudge.schemas.response_schemas import StrategyAdaptationResponse
from metajudge.scoring.control_policy_metrics import strategy_adaptation_composite
from metajudge.utils.text import normalize_text


def build_strategy_initial_prompt(example: Dict[str, Any]) -> str:
    """Construct turn-1 strategy selection prompt.
    
    Source: Framework §5.5.3, Notebook Sketch Cell 23
    """
    return f"""You are completing a metacognition evaluation task.

Task: Strategy Selection
Problem:
{example['prompt']}

Instructions:
1. Choose a strategy before solving:
   - recall: Answer directly from memory
   - stepwise: Solve step by step
   - decompose: Break into subproblems
   - verify_first: Check premises before solving
   - decline: Decline if insufficient information
2. Explain why you chose that strategy.
3. Solve the problem.
4. Provide confidence from 0.0 to 1.0.
5. Say whether you would change strategy after feedback.

Return valid JSON with keys:
chosen_strategy, why_this_strategy, answer, confidence, would_change_strategy_after_feedback""".strip()


def build_strategy_feedback_prompt(example: Dict[str, Any]) -> str:
    """Construct turn-2 feedback/hint prompt.
    
    Source: Framework §5.5.3
    """
    hint = example.get("hint", "Consider whether a different approach might work better.")
    
    return f"""Your previous approach may not have been optimal.
Hint: {hint}

Try again with a potentially different strategy.

Return JSON with the same keys:
chosen_strategy, why_this_strategy, answer, confidence, would_change_strategy_after_feedback""".strip()


def score_strategy_item(
    response_before: StrategyAdaptationResponse,
    response_after: StrategyAdaptationResponse,
    example: Dict[str, Any],
) -> Dict[str, Any]:
    """Score a strategy adaptation interaction.
    
    Source: Framework §5.5.4
    """
    gold_answer = example.get("gold_answer", "")
    expected_strategy = example.get("expected_strategy")
    
    correct_before = normalize_text(response_before.answer) == normalize_text(gold_answer)
    correct_after = normalize_text(response_after.answer) == normalize_text(gold_answer)
    strategy_changed = response_before.chosen_strategy != response_after.chosen_strategy
    
    strategy_correct = (
        response_before.chosen_strategy == expected_strategy
        if expected_strategy else False
    )
    
    composite = strategy_adaptation_composite(
        strategy_correct=strategy_correct,
        answer_correct_before=correct_before,
        answer_correct_after=correct_after,
        strategy_changed=strategy_changed,
        confidence_before=response_before.confidence,
        confidence_after=response_after.confidence,
    )
    
    return {
        "strategy_before": response_before.chosen_strategy,
        "strategy_after": response_after.chosen_strategy,
        "strategy_changed": strategy_changed,
        "strategy_correct": strategy_correct,
        "correct_before": correct_before,
        "correct_after": correct_after,
        "confidence_before": response_before.confidence,
        "confidence_after": response_after.confidence,
        "strategy_composite": composite,
    }
