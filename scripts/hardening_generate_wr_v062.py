"""
Wrong-to-Right Item Generator for Family C Hardening v0.6.2
============================================================
Generates candidate wrong-to-right items for Family C (Self-Correction).
Uses OpenRouter API via the project client. Outputs items in the exact
Family C schema format.

Usage:
    python scripts/hardening_generate_wr_v062.py --batch-size 2 --subfamily C1
    python scripts/hardening_generate_wr_v062.py --batch-size 3 --subfamily C2
    python scripts/hardening_generate_wr_v062.py --canary sc_c1_wr_new_001

Never import or hardcode API keys. Reads from OPENROUTER_API_KEY env var.
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.openrouter.client import query, MODELS


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

OUTPUT_DIR = PROJECT_ROOT / "outputs" / "family_c" / "wr_generation"
DATA_DIR = PROJECT_ROOT / "data" / "family_c"

GENERATION_MODEL = "deepseek/deepseek-chat"  # Cheap Tier A for generation
CANARY_MODEL = "deepseek/deepseek-chat"      # Cheap model for canary validation

WEAKNESS_CATEGORIES = [
    "multi_step_arithmetic",
    "base_rate_neglect",
    "temporal_confusion",
    "spatial_relation_reasoning",
    "order_of_operations_edge",
    "counterintuitive_checkable_math",
    "quantity_comparison_intuition_failure",
]

# Domains to avoid (famous puzzles that models have memorized)
AVOID_PATTERNS = [
    "Monty Hall", "birthday problem", "trolley problem",
    "prisoner's dilemma", "Tower of Hanoi", "traveling salesman",
    "Fibonacci", "FizzBuzz", "two-envelope", "St. Petersburg paradox",
]

# ---------------------------------------------------------------------------
# Prompts
# ---------------------------------------------------------------------------

GENERATION_PROMPT_C1 = """You are generating test items for a cognitive benchmark that measures whether AI models can self-correct their answers.

Generate {batch_size} wrong-to-right items for subfamily C1 (intrinsic self-correction — no external evidence provided).

Each item must:
1. Have a clear, verifiable correct answer
2. Be designed so that a strong LLM is likely to get it WRONG on first attempt (due to a cognitive trap)
3. NOT be a famous puzzle or well-known trick question (avoid: {avoid_list})
4. Target one of these weakness categories: {categories}
5. Have a difficulty of "medium" or "hard"
6. Be solvable with careful step-by-step reasoning (the gold answer must be unambiguous)

For each item, provide a JSON object with these exact fields:
- turn1_prompt: The question text (clear, self-contained, no hints)
- gold_answer: The correct answer (concise)
- gold_answer_aliases: List of acceptable alternative phrasings
- grading_rule: One of "alias_plus_normalization", "approx_numeric_small", "numeric", "code_output"
- challenge_type: "neutral" or "metacognitive"
- difficulty: "medium" or "hard"
- category: Domain tag (arithmetic, reasoning, spatial, logic, mathematics, code)
- mechanism_primary: Descriptive tag for the cognitive trap
- why_models_fail: Brief explanation of why LLMs typically get this wrong

Respond with a JSON array of items. Nothing else."""

GENERATION_PROMPT_C2 = """You are generating test items for a cognitive benchmark that measures whether AI models can self-correct their answers when given evidence.

Generate {batch_size} wrong-to-right items for subfamily C2 (evidence-based self-correction).

Each item must:
1. Have a clear, verifiable correct answer
2. Be designed so that a strong LLM is likely to get it WRONG on first attempt
3. Include an evidence_snippet (1-3 sentences) that hints at the correct answer without giving it away
4. NOT be a famous puzzle or well-known trick question (avoid: {avoid_list})
5. Target one of these weakness categories: {categories}
6. Have a difficulty of "medium" or "hard"

For each item, provide a JSON object with these exact fields:
- turn1_prompt: The question text
- gold_answer: The correct answer
- gold_answer_aliases: List of acceptable alternatives
- grading_rule: One of "alias_plus_normalization", "approx_numeric_small", "numeric", "code_output"
- challenge_type: One of "suggestive_hint", "contradiction"
- evidence_snippet: 1-3 sentences of evidence that nudges toward the correct answer
- difficulty: "medium" or "hard"
- category: Domain tag
- mechanism_primary: Descriptive tag for the cognitive trap
- why_models_fail: Brief explanation of why LLMs typically get this wrong

Respond with a JSON array of items. Nothing else."""


# ---------------------------------------------------------------------------
# Core functions
# ---------------------------------------------------------------------------

def load_existing_items() -> list[dict]:
    """Load all existing Family C items to avoid duplicates."""
    items = []
    for fname in ["family_c_c1_candidates.json", "family_c_c2_candidates.json"]:
        path = DATA_DIR / fname
        if path.exists():
            with open(path) as f:
                items.extend(json.load(f))
    return items


def get_next_id(subfamily: str, existing_items: list[dict]) -> int:
    """Find the next available WR item number for a subfamily."""
    prefix = f"sc_{subfamily.lower()}_wr_"
    existing_nums = []
    for item in existing_items:
        iid = item["item_id"]
        if iid.startswith(prefix):
            try:
                num = int(iid.split("_")[-1])
                existing_nums.append(num)
            except ValueError:
                pass
    # Also check for 'new' items
    for item in existing_items:
        iid = item["item_id"]
        if iid.startswith(prefix + "new_"):
            try:
                num = int(iid.split("_")[-1])
                existing_nums.append(num)
            except ValueError:
                pass
    return max(existing_nums, default=0) + 1


def generate_batch(
    subfamily: str,
    batch_size: int = 2,
    model: str = GENERATION_MODEL,
) -> list[dict]:
    """Generate a batch of WR candidate items via the API."""
    if subfamily == "C1":
        prompt_template = GENERATION_PROMPT_C1
    else:
        prompt_template = GENERATION_PROMPT_C2

    prompt = prompt_template.format(
        batch_size=batch_size,
        avoid_list=", ".join(AVOID_PATTERNS),
        categories=", ".join(WEAKNESS_CATEGORIES),
    )

    messages = [{"role": "user", "content": prompt}]

    print(f"Generating {batch_size} {subfamily} WR items via {model}...")
    result = query(model, messages, temperature=0.7, max_tokens=4096, json_mode=True)

    if result["error"]:
        print(f"ERROR: {result['error']}")
        return []

    try:
        raw = result["response_text"]
        # Try parsing directly
        items = json.loads(raw)
        if isinstance(items, dict) and "items" in items:
            items = items["items"]
        if not isinstance(items, list):
            items = [items]
        print(f"  Generated {len(items)} items ({result['latency_ms']}ms)")
        return items
    except json.JSONDecodeError as e:
        print(f"  JSON parse error: {e}")
        print(f"  Raw response: {raw[:500]}")
        return []


def format_item(
    raw_item: dict,
    subfamily: str,
    item_number: int,
) -> dict:
    """Convert a generated item to the full Family C schema."""
    item_id = f"sc_{subfamily.lower()}_wr_{item_number:03d}"

    formatted = {
        "item_id": item_id,
        "family": "C",
        "subfamily": subfamily,
        "stratum": "wrong_to_right",
        "turn1_prompt": raw_item.get("turn1_prompt", ""),
        "gold_answer": raw_item.get("gold_answer", ""),
        "gold_answer_aliases": raw_item.get("gold_answer_aliases", []),
        "grading_rule": raw_item.get("grading_rule", "alias_plus_normalization"),
        "normative_t2_action": "revise",
        "challenge_type": raw_item.get("challenge_type", "neutral"),
        "evidence_snippet": raw_item.get("evidence_snippet", None),
        "difficulty": raw_item.get("difficulty", "medium"),
        "category": raw_item.get("category", "reasoning"),
        "mechanism_primary": raw_item.get("mechanism_primary", "unknown"),
        "provenance": "hand_authored",
        "draft_status": "draft",
        "is_linking_item": False,
        "linking_item_id": None,
        "audit_notes": f"Generated v0.6.2 hardening sprint. Why models fail: {raw_item.get('why_models_fail', 'N/A')}",
        "three_turn_probe": False,
        "three_turn_purpose": None,
    }

    # Ensure C1 items have no evidence
    if subfamily == "C1":
        formatted["evidence_snippet"] = None

    return formatted


def canary_validate(item: dict, model: str = CANARY_MODEL) -> dict:
    """
    Test whether a cheap model gets the T1 answer wrong.
    For wrong-to-right items, we WANT the model to get it wrong on T1.
    Returns: {model, answer, correct, latency_ms, verdict}
    """
    messages = [
        {
            "role": "user",
            "content": (
                f"{item['turn1_prompt']}\n\n"
                "Respond with a JSON object: "
                '{"answer": "<your answer>", "confidence": <0.0-1.0>, '
                '"reasoning_summary": "<brief reasoning>"}'
            ),
        }
    ]

    result = query(model, messages, temperature=0.3, max_tokens=1024, json_mode=True)

    canary = {
        "model": model,
        "item_id": item["item_id"],
        "latency_ms": result["latency_ms"],
        "error": result["error"],
        "raw_response": result["response_text"],
        "answer": None,
        "correct": None,
        "verdict": None,
    }

    if result["error"]:
        canary["verdict"] = "api_error"
        return canary

    try:
        parsed = json.loads(result["response_text"])
        model_answer = str(parsed.get("answer", "")).strip().lower()
        canary["answer"] = model_answer
    except (json.JSONDecodeError, AttributeError):
        canary["verdict"] = "parse_error"
        return canary

    # Check correctness
    gold = item["gold_answer"].strip().lower()
    aliases = [a.strip().lower() for a in item.get("gold_answer_aliases", [])]
    all_correct = [gold] + aliases

    is_correct = any(model_answer == c for c in all_correct)
    # Also check containment for longer answers
    if not is_correct:
        is_correct = any(c in model_answer for c in all_correct)

    canary["correct"] = is_correct

    if is_correct:
        canary["verdict"] = "FAIL_too_easy"
    else:
        canary["verdict"] = "PASS_model_wrong"

    return canary


def save_batch(items: list[dict], batch_name: str) -> Path:
    """Save a batch of generated items to a durable file."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = OUTPUT_DIR / f"wr_batch_{batch_name}_{timestamp}.json"
    with open(path, "w") as f:
        json.dump(items, f, indent=2)
    print(f"  Saved batch to {path}")
    return path


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Generate wrong-to-right candidate items for Family C"
    )
    parser.add_argument(
        "--batch-size", type=int, default=2,
        help="Number of items to generate per batch (2-4 recommended)"
    )
    parser.add_argument(
        "--subfamily", choices=["C1", "C2"], default="C1",
        help="Target subfamily"
    )
    parser.add_argument(
        "--canary", type=str, default=None,
        help="Run canary validation on a specific item_id from the latest batch"
    )
    parser.add_argument(
        "--canary-all", action="store_true",
        help="Run canary validation on all items in the latest batch"
    )
    parser.add_argument(
        "--model", type=str, default=GENERATION_MODEL,
        help="Model to use for generation"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print the prompt without calling the API"
    )
    args = parser.parse_args()

    # Load existing items
    existing = load_existing_items()
    next_num = get_next_id(args.subfamily, existing)
    print(f"Next {args.subfamily} WR item number: {next_num:03d}")

    if args.canary:
        # Canary mode: validate a specific item
        target = None
        for item in existing:
            if item["item_id"] == args.canary:
                target = item
                break
        if not target:
            # Check latest batch files
            batch_dir = OUTPUT_DIR
            if batch_dir.exists():
                for bf in sorted(batch_dir.glob("wr_batch_*.json"), reverse=True):
                    with open(bf) as f:
                        batch_items = json.load(f)
                    for bi in batch_items:
                        if bi["item_id"] == args.canary:
                            target = bi
                            break
                    if target:
                        break
        if not target:
            print(f"Item {args.canary} not found")
            sys.exit(1)

        print(f"Canary validating {target['item_id']}...")
        result = canary_validate(target)
        print(json.dumps(result, indent=2))
        return

    if args.dry_run:
        template = GENERATION_PROMPT_C1 if args.subfamily == "C1" else GENERATION_PROMPT_C2
        prompt = template.format(
            batch_size=args.batch_size,
            avoid_list=", ".join(AVOID_PATTERNS),
            categories=", ".join(WEAKNESS_CATEGORIES),
        )
        print("=== DRY RUN — Prompt ===")
        print(prompt)
        return

    # Generate batch
    raw_items = generate_batch(args.subfamily, args.batch_size, args.model)
    if not raw_items:
        print("No items generated. Exiting.")
        sys.exit(1)

    # Format items with proper IDs
    formatted = []
    for i, raw in enumerate(raw_items):
        item = format_item(raw, args.subfamily, next_num + i)
        formatted.append(item)
        print(f"  {item['item_id']}: {item['turn1_prompt'][:80]}...")

    # Save immediately
    batch_name = f"{args.subfamily.lower()}_wr"
    batch_path = save_batch(formatted, batch_name)

    # Canary validate all if requested
    if args.canary_all:
        print("\n=== Canary Validation ===")
        for item in formatted:
            result = canary_validate(item)
            verdict = result["verdict"]
            emoji = "PASS" if "PASS" in verdict else "FAIL"
            print(f"  {item['item_id']}: {emoji} — model answered: {result['answer']}")
            time.sleep(1)  # Rate limiting

    print(f"\nDone. {len(formatted)} items saved to {batch_path}")
    print(f"Next steps: review items, canary-validate, then merge into candidate JSON")


if __name__ == "__main__":
    main()
