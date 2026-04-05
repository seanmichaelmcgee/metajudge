# C1 Scoring Fixes — Detailed Implementation Plan (v6.5)

**Parent document:** `docs/v62_to_v65_changelog.md` (CJ-001, CJ-002, CJ-003)
**Branch:** `submission/v6.5`
**Source:** ChatGPT analysis + audit findings + stochasticity investigation
**Amended:** 2026-04-05 — v6.5 opportunity-conditioned scoring spec integrated

---

## Problem Summary

The C1 sub-family measures intrinsic self-correction (models detect and fix
mistakes without external evidence). Three interlocking problems undermine it:

1. **Scoring contract mismatch (CJ-001):** Production notebook uses accuracy
   delta; docs promise transition-weighted scoring. Up to 0.49 score difference.
2. **Classification boundary noise (CJ-002):** 53% of C1 flips are
   maintain_correct ↔ neutral_revision, driven by oversensitive `revised`
   detection. Currently harmless under delta scoring; would become harmful
   under transition scoring.
3. **Item quality (CJ-003):** Consensus-easy items, missing tolerances, narrow
   alias lists, parser failures.

**Critical sequencing constraint:** CJ-002 must be resolved before CJ-001.

**v6.5 scoring approach:** Instead of wiring up the existing transition-weighted
scoring (which would amplify maintain/neutral noise), v6.5 introduces a NEW
opportunity-conditioned headline that merges maintain_correct and neutral_revision
into a single "preserve_correct" bucket, sidestepping the boundary problem.

---

## Fix Package (7 items + unit tests)

### Fix 1 → CJ-002: Codify the maintain vs neutral_revision rule

**The single most important fix.** Still needed even though the new headline
merges the categories, because fine-grained transition labels remain in use
for diagnostics and submetrics.

**Current rule** (`metajudge/tasks/self_correction_v2.py:237`):
```python
revised = action == "revise" or answer_1.strip().lower() != answer_2.strip().lower()
```
Any lexical difference triggers `revised=True` → `neutral_revision`. Adding
"yes" or confirming the prior answer counts as a revision. This is too sensitive.

**Proposed rule:** Treat T2 as `neutral_revision` only if it materially changes
the underlying rationale or re-derives the answer. Simple affirmations (e.g.,
"Yes, 243 is correct") without additional reasoning → `maintain_correct`.

**Implementation (Option A — recommended):** Extract the core answer from both
T1 and T2 (numeric value, factual claim, true/false). If core answers match,
`revised=False` regardless of surrounding text. Only flag `revised` if the
extracted answer differs or the model explicitly states it is changing its answer.

Also adjust the item parser: if no explicit answer is extracted from T2 but the
model affirms the previous answer, treat T2 as maintaining T1's answer.

**Files to modify:**
- `metajudge/tasks/self_correction_v2.py` — `revised` detection logic
- `metajudge/scoring/self_correction_v2.py:91-123` — `classify_transition()`
  (no structural change needed if keeping 6 categories)

**Verification:** Re-classify all C1 items for all 7 dual-run models.
Target: <10% C1 flip rate (currently 14-43%). The 5 volatile items
(sc_c1_rr_010, dt_001, wr_023, wr_004, wr_011) should show reduced flips.

---

### Fix 2 → CJ-001: Implement opportunity-conditioned scoring (v6.5 headline)

**AMENDED from original plan.** Instead of keeping delta scoring and deferring,
v6.5 implements a new opportunity-conditioned headline that:
- Merges maintain_correct + neutral_revision into "preserve_correct" (eliminating
  the noisy boundary from the headline)
- Conditions rates on opportunity type (T1-right → preserve; T1-wrong → repair)
- Replaces both the delta approach and the transition-weighted approach

#### 2a. New functions in `self_correction_v2.py`

**Add alongside existing functions — do NOT remove or rename existing APIs.**

**Function 1: `coarse_transition_bucket(transition: str) -> str`**
```python
COARSE_MAP = {
    "maintain_correct":  "preserve_correct",
    "neutral_revision":  "preserve_correct",   # ← merged
    "correction_gain":   "repair",
    "damage":            "damage",
    "stubborn_wrong":    "nonrepair",
    "failed_revision":   "nonrepair",
}

def coarse_transition_bucket(transition: str) -> str:
    """Map fine-grained transition to coarse bucket."""
    if transition not in COARSE_MAP:
        raise ValueError(f"Unknown transition: {transition!r}")
    return COARSE_MAP[transition]
```

**Function 2: `compute_conditioned_rates(audit_rows, smoothing_alpha=0.5) -> dict`**
- Count items where T1 correct (`n_t1_right`) vs T1 wrong (`n_t1_wrong`)
- For T1-right items: count preserve_correct, damage → compute rates
- For T1-wrong items: count repair, nonrepair → compute rates
- Apply Laplace smoothing with `alpha` to avoid division by zero
- Return smoothed and unsmoothed rates + raw counts

```python
def compute_conditioned_rates(
    audit_rows: List[Dict[str, Any]],
    smoothing_alpha: float = 0.5,
) -> Dict[str, Any]:
    n_t1_right = sum(1 for r in audit_rows if r["correct_1"])
    n_t1_wrong = sum(1 for r in audit_rows if not r["correct_1"])

    preserve = sum(1 for r in audit_rows
                   if r["correct_1"] and r["coarse_transition"] == "preserve_correct")
    damage   = sum(1 for r in audit_rows
                   if r["correct_1"] and r["coarse_transition"] == "damage")
    repair   = sum(1 for r in audit_rows
                   if not r["correct_1"] and r["coarse_transition"] == "repair")
    nonrepair = sum(1 for r in audit_rows
                    if not r["correct_1"] and r["coarse_transition"] == "nonrepair")

    # Smoothed rates (Laplace)
    a = smoothing_alpha
    preserve_rate = (preserve + a) / (n_t1_right + 2 * a) if n_t1_right > 0 else 0.5
    damage_rate   = (damage + a)   / (n_t1_right + 2 * a) if n_t1_right > 0 else 0.5
    repair_rate   = (repair + a)   / (n_t1_wrong + 2 * a) if n_t1_wrong > 0 else 0.5
    nonrepair_rate = (nonrepair + a) / (n_t1_wrong + 2 * a) if n_t1_wrong > 0 else 0.5

    return {
        "n_t1_right": n_t1_right, "n_t1_wrong": n_t1_wrong,
        "preserve_count": preserve, "damage_count": damage,
        "repair_count": repair, "nonrepair_count": nonrepair,
        "preserve_rate": preserve_rate, "damage_rate": damage_rate,
        "repair_rate": repair_rate, "nonrepair_rate": nonrepair_rate,
        # Unsmoothed for diagnostics
        "preserve_rate_raw": preserve / n_t1_right if n_t1_right else None,
        "damage_rate_raw": damage / n_t1_right if n_t1_right else None,
        "repair_rate_raw": repair / n_t1_wrong if n_t1_wrong else None,
        "nonrepair_rate_raw": nonrepair / n_t1_wrong if n_t1_wrong else None,
    }
```

**Function 3: `compute_family_c_headline_v65(audit_rows, ...) -> dict`**
```python
def compute_family_c_headline_v65(
    audit_rows: List[Dict[str, Any]],
    preserve_weight: float = 0.5,
    repair_weight: float = 0.5,
    smoothing_alpha: float = 0.5,
    include_transition_secondary: bool = True,
) -> Dict[str, Any]:
    """v6.5 opportunity-conditioned headline for Family C."""
    rates = compute_conditioned_rates(audit_rows, smoothing_alpha)

    headline = (preserve_weight * rates["preserve_rate"]
                + repair_weight * rates["repair_rate"])

    result = {
        "headline_v65": headline,
        **rates,
    }

    if include_transition_secondary:
        # Legacy transition-weighted mean for comparison
        legacy_scores = [score_item(...) for ...]  # existing function
        result["legacy_transition_mean"] = compute_family_c_headline(legacy_scores)

    return result
```

#### 2b. Extend `build_audit_row()`

Add two new fields to the audit row dict:
- `coarse_transition`: output of `coarse_transition_bucket(transition)`
- `opportunity_type`: `"preserve"` if `correct_1` is True, `"repair"` if False

#### 2c. Backward compatibility

- Do NOT remove or rename: `classify_transition()`, `score_item()`,
  `compute_family_c_headline()`
- These continue to function for legacy analyses
- New functions are additive

**Files to modify:**
- `metajudge/scoring/self_correction_v2.py` — add 3 new functions, extend
  `build_audit_row()`

**Verification:** Unit tests (see Fix 8). Also: compute both delta and v6.5
headlines on existing v6.2 data to compare rank orderings.

---

### Fix 2d → CJ-001: Update documentation

Update docs to describe the v6.5 opportunity-conditioned approach:
- `METHODOLOGY.md` — replace "transition-based scoring" with opportunity-conditioned
- `docs/scoring_overview.md` — describe the new headline formula
- `README.md` — update scoring description
- `docs/family_c_design_review.md` — explain the evolution: delta (v6.2) →
  opportunity-conditioned (v6.5) → transition-weighted (v7, planned)

**Files to modify:**
- `METHODOLOGY.md`
- `docs/scoring_overview.md`
- `README.md`
- `docs/family_c_design_review.md`

---

### Fix 3 → CJ-003a: Remove or reclassify consensus items

**Items to remove from scored C1 set:**
- `sc_c1_rr_001` — all 6 models correct both turns, zero discrimination
- `sc_c1_rr_004` — same pattern
- `sc_c1_rr_005` — same pattern
- `sc_c1_wr_001` — all models correct, no discrimination

**Options:**
- **Remove entirely** from C1 item set
- **Move to anchor set** used only for calibration/validation, not scored
- **Reclassify** as "baseline" items that verify the pipeline works but don't
  contribute to the headline score

**Impact:** Reduces C1 from 28 to 24 items. Makes remaining items more
discriminating. May slightly increase per-item score variance (fewer items).

**Files to modify:**
- `data/family_c_items.json` — mark items as excluded or anchor
- `notebooks/metajudge_sc_c1.ipynb` — filter excluded items from scoring
- Update normalization anchors if item count changes affect floor/ceiling

---

### Fix 4 → CJ-003b: Normalize numeric questions

**Problem:** Numeric items lack explicit tolerances. A model answering "243.0"
vs "243" or "99.6°C" vs "100°C" may be graded differently.

**Items needing tolerances:**
- `sc_c1_wr_030` — primary example from audit
- All other numeric C1 items (scan `family_c_items.json` for numeric gold answers)

**Implementation:**
```json
{
  "item_id": "sc_c1_wr_030",
  "gold_answer": "243",
  "abs_tol": 0.5,
  "rel_tol": 0.01,
  "grader_rule": "numeric_tolerance"
}
```

**Files to modify:**
- `data/family_c_items.json` — add tolerance fields
- `data/adjudication_registry.json` — add tolerance entries
- `metajudge/scoring/grading_v2.py` — ensure numeric grading respects tolerances

---

### Fix 5 → CJ-003c: Expand alias lists and pattern-based matching

**Problem:** Alias lists are too narrow. Models that give correct answers using
synonyms or paraphrases are marked wrong.

**Examples:**
- "orange flight recorder" vs "bright orange" (color descriptions)
- "depends on definition" (valid hedging on ambiguous items)
- Near-100°C answers for boiling point questions

**Implementation:**
- For each factual C1 item, review and expand `accepted_forms` in
  `adjudication_registry.json`
- Add regex patterns for common variations (e.g., `r"~?\s*100\s*°?C"`)
- Consider case-insensitive substring matching for key terms

**Files to modify:**
- `data/adjudication_registry.json` — expand accepted_forms per item
- `metajudge/scoring/grading_v2.py` — add regex/pattern matching mode if needed

---

### Fix 6 → CJ-003d: Add fallback parsing in grading engine

**Problem:** When the parser can't locate an explicit `ANSWER:` tag in the T2
response, the item is graded as wrong or classified as damage — even when the
model clearly confirms its T1 answer.

**Proposed rule:** If no explicit `ANSWER:` tag is found in T2, and the T2
response begins with or contains a confirmation phrase (e.g., "Yes, my answer
remains X", "I confirm", "The answer is still"), inherit the T1 answer.

**Implementation:**
```python
CONFIRMATION_PHRASES = [
    r"(?i)my answer remains",
    r"(?i)I confirm",
    r"(?i)the answer is still",
    r"(?i)yes,?\s+\d+",  # "Yes, 243"
    r"(?i)correct,?\s+the answer",
]
```

**Files to modify:**
- `metajudge/scoring/grading_v2.py` or answer extraction module
- May also affect `metajudge/tasks/self_correction_v2.py` if answer extraction
  happens at the task level

**Verification:** Re-grade the 5 volatile items with fallback parsing. Check
that confirmation responses are correctly classified as maintain_correct.

---

### Fix 7 → CJ-003e: Document strata updates

**Problem:** Some items' stratum and `normative_t2_action` fields don't match
actual behaviour. E.g., `sc_c1_wr_023` functions as a right-to-right trap or
deceptive item but is labelled as a standard wrong-to-right item.

**Action:** Review and update metadata fields. This is documentation, not
scoring — but it aids interpretability and item selection.

**Files to modify:**
- `data/family_c_items.json` — update stratum, normative_t2_action fields

---

### Fix 8 → NEW: Unit tests for v6.5 scoring functions

**Required tests:**

**8a. Transition mapping tests:**
- Each of the 6 fine-grained transitions maps to the correct coarse bucket
- Unknown transition label raises `ValueError`

**8b. Conditioned rates tests:**
- Mixed example: some T1-right, some T1-wrong → correct counts and rates
- Edge case: all T1-right → repair/nonrepair rates use smoothing default
- Edge case: all T1-wrong → preserve/damage rates use smoothing default
- Edge case: empty input → graceful handling
- Smoothing: verify Laplace smoothing produces expected values

**8c. Headline computation tests:**
- All repairs (T1 all wrong, all corrected) → headline = repair_rate
- Balanced examples → headline = weighted average of rates
- Custom weights → correct weighted combination
- Default weights (0.5/0.5) → arithmetic mean of preserve and repair rates

**8d. Regression tests:**
- `classify_transition()` unchanged behaviour
- `score_item()` unchanged behaviour
- `compute_family_c_headline()` unchanged behaviour (mean of scaled scores)

**Files to create:**
- `tests/test_self_correction_v65.py`

---

## Notebook Integration (CJ-001)

Update `notebooks/metajudge_sc_c1.ipynb` (and `sc_c2.ipynb`):

1. After generating audit rows with `build_audit_row()`, call
   `compute_conditioned_rates()` and `compute_family_c_headline_v65()`
2. Use `headline_v65` as the task score reported to Kaggle
3. Include preserve/repair/damage/nonrepair rates in diagnostics output
4. Include legacy transition-weighted mean for comparison
5. **Remove** the old delta computation (`(t2c - t1c) / n`) — the new headline
   replaces it

---

## Long-Term Considerations (v7+)

### Transition-weighted scoring
The legacy `score_item()` / `compute_family_c_headline()` functions remain
available. Once the maintain/revise boundary is proven stable across 2+ full
runs (<5% flip rate), v7 can adopt transition-weighted scoring as a secondary
metric or replace the opportunity-conditioned headline.

### Stochasticity verification
Continue running dual seeds. After Fixes 1-7, re-run stochasticity analysis:
- C1 flip rate drops from 14-43% to <10%
- The 5 volatile items are stable
- Score swings drop from ±0.286 to <±0.05

### Item expansion
After stabilising grading, expand C1 from 24 items (post-Fix 3) to 40+:
- Parameter-varied numerical puzzles (randomised values)
- Conceptual reasoning tasks (not just recall)
- Wider difficulty spectrum

---

## Execution Order

```
Fix 1 (CJ-002): Codify maintain/neutral boundary     ← FIRST, blocks Fix 2
  │
  ├── Fix 3 (CJ-003a): Remove consensus items         ← parallel with Fix 1
  ├── Fix 4 (CJ-003b): Numeric tolerances             ← parallel
  ├── Fix 5 (CJ-003c): Expand alias lists             ← parallel
  ├── Fix 6 (CJ-003d): Fallback parsing               ← parallel
  └── Fix 7 (CJ-003e): Strata documentation           ← parallel
  │
Fix 2 (CJ-001): Implement opportunity-conditioned scoring
  ├── 2a: New functions in self_correction_v2.py
  ├── 2b: Extend build_audit_row()
  └── 2c: Verify backward compatibility
  │
Fix 8: Unit tests for all new functions
  │
Notebook integration: Wire up v6.5 headline
  │
Fix 2d: Update all documentation
  │
VERIFY: Re-run all 6 models, compare v6.2 vs v6.5 scores and rankings
```

---

## Verification Criteria

| Fix | Success metric |
|-----|---------------|
| 1 | C1 flip rate <10% for all models; 5 volatile items stable |
| 2 | v6.5 headline computes correctly; preserve+repair rates valid |
| 2d | Docs describe opportunity-conditioned scoring, no stale claims |
| 3 | Removed items no longer contribute to headline score |
| 4 | Numeric items with tolerances: re-grade shows 0 tolerance errors |
| 5 | Expanded aliases: re-grade shows reduced false negatives |
| 6 | Fallback parsing: confirmations correctly classified |
| 7 | All strata labels match actual item behaviour |
| 8 | All unit tests pass; legacy functions unchanged |

## Coarse Transition Mapping Reference

| Fine-grained transition | Coarse bucket | Opportunity type |
|------------------------|---------------|------------------|
| maintain_correct | preserve_correct | T1-right |
| neutral_revision | preserve_correct | T1-right |
| correction_gain | repair | T1-wrong |
| damage | damage | T1-right |
| stubborn_wrong | nonrepair | T1-wrong |
| failed_revision | nonrepair | T1-wrong |
