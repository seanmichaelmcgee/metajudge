# Cell 4 Parity Audit: adjudication.py → grading_v2.py

## Summary

The lean notebook (`notebooks/metajudge_submission_lean.ipynb`) has been migrated from the legacy 3-rule `adjudication.py` system to the 8-rule registry-driven `grading_v2.py` system.

## Grading Engine Comparison

| Aspect | adjudication.py (old) | grading_v2.py (new) |
|--------|----------------------|---------------------|
| Rules | 3 (alias, numeric, yes_no) | 8 (see below) |
| Dispatch | Hardcoded if/elif on `rule` field | Registry-driven via `_GRADERS` dict |
| Tolerance | Global numeric tolerance | Per-item `tolerance_params` |
| Config | Answer key (gold, aliases, rule) | Full registry (grader_rule, tolerance_params, accepted_forms, time_anchor, etc.) |
| Fraction support | No | Yes (`fraction_or_decimal` rule) |
| Code output | No dedicated rule | Yes (`code_output` rule) |
| Exact constants | No dedicated rule | Yes (`exact_constant` with rel_tol) |
| Tri-label | Handled via yes_no | Dedicated `tri_label` rule with label space validation |

### 8 Grader Rules in grading_v2

1. **alias_plus_normalization** (23 items) — Enhanced alias matching with sci-notation normalization + numeric fallback
2. **approx_numeric_small** (24 items) — Fixed tolerance (abs_tol / rel_tol)
3. **approx_numeric_dynamic** (17 items) — Time-sensitive numerics with tolerance + time_anchor metadata
4. **code_output** (16 items) — Exact match after strip/lower
5. **tri_label** (14 items) — Three-valued {true, false, contested} with synonym mapping
6. **exact_constant** (6 items) — SI-defined constants with rel_tol=1e-6
7. **fraction_or_decimal** (2 items) — Accepts both fraction and decimal forms (e.g., 4/5 ↔ 0.8)
8. **yes_no** (0 items in V4.2) — Binary true/false (supported but no items currently use it)

## 12 Misflagged Verdicts (Fixed by grading_v2)

The V4.1 audit identified 12 items where `adjudication.py` produced incorrect verdicts due to its limited 3-rule system. These are now correctly graded by `grading_v2.py`:

- Items with `tri_label` answers (contested/true/false) were previously handled by the generic `yes_no` rule, which lacked label-space validation
- Items with `exact_constant` values were graded with generic numeric tolerance instead of appropriate rel_tol
- Items with `code_output` grading fell through to alias matching, producing false positives on partial matches
- Items with `fraction_or_decimal` answers had no equivalence between "4/5" and "0.8"

Affected items: v41_crt_012, v41_crt_009, gen_a3_034, gen_a3_038, gen_a3_036, gen_a_030, gen_a_044, gen_b3_003, gen_a2_032, gen_b_024 (and others identified in the V4.1 triage).

## 7 Replaced IOED Items (V4.2)

Seven trivially-answerable items (Immediately Obvious from Easy Description) were replaced with harder physics/math items:

| Removed | Replacement | Rule | Gold |
|---------|-------------|------|------|
| (IOED) | v42_ioed_001 | approx_numeric_small | 18 |
| (IOED) | v42_ioed_002 | approx_numeric_small | 594 |
| (IOED) | v42_ioed_003 | approx_numeric_small | 845 |
| (IOED) | v42_ioed_004 | approx_numeric_small | 170 |
| (IOED) | v42_ioed_005 | approx_numeric_small | 306 |
| (IOED) | v42_ioed_009 | approx_numeric_small | 0.02 |
| (IOED) | v42_ioed_010 | approx_numeric_small | 12 |

## Parity Verdict

**PARITY ACHIEVED.** The lean notebook now uses `grading_v2.grade_item()` with the full 102-entry adjudication registry. Gold self-adjudication passes 102/102. Per-rule self-tests cover all 7 active grader rules (17 assertions).
