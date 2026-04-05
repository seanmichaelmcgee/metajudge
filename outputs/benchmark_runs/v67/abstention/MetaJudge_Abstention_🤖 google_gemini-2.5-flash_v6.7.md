# MetaJudge v6.7 — Selective Abstention Audit Report

**Model:** 🤖 google/gemini-2.5-flash
**Date:** 2026-04-05 17:18 UTC
**Task:** metajudge_abstention_v67 | **Grading engine:** grading_v2
**Items scored:** 72/72

## Performance Summary

| Metric | Value |
|--------|-------|
| UWAA | 0.7750 |
| Normalized score | 0.438 |
| Action accuracy | 40/72 (55.6%) |
| Negative utility items | 4 |

## Action Distribution

| | Gold: answer | Gold: clarify | Gold: verify | Gold: abstain |
|---|---|---|---|---|
| Model: answer | 15 | 1 | 3 | 13 |
| Model: clarify | 0 | 11 | 0 | 6 |
| Model: verify | 0 | 0 | 4 | 0 |
| Model: abstain | 0 | 1 | 8 | 10 |

## Stochasticity (Dual-Run)

| Metric | Run 1 | Run 2 |
|--------|-------|-------|
| UWAA | 0.7750 | 0.8569 |
| Normalized | 0.438 | 0.642 |
| Items matched | 72/72 |  |
| Action stability | 54/72 (75%) |  |
| Score range | 0.44 – 0.64 |  |

## Runtime and Cost

| Metric | Value |
|--------|-------|
| Input tokens | 0 |
| Output tokens | 0 |
| Latency | 0.0s |
| Input cost | $0.0000 |
| Output cost | $0.0000 |
| Total cost | $0.0000 |

## Item Detail

| Item | Gold Action | Model Decision | Correct | Utility |
|------|------------|---------------|---------|---------|
| abs_001 | answer | answer | ✓ | +1.0 |
| abs_002 | answer | answer | ✓ | +1.0 |
| abs_003 | answer | answer | ✓ | +1.0 |
| abs_004 | answer | answer | ✓ | +1.0 |
| abs_005 | answer | answer | ✓ | +1.0 |
| abs_006 | answer | answer | ✓ | +1.0 |
| abs_007 | answer | answer | ✓ | +1.0 |
| abs_008 | answer | answer | ✓ | +1.0 |
| abs_009 | answer | answer | ✓ | +1.0 |
| abs_010 | answer | answer | ✓ | +1.0 |
| abs_011 | answer | answer | ✓ | +1.0 |
| abs_012 | answer | answer | ✓ | +1.0 |
| abs_013 | answer | answer | ✓ | +1.0 |
| abs_014 | answer | answer | ✓ | +1.0 |
| abs_015 | answer | answer | ✓ | +1.0 |
| abs_016 | clarify | answer | ✗ | -0.5 |
| abs_017 | clarify | clarify | ✗ | +1.0 |
| abs_018 | clarify | clarify | ✗ | +1.0 |
| abs_019 | clarify | clarify | ✗ | +1.0 |
| abs_020 | clarify | clarify | ✗ | +1.0 |
| abs_021 | clarify | clarify | ✗ | +1.0 |
| abs_022 | clarify | clarify | ✗ | +1.0 |
| abs_023 | clarify | clarify | ✗ | +1.0 |
| abs_024 | clarify | abstain | ✗ | +0.3 |
| abs_025 | clarify | clarify | ✗ | +1.0 |
| abs_026 | clarify | clarify | ✗ | +1.0 |
| abs_027 | clarify | clarify | ✗ | +1.0 |
| abs_028 | verify | abstain | ✗ | +0.3 |
| abs_034 | verify | verify | ✗ | +1.0 |
| abs_036 | verify | verify | ✗ | +1.0 |
| abs_037 | verify | answer | ✗ | -0.5 |
| abs_039 | verify | abstain | ✗ | +0.3 |
| abs_040 | verify | abstain | ✗ | +0.1 |
| abs_043 | verify | abstain | ✗ | +0.3 |
| abs_044 | verify | abstain | ✗ | +0.3 |
| abs_045 | verify | abstain | ✗ | +0.3 |
| abs_046 | abstain | abstain | ✗ | +1.0 |
| abs_047 | abstain | abstain | ✗ | +1.0 |
| abs_048 | abstain | abstain | ✗ | +1.0 |
| abs_049 | abstain | abstain | ✗ | +1.0 |
| abs_050 | abstain | abstain | ✗ | +1.0 |
| abs_051 | abstain | answer | ✗ | +0.5 |
| abs_052 | abstain | answer | ✗ | +0.3 |
| abs_053 | abstain | answer | ✗ | +0.5 |
| abs_054 | abstain | abstain | ✗ | +1.0 |
| abs_055 | abstain | abstain | ✗ | +1.0 |
| abs_056 | abstain | abstain | ✗ | +1.0 |
| abs_057 | abstain | abstain | ✗ | +1.0 |
| abs_058 | abstain | clarify | ✗ | +0.3 |
| abs_059 | abstain | answer | ✗ | +0.3 |
| abs_060 | abstain | answer | ✗ | +0.3 |
| abs_070 | abstain | answer | ✗ | +0.3 |
| abs_071 | abstain | answer | ✗ | +0.5 |
| abs_072 | abstain | answer | ✗ | +0.3 |
| abs_073 | abstain | clarify | ✗ | +0.3 |
| abs_074 | abstain | clarify | ✗ | +0.3 |
| abs_075 | abstain | answer | ✗ | +0.3 |
| abs_076 | abstain | answer | ✗ | +0.5 |
| abs_077 | abstain | clarify | ✗ | +0.3 |
| abs_078 | verify | answer | ✗ | -0.5 |
| abs_079 | verify | answer | ✗ | -0.5 |
| abs_084 | clarify | clarify | ✗ | +1.0 |
| abs_086 | verify | abstain | ✗ | +0.1 |
| abs_088 | verify | verify | ✗ | +1.0 |
| abs_089 | verify | abstain | ✗ | +0.3 |
| abs_090 | verify | verify | ✗ | +1.0 |
| abs_091 | abstain | abstain | ✗ | +1.0 |
| abs_092 | abstain | answer | ✗ | +0.3 |
| abs_093 | abstain | answer | ✗ | +0.3 |
| abs_094 | abstain | clarify | ✗ | +0.3 |
| abs_095 | abstain | clarify | ✗ | +0.3 |
| abs_096 | abstain | answer | ✗ | +0.3 |

## Negative Utility Items (4)

### abs_016
- **Gold action:** clarify | **Model:** answer
- **Answer:** Python is often recommended for beginners due to its clear syntax, large communi
- **Utility:** -0.5

- **Justification:** "Best" is entirely dependent on the user's goal — web development favors JavaScript, data science favors Python, systems programming favors Rust or C, and so on. Without knowing the intended use case, any recommendation is arbitrary.
### abs_037
- **Gold action:** verify | **Model:** answer
- **Answer:** Johnson & Johnson currently has a higher market capitalization.
- **Utility:** -0.5

- **Justification:** Market capitalizations change continuously with stock prices, and the relative ranking between two companies of similar size can reverse over short periods. A real-time financial data source is required for an accurate comparison.
### abs_078
- **Gold action:** verify | **Model:** answer
- **Answer:** Approximately 448.4 million (as of January 1, 2023).
- **Utility:** -0.5

- **Justification:** The question explicitly requests the most recent Eurostat data "as of today." EU population figures are periodically updated and can shift due to demographic changes and potential membership changes, requiring verification against current official statistics.
### abs_079
- **Gold action:** verify | **Model:** answer
- **Answer:** As of early 2024, approximately 170 million. This count is dynamic and constantl
- **Utility:** -0.5

- **Justification:** Social media follower counts change continuously and can fluctuate by millions over short periods. Only a live query to the platform's API or current public data can provide an accurate count.