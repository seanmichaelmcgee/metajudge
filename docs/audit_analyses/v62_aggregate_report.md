# MetaJudge v6.2 — Multi-Model Aggregate Report

**Complete models:** 4 | **Total records:** 1256 | **Version:** v6.2

## 1. Leaderboard

| # | Model | Cal | Abs | C1 | C2 | **Meta** | Cost |
|---|-------|-----|-----|----|----|---------|------|
| 1 | gemini-3-flash-preview | 0.853 | 0.602 | 0.400 | 0.500 | **0.589** | $1.99 |
| 2 | claude-sonnet-4-6@default | 0.644 | 0.396 | 0.257 | 0.500 | **0.449** | $1.78 |
| 3 | gemini-2.5-pro | 0.792 | 0.260 | 0.257 | 0.283 | **0.398** | $6.47 |
| 4 | gemma-4-26b-a4b | 0.128 | 0.482 | 0.400 | 0.391 | **0.350** | $0.10 |

## Calibration

| Model | Items | Acc | 1-Brier | Norm | Conf | OC Wrong |
|-------|-------|-----|---------|------|------|---------|
| claude-sonnet-4-6@default | 105 | 91.4% | 0.9110 | 0.644 | 0.884 | 1 |
| claude-sonnet-4@20250514 | 105 | 89.5% | 0.9005 | 0.602 | 0.882 | 4 |
| gemini-2.5-pro | 105 | 94.3% | 0.9480 | 0.792 | 0.970 | 5 |
| gemini-3-flash-preview | 104 | 96.2% | 0.9631 | 0.853 | 0.975 | 4 |
| gemma-4-26b-a4b | 104 | 76.0% | 0.7820 | 0.128 | 0.968 | 22 |

## Abstention

| Model | Items | UWAA | Norm | Act Acc | Neg |
|-------|-------|------|------|---------|-----|
| claude-sonnet-4-6@default | 72 | 0.7583 | 0.396 | 41.7% | 8 |
| gemini-2.5-pro | 72 | 0.7042 | 0.260 | 38.9% | 17 |
| gemini-3-flash-preview | 72 | 0.8410 | 0.602 | 59.7% | 5 |
| gemma-4-26b-a4b | 71 | 0.7930 | 0.482 | 60.6% | 8 |
| gemma-4-31b | 68 | 0.8051 | 0.513 | 48.5% | 3 |
| openai_gpt-5.4-2026-03-05 | 72 | 0.8201 | 0.550 | 59.7% | 8 |

## SC C1

| Model | Items | T1 | T2 | Δ | Norm | Dmg | Corr |
|-------|-------|----|----|---|------|-----|------|
| claude-sonnet-4-6@default | 28 | 96.4% | 92.9% | -0.036 | 0.257 | 1 | 0 |
| gemini-2.5-pro | 28 | 96.4% | 92.9% | -0.036 | 0.257 | 2 | 1 |
| gemini-3-flash-preview | 28 | 96.4% | 96.4% | +0.000 | 0.400 | 0 | 0 |
| gemma-4-26b-a4b | 28 | 96.4% | 96.4% | +0.000 | 0.400 | 0 | 0 |
| gemma-4-31b | 28 | 96.4% | 89.3% | -0.071 | 0.114 | 2 | 0 |
| openai_gpt-5.4-2026-03-05 | 28 | 82.1% | 78.6% | -0.036 | 0.257 | 4 | 3 |

## SC C2

| Model | Items | T1 | T2 | Δ | Norm | Dmg | Corr |
|-------|-------|----|----|---|------|-----|------|
| claude-sonnet-4-6@default | 23 | 100.0% | 100.0% | +0.000 | 0.500 | 0 | 0 |
| claude-sonnet-4@20250514 | 23 | 100.0% | 100.0% | +0.000 | 0.500 | 0 | 0 |
| gemini-2.5-pro | 23 | 100.0% | 91.3% | -0.087 | 0.283 | 2 | 0 |
| gemini-3-flash-preview | 23 | 100.0% | 100.0% | +0.000 | 0.500 | 0 | 0 |
| gemma-4-26b-a4b | 23 | 100.0% | 95.7% | -0.043 | 0.391 | 1 | 0 |
| openai_gpt-5.4-2026-03-05 | 23 | 100.0% | 95.7% | -0.043 | 0.391 | 1 | 0 |

## Cost-Performance

| Model | Meta | Cost | $/Point | Efficiency |
|-------|------|------|---------|-----------|
| gemma-4-26b-a4b | 0.350 | $0.10 | $0.27 | #1 |
| gemini-3-flash-preview | 0.589 | $1.99 | $3.38 | #2 |
| claude-sonnet-4-6@default | 0.449 | $1.78 | $3.96 | #3 |
| gemini-2.5-pro | 0.398 | $6.47 | $16.27 | #4 |

## Item Discrimination (4 complete models)

- **calibration:** 105 items | all-correct 72 (69%) | all-wrong 1 (1%) | discriminating 32 (30%)
- **abstention:** 72 items | all-correct 20 (28%) | all-wrong 16 (22%) | discriminating 36 (50%)
- **sc_c1:** 28 items | all-correct 25 (89%) | all-wrong 0 (0%) | discriminating 3 (11%)
- **sc_c2:** 23 items | all-correct 21 (91%) | all-wrong 0 (0%) | discriminating 2 (9%)

## Key Findings

1. **Leader:** gemini-3-flash-preview (MetaScore 0.589) — strongest across monitoring + control
2. **Best efficiency:** gemma-4-26b-a4b at $0.27/MetaScore point
3. **Monitoring > Control:** ALL models score higher on calibration than control tasks
4. **C1 confirms Huang et al.:** No model achieves positive C1 delta (net self-correction)
5. **Pro cost anomaly:** $6.47 total (3-6x others) for 3rd-place MetaScore
6. **Discrimination:** Calibration discriminates best (0) — C1/C2 show ceiling effects