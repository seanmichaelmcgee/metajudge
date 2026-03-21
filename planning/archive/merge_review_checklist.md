# Merge Review: feat/dataset-validation → main

**Date:** March 19, 2026
**Branch:** `origin/feat/dataset-validation` (commit `1bfcef8`)
**Base:** `origin/main` (commit `94f9ea0`)
**Status:** ✅ RESOLVED — all useful work absorbed into main; branch can be closed.

---

## Resolution Summary

All five regressions from the branch have been addressed by keeping main's versions.
The one valuable contribution (validation suite) was cherry-picked and adapted.
Schema has been canonicalized to `gold_answer` / `aliases` / `rule` across all files.

**Schema decision:** `gold_answer` / `aliases` / `rule`
- Rationale: `gold_answer` is unambiguous for coding agents (won't drift to `canonical` vs `canonical_answer`), largest data artifact (`calibration_answer_key.json`) already used `gold_answer`/`aliases`, and CSV column headers match.
- `rule` chosen over `grader_rule` for brevity — consistently short field names.
- Deprecated names documented in SOUL.md §"Canonical schema: answer key".

## Issues from branch — all resolved

### 1. ✅ SOUL.md — Reverted verified model keys (was CRITICAL)
**Resolution:** Kept main's verified keys. Branch's wrong keys rejected.

### 2. ✅ Notebook — Reverted to pilot version (was CRITICAL)
**Resolution:** Kept main's v3 notebook (936 lines, 100-item dataset, dataclass fix, retry logic). Updated Cell 3 and Cell 4 to use `gold_answer` schema.

### 3. ✅ Deleted planning docs
**Resolution:** Kept main's versions of all three planning docs.

### 4. ✅ Undid archive moves
**Resolution:** Kept main's archive structure.

### 5. ✅ Restored auditor_test.md junk file
**Resolution:** Kept it deleted.

## Cherry-picked from branch

### Validation suite (adapted to gold_answer schema)
- `metajudge/validation/__init__.py`
- `metajudge/validation/dataset_checks.py` — 9 structural checks
- `metajudge/validation/run_checks.py` — CLI runner
- `tests/unit/test_dataset_checks.py` — comprehensive tests

All field references updated from `canonical`/`accepted_aliases`/`grader_rule` to `gold_answer`/`aliases`/`rule`.

## Files modified in schema canonicalization

| File | Changes |
|------|---------|
| `SOUL.md` | Added "Canonical schema: answer key" section, rule #6 on deprecated names |
| `metajudge/scoring/adjudication.py` | All field refs → `gold_answer`/`aliases`/`rule` |
| `data/calibration_answer_key.json` | `grader_rule` → `rule`, dropped extra fields (100 items × 3 fields) |
| `notebooks/metajudge_submission.ipynb` | Cell 3 ANSWER_KEY + Cell 4 adjudication → `gold_answer` |
| `scripts/update_notebook.py` | Updated to match new schema |
| `tests/unit/test_scoring.py` | Test fixtures → new schema |

## Verification (all passing)

```
$ python -m pytest tests/ -q
96 passed in 0.47s
```

## Recommended branch disposition

**Close `feat/dataset-validation` without merging.** All useful work has been absorbed into main via cherry-pick. The branch has 5 regressions that would reintroduce bugs. Closing it keeps the git history clean.
