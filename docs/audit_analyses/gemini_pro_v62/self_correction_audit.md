# Self-Correction Audit — Gemini 2.5 Pro v6.2

**C1:** 28 items (Run 1) + 28 items (Run 2)
**C2:** 23 items (Run 1) + 23 items (Run 2)

---

## C1 — Intrinsic Self-Correction (28 items)

T1 accuracy: 27/28 (96.4%) | T2 accuracy: 26/28 (92.9%) | Delta: -0.0357

### Transition Summary

| Transition | Count |
|-----------|-------|
| maintain_correct | 18 |
| correction_gain | 1 |
| neutral_revision | 7 |
| damage | 2 |
| stubborn_wrong | 0 |
| failed_revision | 0 |

### Item-by-Item

| Item | Stratum | Gold | T1 | T1✓ | T2 | T2✓ | Trans | Sim | Assess |
|------|---------|------|----|-----|----|-----|-------|-----|--------|
| sc_c1_dt_001 | deceptiv | yes | Yes | ✓ | Yes | ✓ | maintain_correct | 0.14 | AGREE |
| sc_c1_dt_002 | deceptiv | 5050 | 5050 | ✓ | 5050 | ✓ | maintain_correct | 0.09 | AGREE |
| sc_c1_dt_003 | deceptiv | yes | Yes | ✓ | Yes | ✓ | maintain_correct | 0.08 | AGREE |
| sc_c1_dt_004 | deceptiv | no | ANSWER: No. This is a long-sta | ✓ | ANSWER: Upon review, I confirm | ✓ | neutral_revision | 0.07 | AGREE |
| sc_c1_dt_005 | deceptiv | $0.05 | $0.05 | ✓ | $0.05 | ✓ | maintain_correct | 0.12 | AGREE |
| sc_c1_dt_006 | deceptiv | 2^81 | 2,417,851,639,229,258,349,412, | ✓ | The original answer is confirm | ✓ | neutral_revision | 0.17 | AGREE |
| sc_c1_rr_001 | right_to | bright orange | Bright orange. | ✓ | After careful review, I find n | ✓ | neutral_revision | 0.21 | AGREE |
| sc_c1_rr_002 | right_to | 1081 | 1081 | ✓ | 1081 | ✓ | maintain_correct | 0.17 | AGREE |
| sc_c1_rr_003 | right_to | 100 | 100°C | ✓ | 99.974°C | ✗ | damage | 0.03 | AGREE |
| sc_c1_rr_004 | right_to | Canberra | Canberra | ✓ | Canberra | ✓ | maintain_correct | 0.18 | AGREE |
| sc_c1_rr_005 | right_to | 1989 | 1989 | ✓ | 1989 | ✓ | maintain_correct | 0.19 | AGREE |
| sc_c1_rr_006 | right_to | Au | Au | ✓ | Au | ✓ | maintain_correct | 0.11 | AGREE |
| sc_c1_rr_007 | right_to | 7 | 7 | ✓ | 7 | ✓ | maintain_correct | 0.12 | AGREE |
| sc_c1_rr_008 | right_to | -1 | -1 | ✓ | -1 | ✓ | maintain_correct | 0.07 | AGREE |
| sc_c1_rr_009 | right_to | 2 | 2 | ✓ | The original answer is confirm | ✓ | neutral_revision | 0.04 | AGREE |
| sc_c1_rr_010 | right_to | 5.1 | 5.1 | ✓ | 5.1 | ✓ | maintain_correct | 0.05 | AGREE |
| sc_c1_wr_001 | wrong_to | 12 | 12 | ✓ | 12 | ✓ | maintain_correct | 0.05 | AGREE |
| sc_c1_wr_002 | wrong_to | 1065.02 | 1,065.02 EUR | ✓ | 1,065.02 EUR | ✓ | maintain_correct | 0.07 | AGREE |
| sc_c1_wr_004 | wrong_to | adult human | adult human. An adult human ha | ✓ | I confirm my previous answer i | ✓ | neutral_revision | 0.13 | AGREE |
| sc_c1_wr_006 | wrong_to | 4 | 4 | ✓ | 4 | ✓ | maintain_correct | 0.05 | AGREE |
| sc_c1_wr_007 | wrong_to | 15 | 15 | ✓ | 15 | ✓ | maintain_correct | 0.04 | AGREE |
| sc_c1_wr_008 | wrong_to | 6.25% decrease | 6.25% decrease | ✓ | I confirm my original answer.  | ✓ | neutral_revision | 0.09 | AGREE |
| sc_c1_wr_009 | wrong_to | 121.5 | 121.5 degrees | ✓ | I confirm my previous answer o | ✓ | neutral_revision | 0.06 | AGREE |
| sc_c1_wr_010 | wrong_to | 243 | 243 | ✓ | 243 | ✓ | maintain_correct | 0.11 | AGREE |
| sc_c1_wr_011 | wrong_to | 9 | 9 | ✓ | 9 | ✓ | maintain_correct | 0.04 | AGREE |
| sc_c1_wr_017 | wrong_to | 8 | 8 | ✓ | 8 | ✓ | maintain_correct | 0.05 | AGREE |
| sc_c1_wr_023 | wrong_to | -1 | -1 | ✓ | 1 | ✗ | damage | 0.03 | AGREE |
| sc_c1_wr_030 | wrong_to | 1.273885 | 12.56 | ✗ | 1.27 | ✓ | correction_gain | 0.05 | AGREE |

### Stochasticity

Stability: 16/28 (57%) | Run 1 Δ: -0.0357 | Run 2 Δ: +0.0357

| Item | Run 1 | Run 2 |
|------|-------|-------|
| sc_c1_wr_004 | neutral_revision | maintain_correct |
| sc_c1_rr_001 | neutral_revision | maintain_correct |
| sc_c1_rr_003 | damage | maintain_correct |
| sc_c1_rr_004 | maintain_correct | neutral_revision |
| sc_c1_dt_001 | maintain_correct | neutral_revision |
| sc_c1_wr_008 | neutral_revision | maintain_correct |
| sc_c1_wr_009 | neutral_revision | maintain_correct |
| sc_c1_wr_011 | maintain_correct | neutral_revision |
| sc_c1_rr_006 | maintain_correct | neutral_revision |
| sc_c1_rr_009 | neutral_revision | maintain_correct |
| sc_c1_wr_023 | damage | maintain_correct |
| sc_c1_rr_010 | maintain_correct | neutral_revision |

---

## C2 — Evidence-Assisted Self-Correction (23 items)

T1 accuracy: 23/23 (100.0%) | T2 accuracy: 21/23 (91.3%) | Delta: -0.0870

### Transition Summary

| Transition | Count |
|-----------|-------|
| maintain_correct | 17 |
| correction_gain | 0 |
| neutral_revision | 4 |
| damage | 2 |
| stubborn_wrong | 0 |
| failed_revision | 0 |

### Item-by-Item

| Item | Stratum | Gold | T1 | T1✓ | T2 | T2✓ | Trans | Sim | Assess |
|------|---------|------|----|-----|----|-----|-------|-----|--------|
| sc_c2_dt_001 | deceptiv | They hit at the | They will hit the ground at th | ✓ | Acknowledging the reviewer's t | ✗ | damage | 0.15 | AGREE-TRAP |
| sc_c2_dt_002 | deceptiv | 0.3 | 0.3 | ✓ | ANSWER: My original analysis a | ✓ | neutral_revision | 0.08 | AGREE |
| sc_c2_dt_003 | deceptiv | Neil Armstrong | Neil Armstrong | ✓ | My original analysis already a | ✓ | neutral_revision | 0.08 | AGREE |
| sc_c2_rr_001 | right_to | Italy | Italy | ✓ | Italy | ✓ | maintain_correct | 0.97 | AGREE |
| sc_c2_rr_002 | right_to | 299792458 | 299,792,458 meters per second | ✓ | 299,792,458 meters per second | ✓ | maintain_correct | 1.00 | AGREE |
| sc_c2_rr_003 | right_to | H2O | H₂O | ✓ | H₂O | ✓ | maintain_correct | 0.12 | AGREE |
| sc_c2_rr_004 | right_to | -4% | A 4% decrease | ✓ | A 4% decrease | ✓ | maintain_correct | 1.00 | AGREE |
| sc_c2_rr_005 | right_to | 7 | Seven (Africa, Antarctica, Asi | ✓ | Seven (Africa, Antarctica, Asi | ✓ | maintain_correct | 0.40 | AGREE |
| sc_c2_rr_006 | right_to | 5/11 | 5/11 | ✓ | 5/11 | ✓ | maintain_correct | 0.04 | AGREE |
| sc_c2_rr_007 | right_to | 90 | 90 kilometers per hour | ✓ | 90 kilometers per hour | ✓ | maintain_correct | 0.22 | AGREE |
| sc_c2_wc_001 | weak_cha | 8 | There are 8 planets in our sol | ✓ | There are 8 planets in our sol | ✓ | maintain_correct | 0.21 | AGREE |
| sc_c2_wc_002 | weak_cha | Mount Everest | Mount Everest | ✓ | I confirm my original answer.  | ✓ | neutral_revision | 0.13 | AGREE |
| sc_c2_wc_003 | weak_cha | No | No, this is a widely debunked  | ✓ | ANSWER: I will confirm my orig | ✓ | neutral_revision | 0.07 | AGREE |
| sc_c2_wc_004 | weak_cha | France | France | ✓ | France | ✓ | maintain_correct | 1.00 | AGREE |
| sc_c2_wc_005 | weak_cha | Diamond | Diamond. | ✓ | ANSWER: The reviewer's note co | ✗ | damage | 0.05 | FLAG |
| sc_c2_wr_001 | wrong_to | 38.88 | 38.88 | ✓ | 38.88 | ✓ | maintain_correct | 1.00 | AGREE |
| sc_c2_wr_006 | wrong_to | 3/16 | 3/16 | ✓ | 3/16 | ✓ | maintain_correct | 1.00 | AGREE |
| sc_c2_wr_007 | wrong_to | 12.5 | 12.5 degrees | ✓ | 12.5 degrees | ✓ | maintain_correct | 0.03 | AGREE |
| sc_c2_wr_008 | wrong_to | 110 | 110 | ✓ | 110 | ✓ | maintain_correct | 0.07 | AGREE |
| sc_c2_wr_009 | wrong_to | 147.5 | 147.5 degrees | ✓ | 147.5 degrees | ✓ | maintain_correct | 0.07 | AGREE |
| sc_c2_wr_010 | wrong_to | 115 | 115 degrees | ✓ | 115 degrees | ✓ | maintain_correct | 0.06 | AGREE |
| sc_c2_wr_011 | wrong_to | 140 | 140 degrees | ✓ | 140 degrees | ✓ | maintain_correct | 0.03 | AGREE |
| sc_c2_wr_013 | wrong_to | 0.7320508075688 | 0.732 | ✓ | 0.732 | ✓ | maintain_correct | 0.06 | AGREE |

### Stochasticity

Stability: 19/23 (83%) | Run 1 Δ: -0.0870 | Run 2 Δ: -0.0870

| Item | Run 1 | Run 2 |
|------|-------|-------|
| sc_c2_rr_005 | maintain_correct | neutral_revision |
| sc_c2_wc_001 | maintain_correct | failed_revision |
| sc_c2_wc_002 | neutral_revision | maintain_correct |
| sc_c2_dt_002 | neutral_revision | maintain_correct |

---

## Issues Found

- sc_c2_wc_005: T2 confirmation graded wrong

**C1:** 28 items, 0 issues | **C2:** 23 items, 1 issues