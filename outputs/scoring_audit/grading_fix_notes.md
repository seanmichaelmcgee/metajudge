# v6.2 Grading & Truncation Fix Notes

## Three issues found from scoring audit

### Issue 1: Short confirmation not detected (rr_009)
- **T2:** "The original answer is sound." (29 chars)
- **Root cause:** `is_confirmation_without_restatement` requires `len(t2_answer) > 40`
- **Also:** "the original answer is sound" not in `_CONFIRMATION_PHRASES`
- **Fix:** Add phrase + lower threshold to 15 chars

### Issue 2: "No error" prefix not detected (dt_001)  
- **T2:** "No error. There are approximately 3 trillion trees..."
- **Root cause:** `parse_answer_confidence` extracts full text starting with "No error"
- **Also:** "no error" not caught as confirmation because gold "yes" is not in the text
- Actually: "no error found" IS in the phrases, but "no error." alone is not
- **Fix:** Add "no error" as a phrase (shorter match)

### Issue 3: Answer truncation in reports
- **Helper task:** `t1_answer[:200]` and `t2_answer[:200]` in return dict
- **Markdown report:** `str(row['t1_answer'])[:80]` in rpt.append
- **Fix:** Remove both truncations; store and display full answers

## Files to change

### Package (grading engine — affects scores):
- `metajudge/tasks/self_correction_v2.py`
- `kaggle-package-v3/metajudge/tasks/self_correction_v2.py`
  - Add to `_CONFIRMATION_PHRASES`: "the original answer is sound", "no error"
  - Lower length threshold from 40 to 15

### Notebooks (reporting — affects readability):
- All 4 notebooks: `metajudge_sc_c1.ipynb`, `metajudge_sc_c2.ipynb`
  - Helper task: remove `[:200]` truncation on t1_answer, t2_answer
  - Main task markdown: remove `[:80]` truncation in report lines

### Requires re-upload:
- `kaggle-package-v6-2` (updated grading logic)
