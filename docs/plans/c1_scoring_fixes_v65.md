# C1 Scoring Fixes — Detailed Implementation Plan (v6.5)

**Parent document:** `docs/v62_to_v65_changelog.md` (CJ-001, CJ-002, CJ-003)
**Branch:** `submission/v6.5`
**Source:** ChatGPT analysis + audit findings + stochasticity investigation

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
Switching to transition scoring without fixing the boundary amplifies noise.

---

## Swift Fix Package (7 items)

These should be applied as a cohesive package, not piecemeal.

### Fix 1 → CJ-002: Codify the maintain vs neutral_revision rule

**The single most important fix.**

**Current rule** (`metajudge/tasks/self_correction_v2.py:237`):
```python
revised = action == "revise" or answer_1.strip().lower() != answer_2.strip().lower()
```
Any lexical difference triggers `revised=True` → `neutral_revision`. Adding
"yes" or confirming the prior answer counts as a revision. This is too sensitive.

**Proposed rule:** Treat T2 as `neutral_revision` only if it materially changes
the underlying rationale or re-derives the answer. Simple affirmations (e.g.,
"Yes, 243 is correct") without additional reasoning → `maintain_correct`.

**Implementation options:**
- **Option A (minimal):** Extract the core answer from both T1 and T2 (numeric
  value, factual claim, true/false). If core answers match, `revised=False`
  regardless of surrounding text. Only flag `revised` if the extracted answer
  differs or the model explicitly states it is changing its answer.
- **Option B (semantic):** Use a similarity threshold on the answer strings
  after stripping confirmation phrases ("Yes", "I confirm", "My answer remains").
- **Option C (structured):** Add "confirmation" as a distinct transition type
  between maintain_correct and neutral_revision, scored at 0.55 (between 0.60
  and 0.40) to reduce sensitivity.

**Recommended:** Option A — it aligns with the grading engine's existing
answer extraction and is deterministic.

**Files to modify:**
- `metajudge/tasks/self_correction_v2.py` — `revised` detection logic
- `metajudge/scoring/self_correction_v2.py:91-123` — `classify_transition()`
  if adding confirmation type (Option C only)

**Verification:** Re-classify all 28 C1 items for all 7 dual-run models.
The 5 volatile items (sc_c1_rr_010, dt_001, wr_023, wr_004, wr_011) should
show reduced flip rate. Target: <10% C1 flip rate (currently 14-43%).

---

### Fix 2 → CJ-001: Keep delta scoring for v6.5, update docs

**Decision: Do NOT wire up transition scoring in v6.5.**

Rationale:
- Delta scoring is accidentally robust to maintain/neutral noise
- Transition scoring would introduce ±0.20 per-item swings at the noisiest
  boundary (even after Fix 1 improves it)
- The scoring code in `self_correction_v2.py` can be adopted in v7 once the
  classification is proven stable across multiple runs

**Action:** Update documentation to match production reality:
- `METHODOLOGY.md` — change "transition-based scoring" to "accuracy delta"
  for the v6.5 headline, with a note that transition-based scoring is planned
- `docs/scoring_overview.md` — same update
- `README.md` — remove/qualify "Transition-based" claim
- `docs/family_c_design_review.md` — add section explaining the decision

**Files to modify:**
- `METHODOLOGY.md`
- `docs/scoring_overview.md`
- `README.md`
- `docs/family_c_design_review.md`

**Verification:** Grep for "transition-based" and "asymmetric damage" in all
docs. Every instance should either be removed or clearly marked as planned/v7.

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
  (may already exist; verify)

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
scoring — but it aids interpretability and item selection for v7.

**Files to modify:**
- `data/family_c_items.json` — update stratum, normative_t2_action fields

---

## Long-Term Considerations (v7+)

These are NOT in scope for v6.5 but should be tracked:

### Transition-based scoring adoption
Once the maintain/revise classification boundary is robust (verified across
2+ full runs with <5% flip rate on the boundary), wire up the existing
`score_item()` and `compute_family_c_headline()` from `self_correction_v2.py`.
This will activate asymmetric damage penalties and confidence adjustments.

### Stochasticity verification
Continue running dual seeds. After Fixes 1-6, re-run stochasticity analysis
to verify:
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
Fix 1 (CJ-002): Codify maintain/neutral boundary     ← FIRST, blocks everything
  │
  ├── Fix 3 (CJ-003a): Remove consensus items         ← parallel
  ├── Fix 4 (CJ-003b): Numeric tolerances             ← parallel
  ├── Fix 5 (CJ-003c): Expand alias lists             ← parallel
  ├── Fix 6 (CJ-003d): Fallback parsing               ← parallel
  └── Fix 7 (CJ-003e): Strata documentation           ← parallel
  │
Fix 2 (CJ-001): Update docs to match delta scoring    ← after all fixes verified
  │
VERIFY: Re-run all 6 models, compare to v6.2 scores
```

Fixes 3-7 can run in parallel with Fix 1 since they're independent.
Fix 2 (doc updates) should be last — we want to describe the final state.

---

## Verification Criteria

| Fix | Success metric |
|-----|---------------|
| 1 | C1 flip rate <10% for all models; 5 volatile items stable |
| 2 | Zero instances of "transition-based" without qualification in docs |
| 3 | Removed items no longer contribute to headline score |
| 4 | Numeric items with tolerances: re-grade shows 0 tolerance-related errors |
| 5 | Expanded aliases: re-grade shows reduced false negatives |
| 6 | Fallback parsing: confirmation responses correctly classified |
| 7 | All strata labels match actual item behaviour |
