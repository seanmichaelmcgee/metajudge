# Merge Review: feat/dataset-validation → main

**Date:** March 19, 2026
**Branch:** `origin/feat/dataset-validation` (commit `1bfcef8`)
**Base:** `origin/main` (commit `94f9ea0`)

---

## Summary

The branch adds useful validation infrastructure (307-line check suite + 299-line test suite) but has several regressions that must be fixed before merging.

## MUST FIX before merge

### 1. SOUL.md — Reverted verified model keys (CRITICAL)

The branch replaces our Kaggle-verified keys with incorrect guesses and deletes the 5-model sweep history.

**What to keep (main):**
```
Verified keys (all confirmed on Kaggle, March 19 2026):
- "google/gemini-2.5-flash"
- "google/gemini-2.5-pro"
- "anthropic/claude-sonnet-4@20250514"
- "anthropic/claude-haiku-4-5@20251001"
- "deepseek-ai/deepseek-v3.1"
```

**What to reject (branch):**
```
Verified keys (confirmed in SDK):
- "google/gemini-2.5-flash"
- "meta/llama-3.1-70b"
Unverified keys (guesses):
- "anthropic/claude-sonnet-4-20250514"   ← wrong separator (dash not @)
- "anthropic/claude-3-5-haiku-20241022"  ← wrong model name entirely
- "deepseek/deepseek-v3"                ← wrong provider (deepseek-ai, not deepseek)
```

Also keep the project history entries for the 5-model sweep — the branch deleted them.

### 2. Notebook — Reverted to pilot version (CRITICAL)

The branch overwrites the working v3 notebook (936 lines, 100-item dataset, dataclass __init__ fix, retry logic) with what appears to be an older version:
- Removes the `CalibrationResponse.__init__` override that handles misspelled fields
- Removes Cell 7 retry logic (one-model-at-a-time with backoff)
- Reverts description to "20-item pilot set"
- Strips out Cell 4's full adjudication function

**Resolution:** Keep main's notebook entirely. The branch's notebook changes are regressions.

### 3. Deleted planning docs

The branch deletes `calibration_research_brief.md`, `calibration_research_directive.md`, and `progress_report_sprint2.md` because it branched before those were pushed.

**Resolution:** Keep main's versions of all three files.

### 4. Undoes archive moves

The branch moves archived files back to their original locations (undoing our cleanup commit).

**Resolution:** Keep main's archive structure.

### 5. Restores auditor_test.md junk file

**Resolution:** Keep it deleted.

## Schema Decision: THREE options

The branch chose `canonical` / `aliases` / `rule` (notebook Cell 3 schema).
Our research brief recommended `gold_answer` / `aliases` / `grader_rule` (production JSON schema).
The original adjudication.py used `canonical_answer` / `accepted_aliases` / `grader_rule`.

| Convention | Used by | Pros | Cons |
|-----------|---------|------|------|
| `canonical` / `aliases` / `rule` | Notebook Cell 3, branch's adjudication.py | Shortest names; notebook is source of truth on Kaggle | Requires migrating 100-entry answer_key.json |
| `gold_answer` / `aliases` / `grader_rule` | Production answer_key.json (100 entries), CSV schema | Zero data migration; matches scoring_plan.md intent | Notebook Cell 3 needs update |
| `canonical_answer` / `accepted_aliases` / `grader_rule` | Original adjudication.py | Matches scoring_plan.md literally | Most verbose; requires both data and notebook migration |

**Recommendation:** Either option 1 or 2 works — the key is picking ONE and applying it everywhere. The branch went with option 1. If you accept that, the answer_key.json migration they did is correct. If you prefer option 2 (no data migration), their adjudication.py changes need to be redone.

## KEEP from the branch

### Validation suite (good work)
- `metajudge/validation/__init__.py`
- `metajudge/validation/dataset_checks.py` (307 lines) — 9 structural checks
- `metajudge/validation/run_checks.py` (119 lines) — CLI runner
- `tests/unit/test_dataset_checks.py` (299 lines) — comprehensive tests

These are clean additions with no conflicts. They should be cherry-picked regardless of how other conflicts are resolved.

## Post-merge verification checklist

After resolving the merge, run:
```bash
# 1. Verify model keys in SOUL.md match verified keys
grep -A5 "Verified keys" SOUL.md

# 2. Verify answer_key.json schema is consistent
python3 -c "import json; d=json.load(open('data/calibration_answer_key.json')); print(list(d['cal_001'].keys()))"

# 3. Verify adjudication.py field names match answer_key.json
grep "spec\[" metajudge/scoring/adjudication.py

# 4. Verify notebook Cell 4 field names match answer_key.json
python3 -c "import json; nb=json.load(open('notebooks/metajudge_submission.ipynb')); [print(l.rstrip()) for l in nb['cells'][4]['source'] if 'canonical' in l or 'gold' in l or 'aliases' in l or 'rule' in l]"

# 5. Run tests
pytest tests/ -v

# 6. Verify notebook is v3 (100 items, not 20)
python3 -c "import json; nb=json.load(open('notebooks/metajudge_submission.ipynb')); print(len(nb['cells']), 'cells')"
```
