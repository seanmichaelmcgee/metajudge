#!/usr/bin/env python3
"""
MetaJudge V4 Phase 2 — Final Classification & Summary

Merges Sonnet stress test results with Flash escalation results.
Produces:
  1. phase2_final_results.json — all items with final tier/decision
  2. phase2_summary.md — human-readable summary with tier breakdown
"""

import json
from pathlib import Path
from collections import defaultdict

PROGRESS_FILE = "/home/user/workspace/phase2_progress.json"
ESCALATION_FILE = "/home/user/workspace/escalation_progress.json"
ITEMS_A = "/home/user/workspace/gen_agent_a_items.json"
ITEMS_B = "/home/user/workspace/gen_agent_b_items.json"
OUTPUT_JSON = "/home/user/workspace/phase2_final_results.json"
OUTPUT_MD = "/home/user/workspace/phase2_summary.md"

# Load everything
with open(PROGRESS_FILE) as f:
    sonnet_results = json.load(f)
with open(ESCALATION_FILE) as f:
    escalation_results = json.load(f)

items_by_id = {}
for fname in [ITEMS_A, ITEMS_B]:
    with open(fname) as f:
        for item in json.load(f):
            items_by_id[item["item_id"]] = item

# Build final results
final_results = []
for item_id, sonnet in sonnet_results.items():
    item = items_by_id.get(item_id, {})
    original_tier = sonnet["tier"]
    original_class = sonnet["classification"]

    # Determine final tier
    if original_tier == 6:
        # Check escalation
        esc = escalation_results.get(item_id)
        if esc and esc["escalation_decision"] == "REJECT":
            final_tier = -1
            final_class = "REJECTED"
            final_reason = "Both Sonnet and Flash correct with high confidence"
        else:
            # Promoted to Borderline
            final_tier = 5
            final_class = "BORDERLINE_PROMOTED"
            final_reason = f"Flash {'wrong' if not esc.get('flash_correct') else 'low confidence'}: discriminates models"
    else:
        final_tier = original_tier
        final_class = original_class
        final_reason = "Sonnet stress test result"

    entry = {
        "item_id": item_id,
        "mechanism_primary": sonnet.get("mechanism_primary", item.get("mechanism_primary", "")),
        "question": item.get("question", "")[:120],
        "gold_answer": item.get("gold_answer", ""),
        "sonnet_answer": sonnet.get("stress_answer"),
        "sonnet_confidence": sonnet.get("stress_confidence"),
        "sonnet_correct": sonnet.get("stress_correct"),
        "sonnet_tier": original_tier,
        "sonnet_class": original_class,
        "final_tier": final_tier,
        "final_class": final_class,
        "final_reason": final_reason,
        "brier_score": sonnet.get("brier_score"),
    }

    # Add Flash data if available
    esc = escalation_results.get(item_id)
    if esc:
        entry["flash_answer"] = esc.get("flash_answer")
        entry["flash_confidence"] = esc.get("flash_confidence")
        entry["flash_correct"] = esc.get("flash_correct")

    final_results.append(entry)

# Sort by final_tier (ascending = best items first), then by item_id
final_results.sort(key=lambda x: (x["final_tier"], x["item_id"]))

# Save JSON
with open(OUTPUT_JSON, "w") as f:
    json.dump(final_results, f, indent=2)

# Build summary markdown
tier_groups = defaultdict(list)
for r in final_results:
    tier_groups[r["final_tier"]].append(r)

mechanism_counts = defaultdict(lambda: defaultdict(int))
for r in final_results:
    mechanism_counts[r["mechanism_primary"]][r["final_tier"]] += 1

total = len(final_results)
accepted = [r for r in final_results if r["final_tier"] in (1, 2, 3, 4, 5)]
rejected = [r for r in final_results if r["final_tier"] == -1]

md = []
md.append("# MetaJudge V4 — Phase 2 Stress Test Summary")
md.append("")
md.append("## Executive Summary")
md.append("")
md.append(f"- **Total items generated:** {total}")
md.append(f"- **Primary model tested:** Claude Sonnet 4 (2025-05-14)")
md.append(f"- **Escalation model:** Gemini 2.5 Flash")
md.append(f"- **Items surviving (Tiers 1-5):** {len(accepted)} ({100*len(accepted)/total:.1f}%)")
md.append(f"- **Items rejected (both models ace):** {len(rejected)} ({100*len(rejected)/total:.1f}%)")
md.append(f"- **Yield rate:** {100*len(accepted)/total:.1f}%")
md.append("")

md.append("## Final Tier Distribution")
md.append("")
md.append("| Final Tier | Classification | Count | % |")
md.append("|:----------:|:---------------|------:|--:|")

tier_labels = {
    -1: "REJECTED (both models ace)",
    1: "STRONG_ACCEPT (wrong, conf≥0.75)",
    2: "ACCEPT (wrong, conf 0.50-0.74)",
    3: "CONDITIONAL_ACCEPT (wrong, conf<0.50)",
    4: "CONDITIONAL_ACCEPT (right, conf<0.70)",
    5: "BORDERLINE (right, conf 0.70-0.84 / promoted)",
}

for tier in [-1, 1, 2, 3, 4, 5]:
    items_in_tier = tier_groups.get(tier, [])
    count = len(items_in_tier)
    pct = 100 * count / total if total > 0 else 0
    label = tier_labels.get(tier, f"Tier {tier}")
    md.append(f"| {tier} | {label} | {count} | {pct:.1f}% |")

md.append("")

md.append("## High-Value Items (Tiers 1-3: Sonnet Got Wrong)")
md.append("")
md.append("These are the strongest benchmark items — Sonnet answered incorrectly.")
md.append("")
md.append("| Item ID | Mechanism | Gold Answer | Sonnet Answer | Sonnet Conf | Brier |")
md.append("|:--------|:----------|:------------|:--------------|:-----------:|------:|")

for r in final_results:
    if r["final_tier"] in (1, 2, 3):
        md.append(f"| {r['item_id']} | {r['mechanism_primary']} | {r['gold_answer']} | {r['sonnet_answer']} | {r['sonnet_confidence']:.2f} | {r['brier_score']:.4f} |")

md.append("")

md.append("## Borderline Items (Tier 4-5: Right but Uncertain / Flash Discriminates)")
md.append("")
md.append("| Item ID | Mechanism | Gold | Sonnet Conf | Flash Correct | Flash Conf | Source |")
md.append("|:--------|:----------|:-----|:-----------:|:-------------:|:----------:|:-------|")

for r in final_results:
    if r["final_tier"] in (4, 5):
        flash_correct = r.get("flash_correct", "N/A")
        flash_conf = r.get("flash_confidence", "N/A")
        flash_conf_str = f"{flash_conf:.2f}" if isinstance(flash_conf, (int, float)) else str(flash_conf)
        source = "Escalation promoted" if r.get("final_class") == "BORDERLINE_PROMOTED" else "Sonnet borderline"
        md.append(f"| {r['item_id']} | {r['mechanism_primary']} | {r['gold_answer']} | {r['sonnet_confidence']:.2f} | {flash_correct} | {flash_conf_str} | {source} |")

md.append("")

md.append("## Mechanism Breakdown")
md.append("")
md.append("| Mechanism | Total | Tier 1-3 | Tier 4-5 | Rejected | Yield % |")
md.append("|:----------|------:|---------:|---------:|---------:|--------:|")

all_mechs = sorted(mechanism_counts.keys())
for mech in all_mechs:
    counts = mechanism_counts[mech]
    t_total = sum(counts.values())
    t_13 = sum(counts.get(t, 0) for t in (1, 2, 3))
    t_45 = sum(counts.get(t, 0) for t in (4, 5))
    t_rej = counts.get(-1, 0)
    surviving = t_13 + t_45
    yield_pct = 100 * surviving / t_total if t_total > 0 else 0
    md.append(f"| {mech} | {t_total} | {t_13} | {t_45} | {t_rej} | {yield_pct:.0f}% |")

md.append("")

md.append("## Yield Assessment vs. Risk Thresholds")
md.append("")
total_surviving = len(accepted)
md.append(f"- **Current yield:** {total_surviving} items from {total} generated ({100*total_surviving/total:.1f}%)")
md.append(f"- **V1 baseline yield:** ~3.3% (3/91)")
md.append(f"- **V4 yield:** {100*total_surviving/total:.1f}%")
md.append(f"- **Risk assessment floor (§7):** 8 items minimum")
md.append(f"- **Status:** {'✓ ABOVE floor' if total_surviving >= 8 else '✗ BELOW floor — activate contingency'}")
md.append("")

if total_surviving < 15:
    md.append("### Contingency Recommendation")
    md.append("")
    md.append("Yield is modest. Recommended next steps from risk_assessment §7:")
    md.append("1. Run surviving items through DeepSeek-V3 and Gemini Pro for full model matrix")
    md.append("2. Items that discriminate (different results across models) are highest value")
    md.append("3. Consider expanding generation with harder mechanism variants")
    md.append("4. AmbiguityMetacognition and IOED mechanisms showed highest yield — double down")
    md.append("")

md.append("## Phase 2 Complete — Next Steps")
md.append("")
md.append("1. **Immediate:** Export Tier 1-5 items as candidate dataset items")
md.append("2. **Short-term:** Run full model matrix (DeepSeek, Gemini Pro, Haiku) on Tier 1-5 items")
md.append("3. **Medium-term:** Expand generation focusing on high-yield mechanisms")
md.append("4. **Integration:** Merge surviving items into metajudge dataset format")
md.append("")

with open(OUTPUT_MD, "w") as f:
    f.write("\n".join(md))

print(f"Final results saved to {OUTPUT_JSON}")
print(f"Summary saved to {OUTPUT_MD}")
print(f"\nTotal items: {total}")
print(f"Surviving (Tiers 1-5): {len(accepted)}")
print(f"Rejected: {len(rejected)}")
print(f"Yield: {100*len(accepted)/total:.1f}%")
print(f"\nTier breakdown:")
for tier in [-1, 1, 2, 3, 4, 5]:
    count = len(tier_groups.get(tier, []))
    print(f"  Tier {tier:>2}: {count}")
