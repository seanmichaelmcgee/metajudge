#!/usr/bin/env python3
"""
Build the 4-model discrimination matrix from multimodel results + phase2 data.

Models: Sonnet (from phase2), Flash (from escalation), Gemini Pro, DeepSeek, Haiku
"""

import json
from pathlib import Path
from collections import defaultdict

PHASE2_FILE = "/home/user/workspace/phase2_final_results.json"
ESCALATION_FILE = "/home/user/workspace/escalation_progress.json"
MULTIMODEL_FILE = "/home/user/workspace/multimodel_results.json"
ITEMS_A = "/home/user/workspace/gen_agent_a_items.json"
ITEMS_B = "/home/user/workspace/gen_agent_b_items.json"
OUTPUT_JSON = "/home/user/workspace/discrimination_matrix.json"
OUTPUT_MD = "/home/user/workspace/discrimination_matrix.md"

# Load everything
with open(PHASE2_FILE) as f:
    phase2 = json.load(f)
with open(MULTIMODEL_FILE) as f:
    multimodel = json.load(f)

escalation = {}
if Path(ESCALATION_FILE).exists():
    with open(ESCALATION_FILE) as f:
        escalation = json.load(f)

items_by_id = {}
for fname in [ITEMS_A, ITEMS_B]:
    with open(fname) as f:
        for item in json.load(f):
            items_by_id[item["item_id"]] = item

# Get survivors
survivors = [r for r in phase2 if r["final_tier"] in (1, 2, 3, 4, 5)]

# Build matrix
MODELS = ["sonnet", "flash", "gemini_pro", "deepseek", "haiku"]
MODEL_LABELS = {
    "sonnet": "Claude Sonnet 4",
    "flash": "Gemini 2.5 Flash",
    "gemini_pro": "Gemini 2.5 Pro",
    "deepseek": "DeepSeek V3.1",
    "haiku": "Claude Haiku 4.5",
}

matrix = []
for r in survivors:
    iid = r["item_id"]
    item = items_by_id.get(iid, {})
    esc = escalation.get(iid, {})
    mm = multimodel.get(iid, {})

    row = {
        "item_id": iid,
        "mechanism": r.get("mechanism_primary", ""),
        "gold_answer": item.get("gold_answer", ""),
        "final_tier": r["final_tier"],
        "models": {}
    }

    # Sonnet (from phase2)
    row["models"]["sonnet"] = {
        "correct": r.get("sonnet_correct", False),
        "confidence": r.get("sonnet_confidence", 0),
        "answer": r.get("sonnet_answer", ""),
        "brier": r.get("brier_score", 0),
    }

    # Flash (from escalation if available, only for Tier 6 → promoted items)
    if esc:
        row["models"]["flash"] = {
            "correct": esc.get("flash_correct", False),
            "confidence": esc.get("flash_confidence", 0),
            "answer": esc.get("flash_answer", ""),
            "brier": round((esc.get("flash_confidence", 0) - (1 if esc.get("flash_correct") else 0)) ** 2, 4) if esc.get("flash_confidence") is not None else None,
        }

    # Gemini Pro, DeepSeek, Haiku from multimodel
    for mk in ["gemini_pro", "deepseek", "haiku"]:
        if mk in mm:
            row["models"][mk] = {
                "correct": mm[mk].get("correct", False),
                "confidence": mm[mk].get("confidence", 0),
                "answer": mm[mk].get("answer", ""),
                "brier": mm[mk].get("brier_score", 0),
            }

    # Compute discrimination score: how many models disagree
    model_results = []
    for mk in MODELS:
        if mk in row["models"]:
            model_results.append(row["models"][mk]["correct"])
    
    n_correct = sum(model_results)
    n_models = len(model_results)
    row["n_models_tested"] = n_models
    row["n_correct"] = n_correct
    row["n_wrong"] = n_models - n_correct
    row["discrimination_score"] = min(n_correct, n_models - n_correct) / max(n_models, 1)  # 0 = all agree, 0.5 = max disagreement

    matrix.append(row)

# Sort by discrimination score (highest = most discriminating)
matrix.sort(key=lambda x: (-x["discrimination_score"], x["final_tier"], x["item_id"]))

with open(OUTPUT_JSON, "w") as f:
    json.dump(matrix, f, indent=2)

# Build markdown report
md = []
md.append("# 4-Model Discrimination Matrix — Batch 1 Survivors")
md.append("")
md.append("## Model Accuracy Summary")
md.append("")

model_acc = defaultdict(lambda: {"correct": 0, "total": 0, "brier_sum": 0.0})
for row in matrix:
    for mk in MODELS:
        if mk in row["models"]:
            model_acc[mk]["total"] += 1
            if row["models"][mk]["correct"]:
                model_acc[mk]["correct"] += 1
            b = row["models"][mk].get("brier")
            if b is not None:
                model_acc[mk]["brier_sum"] += b

md.append("| Model | Correct | Total | Accuracy | Avg Brier |")
md.append("|:------|--------:|------:|---------:|----------:|")
for mk in MODELS:
    if model_acc[mk]["total"] > 0:
        acc = model_acc[mk]
        pct = 100 * acc["correct"] / acc["total"]
        avg_brier = acc["brier_sum"] / acc["total"]
        md.append(f"| {MODEL_LABELS[mk]} | {acc['correct']} | {acc['total']} | {pct:.1f}% | {avg_brier:.4f} |")

md.append("")

# Brier spread
brier_scores = {}
for mk in MODELS:
    if model_acc[mk]["total"] > 0:
        brier_scores[mk] = model_acc[mk]["brier_sum"] / model_acc[mk]["total"]
if brier_scores:
    brier_range = max(brier_scores.values()) - min(brier_scores.values())
    md.append(f"**Brier spread:** {brier_range:.4f} (target: ≥0.05)")
    md.append(f"**Best:** {MODEL_LABELS[min(brier_scores, key=brier_scores.get)]} ({min(brier_scores.values()):.4f})")
    md.append(f"**Worst:** {MODEL_LABELS[max(brier_scores, key=brier_scores.get)]} ({max(brier_scores.values()):.4f})")
    md.append("")

md.append("## Per-Item Discrimination Matrix")
md.append("")
md.append("| Item ID | Mechanism | Tier | Gold | Sonnet | Flash | Pro | DeepSeek | Haiku | Disc |")
md.append("|:--------|:----------|:----:|:-----|:------:|:-----:|:---:|:--------:|:-----:|:----:|")

for row in matrix:
    cells = [row["item_id"], row["mechanism"][:12], str(row["final_tier"]), str(row["gold_answer"])[:15]]
    for mk in MODELS:
        if mk in row["models"]:
            m = row["models"][mk]
            icon = "✓" if m["correct"] else "✗"
            cells.append(f"{icon} {m['confidence']:.2f}")
        else:
            cells.append("—")
    cells.append(f"{row['discrimination_score']:.2f}")
    md.append("| " + " | ".join(cells) + " |")

md.append("")

md.append("## Key Discrimination Items")
md.append("")
md.append("Items where models disagree most (discrimination score > 0):")
md.append("")

for row in matrix:
    if row["discrimination_score"] > 0:
        wrong_models = []
        right_models = []
        for mk in MODELS:
            if mk in row["models"]:
                if row["models"][mk]["correct"]:
                    right_models.append(MODEL_LABELS[mk])
                else:
                    wrong_models.append(MODEL_LABELS[mk])
        
        md.append(f"### {row['item_id']} ({row['mechanism']}, Tier {row['final_tier']})")
        md.append(f"- Gold: {row['gold_answer']}")
        md.append(f"- Correct ({len(right_models)}): {', '.join(right_models) if right_models else 'none'}")
        md.append(f"- Wrong ({len(wrong_models)}): {', '.join(wrong_models) if wrong_models else 'none'}")
        md.append("")

md.append("## Assessment")
md.append("")

# Count high-discrimination items
high_disc = sum(1 for r in matrix if r["discrimination_score"] >= 0.3)
any_disc = sum(1 for r in matrix if r["discrimination_score"] > 0)
md.append(f"- **Items with any model disagreement:** {any_disc}/{len(matrix)}")
md.append(f"- **Items with high discrimination (≥0.3):** {high_disc}/{len(matrix)}")
md.append(f"- **Items where ALL models correct:** {sum(1 for r in matrix if r['n_wrong'] == 0)}")
md.append(f"- **Items where ALL models wrong:** {sum(1 for r in matrix if r['n_correct'] == 0)}")
md.append("")

with open(OUTPUT_MD, "w") as f:
    f.write("\n".join(md))

print(f"Matrix saved to {OUTPUT_JSON}")
print(f"Report saved to {OUTPUT_MD}")
print(f"\nSummary:")
for mk in MODELS:
    if model_acc[mk]["total"] > 0:
        acc = model_acc[mk]
        print(f"  {MODEL_LABELS[mk]:20s}: {acc['correct']}/{acc['total']} ({100*acc['correct']/acc['total']:.1f}%)")
print(f"\nDiscrimination: {any_disc}/{len(matrix)} items show model disagreement")
if brier_scores:
    print(f"Brier spread: {brier_range:.4f}")
