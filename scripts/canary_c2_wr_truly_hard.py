"""
Canary TRULY HARD round.
Focus on problems where the model ACTUALLY gets wrong.
Known genuine failures so far:
1. Coin flip 4 times, P(exactly 2 heads AND consecutive) - model said 1/4, correct is 3/16
2. Clock 5:25 angle - model said 47.5, correct is 12.5
3. Palindrome after 15951 - model said 10, correct is 110

Pattern: The model fails when it needs to enumerate precisely and
check multiple constraints, OR when it makes an error in a multi-step
process that it doesn't verify.

NEW STRATEGY: Questions where the "obvious" enumeration misses a case
or includes an extra case, and where the answer is NOT a standard
result that the model has memorized.
"""

import json
import os
import re
import time
import urllib.request

API_KEY = os.environ["OPENROUTER_API_KEY"]
API_URL = "https://openrouter.ai/api/v1/chat/completions"


def query_model(question: str) -> dict:
    payload = json.dumps({
        "model": "deepseek/deepseek-chat",
        "messages": [
            {"role": "user", "content": f"{question}\n\nGive your answer concisely."}
        ],
        "max_tokens": 600,
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
        with urllib.request.urlopen(req, timeout=90) as resp:
            data = json.loads(resp.read().decode())
            return {"content": data["choices"][0]["message"]["content"], "error": None}
    except Exception as e:
        return {"content": "", "error": str(e)}


def smart_check(model_text, correct, aliases, num=None, tolerance=0.5):
    """Check if model answer matches, handling LaTeX notation."""
    text = model_text.lower()

    # Direct alias match
    for a in aliases:
        if a.lower() in text:
            return True

    # LaTeX fraction match: look for \frac{X}{Y} and check if X/Y matches
    frac_matches = re.findall(r'\\frac\{(\d+)\}\{(\d+)\}', model_text)
    for num_str, den_str in frac_matches:
        frac_val = f"{num_str}/{den_str}"
        if frac_val in [a for a in aliases]:
            return True

    # Boxed answer match
    boxed = re.findall(r'\\boxed\{([^}]+)\}', model_text)
    for b in boxed:
        b_clean = b.replace('\\,', '').replace(' ', '').replace('\\text{', '').replace('}', '').lower()
        for a in aliases:
            if a.lower() in b_clean or b_clean == a.lower():
                return True

    # Numeric match
    if num is not None:
        numbers = re.findall(r'[\d.]+', text)
        for n in numbers:
            try:
                val = float(n)
                if abs(val - num) < tolerance:
                    return True
            except ValueError:
                pass

    return False


ITEMS = [
    # Retest the non-adjacent heads problem that timed out
    {
        "item_id": "h01",
        "question": "A fair coin is flipped 6 times. What is the probability that there are exactly 3 heads AND no two heads are adjacent? Express as a simplified fraction.",
        "correct_answer": "1/16",
        "num": 0.0625,
        "aliases": ["1/16", "4/64"],
        "weakness": "non_adjacent_constraint",
        "explanation": "Valid arrangements: {1,3,5},{1,3,6},{1,4,6},{2,4,6} = 4 out of 64. P=1/16.",
    },
    # More multi-constraint counting problems
    {
        "item_id": "h02",
        "question": "How many 5-digit numbers (10000-99999) have their digits in strictly non-decreasing order (each digit is greater than or equal to the previous digit)? For example, 11234, 22579, 11111 count, but 21345 does not.",
        "correct_answer": "2002",
        "num": 2002,
        "aliases": ["2002", "2,002"],
        "weakness": "stars_and_bars_counting",
        "explanation": "Choose 5 digits from {1,...,9} with repetition in non-decreasing order (first digit can't be 0). This is C(9+5-1, 5) = C(13,5) = 1287. Wait, that allows 0. Since first digit > 0 and non-decreasing, all digits >= first digit >= 1. So choose 5 from {1,...,9} with repetition: C(9+5-1,5) = C(13,5) = 1287. Hmm, but I said 2002. Let me recalculate. C(13,5) = 13!/(5!8!) = (13×12×11×10×9)/(120) = 154440/120 = 1287. So 1287 not 2002. If digits can be 0-9 and non-decreasing with first ≥ 1: first digit 1-9, rest ≥ first digit. This is C(9+5-1,5) = C(13,5) = 1287. Or is it? Stars and bars: choosing 5 from {1,...,9} with replacement = C(9+4,5) = C(13,5) = 1287. If we include 0: choosing 5 from {0,...,9} with first ≥ 1 and non-decreasing. If all digits ≥ 1: 1287. Actually no, non-decreasing from {0,...,9} with first digit ≥ 1 means first digit ≥ 1 and all subsequent ≥ first ≥ 1. So effectively from {1,...,9}: C(9+4,5) = C(13,5) = 1287. My 2002 was wrong.",
        "SKIP": True,
    },
    {
        "item_id": "h02",
        "question": "You roll two fair 6-sided dice. What is the probability that one die shows exactly double the value of the other? Express as a simplified fraction.",
        "correct_answer": "1/6",
        "num": 0.1667,
        "aliases": ["1/6", "6/36"],
        "weakness": "dice_double_value",
        "explanation": "Pairs where one is double the other: (1,2),(2,1),(2,4),(4,2),(3,6),(6,3) = 6 pairs. P=6/36=1/6.",
    },
    {
        "item_id": "h03",
        "question": "You deal 3 cards from a standard 52-card deck. What is the probability that exactly 2 of the 3 cards are red (hearts or diamonds)? Express as a simplified fraction.",
        "correct_answer": "13/34",
        "num": 0.3824,
        "aliases": ["13/34"],
        "weakness": "card_probability_computation",
        "explanation": "C(26,2)×C(26,1)/C(52,3) = 325×26/22100 = 8450/22100 = 169/442 = 13/34.",
    },
    {
        "item_id": "h04",
        "question": "What is 2^15?",
        "correct_answer": "32768",
        "num": 32768,
        "aliases": ["32768", "32,768"],
        "weakness": "power_computation",
        "explanation": "2^10=1024, 2^15=1024×32=32768.",
    },
    {
        "item_id": "h05",
        "question": "A group of 8 friends sits around a circular table. How many distinct seating arrangements are there? (Two arrangements are the same if one is a rotation of the other.)",
        "correct_answer": "5040",
        "num": 5040,
        "aliases": ["5040", "5,040"],
        "weakness": "circular_permutation",
        "explanation": "(8-1)! = 7! = 5040.",
    },
    {
        "item_id": "h06",
        "question": "You have a string of 6 lights in a row. Each light is either ON or OFF. How many configurations have NO two adjacent lights both ON?",
        "correct_answer": "21",
        "num": 21,
        "aliases": ["21"],
        "weakness": "fibonacci_like_counting",
        "explanation": "Let f(n) = configs of n lights with no 2 adjacent ON. f(1)=2, f(2)=3, f(n)=f(n-1)+f(n-2). f(3)=5, f(4)=8, f(5)=13, f(6)=21.",
    },
    {
        "item_id": "h07",
        "question": "In the word BANANA, how many distinct 4-letter subsequences (not necessarily contiguous, preserving order) can be formed? Count each distinct string once.",
        "correct_answer": "7",
        "num": 7,
        "aliases": ["7", "seven"],
        "weakness": "subsequence_counting_with_repeats",
        "explanation": "BANANA = B,A,N,A,N,A. 4-letter subsequences preserving order. Distinct strings: BANA, BANN, BAAN, BANA (dup), BNAN, ANAN, ANNA, BANA, ... Let me enumerate carefully. Available letters at positions: B(1),A(2),N(3),A(4),N(5),A(6). Choose 4 positions. C(6,4)=15 subsequences, but many give same string. The distinct strings: Let me list position combinations and their strings. (1,2,3,4)=BANA, (1,2,3,5)=BANN, (1,2,3,6)=BANA, (1,2,4,5)=BAAN, (1,2,4,6)=BAAA, wait no: pos 4=A, pos 6=A: BAAA. Hmm, (1,2,4,6)=B,A,A,A=BAAA. (1,2,5,6)=B,A,N,A=BANA. (1,3,4,5)=B,N,A,N=BNAN. (1,3,4,6)=B,N,A,A=BNAA. (1,3,5,6)=B,N,N,A=BNNA. (1,4,5,6)=B,A,N,A=BANA. (2,3,4,5)=A,N,A,N=ANAN. (2,3,4,6)=A,N,A,A=ANAA. (2,3,5,6)=A,N,N,A=ANNA. (2,4,5,6)=A,A,N,A=AANA. (3,4,5,6)=N,A,N,A=NANA. Distinct: BANA, BANN, BAAN, BAAA, BNAN, BNAA, BNNA, ANAN, ANAA, ANNA, AANA, NANA = 12 distinct strings. Not 7. My count was wrong.",
        "SKIP": True,
    },
    {
        "item_id": "h07",
        "question": "How many ways can 8 people form 2 groups of 4? (The groups are unordered — swapping the two groups doesn't count as a different arrangement.)",
        "correct_answer": "35",
        "num": 35,
        "aliases": ["35"],
        "weakness": "unordered_group_partition",
        "explanation": "C(8,4)/2 = 70/2 = 35. Divide by 2 because the groups are unordered.",
    },
    {
        "item_id": "h08",
        "question": "What is 17^2 + 19^2?",
        "correct_answer": "650",
        "num": 650,
        "aliases": ["650"],
        "weakness": "mental_arithmetic",
        "explanation": "17^2=289, 19^2=361. 289+361=650.",
    },
    {
        "item_id": "h09",
        "question": "How many integers between 100 and 999 (inclusive) have all digits distinct AND the digits are in neither strictly increasing nor strictly decreasing order?",
        "correct_answer": "576",
        "num": 576,
        "aliases": ["576"],
        "weakness": "complement_counting_tricky",
        "explanation": "Total 3-digit numbers with distinct digits: 9×9×8=648. Strictly increasing: C(9,3)=84 (from {1,...,9}). Strictly decreasing: numbers like 987, 321. Choose 3 from {0,...,9}: C(10,3)=120. But leading digit can't be 0, and strictly decreasing means first > second > third, so first digit is the largest. If largest digit ≥ 1, that's all valid except... well first digit is the largest so it's ≥ 1 always (since we need 3 distinct digits and at least one is ≥ 1). Actually if digits are 0,1,2 in decreasing order: 210, that's fine. So all C(10,3)=120 work. Neither inc nor dec: 648 - 84 - 120 = 444. Hmm, not 576. Let me recheck. 9×9×8: first digit 1-9 (9), second digit 0-9 minus first (9), third 0-9 minus first two (8). 9×9×8=648. Increasing: choose 3 from {1,...,9} = C(9,3)=84. Decreasing: choose 3 from {0,...,9} = C(10,3)=120, all valid as 3-digit. 648-84-120=444. Not 576.",
        "SKIP": True,
    },
    {
        "item_id": "h09",
        "question": "You have 5 distinguishable books. In how many ways can you divide them into a group of 3 and a group of 2? (The two groups are distinguishable — 'Group A' and 'Group B'.)",
        "correct_answer": "10",
        "num": 10,
        "aliases": ["10", "ten"],
        "weakness": "simple_combination",
        "explanation": "C(5,3) = 10 (choose 3 for group A, rest go to group B).",
    },
    {
        "item_id": "h10",
        "question": "A bag contains 3 red, 3 blue, and 3 green marbles. You draw 2 marbles without replacement. What is the probability that they are different colors? Express as a simplified fraction.",
        "correct_answer": "3/4",
        "num": 0.75,
        "aliases": ["3/4", "0.75", "27/36"],
        "weakness": "complementary_probability",
        "explanation": "P(same color) = 3×C(3,2)/C(9,2) = 3×3/36 = 9/36 = 1/4. P(different) = 1-1/4 = 3/4.",
    },
    {
        "item_id": "h11",
        "question": "At a party, every pair of people either shakes hands or doesn't. If there are 6 people at the party and a total of 12 handshakes occurred, how many pairs of people did NOT shake hands?",
        "correct_answer": "3",
        "num": 3,
        "aliases": ["3", "three"],
        "weakness": "complement_pairs",
        "explanation": "Total pairs: C(6,2) = 15. Handshakes: 12. Non-handshakes: 15-12=3.",
    },
    {
        "item_id": "h12",
        "question": "A fair 6-sided die is rolled. If it shows 1 or 2, you flip a fair coin once. If it shows 3, 4, 5, or 6, you flip the coin twice. What is the probability of getting exactly one head total? Express as a simplified fraction.",
        "correct_answer": "1/2",
        "num": 0.5,
        "aliases": ["1/2", "0.5"],
        "weakness": "conditional_probability_branches",
        "explanation": "P(die 1-2)=1/3. P(1 head | 1 flip)=1/2. P(die 3-6)=2/3. P(1 head | 2 flips)=2/4=1/2. Total: (1/3)(1/2) + (2/3)(1/2) = 1/6 + 1/3 = 1/2.",
    },
]

ITEMS = [item for item in ITEMS if not item.get("SKIP", False)]


def main():
    results = []
    for item in ITEMS:
        print(f"\n{'='*60}")
        print(f"Testing: {item['item_id']}")
        print(f"Q: {item['question'][:120]}...")
        print(f"Correct: {item['correct_answer']}")

        resp = query_model(item["question"])
        if resp["error"]:
            print(f"ERROR: {resp['error']}")
            results.append({"item_id": item["item_id"], "verdict": "api_error", "error": resp["error"]})
            continue

        model_answer = resp["content"].strip()
        print(f"Model: {model_answer[:300]}")

        got_right = smart_check(model_answer, item["correct_answer"], item["aliases"], item.get("num"))
        verdict = "REJECT_too_easy" if got_right else "ACCEPT_model_wrong"
        print(f"Got right? {got_right} → {verdict}")

        results.append({
            "item_id": item["item_id"],
            "model_answer": model_answer,
            "correct_answer": item["correct_answer"],
            "model_got_wrong": not got_right,
            "verdict": verdict,
            "weakness": item["weakness"],
        })

        time.sleep(2)

    print(f"\n{'='*60}")
    print("SUMMARY")
    accepted = [r for r in results if r["verdict"] == "ACCEPT_model_wrong"]
    rejected = [r for r in results if r["verdict"] == "REJECT_too_easy"]
    errors = [r for r in results if r["verdict"] == "api_error"]
    print(f"Accepted: {len(accepted)}, Rejected: {len(rejected)}, Errors: {len(errors)}")
    for r in accepted:
        print(f"  ACCEPT: {r['item_id']} ({r.get('weakness','')})")
        print(f"    Model said: {r.get('model_answer','')[:100]}")
    for r in rejected:
        print(f"  REJECT: {r['item_id']} ({r.get('weakness','')})")

    with open("/tmp/canary_results_hard.json", "w") as f:
        json.dump({"results": results}, f, indent=2)


if __name__ == "__main__":
    main()
