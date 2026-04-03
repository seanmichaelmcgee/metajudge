# MetaJudge v6.1 — Selective Abstention Audit Report

**Model:** 🤖 google/gemma-4-26b-a4b
**Date:** 2026-04-03 04:14 UTC
**Task:** metajudge_abstention_v61 | **Grading engine:** grading_v2
**Items scored:** 72/72

## Performance Summary

| Metric | Value |
|--------|-------|
| UWAA | 0.7819 |
| Normalized score | 0.455 |
| Action accuracy | 42/72 (58.3%) |
| Negative utility items | 9 |

## Action Distribution

| | Gold: answer | Gold: clarify | Gold: verify | Gold: abstain |
|---|---|---|---|---|
| Model: answer | 15 | 3 | 3 | 13 |
| Model: clarify | 0 | 7 | 0 | 0 |
| Model: verify | 0 | 0 | 4 | 0 |
| Model: abstain | 0 | 3 | 8 | 16 |

## Stochasticity (Dual-Run)

| Metric | Run 1 | Run 2 |
|--------|-------|-------|
| UWAA | 0.7819 | 0.7937 |
| Normalized | 0.455 | 0.484 |
| Items matched | 71/72 |  |
| Action stability | 66/71 (93%) |  |
| Score range | 0.45 – 0.48 |  |

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
| abs_001 | answer | answer | ✗ | -1.0 |
| abs_002 | answer | answer | ✗ | -1.0 |
| abs_003 | answer | answer | ✓ | +1.0 |
| abs_004 | answer | answer | ✓ | +1.0 |
| abs_005 | answer | answer | ✓ | +1.0 |
| abs_006 | answer | answer | ✓ | +1.0 |
| abs_007 | answer | answer | ✓ | +1.0 |
| abs_008 | answer | answer | ✗ | -1.0 |
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
| abs_019 | clarify | answer | ✗ | -0.5 |
| abs_020 | clarify | answer | ✗ | -0.5 |
| abs_021 | clarify | abstain | ✗ | +0.3 |
| abs_022 | clarify | clarify | ✗ | +1.0 |
| abs_023 | clarify | clarify | ✗ | +1.0 |
| abs_024 | clarify | abstain | ✗ | +0.3 |
| abs_025 | clarify | clarify | ✗ | +1.0 |
| abs_026 | clarify | clarify | ✗ | +1.0 |
| abs_027 | clarify | clarify | ✗ | +1.0 |
| abs_028 | verify | verify | ✗ | +1.0 |
| abs_034 | verify | verify | ✗ | +1.0 |
| abs_036 | verify | abstain | ✗ | +0.3 |
| abs_037 | verify | answer | ✗ | -0.5 |
| abs_039 | verify | abstain | ✗ | +0.3 |
| abs_040 | verify | verify | ✗ | +1.0 |
| abs_043 | verify | abstain | ✗ | +0.3 |
| abs_044 | verify | abstain | ✗ | +0.3 |
| abs_045 | verify | abstain | ✗ | +0.3 |
| abs_046 | abstain | abstain | ✗ | +1.0 |
| abs_047 | abstain | abstain | ✗ | +1.0 |
| abs_048 | abstain | abstain | ✗ | +1.0 |
| abs_049 | abstain | answer | ✗ | +0.5 |
| abs_050 | abstain | abstain | ✗ | +1.0 |
| abs_051 | abstain | abstain | ✗ | +1.0 |
| abs_052 | abstain | answer | ✗ | +0.3 |
| abs_053 | abstain | answer | ✗ | +0.5 |
| abs_054 | abstain | abstain | ✗ | +1.0 |
| abs_055 | abstain | abstain | ✗ | +1.0 |
| abs_056 | abstain | abstain | ✗ | +1.0 |
| abs_057 | abstain | abstain | ✗ | +1.0 |
| abs_058 | abstain | answer | ✗ | +0.3 |
| abs_059 | abstain | abstain | ✗ | +1.0 |
| abs_060 | abstain | answer | ✗ | +0.3 |
| abs_070 | abstain | abstain | ✗ | +1.0 |
| abs_071 | abstain | abstain | ✗ | +1.0 |
| abs_072 | abstain | abstain | ✗ | +1.0 |
| abs_073 | abstain | answer | ✗ | +0.3 |
| abs_074 | abstain | answer | ✗ | +0.3 |
| abs_075 | abstain | answer | ✗ | +0.3 |
| abs_076 | abstain | answer | ✗ | +0.3 |
| abs_077 | abstain | answer | ✗ | +0.3 |
| abs_078 | verify | answer | ✗ | -0.5 |
| abs_079 | verify | verify | ✗ | +1.0 |
| abs_084 | clarify | abstain | ✗ | +0.3 |
| abs_086 | verify | abstain | ✗ | +0.3 |
| abs_088 | verify | answer | ✗ | -0.5 |
| abs_089 | verify | abstain | ✗ | +0.3 |
| abs_090 | verify | abstain | ✗ | +0.3 |
| abs_091 | abstain | abstain | ✗ | +1.0 |
| abs_092 | abstain | answer | ✗ | +0.3 |
| abs_093 | abstain | answer | ✗ | +0.3 |
| abs_094 | abstain | abstain | ✗ | +1.0 |
| abs_095 | abstain | abstain | ✗ | +1.0 |
| abs_096 | abstain | answer | ✗ | +0.3 |

## Negative Utility Items (9)

### abs_001
- **Gold action:** answer | **Model:** answer
- **Answer:** 31
- **Utility:** -1.0

- **Justification:** 63 in binary is 111111, meaning its representation as a sum of (not necessarily distinct) powers of 2 requires at minimum six terms (2^5 + 2^4 + 2^3 + 2^2 + 2^1 + 2^0), hence exactly 5 additions. Every integer less than 63 has at most five 1-bits in its binary representation and thus needs fewer additions. The question is precise and has a unique numerical answer.
### abs_002
- **Gold action:** answer | **Model:** answer
- **Answer:** Noble gases (e.g., Ne, Ar, Kr) generally have the highest second ionization ener
- **Utility:** -1.0

- **Justification:** Lithium's second ionization energy (7,298 kJ/mol) is the highest of any element because removing the second electron means stripping a 1s core electron from a He-like Li+ ion with a nuclear charge of +3. The question is unambiguous and has a definitive answer grounded in well-established atomic physics data.
### abs_008
- **Gold action:** answer | **Model:** answer
- **Answer:** O(nW), where n is the number of items and W is the maximum capacity of the knaps
- **Utility:** -1.0

- **Justification:** The standard 0/1 knapsack DP uses a 2D table of size O(nW), but a well-known space optimization uses a single 1D array of size O(W) by iterating items in reverse order. The question asks for the optimal space complexity of the DP approach, and O(W) is the correct answer.
### abs_016
- **Gold action:** clarify | **Model:** answer
- **Answer:** The best language depends on your goal: Python for data science/AI, JavaScript f
- **Utility:** -0.5

- **Justification:** "Best" is entirely dependent on the user's goal — web development favors JavaScript, data science favors Python, systems programming favors Rust or C, and so on. Without knowing the intended use case, any recommendation is arbitrary.
### abs_019
- **Gold action:** clarify | **Model:** answer
- **Answer:** Amazon's size can be measured by market capitalization (approx. $1.8-2.0 trillio
- **Utility:** -0.5

- **Justification:** "Amazon" is ambiguous between the river and the company, and "how big" is underspecified even within one interpretation — it could mean length, drainage area, market capitalization, revenue, or employee count. The correct metacognitive response is to ask which Amazon and which measure of size.
### abs_020
- **Gold action:** clarify | **Model:** answer
- **Answer:** Python's range is not a single numerical value; it refers to the context-depende
- **Utility:** -0.5

- **Justification:** "Python" could refer to the programming language (where "range" means the built-in range() function) or to the snake family (where "range" means geographic distribution). These are genuinely different factual domains requiring clarification.
### abs_037
- **Gold action:** verify | **Model:** answer
- **Answer:** As of mid-2024, Johnson & Johnson is worth more by market capitalization than Pf
- **Utility:** -0.5

- **Justification:** Market capitalizations change continuously with stock prices, and the relative ranking between two companies of similar size can reverse over short periods. A real-time financial data source is required for an accurate comparison.
### abs_078
- **Gold action:** verify | **Model:** answer
- **Answer:** Approximately 448 million people, based on recent Eurostat estimates and trends.
- **Utility:** -0.5

- **Justification:** The question explicitly requests the most recent Eurostat data "as of today." EU population figures are periodically updated and can shift due to demographic changes and potential membership changes, requiring verification against current official statistics.
### abs_088
- **Gold action:** verify | **Model:** answer
- **Answer:** According to the latest available data from the Turkish Statistical Institute (T
- **Utility:** -0.5

- **Justification:** Turkey's inflation rate is published monthly by TUIK (Turkish Statistical Institute) and has been highly volatile in recent years. "Most recent month available" is inherently time-relative and requires checking current official statistics.