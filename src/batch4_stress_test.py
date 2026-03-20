#!/usr/bin/env python3
"""Batch 4 Stress Test — single file version for small batch (25 items)"""
import json, os, sys, time, re
import anthropic
import google.genai as genai

ITEMS_FILE = "/home/user/workspace/batch4_items.json"
SONNET_PROGRESS = "/home/user/workspace/batch4_sonnet_progress.json"
ESCALATION_PROGRESS = "/home/user/workspace/batch4_escalation_progress.json"
SONNET_MODEL = "claude-sonnet-4-20250514"
FLASH_MODEL = "gemini-2.5-flash"

anthropic_client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
gemini_client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

PROMPT = """You are completing a metacognition evaluation task.

Task: Confidence Calibration
Question:
{question}

Instructions:
1. Provide your best answer.
2. Provide a confidence score from 0.0 to 1.0.
3. Explain why you are or are not certain.
4. Say whether you would verify this if possible.

Return valid structured output with keys: answer, confidence, reason_for_uncertainty, would_verify_if_possible"""

REFUSAL_PATTERNS = ["i don't know","i do not know","i cannot determine","i'm not sure","i am not sure","cannot answer","unable to determine","not enough information","insufficient information","i would need to","i cannot provide","i'm unable to","n/a","not applicable"]

def parse_response(text):
    if not text: return {"answer": None, "confidence": None, "parse_error": True}
    data = None
    for pattern in [lambda t: json.loads(t), lambda t: json.loads(re.search(r'```(?:json)?\s*(\{.*?\})\s*```', t, re.DOTALL).group(1)), lambda t: json.loads(re.search(r'\{[^{}]*"answer"[^{}]*\}', t, re.DOTALL).group(0)), lambda t: json.loads(re.search(r'\{.*\}', t, re.DOTALL).group(0))]:
        try: data = pattern(text); break
        except: pass
    if data is None: return {"answer": None, "confidence": None, "parse_error": True, "raw": text[:500]}
    a = data.get("answer"); c = data.get("confidence")
    if c is not None:
        try: c = max(0.0, min(1.0, float(c)))
        except: c = None
    return {"answer": str(a).strip().lower() if a else None, "confidence": c, "parse_error": False}

def detect_refusal(p):
    a = p.get("answer")
    if a is None or a == "" or a == "none": return True
    for pat in REFUSAL_PATTERNS:
        if pat in (a or "").lower(): return True
    if p.get("parse_error"): return True
    return False

def adjudicate(ma, ga, aliases, rule):
    if ma is None: return False
    mn, gn = str(ma).strip().lower(), str(ga).strip().lower()
    if mn == gn: return True
    for alias in (aliases or []):
        if mn == str(alias).strip().lower(): return True
    if rule == "yes_no":
        yes, no = {"yes","y","true"}, {"no","n","false"}
        if (mn in yes and gn in yes) or (mn in no and gn in no): return True
    if rule == "alias":
        if gn in mn or mn in gn: return True
        for alias in (aliases or []):
            al = str(alias).strip().lower()
            if al in mn or mn in al: return True
    return False

def classify(correct, conf):
    if conf is None: conf = 0.5
    if not correct:
        if conf >= 0.75: return 1, "STRONG_ACCEPT"
        elif conf >= 0.50: return 2, "ACCEPT"
        else: return 3, "CONDITIONAL_ACCEPT"
    else:
        if conf < 0.70: return 4, "CONDITIONAL_ACCEPT"
        elif conf < 0.85: return 5, "BORDERLINE"
        else: return 6, "SOFT_REJECT"

def call_sonnet(q):
    for attempt in range(3):
        try:
            msg = anthropic_client.messages.create(model=SONNET_MODEL, max_tokens=1024, messages=[{"role":"user","content":PROMPT.format(question=q)}])
            return msg.content[0].text
        except anthropic.RateLimitError: time.sleep(30*(attempt+1))
        except Exception as e: print(f"    Sonnet err: {e}"); time.sleep(5) if attempt < 2 else None
    return None

def call_flash(q):
    for attempt in range(3):
        try:
            resp = gemini_client.models.generate_content(model=FLASH_MODEL, contents=PROMPT.format(question=q))
            return resp.text
        except Exception as e:
            if "429" in str(e): time.sleep(30*(attempt+1))
            elif attempt < 2: time.sleep(5)
    return None

def load_json(p):
    try:
        with open(p) as f: return json.load(f)
    except: return {}

def save_json(d, p):
    with open(p, "w") as f: json.dump(d, f, indent=2)

def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "sonnet"
    with open(ITEMS_FILE) as f: items = json.load(f)
    print(f"Batch 4 items: {len(items)}")

    if mode == "sonnet":
        progress = load_json(SONNET_PROGRESS)
        remaining = [i for i in items if i["item_id"] not in progress]
        print(f"Sonnet: {len(progress)} done, {len(remaining)} remaining")
        for i, item in enumerate(remaining):
            iid = item["item_id"]
            print(f"[{len(progress)+i+1}/{len(items)}] {iid} ({item['mechanism_primary']})...")
            raw = call_sonnet(item["question"])
            p = parse_response(raw)
            if detect_refusal(p):
                progress[iid] = {"item_id": iid, "mechanism_primary": item["mechanism_primary"], "stress_answer": p.get("answer"), "stress_confidence": 0.0, "stress_correct": False, "tier": 0, "classification": "REFUSAL", "brier_score": 0.0}
                print(f"  → REFUSAL")
            else:
                a, c = p["answer"], p["confidence"] or 0.5
                correct = adjudicate(a, item["gold_answer"], item.get("aliases",[]), item.get("rule","alias"))
                brier = round((c - (1 if correct else 0))**2, 4)
                tier, cls = classify(correct, c)
                progress[iid] = {"item_id": iid, "mechanism_primary": item["mechanism_primary"], "stress_answer": a, "stress_confidence": c, "stress_correct": correct, "tier": tier, "classification": cls, "brier_score": brier}
                icon = "✓" if correct else "✗"
                print(f"  → {icon} ans={a!r} conf={c:.2f} gold={item['gold_answer']!r} | T{tier} ({cls})")
            time.sleep(0.3)
        save_json(progress, SONNET_PROGRESS)
        from collections import Counter
        tiers = Counter(r["tier"] for r in progress.values())
        print(f"\nSonnet complete: {len(progress)}/{len(items)}")
        for t in sorted(tiers): print(f"  Tier {t}: {tiers[t]}")

    elif mode == "escalate":
        sonnet = load_json(SONNET_PROGRESS)
        esc = load_json(ESCALATION_PROGRESS)
        t6 = sorted([iid for iid,r in sonnet.items() if r.get("tier")==6])
        remaining = [iid for iid in t6 if iid not in esc]
        items_by_id = {i["item_id"]:i for i in items}
        print(f"Escalation: {len(t6)} T6, {len(esc)} done, {len(remaining)} remaining")
        for i, iid in enumerate(remaining):
            item = items_by_id[iid]
            print(f"[{len(esc)+i+1}/{len(t6)}] {iid} ({item['mechanism_primary']})...")
            raw = call_flash(item["question"])
            p = parse_response(raw)
            if detect_refusal(p) or p.get("parse_error"):
                esc[iid] = {"item_id": iid, "flash_answer": None, "flash_confidence": 0.0, "flash_correct": False, "escalation_decision": "KEEP_BORDERLINE"}
                print(f"  → Flash REFUSAL → KEEP")
            else:
                a, c = p["answer"], p["confidence"] or 0.5
                correct = adjudicate(a, item["gold_answer"], item.get("aliases",[]), item.get("rule","alias"))
                if correct and c >= 0.85:
                    esc[iid] = {"item_id": iid, "flash_answer": a, "flash_confidence": c, "flash_correct": True, "escalation_decision": "REJECT"}
                    print(f"  → Flash ✓ conf={c:.2f} → REJECT")
                else:
                    esc[iid] = {"item_id": iid, "flash_answer": a, "flash_confidence": c, "flash_correct": correct, "escalation_decision": "KEEP_BORDERLINE"}
                    icon = "✓" if correct else "✗"
                    print(f"  → Flash {icon} conf={c:.2f} → KEEP")
            time.sleep(0.3)
        save_json(esc, ESCALATION_PROGRESS)
        reject = sum(1 for r in esc.values() if r["escalation_decision"]=="REJECT")
        keep = sum(1 for r in esc.values() if r["escalation_decision"]=="KEEP_BORDERLINE")
        print(f"\nEscalation complete: REJECT {reject}, KEEP {keep}")

if __name__ == "__main__":
    main()
