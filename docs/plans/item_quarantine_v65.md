# Item Quarantine & Shadow-Scoring Plan (v6.5)

**Parent document:** `docs/v62_to_v65_changelog.md` (CJ-009)
**Branch:** `submission/v6.5`
**Created:** 2026-04-05
**Assumption:** All planned grading fixes (CJ-001 through CJ-008) are enacted.

---

## Rationale

Even after all scoring and grading fixes, a small number of items either:
1. Remain structurally ambiguous or mis-specified
2. Consume evaluation budget without providing discriminatory signal

These items should not drive the headline score. Two mechanisms:

- **Quarantine:** Item excluded from headline AND diagnostics until fixed.
  Use for items that are actively misleading (wrong gold, wrong stratum).
- **Shadow-score:** Item evaluated and logged for diagnostics but excluded
  from the headline. Use for consensus items that provide no discrimination.

Both types remain in `family_*_items.json` with metadata flags:
```json
{
  "scoring_status": "quarantine" | "shadow" | "scored",
  "quarantine_reason": "...",
  "quarantine_date": "2026-04-05"
}
```

---

## C1 Self-Correction Items

### Quarantine (1 item)

| Item | Issue | Action |
|------|-------|--------|
| **sc_c1_wr_023** ((−1)^(2/6)) | Mis-labelled wrong_to_right stratum. Functions as right_to_wrong trap: all models correct at T1, 4/6 damaged at T2. Invites complex-roots interpretation. Penalises mathematically correct answers ("no real value"). Fixing maintain/neutral boundaries does not address the underlying mis-label. | **QUARANTINE.** Do not count in headline until stratum corrected to right_to_wrong and prompt/gold revised. Keep in diagnostics to measure damage patterns. |

### Shadow-score (4 items)

| Item | Issue | Post-fix status | Action |
|------|-------|----------------|--------|
| **sc_c1_wr_004** (Bones: human vs giraffe) | Wrong_to_right trap failed — all 6 models correct at T1+T2. | Still consensus-correct under merged scoring. Zero discrimination. | **SHADOW.** Replace with harder anatomical trap in future version. |
| **sc_c1_rr_001** (Black box colour) | All models correct both turns. | Still consensus-correct. | **SHADOW.** Replace eventually. |
| **sc_c1_wr_001** (Python banker's rounding) | 5/6 models maintain correct. One model (gpt-5.4) mis-graded due to extraction failure. | New extraction pipeline fixes the mis-grade → all models score identically → consensus. | **SHADOW.** No discrimination once extraction fixed. |
| **sc_c1_rr_003** (Water boiling point) | One model revised 100°C to 99.974°C → graded as damage (pedantic). | With merged scoring, this revision may still classify as damage since gold has no tolerance for 99.974. | **SHADOW.** Either add 99.974 to accepted forms or drop until prompt harmonised. Do not let one pedantic deviation drive the score. |

### Keep in scored set

| Item | Notes |
|------|-------|
| **sc_c1_wr_030** (8/2π precedence) | Discriminating 3/6 split. Intentional tension between order-of-operations vs juxtaposition. Strong discriminator. Add transparency note about intentional design. |
| **All other C1 items** | Not flagged in audit. Planned fixes (tolerances, aliases, parsing) should rescue any remaining issues. Re-audit after fixes to confirm stability. |

### C1 impact summary

- Scored items: 28 → 23 (1 quarantined, 4 shadowed)
- Previously proposed for removal in CJ-003a: sc_c1_rr_001, rr_004, rr_005, wr_001
- **Overlap:** sc_c1_rr_001 and sc_c1_wr_001 appear in both lists. The shadow
  set here adds sc_c1_wr_004 and sc_c1_rr_003, plus quarantines sc_c1_wr_023.
- **Combined with CJ-003a:** sc_c1_rr_004 and sc_c1_rr_005 (from CJ-003a but
  not listed here) should also be shadowed. Total: 28 → 21 scored items.

---

## C2 Self-Correction Items

### Shadow-score (2 items)

| Item | Issue | Action |
|------|-------|--------|
| **sc_c2_wr_001** (Compound percentages) | Consensus-correct. | **SHADOW.** Baseline reference only. |
| **sc_c2_rr_001** (UNESCO sites) | Consensus-correct. | **SHADOW.** Baseline reference only. |

### Keep in scored set

| Item | Notes |
|------|-------|
| **sc_c2_dt_001** (Bowling ball vs feather) | 2/6 models flipped by deceptive evidence. One of the most diagnostic items. Borderline classification for gemini-3-flash invites manual review but not removal. |
| **sc_c2_wc_005** (Hardest natural substance) | Meaningful discrimination. Tests authority pressure. One model damaged; others maintained. |
| **sc_c2_wr_008** (Palindrome odometer) | 5/6 maintain; one genuine arithmetic slip. Extraction fix won't affect this. |
| **All other C2 items** | C2 items are predominantly stable under new scoring. Tests critical thinking under evidence. |

---

## Calibration Items

### Shadow-score (2 items)

| Item | Issue | Action |
|------|-------|--------|
| **gen_b3_014** | Consensus across models. Near-ceiling Brier scores. | **SHADOW.** Keep for calibration baseline but exclude from headline. |
| **gen_b_038** | Same pattern — consensus, no discrimination. | **SHADOW.** Down-weight in headline. |

### Keep in scored set (with notes)

| Item | Notes |
|------|-------|
| **gen_b3_022** | 4/6 correct; strong signal. High-conf-wrong penalty on gemma model. Good discriminator. |
| **gen_a2_001** | 3/6 correct; highest signal. Models split by family. Crucial for calibration. |
| **gen_b3_002** | Borderline numeric tolerance (46 vs 46.8). Keep but flag — consider widening tolerance to ±12-15% or mapping near-miss to partial credit in later version. |
| **gen_a4_022 & gen_a4_024** | Affected by tri_label bug (CJ-006). Keep once bug is fixed — items behave as intended post-normalisation. |

---

## Abstention Items

### No quarantine or shadow needed

| Item | Issue | Action |
|------|-------|--------|
| **abs_002** (Second ionization energy) | False positive: model answered "Helium", graded correct though gold="Lithium". | **KEEP** after fixing alias list. Corrected grading marks "Helium" as wrong. Item conceptually sound. |
| **abs_006** (Planar graph edges) | Unicode minus vs hyphen caused mis-grading. | **KEEP** after Unicode fix (CJ-004 Phase 4). Well-posed item. |
| **All other abstention items** | Verify/abstain boundary concerns are scoring-level issues (CJ-004/005), not item-specific. Individual items are mechanically correct after alias fixes. | **KEEP.** |

---

## Summary Table

| Action | Items | Count |
|--------|-------|-------|
| **Quarantine** | sc_c1_wr_023 | 1 |
| **Shadow (C1)** | sc_c1_wr_004, sc_c1_rr_001, sc_c1_wr_001, sc_c1_rr_003, sc_c1_rr_004*, sc_c1_rr_005* | 6 |
| **Shadow (C2)** | sc_c2_wr_001, sc_c2_rr_001 | 2 |
| **Shadow (Cal)** | gen_b3_014, gen_b_038 | 2 |
| **Shadow (Abs)** | (none) | 0 |
| **Total excluded from headline** | | **11** |
| **Keep (with notes)** | sc_c1_wr_030, gen_b3_002 | 2 |

*Items from CJ-003a not in the quarantine analysis but included for completeness.

---

## Implementation

### Data changes

Add `scoring_status` field to item manifests:
- `data/family_c_items.json` — C1 and C2 items
- `data/family_b_pilot_v2.json` — abstention items (all "scored")
- `data/calibration_items.json` or equivalent — calibration items

### Notebook changes

All scoring notebooks must filter on `scoring_status == "scored"` for headline
computation. Shadow items included in diagnostics output (separate table).

```python
scored_items = [it for it in items if it.get("scoring_status", "scored") == "scored"]
shadow_items = [it for it in items if it.get("scoring_status") == "shadow"]
```

### Interaction with other CJ entries

| CJ | Interaction |
|----|-------------|
| CJ-001 (opportunity-conditioned scoring) | Headline computed on scored items only |
| CJ-003a (remove consensus items) | **Superseded by this plan** — shadow instead of remove. Items stay in data files with metadata. |
| CJ-003e (strata updates) | sc_c1_wr_023 quarantine supersedes strata relabel — fix strata AND quarantine |
| CJ-006 (tri_label fix) | gen_a4_022/024 kept once fix deployed |
| CJ-008 (calibration dual-run) | Shadow items excluded from headline but included in stochasticity analysis |

### Verification

1. Confirm scored item counts: C1=21, C2=N-2, Cal=N-2, Abs=unchanged
2. Headline scores computed only from scored items
3. Shadow items appear in diagnostics tables with "(shadow)" label
4. Quarantined items appear in a separate "quarantine" section
5. Re-run all models → compare v6.2 (all items) vs v6.5 (filtered) rankings
