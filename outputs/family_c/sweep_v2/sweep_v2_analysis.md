# Sprint v2 Validation Sweep Analysis
**Total trials:** 245 (5 models × items)

## 1. Accuracy Summary

| Model | Items | T1 Acc | T2 Acc | Δ(T2-T1) | T1 Err | T2 Err |
|-------|-------|--------|--------|----------|--------|--------|
| sonnet-4.6 | 45 | 97.8% | 91.1% | -6.7% | 0 | 1 |
| ds-r1 | 45 | 91.1% | 91.1% | +0.0% | 0 | 1 |
| gem-flash | 55 | 83.6% | 92.7% | +9.1% | 0 | 0 |
| gpt-5-mini | 55 | 89.1% | 89.1% | +0.0% | 0 | 0 |
| gpt-5.2 | 45 | 62.2% | 60.0% | -2.2% | 0 | 1 |

## 2. Transition Matrices

**sonnet-4.6:**
| Transition | Count | % |
|-----------|-------|---|
| right_to_right | 41 | 91.1% |
| wrong_to_right | 0 | 0.0% |
| right_to_wrong | 3 | 6.7% |
| wrong_to_wrong | 1 | 2.2% |

**ds-r1:**
| Transition | Count | % |
|-----------|-------|---|
| right_to_right | 40 | 88.9% |
| wrong_to_right | 1 | 2.2% |
| right_to_wrong | 1 | 2.2% |
| wrong_to_wrong | 3 | 6.7% |

**gem-flash:**
| Transition | Count | % |
|-----------|-------|---|
| right_to_right | 45 | 81.8% |
| wrong_to_right | 6 | 10.9% |
| right_to_wrong | 1 | 1.8% |
| wrong_to_wrong | 3 | 5.5% |

**gpt-5-mini:**
| Transition | Count | % |
|-----------|-------|---|
| right_to_right | 48 | 87.3% |
| wrong_to_right | 1 | 1.8% |
| right_to_wrong | 1 | 1.8% |
| wrong_to_wrong | 5 | 9.1% |

**gpt-5.2:**
| Transition | Count | % |
|-----------|-------|---|
| right_to_right | 26 | 57.8% |
| wrong_to_right | 1 | 2.2% |
| right_to_wrong | 2 | 4.4% |
| wrong_to_wrong | 16 | 35.6% |

## 3. B0 Re-answering Baseline

B0 ran on 118 trials (diagnostic subset × models)

| Model | B0 Items | T1 Acc | T2 Acc | B0 Acc | C1−B0 | Systematic Err |
|-------|----------|--------|--------|--------|-------|---------------|
| sonnet-4.6 | 45 | 97.8% | 91.1% | 35.6% | +55.6% | 1/45 |
| ds-r1 | 16 | 100.0% | 100.0% | 100.0% | +0.0% | 0/16 |
| gem-flash | 21 | 71.4% | 95.2% | 71.4% | +23.8% | 6/21 |
| gpt-5-mini | 21 | 95.2% | 95.2% | 95.2% | +0.0% | 1/21 |
| gpt-5.2 | 15 | 33.3% | 26.7% | 40.0% | -13.3% | 9/15 |

## 4. Confidence Dynamics

| Model | T1 Conf (mean) | T2 Conf (mean) | Δ Conf | Parse Rate |
|-------|---------------|---------------|--------|-----------|
| sonnet-4.6 | nan% | nan% | nan% | 0% |
| ds-r1 | nan% | nan% | nan% | 0% |
| gem-flash | 99.5% | 99.5% | +0.0% | 18% |
| gpt-5-mini | 95.0% | 90.5% | -4.5% | 18% |
| gpt-5.2 | nan% | nan% | nan% | 0% |

## 5. Edit Distance (T1↔T2 Similarity)

| Model | Mean Sim | No Change (>0.9) | Targeted (0.4-0.9) | Rewrite (<0.4) |
|-------|---------|-----------------|-------------------|---------------|
| sonnet-4.6 | 0.117 | 0 (0%) | 3 (7%) | 42 (93%) |
| ds-r1 | 0.228 | 3 (7%) | 6 (13%) | 36 (80%) |
| gem-flash | 0.139 | 2 (4%) | 3 (5%) | 50 (91%) |
| gpt-5-mini | 0.195 | 2 (4%) | 11 (20%) | 42 (76%) |
| gpt-5.2 | 0.403 | 7 (16%) | 15 (33%) | 23 (51%) |

## 6. C1 Prompt Selection

| Model | Primary (>500ch) | Fallback (≤500ch) |
|-------|-----------------|------------------|
| sonnet-4.6 | 4 | 19 |
| ds-r1 | 1 | 22 |
| gem-flash | 5 | 23 |
| gpt-5-mini | 0 | 28 |
| gpt-5.2 | 0 | 23 |

## 7. Item Difficulty Profile

Items with T1 accuracy < 100% across models (potential WR differentiators):

| Item | Subfamily | Stratum | T1 Acc (across models) | T2 Acc | W→R |
|------|-----------|---------|----------------------|--------|-----|
| sc_c1_ur_001 | C1 | unresolved | 20% | 40% | 2 |
| sc_c1_ur_002 | C1 | unresolved | 20% | 20% | 0 |
| sc_c2_ur_001 | C2 | unresolved_capable | 20% | 20% | 0 |
| sc_c2_ur_002 | C2 | unresolved_capable | 20% | 40% | 1 |
| sc_c1_wr_009 | C1 | wrong_to_right | 43% | 71% | 2 |
| sc_c1_wr_010 | C1 | wrong_to_right | 57% | 71% | 1 |
| sc_c2_wr_001 | C2 | wrong_to_right | 71% | 86% | 1 |
| sc_c1_dt_002 | C1 | deceptive_trap | 80% | 80% | 0 |
| sc_c1_rr_002 | C1 | right_to_right | 80% | 80% | 0 |
| sc_c1_wr_002 | C1 | wrong_to_right | 80% | 80% | 0 |
| sc_c1_wr_008 | C1 | wrong_to_right | 80% | 100% | 1 |
| sc_c1_wr_011 | C1 | wrong_to_right | 80% | 80% | 0 |
| sc_c2_rr_004 | C2 | right_to_right | 80% | 80% | 1 |
| sc_c2_wr_007 | C2 | wrong_to_right | 80% | 80% | 0 |
| sc_c2_wr_008 | C2 | wrong_to_right | 80% | 80% | 0 |
| sc_c2_wr_009 | C2 | wrong_to_right | 80% | 80% | 0 |
| sc_c2_wr_010 | C2 | wrong_to_right | 80% | 80% | 0 |
| sc_c2_wr_011 | C2 | wrong_to_right | 80% | 80% | 0 |
| sc_c2_wr_006 | C2 | wrong_to_right | 86% | 71% | 0 |

## 8. Gradeability Gate

Gradeable output: 242/245 (98.8%)
Gate (≥90%): **PASS**
