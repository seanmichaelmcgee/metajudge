"""
FINAL canary round. Strategy:
- More clock angles (the 5:25 one worked)
- More palindrome gaps (the 15951 one worked)
- More multi-constraint probability (the coin one worked)
- Novel question types: complex word problems with subtle traps
"""

import json
import os
import re
import time
import urllib.request

API_KEY = os.environ["OPENROUTER_API_KEY"]
API_URL = "https://openrouter.ai/api/v1/chat/completions"


def query_model(question: str, max_tokens=400) -> dict:
    payload = json.dumps({
        "model": "deepseek/deepseek-chat",
        "messages": [
            {"role": "user", "content": f"{question}\n\nGive your answer concisely."}
        ],
        "max_tokens": max_tokens,
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


def check(model_text, aliases, expected_num=None, tolerance=0.5):
    """Better answer checker that handles LaTeX and various formats."""
    text = model_text.lower().strip()
    # Strip LaTeX formatting
    text_clean = re.sub(r'\\text\{([^}]*)\}', r'\1', text)
    text_clean = re.sub(r'\\[,;:\s]', ' ', text_clean)
    text_clean = re.sub(r'\\boxed\{([^}]*)\}', r'\1', text_clean)
    text_clean = text_clean.replace('{', '').replace('}', '')
    text_clean = text_clean.replace('\\', '')

    for alias in aliases:
        if alias.lower() in text_clean:
            return True
        if alias.lower() in text:
            return True

    if expected_num is not None:
        # Extract all numbers from the clean text
        numbers = re.findall(r'[\d.]+', text_clean)
        for n in numbers:
            try:
                val = float(n)
                if abs(val - expected_num) < tolerance:
                    return True
            except ValueError:
                pass
    return False


ITEMS = [
    # === Clock angles (the 5:25 approach worked) ===
    {
        "item_id": "f01",
        "question": "A standard analog clock reads 10:10. What is the exact angle in degrees between the hour hand and the minute hand? Give a single number.",
        "correct_answer": "115",
        "num": 115,
        "aliases": ["115"],
        "weakness": "clock_angle",
        "explanation": "Min hand: 10×6=60°. Hour hand: 10×30+10×0.5=300+5=305°. |305-60|=245°. Smaller=360-245=115°.",
    },
    {
        "item_id": "f02",
        "question": "A standard analog clock reads 3:40. What is the exact angle in degrees between the hour hand and the minute hand? Give a single number.",
        "correct_answer": "130",
        "num": 130,
        "aliases": ["130"],
        "weakness": "clock_angle",
        "explanation": "Min hand: 40×6=240°. Hour hand: 3×30+40×0.5=90+20=110°. |240-110|=130°.",
    },
    {
        "item_id": "f03",
        "question": "A standard analog clock reads 12:25. What is the exact angle in degrees between the hour hand and the minute hand? Give a single number.",
        "correct_answer": "137.5",
        "num": 137.5,
        "aliases": ["137.5"],
        "weakness": "clock_angle",
        "explanation": "Min hand: 25×6=150°. Hour hand: 0×30+25×0.5=12.5°. |150-12.5|=137.5°.",
    },
    {
        "item_id": "f04",
        "question": "A standard analog clock reads 4:50. What is the exact angle in degrees between the hour hand and the minute hand? Give a single number.",
        "correct_answer": "155",
        "num": 155,
        "aliases": ["155"],
        "weakness": "clock_angle",
        "explanation": "Min hand: 50×6=300°. Hour hand: 4×30+50×0.5=120+25=145°. |300-145|=155°.",
    },

    # === Palindrome gaps ===
    {
        "item_id": "f05",
        "question": "An odometer reads 16961 miles, which is a palindrome. What is the minimum number of additional miles until the odometer shows the next palindrome?",
        "correct_answer": "110",
        "num": 110,
        "aliases": ["110"],
        "weakness": "palindrome_gap",
        "explanation": "16961: a=1,b=6,c=9. c=9 is maxed. Next: increment b=6→7, c=0. 17071. 17071-16961=110.",
    },
    {
        "item_id": "f06",
        "question": "An odometer reads 23932 miles, which is a palindrome. What is the minimum number of additional miles until the odometer shows the next palindrome?",
        "correct_answer": "110",
        "num": 110,
        "aliases": ["110"],
        "weakness": "palindrome_gap",
        "explanation": "23932: a=2,b=3,c=9. c maxed. Next: b=4,c=0 → 24042. 24042-23932=110.",
    },
    {
        "item_id": "f07",
        "question": "An odometer reads 79897 miles, which is a palindrome. What is the minimum number of additional miles until the odometer shows the next palindrome?",
        "correct_answer": "110",
        "num": 110,
        "aliases": ["110"],
        "weakness": "palindrome_gap_carry_hard",
        "explanation": "79897: a=7,b=9,c=8. Next: c=9→79997. 79997-79897=100. Wait - is 79997 a palindrome? 7-9-9-9-7. Yes! So it's 100, not 110. Hmm. But 79997+?→next? After 79997, c=9 again, maxed. b=9 also maxed. So need a=8: 80008. Let me recheck whether I should use this one. Starting palindrome is 79897, next is 79997 (100 away), not 110.",
        "SKIP": True,
    },
    {
        "item_id": "f07",
        "question": "An odometer reads 45954 miles, which is a palindrome. What is the minimum number of additional miles until the odometer shows the next palindrome?",
        "correct_answer": "110",
        "num": 110,
        "aliases": ["110"],
        "weakness": "palindrome_gap",
        "explanation": "45954: a=4,b=5,c=9. c=9 maxed. Next: b=6,c=0→46064. 46064-45954=110.",
    },

    # === Multi-constraint probability ===
    {
        "item_id": "f08",
        "question": "You roll a fair die 3 times. What is the probability of getting exactly 2 sixes, with the two sixes being on consecutive rolls (i.e., rolls 1&2, or rolls 2&3, but not rolls 1&3)? Express as a simplified fraction.",
        "correct_answer": "5/108",
        "num": 0.0463,
        "aliases": ["5/108"],
        "weakness": "constrained_dice_probability",
        "explanation": "Total: 6^3=216. Cases with exactly 2 sixes, consecutive: 66X (X≠6): 5 outcomes. X66 (X≠6): 5 outcomes. But 666 has 3 sixes not 2. What about 6-6-X and X-6-6 overlap? 666 would be in both, but we need exactly 2 sixes. So: 66X where X≠6: 5 cases. X66 where X≠6: 5 cases. Total=10. P=10/216=5/108.",
    },
    {
        "item_id": "f09",
        "question": "You flip a fair coin 5 times. What is the probability of getting exactly 3 heads AND having all 3 heads appear consecutively? Express as a simplified fraction.",
        "correct_answer": "3/32",
        "num": 0.09375,
        "aliases": ["3/32"],
        "weakness": "constrained_coin_probability",
        "explanation": "Total: 2^5=32. Need exactly 3 heads, all consecutive: HHHTT, THHHT, TTHHH. 3 sequences. P=3/32.",
    },
    {
        "item_id": "f10",
        "question": "A fair coin is flipped 6 times. What is the probability that there are exactly 3 heads AND no two heads are adjacent? Express as a simplified fraction.",
        "correct_answer": "1/16",
        "num": 0.0625,
        "aliases": ["1/16", "4/64"],
        "weakness": "non_adjacent_constraint_probability",
        "explanation": "Total: 2^6=64. Exactly 3 heads, no two adjacent. Place 3 Hs among 6 positions with no adjacency. Equivalently, choose 3 from 4 'slots' created by 3 tails (think of it as placing H in gaps around T). Number of ways: C(4,3)=4. P=4/64=1/16. Let me verify by enumeration: HTHTTH, HTTHTH, HTTHT? Wait, 6 flips. Let me list: positions 1-6. H at non-adjacent positions among {1,2,3,4,5,6}, exactly 3 of them. Possible sets: {1,3,5}, {1,3,6}, {1,4,6}, {2,4,6}. That's 4 arrangements. 4/64=1/16.",
    },
    {
        "item_id": "f11",
        "question": "How many 3-digit numbers have exactly two digits that are the same? (For example, 112, 343, 988 count, but 111, 222, 123 do not.)",
        "correct_answer": "243",
        "num": 243,
        "aliases": ["243"],
        "weakness": "digit_counting_with_constraint",
        "explanation": "3-digit numbers from 100-999. Exactly 2 digits same means a pair and one different. Choose which digit repeats: 0-9 (10 options). Choose which digit is different: 9 options. Choose which position has the different digit: 3. Total=10×9×3=270. BUT subtract cases where leading digit is 0. If repeated digit is 0 and different digit is in position 1: 9 options for different × 1 (positions 2,3 have 0). That's 9 cases. If different digit is 0 and repeated digit is in positions with one at position 1: repeated can be 1-9 (nonzero since position 1), positions 1&2 or 1&3 have repeated. But wait, 'different digit is 0' and repeated digit at positions 1&2: number=XX0, that's fine. Repeated at 1&3: X0X, fine. Repeated at 2&3: 0XX, leading 0, invalid. So subtract cases: repeated digit non-zero, different digit=0, different at position 1: number is 0YY. Invalid leading zero. Different digit at pos 1 means pos 1 is different. If different digit = 0 and position 1, that's 0XX. So 9 cases (repeated digit 1-9). Total invalid from repeated=non-zero, different=0, diff at pos1: 9. But if repeated=0, different at pos1: number is D00 where D≠0. Valid. Repeated=0, different at pos2: 0D0, invalid (leading 0). Repeated=0, different at pos3: 00D, invalid. So subtract 2 more for repeated=0 cases where different is NOT in position 1. Wait, I'm overcomplicating this. Let me just compute directly. Total with exactly 2 same digits (allowing any first digit, no leading 0): case AAB where A≠B. Pick A (the repeated digit): 10 choices. Pick B (different): 9 choices. Pick which position B is in: 3. Total = 270. Subtract invalid (leading 0): B=0 in pos1 but A≠0: not a problem (number=0AA is invalid... wait, if B is in position 1 and B=0, invalid. But also if A=0 and B is NOT in position 1, the number could be like 0B0 if A is in positions 1 and 3. Hmm, this is just: count numbers with leading zero. A number has leading zero if position 1 is 0. That happens when: (a) A=0 and B is in position 1 (B≠0), both positions 2,3 are 0: count = 9 (B=1-9). (b) A≠0 and B=0 and position 1 has B: not this, because B is in position 1 and B=0, so leading 0. Count = 9 (A=1-9). Hmm wait: also (c) A=0 and B is in position 2 or 3: number = 0-something, 0 in position 1. If A=0, A is in 2 of the 3 positions. If B is in position 2 or 3, then A=0 is in the remaining 2 positions including position 1. So position 1 is 0 → leading zero. Count = 9 options for B × 2 positions = 18 but B goes from 1-9, so 9 × 2 = 18. Total subtract: case (a): already counted in (c). Hmm. Let me restructure. For A=0: B is nonzero (9 choices), B can be in position 1,2,3 (3 choices). If B is in position 1: number is B00, valid. If B in position 2: 0B0, invalid. If B in position 3: 00B, invalid. So subtract 9×2=18. For A≠0, B=0: A is 1-9 (9 choices), B in position 1: 0AA, invalid. B in position 2: A0A, valid. B in position 3: AA0, valid. So subtract 9 for B in position 1. Total subtract = 18+9 = 27. Answer = 270-27 = 243.",
    },
    {
        "item_id": "f12",
        "question": "A bus makes 4 stops. At each stop, it either picks up 1 passenger or drops off 1 passenger (not both). The bus starts empty and must end empty after the 4th stop. How many valid sequences of pickups and dropoffs are there? (The bus cannot have a negative number of passengers at any point.)",
        "correct_answer": "2",
        "num": 2,
        "aliases": ["2", "two"],
        "weakness": "constrained_sequence_counting",
        "explanation": "Must go 0→?→?→?→0. Each step ±1. Start at 0, end at 0 in 4 steps, never go negative. Sequences: PPDD (0→1→2→1→0), PDPD (0→1→0→1→0). PDDP: 0→1→0→-1→nope. DPPD: 0→-1→nope. DDPP: 0→-1→nope. DPDP: 0→-1→nope. So 2 valid sequences.",
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

        resp = query_model(item["question"], max_tokens=600)
        if resp["error"]:
            print(f"ERROR: {resp['error']}")
            results.append({"item_id": item["item_id"], "verdict": "api_error", "error": resp["error"]})
            continue

        model_answer = resp["content"].strip()
        print(f"Model: {model_answer[:300]}")

        got_right = check(model_answer, item["aliases"], item.get("num"))
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
        print(f"  ACCEPT: {r['item_id']} ({r.get('weakness','')}) model={r.get('model_answer','')[:100]}")
    for r in rejected:
        print(f"  REJECT: {r['item_id']} ({r.get('weakness','')})")

    with open("/tmp/canary_results_final.json", "w") as f:
        json.dump({"results": results}, f, indent=2)


if __name__ == "__main__":
    main()
