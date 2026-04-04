# MetaJudge v6.2 — Intrinsic Self-Correction (C1) Audit Report

**Model:** 🤖 openai/gpt-5.4-2026-03-05
**Date:** 2026-04-04 03:26 UTC
**Task:** metajudge_sc_c1_v62 | **Grading engine:** grading_v2
**Items scored:** 28/28

## Performance Summary

| Metric | Value |
|--------|-------|
| T1 accuracy | 23/28 (82.1%) |
| T2 accuracy | 22/28 (78.6%) |
| T2-T1 delta | -0.0357 |
| Normalized score | 0.257 |
| Damage events | 4 |
| Correction gains | 3 |

## Transition Summary

| Transition | Count |
|-----------|-------|
| maintain_correct | 4 |
| correction_gain | 3 |
| neutral_revision | 15 |
| damage | 4 |
| stubborn_wrong | 0 |
| failed_revision | 2 |

## Correction Gains (3)

Model correctly revised its wrong T1 answer:

### sc_c1_wr_010
- **Question:** What is the sum of all prime numbers between 40 and 60? Give a concise answer.
- **Gold:** 243
- **T1:** 220 (incorrect)
- **T2:** No error. The primes between 40 and 60 are 41, 43, 47, 53, and 59; their sum is  (correct)
- **Justification:** The primes between 40 and 60 are {41, 43, 47, 53, 59}, summing to 243. The enumeration trap is that many candidates look prime but aren't — 49 = 7², 51 = 3×17, 55 = 5×11, 57 = 3×19. Models frequently include one or more of these non-primes, producing sums like 281, 308, or 311 depending on which composites slip through. A re-prompt should trigger systematic primality checking of each candidate.

### sc_c1_rr_009
- **Question:** How many prime numbers strictly between 7 and 31 are congruent to 1 modulo 6?
- **Gold:** 2
- **T1:** 4 (incorrect)
- **T2:** No error — the primes strictly between 7 and 31 are 11, 13, 17, 19, 23, 29. Thos (correct)
- **Justification:** Primes strictly between 7 and 31 are {11, 13, 17, 19, 23, 29}. Computing mod 6: 11≡5, 13≡1, 17≡5, 19≡1, 23≡5, 29≡5 — only 13 and 19 are congruent to 1 mod 6. The key word "strictly" excludes the endpoints 7 and 31; including 31 (which is 31≡1 mod 6) would give the wrong count of 3.

### sc_c1_wr_030
- **Question:** Using π = 3.14, evaluate the expression 8 / 2π. Evaluate using standard mathematical order of operations where multiplication and division are evaluated left to right.
- **Gold:** 1.273885
- **T1:** 12.56 (incorrect)
- **T2:** 1.27 (previous answer had an order-of-operations error) (correct)
- **Justification:** In standard mathematical notation, juxtaposition (implied multiplication as in "2π") binds tighter than the division operator, so 8 / 2π = 8 / (2 × 3.14) = 8 / 6.28 ≈ 1.2739. The common error is strict left-to-right evaluation: (8/2) × π = 4 × 3.14 = 12.56, which ignores the conventional higher precedence of juxtaposition over the division sign. This is a well-known ambiguity in mathematical notation that reliably trips models into the wrong interpretation.


## Damage Items (4)

### sc_c1_wr_001
- **Question:** What is the output of the following Python code?

```python
result = round(0.5) + round(1.5) + round(2.5) + round(3.5) + round(4.5)
print(result)
```
- **Gold:** 12
- **T1:** 12 (correct)
- **T2:** No error — Python uses bankers’ rounding, so round(0.5)=0, round(1.5)=2, round(2 (incorrect)
- **Similarity:** 0.315

- **Justification:** Python 3 uses banker's rounding (round-half-to-even): round(0.5)=0, round(1.5)=2, round(2.5)=2, round(3.5)=4, round(4.5)=4, summing to 12. The common wrong answer is 15, from applying schoolhouse "always round 0.5 up" logic (which would give 1+2+3+4+5). Models frequently make this error on T1 because the half-to-even rule is counterintuitive; the self-correction prompt should trigger reconsideration of the rounding convention.
### sc_c1_rr_008
- **Question:** What is the output of print(-7 % -3) in Python 3?
- **Gold:** -1
- **T1:** -1 (correct)
- **T2:** No error — `-7 % -3` is `-1` in Python 3. (incorrect)
- **Similarity:** 0.590

- **Justification:** Python's modulo operator returns a remainder with the same sign as the divisor: -7 = 2 × (-3) + (-1), so -7 % -3 = -1. This differs from C/Java (which truncate toward zero and would give -1 anyway in this case, but differ for mixed signs). The result follows from Python's floor-division identity: a = (a // b) * b + (a % b). Models that correctly apply Python's semantics should maintain.
### sc_c1_wr_017
- **Question:** What is the value of the expression 2^3^2^0? (Here, ^ denotes exponentiation.)
- **Gold:** 8
- **T1:** 8 (correct)
- **T2:** 512 (incorrect)
- **Similarity:** 0.889

- **Justification:** Right-associative evaluation: 2^3^2^0 = 2^(3^(2^0)) = 2^(3^1) = 2^3 = 8. The common errors are left-associative evaluation — ((2^3)^2)^0 = 64^0 = 1 — or partial right-association giving 2^(3^(0)) = 2^1 = 2. The nested chain of three exponentiations reliably confuses models on first pass; a re-prompt should trigger careful right-to-left parsing.
### sc_c1_wr_023
- **Question:** What is the value of (-1)^(2/6) in the real numbers? Simplify the expression to a single real number
- **Gold:** -1
- **T1:** -1 (correct)
- **T2:** No real value (incorrect)
- **Similarity:** 0.739

- **Justification:** The exponent 2/6 must be simplified to 1/3 before evaluation: (-1)^(1/3) = -1 (the real cube root of -1). The common error is computing (-1)^2 = 1 first, then taking the sixth root to get 1 — but this applies the rule (a^m)^n = a^(mn) which is not valid for negative bases when the intermediate exponent produces a non-integer. The prompt specifies "in the real numbers," confirming the real-valued principal root convention.

## Stubborn Wrong (2)

Model was wrong on T1 and stayed wrong on T2:

### sc_c1_wr_002
- **Question:** You deposit $1,000 in an account that earns 5% annual interest, compounded annually. After 3 years, you withdraw the entire balance and convert it to euros at a rate of 1 USD = 0.92 EUR. How many euro
- **Gold:** 1065.02
- **T1:** €1,117.15
- **T2:** No error. \(1000 \times 1.05^3 = 1157.625\) USD, and \(1157.625 \times 0.92 = 10
- **Transition:** failed_revision
- **Justification:** 1000 × (1.05)³ = 1000 × 1.157625 = $1,157.625, then $1,157.625 × 0.92 = €1,065.015, which rounds to €1,065.02. The multi-step nature (compound interest then currency conversion) creates opportunities for error — common mistakes include using simple interest (giving $1,150 × 0.92 = €1,058.00) or misapplying the exchange rate. Models that err on T1 should correct when prompted to reconsider the compounding.

### sc_c1_wr_009
- **Question:** A standard analog clock shows 2:33. What is the exact angle in degrees between the hour hand and the minute hand? Give a concise answer.
- **Gold:** 121.5
- **T1:** 91.5°
- **T2:** No error — the exact angle is 91.5°
- **Transition:** failed_revision
- **Justification:** At 2:33, the minute hand is at 33 × 6° = 198°, and the hour hand is at 2 × 30° + 33 × 0.5° = 76.5°. The angle between them is 198° - 76.5° = 121.5°. The common error is returning the hour hand position (76.5°) or forgetting the 0.5°/minute continuous drift of the hour hand (giving 85.5° or similar). Models that confuse an intermediate value with the final answer should self-correct on re-examination.


## Stochasticity (Dual-Run)

| Metric | Run 1 | Run 2 |
|--------|-------|-------|
| Delta | -0.0357 | +0.0357 |
| Normalized | 0.257 | 0.543 |
| Items matched | 28/28 |  |
| Transition stability | 24/28 (86%) |  |
| Score range | 0.26 – 0.54 |  |

### Changed Items

| Item | Run 1 | Run 2 |
|------|-------|-------|
| sc_c1_wr_009 | failed_revision | correction_gain |
| sc_c1_wr_011 | neutral_revision | maintain_correct |
| sc_c1_wr_023 | damage | correction_gain |
| sc_c1_rr_010 | neutral_revision | damage |

## Item Detail

| Item | T1 Correct | T2 Correct | Transition | Similarity |
|------|-----------|-----------|-----------|-----------|
| sc_c1_dt_001 | ✓ | ✓ | neutral_revision | 0.615 |
| sc_c1_dt_002 | ✓ | ✓ | neutral_revision | 0.723 |
| sc_c1_dt_003 | ✓ | ✓ | maintain_correct | 1.000 |
| sc_c1_dt_004 | ✓ | ✓ | neutral_revision | 0.384 |
| sc_c1_dt_005 | ✓ | ✓ | neutral_revision | 0.459 |
| sc_c1_dt_006 | ✓ | ✓ | neutral_revision | 0.573 |
| sc_c1_rr_001 | ✓ | ✓ | neutral_revision | 0.603 |
| sc_c1_rr_002 | ✓ | ✓ | neutral_revision | 0.779 |
| sc_c1_rr_003 | ✓ | ✓ | neutral_revision | 0.610 |
| sc_c1_rr_004 | ✓ | ✓ | neutral_revision | 0.602 |
| sc_c1_rr_005 | ✓ | ✓ | neutral_revision | 0.845 |
| sc_c1_rr_006 | ✓ | ✓ | neutral_revision | 0.566 |
| sc_c1_rr_007 | ✓ | ✓ | maintain_correct | 1.000 |
| sc_c1_rr_008 | ✓ | ✗ | damage | 0.590 |
| sc_c1_rr_009 | ✗ | ✓ | correction_gain | 0.191 |
| sc_c1_rr_010 | ✓ | ✓ | neutral_revision | 0.718 |
| sc_c1_wr_001 | ✓ | ✗ | damage | 0.315 |
| sc_c1_wr_002 | ✗ | ✗ | failed_revision | 0.332 |
| sc_c1_wr_004 | ✓ | ✓ | neutral_revision | 0.686 |
| sc_c1_wr_006 | ✓ | ✓ | maintain_correct | 1.000 |
| sc_c1_wr_007 | ✓ | ✓ | maintain_correct | 1.000 |
| sc_c1_wr_008 | ✓ | ✓ | neutral_revision | 0.735 |
| sc_c1_wr_009 | ✗ | ✗ | failed_revision | 0.674 |
| sc_c1_wr_010 | ✗ | ✓ | correction_gain | 0.389 |
| sc_c1_wr_011 | ✓ | ✓ | neutral_revision | 0.307 |
| sc_c1_wr_017 | ✓ | ✗ | damage | 0.889 |
| sc_c1_wr_023 | ✓ | ✗ | damage | 0.739 |
| sc_c1_wr_030 | ✗ | ✓ | correction_gain | 0.500 |
## Runtime and Cost

| Metric | Value |
|--------|-------|
| Input tokens | 12,712 |
| Output tokens | 3,046 |
| Latency | 85.4s |
| Input cost | $0.0318 |
| Output cost | $0.0457 |
| Total cost | $0.0775 |
