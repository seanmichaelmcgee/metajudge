# Cross-Model Item-Level Audit — v6.2

**Models:** 5 | **Total items audited:** 1137

## Summary by Model

| Model | Task | Items | AGREE | KNOWN-BUG | FLAG | DISAGREE |
|-------|------|-------|-------|-----------|------|---------|
| claude-sonnet-4-6@default | calibration | 105 | 103 | 2 | 0 | 0 |
| claude-sonnet-4-6@default | abstention | 72 | 71 | 0 | 1 | 0 |
| claude-sonnet-4-6@default | sc_c1 | 28 | 28 | 0 | 0 | 0 |
| claude-sonnet-4-6@default | sc_c2 | 23 | 23 | 0 | 0 | 0 |
| claude-sonnet-4@20250514 | calibration | 105 | 103 | 2 | 0 | 0 |
| claude-sonnet-4@20250514 | abstention | 72 | 71 | 0 | 1 | 0 |
| claude-sonnet-4@20250514 | sc_c1 | 28 | 28 | 0 | 0 | 0 |
| claude-sonnet-4@20250514 | sc_c2 | 23 | 23 | 0 | 0 | 0 |
| gemini-2.5-pro | calibration | 105 | 103 | 2 | 0 | 0 |
| gemini-2.5-pro | abstention | 72 | 72 | 0 | 0 | 0 |
| gemini-2.5-pro | sc_c1 | 28 | 28 | 0 | 0 | 0 |
| gemini-2.5-pro | sc_c2 | 23 | 23 | 0 | 0 | 0 |
| gemini-3-flash-preview | calibration | 104 | 102 | 2 | 0 | 0 |
| gemini-3-flash-preview | abstention | 72 | 72 | 0 | 0 | 0 |
| gemini-3-flash-preview | sc_c1 | 28 | 28 | 0 | 0 | 0 |
| gemini-3-flash-preview | sc_c2 | 23 | 23 | 0 | 0 | 0 |
| gemma-4-26b-a4b | calibration | 104 | 103 | 1 | 0 | 0 |
| gemma-4-26b-a4b | abstention | 71 | 68 | 0 | 3 | 0 |
| gemma-4-26b-a4b | sc_c1 | 28 | 28 | 0 | 0 | 0 |
| gemma-4-26b-a4b | sc_c2 | 23 | 23 | 0 | 0 | 0 |

## Issues Found (5)

- anthropic_claude-sonnet-4-6@default|abstention|abs_006: Correct action but negative utility
- anthropic_claude-sonnet-4@20250514|abstention|abs_006: Correct action but negative utility
- google_gemma-4-26b-a4b|abstention|abs_001: Correct action but negative utility
- google_gemma-4-26b-a4b|abstention|abs_002: Correct action but negative utility
- google_gemma-4-26b-a4b|abstention|abs_008: Correct action but negative utility

## Totals

- **Items audited:** 1137
- **AGREE:** 1123 (98.8%)
- **KNOWN-BUG:** 9 (tri_label accepted_forms — fix deployed but not re-run)
- **FLAG:** 5
- **DISAGREE:** 0
- **Pipeline accuracy:** 99.6% (including known bugs as correct-after-fix)