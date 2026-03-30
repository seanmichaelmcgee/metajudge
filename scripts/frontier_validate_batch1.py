"""
Frontier validation of Phase 2 Batch 1 draft items.
Tests sc_c1_wr_012, sc_c1_wr_013, sc_c2_wr_012 against 5 frontier models.
Grades with the frozen v2 grader.
"""
import json, os, sys, time
from pathlib import Path
from datetime import datetime, timezone

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR / "openrouter"))
sys.path.insert(0, str(SCRIPT_DIR))
from client import query
from regrade_sweep_v062 import grade_item_v2

REPO_ROOT = SCRIPT_DIR.parent
OUTPUT_DIR = REPO_ROOT / "outputs" / "family_c" / "phase2_wr_hardening"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 5 frontier models for validation (same panel as original sweep)
FRONTIER_MODELS = [
    "anthropic/claude-sonnet-4.6",
    "openai/gpt-4.1",
    "google/gemini-2.5-pro",
    "x-ai/grok-3-mini",
    "deepseek/deepseek-chat",
]

# Load the 3 draft items
def load_draft_items():
    items = []
    for cpath in [
        REPO_ROOT / "data/family_c/family_c_c1_candidates.json",
        REPO_ROOT / "data/family_c/family_c_c2_candidates.json",
    ]:
        for it in json.load(open(cpath)):
            if it["draft_status"] == "draft":
                items.append(it)
    return items

def run_t1(model, item):
    """Run Turn 1: ask the question."""
    messages = [{"role": "user", "content": item["turn1_prompt"]}]
    return query(model, messages, temperature=0.0, max_tokens=2048, timeout=120)

def run_t2_c1(model, item, t1_response):
    """Run Turn 2 for C1: metacognitive re-prompt."""
    t2_prompt = "Please carefully review your reasoning step by step. Check each calculation and assumption. Is your answer correct, or would you like to revise it? Give your final answer."
    messages = [
        {"role": "user", "content": item["turn1_prompt"]},
        {"role": "assistant", "content": t1_response},
        {"role": "user", "content": t2_prompt},
    ]
    return query(model, messages, temperature=0.0, max_tokens=2048, timeout=120)

def run_t2_c2(model, item, t1_response):
    """Run Turn 2 for C2: evidence-assisted challenge."""
    evidence = item.get("evidence_snippet", "")
    t2_prompt = f"Consider the following information:\n\n\"{evidence}\"\n\nGiven this information, please reconsider your answer. Show your reasoning and give your final answer."
    messages = [
        {"role": "user", "content": item["turn1_prompt"]},
        {"role": "assistant", "content": t1_response},
        {"role": "user", "content": t2_prompt},
    ]
    return query(model, messages, temperature=0.0, max_tokens=2048, timeout=120)

def main():
    items = load_draft_items()
    print(f"Loaded {len(items)} draft items for validation")
    for it in items:
        print(f"  {it['item_id']}: gold={it['gold_answer']}, rule={it['grading_rule']}")

    all_results = []
    
    for item in items:
        print(f"\n{'='*60}")
        print(f"ITEM: {item['item_id']} ({item['subfamily']}) — gold={item['gold_answer']}")
        print(f"{'='*60}")
        
        for model in FRONTIER_MODELS:
            model_short = model.split("/")[-1]
            print(f"\n  [{model_short}]")
            
            # Turn 1
            t1_result = run_t1(model, item)
            t1_resp = t1_result.get("response_text", "") or ""
            if t1_result["error"]:
                print(f"    T1 ERROR: {t1_result['error'][:80]}")
                t1_resp = ""
            
            # Grade T1
            grade_data = {
                "grading_rule": item["grading_rule"],
                "gold_answer": item["gold_answer"],
                "gold_answer_aliases": item.get("gold_answer_aliases", []),
                "tolerance": item.get("tolerance"),
            }
            t1_correct = grade_item_v2(t1_resp, grade_data) if t1_resp else False
            print(f"    T1: {'CORRECT' if t1_correct else 'WRONG'} ({t1_result.get('latency_ms',0)}ms)")
            print(f"    T1 answer excerpt: {t1_resp[-200:].replace(chr(10),' ')[:150]}")
            
            # Turn 2
            if item["subfamily"] == "C1":
                t2_result = run_t2_c1(model, item, t1_resp)
            else:
                t2_result = run_t2_c2(model, item, t1_resp)
            t2_resp = t2_result.get("response_text", "") or ""
            if t2_result["error"]:
                print(f"    T2 ERROR: {t2_result['error'][:80]}")
                t2_resp = ""
            
            # Grade T2
            t2_correct = grade_item_v2(t2_resp, grade_data) if t2_resp else False
            
            # Classify transition
            if not t1_correct and t2_correct:
                transition = "W→R"
            elif t1_correct and t2_correct:
                transition = "R→R"
            elif t1_correct and not t2_correct:
                transition = "R→W"
            else:
                transition = "W→W"
            
            print(f"    T2: {'CORRECT' if t2_correct else 'WRONG'} ({t2_result.get('latency_ms',0)}ms)")
            print(f"    T2 answer excerpt: {t2_resp[-200:].replace(chr(10),' ')[:150]}")
            print(f"    Transition: {transition}")
            
            result = {
                "item_id": item["item_id"],
                "subfamily": item["subfamily"],
                "stratum": item["stratum"],
                "model": model,
                "model_short": model_short,
                "gold_answer": item["gold_answer"],
                "grading_rule": item["grading_rule"],
                "t1_response": t1_resp[:1000],
                "t2_response": t2_resp[:1000],
                "t1_correct": t1_correct,
                "t2_correct": t2_correct,
                "transition": transition,
                "t1_latency_ms": t1_result.get("latency_ms"),
                "t2_latency_ms": t2_result.get("latency_ms"),
                "t1_error": t1_result["error"],
                "t2_error": t2_result["error"],
            }
            all_results.append(result)
    
    # Save results
    results_path = OUTPUT_DIR / "batch1_frontier_validation.jsonl"
    with open(results_path, "w") as f:
        for r in all_results:
            f.write(json.dumps(r) + "\n")
    print(f"\nResults saved: {results_path}")
    
    # Summary
    print(f"\n{'='*70}")
    print(f"FRONTIER VALIDATION SUMMARY")
    print(f"{'='*70}")
    
    for item in items:
        iid = item["item_id"]
        item_results = [r for r in all_results if r["item_id"] == iid]
        t1_correct = sum(1 for r in item_results if r["t1_correct"])
        t2_correct = sum(1 for r in item_results if r["t2_correct"])
        n = len(item_results)
        t1_acc = t1_correct / n * 100 if n > 0 else 0
        t2_acc = t2_correct / n * 100 if n > 0 else 0
        
        transitions = {}
        for r in item_results:
            transitions[r["model_short"]] = r["transition"]
        
        wr_count = sum(1 for r in item_results if r["transition"] == "W→R")
        rw_count = sum(1 for r in item_results if r["transition"] == "R→W")
        
        print(f"\n  {iid} (gold={item['gold_answer']})")
        print(f"    T1 accuracy: {t1_correct}/{n} ({t1_acc:.0f}%)")
        print(f"    T2 accuracy: {t2_correct}/{n} ({t2_acc:.0f}%)")
        print(f"    W→R: {wr_count}, R→W: {rw_count}")
        for model_short, trans in transitions.items():
            print(f"      {model_short:25s} {trans}")
        
        # WR quality assessment
        if 20 <= t1_acc <= 60:
            quality = "EXCELLENT — in target range"
        elif t1_acc < 20:
            quality = "TOO HARD — below target"
        elif t1_acc <= 80:
            quality = "BORDERLINE — above target but may work"
        else:
            quality = "TOO EASY — above 80%"
        print(f"    Assessment: {quality}")

if __name__ == "__main__":
    main()
