"""
Canary validation for manually crafted C2 WR batch 1 items.
Tests each question against deepseek-chat to verify models get T1 wrong.
"""

import json
import os
import time
import urllib.request
import urllib.error

API_KEY = os.environ["OPENROUTER_API_KEY"]
API_URL = "https://openrouter.ai/api/v1/chat/completions"


def query_model(question: str) -> dict:
    """Send a question to deepseek-chat and return the response."""
    payload = json.dumps({
        "model": "deepseek/deepseek-chat",
        "messages": [
            {"role": "user", "content": f"{question}\n\nGive your answer concisely."}
        ],
        "max_tokens": 300,
        "temperature": 0.3,
    }).encode()

    req = urllib.request.Request(
        API_URL,
        data=payload,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode())
            return {
                "content": data["choices"][0]["message"]["content"],
                "error": None,
            }
    except Exception as e:
        return {"content": "", "error": str(e)}


# ---- The 6 hand-crafted C2 WR items ----

ITEMS = [
    {
        "item_id": "sc_c2_wr_006",
        "question": "A medical test for a rare disease has a sensitivity of 95% (true positive rate) and a specificity of 95% (true negative rate). If 1 in 500 people in the population actually has the disease, and a randomly selected person tests positive, what is the approximate probability that they actually have the disease? Give your answer as a percentage rounded to the nearest whole number.",
        "correct_answer": "4%",
        "correct_answer_numeric": 3.7,
        "correct_aliases": ["4%", "3.7%", "about 4%", "approximately 4%", "~4%", "3.8%"],
        "weakness": "base_rate_neglect",
        "explanation": "P(disease|positive) = (0.95 * 0.002) / (0.95*0.002 + 0.05*0.998) = 0.0019 / (0.0019 + 0.0499) = 0.0019/0.0518 ≈ 0.037 or ~4%. Models typically ignore the low base rate and answer ~95%.",
        "evidence_snippet": "In diagnostic testing, the positive predictive value depends heavily on the prevalence of the condition in the population being tested. When a condition is rare, even a highly accurate test produces many false positives relative to true positives. Consider applying Bayes' theorem: P(Disease|Positive) = P(Positive|Disease) × P(Disease) / P(Positive).",
        "evidence_source_type": "constructed",
    },
    {
        "item_id": "sc_c2_wr_007",
        "question": "A store has a sale: 40% off everything. After the sale ends, they raise all prices by 40%. Compared to the original price before any changes, a customer buying after the raise pays what percentage of the original price?",
        "correct_answer": "84%",
        "correct_answer_numeric": 84,
        "correct_aliases": ["84%", "84 percent", "0.84"],
        "weakness": "counterintuitive_percentage_asymmetry",
        "explanation": "If original price is $100: 40% off → $60. Then 40% increase on $60 → $60 × 1.40 = $84. So the customer pays 84% of the original. Models often say 100% (thinking the changes cancel out).",
        "evidence_snippet": "Percentage decreases and increases are not symmetric operations. A percentage decrease reduces the base, so a subsequent equal percentage increase operates on a smaller base. For example, reducing something by 50% and then increasing by 50% does not return to the original — it yields 75% of the original.",
        "evidence_source_type": "constructed",
    },
    {
        "item_id": "sc_c2_wr_008",
        "question": "January 1, 2024 was a Monday. What day of the week was March 1, 2024?",
        "correct_answer": "Friday",
        "correct_answer_numeric": None,
        "correct_aliases": ["Friday", "friday", "Fri"],
        "weakness": "temporal_calendar_reasoning",
        "explanation": "Jan has 31 days, Feb 2024 has 29 days (leap year). Jan 1 = Monday. Jan 1 to Mar 1 = 31 + 29 = 60 days. 60 mod 7 = 4 days after Monday = Friday. Models often forget 2024 is a leap year (29 days in Feb) or miscount.",
        "evidence_snippet": "When computing days between dates, be careful about leap years. A year is a leap year if it is divisible by 4, except for century years which must be divisible by 400. The year 2024 is divisible by 4 and is not a century year, so February 2024 has 29 days.",
        "evidence_source_type": "constructed",
    },
    {
        "item_id": "sc_c2_wr_009",
        "question": "You have a 10-liter container full of pure water. You remove 3 liters and replace them with pure alcohol. You mix thoroughly, then remove 3 liters of the mixture and replace with pure alcohol again. What fraction of the container is now water? Express as a simplified fraction.",
        "correct_answer": "49/100",
        "correct_answer_numeric": 0.49,
        "correct_aliases": ["49/100", "0.49", "49%"],
        "weakness": "serial_dilution_intuition",
        "explanation": "After first replacement: 7L water / 10L total = 70% water. Remove 3L of mixture: remove 3×0.7=2.1L water, leaving 4.9L water. Add 3L alcohol. Now 4.9/10 = 49/100 water. Models often incorrectly track the dilution steps.",
        "evidence_snippet": "In serial dilution problems, each removal step takes out a proportional amount of each component based on the current mixture ratio. After removing volume V from a total volume T that contains concentration C of a substance, the remaining amount of that substance is C × (1 - V/T). Applying this formula iteratively gives the correct result.",
        "evidence_source_type": "constructed",
    },
    {
        "item_id": "sc_c2_wr_010",
        "question": "A snail is climbing a 21-foot wall. Each day it climbs up 3 feet, but each night it slides back down 2 feet. On which day does the snail first reach the top of the wall?",
        "correct_answer": "19",
        "correct_answer_numeric": 19,
        "correct_aliases": ["19", "day 19", "19th day", "the 19th day"],
        "weakness": "boundary_condition_error",
        "explanation": "Each full day-night cycle nets +1 foot. After 18 cycles, the snail is at 18 feet. On day 19, it climbs 3 feet to reach 21 feet — it reaches the top during the day before sliding back. The answer is day 19, NOT day 21 (which ignores that the snail reaches the top mid-day).",
        "evidence_snippet": "In climbing problems with daily progress and nightly regression, the final day is special: once the climber reaches the top during the day, it stays there and does not slide back. This means you should check whether the climber can reach the goal on its daytime climb from its current position, before applying the nighttime regression.",
        "evidence_source_type": "constructed",
    },
    {
        "item_id": "sc_c2_wr_011",
        "question": "A restaurant bill is $85.00 before tax. Tax is 8%. You want to leave a 20% tip. If you calculate the tip on the pre-tax amount and then add both tax and tip to the bill, what is the total amount you pay? Round to the nearest cent.",
        "correct_answer": "$108.80",
        "correct_answer_numeric": 108.80,
        "correct_aliases": ["$108.80", "108.80", "$108.8", "108.8"],
        "weakness": "order_of_operations_real_world",
        "explanation": "Tax = 85 × 0.08 = $6.80. Tip = 85 × 0.20 = $17.00. Total = 85 + 6.80 + 17.00 = $108.80. Models may compute tip on the post-tax amount or make other calculation errors.",
        "evidence_snippet": "Tipping etiquette in many regions specifies that tips should be calculated on the pre-tax subtotal, not the post-tax total. When computing a final bill: first find the tax amount (subtotal × tax rate), then find the tip amount (subtotal × tip rate), then add all three: subtotal + tax + tip.",
        "evidence_source_type": "constructed",
    },
]


def main():
    results = []
    for item in ITEMS:
        print(f"\n{'='*60}")
        print(f"Testing: {item['item_id']}")
        print(f"Question: {item['question'][:100]}...")
        print(f"Correct: {item['correct_answer']}")
        print(f"Weakness: {item['weakness']}")

        resp = query_model(item["question"])
        if resp["error"]:
            print(f"ERROR: {resp['error']}")
            results.append({
                "item_id": item["item_id"],
                "model_answer": None,
                "correct_answer": item["correct_answer"],
                "model_got_wrong": None,
                "error": resp["error"],
                "verdict": "api_error",
            })
            continue

        model_answer = resp["content"].strip()
        print(f"Model answer: {model_answer}")

        # Check if model got it right
        answer_lower = model_answer.lower()
        correct_lower = item["correct_answer"].lower()
        aliases_lower = [a.lower() for a in item["correct_aliases"]]

        got_right = any(alias in answer_lower for alias in aliases_lower)

        # Also check for numeric match if applicable
        if item["correct_answer_numeric"] is not None and not got_right:
            import re
            numbers = re.findall(r'[\d.]+', answer_lower)
            for n in numbers:
                try:
                    val = float(n)
                    if abs(val - item["correct_answer_numeric"]) < 1.0:
                        got_right = True
                        break
                except ValueError:
                    pass

        verdict = "REJECT_too_easy" if got_right else "ACCEPT_model_wrong"
        print(f"Model got it right? {got_right}")
        print(f"Verdict: {verdict}")

        results.append({
            "item_id": item["item_id"],
            "model_answer": model_answer,
            "correct_answer": item["correct_answer"],
            "model_got_wrong": not got_right,
            "error": None,
            "verdict": verdict,
        })

        time.sleep(2)  # Rate limiting

    # Print summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    accepted = [r for r in results if r["verdict"] == "ACCEPT_model_wrong"]
    rejected = [r for r in results if r["verdict"] == "REJECT_too_easy"]
    errors = [r for r in results if r["verdict"] == "api_error"]
    print(f"Accepted (model wrong): {len(accepted)}")
    print(f"Rejected (too easy):    {len(rejected)}")
    print(f"Errors:                 {len(errors)}")

    # Save results
    output = {
        "validation_run": "c2_wr_batch1",
        "canary_model": "deepseek/deepseek-chat",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "results": results,
        "summary": {
            "total": len(results),
            "accepted": len(accepted),
            "rejected": len(rejected),
            "errors": len(errors),
        },
    }

    with open("/tmp/canary_results.json", "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to /tmp/canary_results.json")


if __name__ == "__main__":
    main()
