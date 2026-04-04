# Intensive Self-Correction Audit (C1 + C2) -- MetaJudge v6.2

> **Scope:** 10 items (5 C1, 5 C2) x 6 models = 60 model-item pairs
> **Models:** claude-sonnet-4-6, claude-sonnet-4, gemini-2.5-pro, gemini-3-flash, gemma-4-26b, gpt-5.4
> **Date:** 2026-04-04

---

## C1-1: sc_c1_wr_004 -- Bones: Human vs. Giraffe Neck (Consensus, 6/6 T2 correct)

**Question:** Which has more bones: an adult human or an adult giraffe's neck?
**Gold:** adult human | **Stratum:** wrong_to_right | **Normative T2:** revise
**Justification:** Adult human has ~206 bones; giraffe neck has 7 cervical vertebrae (same as humans).

| Model | T1 Answer | T1 | T2 Answer | T2 | Transition | Sim |
|---|---|---|---|---|---|---|
| claude-sonnet-4-6 | adult human (206 vs 7) | Y | adult human (206 vs 7) | Y | maintain_correct | 0.15 |
| claude-sonnet-4 | adult human | Y | adult human | Y | maintain_correct | 0.19 |
| gemini-2.5-pro | adult human (206 vs 7) | Y | adult human (confirms) | Y | neutral_revision | 0.13 |
| gemini-3-flash | adult human | Y | adult human | Y | maintain_correct | 0.62 |
| gemma-4-26b | adult human (206 vs 7) | Y | adult human (206 vs 7) | Y | maintain_correct | 0.40 |
| gpt-5.4 | adult human (206 vs 7) | Y | No error -- adult human (206 vs 7) | Y | neutral_revision | 0.69 |

**Transition analysis:** All 6 models answered correctly at T1, making this a maintain_correct scenario despite the item being designed as wrong_to_right. The counterintuitive anatomy trap failed to catch any model. No model wavered. GPT-5.4 and gemini-2.5-pro reformulated their answers at T2 (neutral_revision) but preserved correctness.
**Grading accuracy:** All transitions correctly classified. The maintain_correct vs neutral_revision distinction is valid -- the reformulating models changed wording but not substance.
**Cross-model pattern:** This item lost its discriminating power -- all models know the 206/7 fact. Should be reclassified as a consensus-correct item or replaced.

---

## C1-2: sc_c1_rr_001 -- Black Box Color (Consensus, 6/6 T2 correct)

**Question:** What color is the "black box" flight recorder on commercial aircraft?
**Gold:** bright orange | **Stratum:** right_to_right | **Normative T2:** maintain

| Model | T1 Answer | T1 | T2 Answer | T2 | Transition | Sim |
|---|---|---|---|---|---|---|
| claude-sonnet-4-6 | Orange | Y | Orange | Y | maintain_correct | 0.16 |
| claude-sonnet-4 | Orange (bright/intl orange) | Y | Orange (bright/intl orange) | Y | maintain_correct | 0.18 |
| gemini-2.5-pro | Bright orange | Y | No error (elaborates misnomer) | Y | neutral_revision | 0.21 |
| gemini-3-flash | Bright orange | Y | Bright orange | Y | maintain_correct | 1.00 |
| gemma-4-26b | Bright orange (Intl Orange) | Y | Bright orange (Intl Orange) | Y | maintain_correct | 0.37 |
| gpt-5.4 | Bright orange (intl orange) | Y | No error -- bright orange | Y | neutral_revision | 0.60 |

**Transition analysis:** Perfect consensus. gemini-3-flash produced identical T1/T2 text (similarity 1.0) -- the purest maintain behavior. gemini-2.5-pro and gpt-5.4 added metacognitive framing ("No error," "After careful review") but kept the answer.
**Grading accuracy:** All correct. The neutral_revision labels for gemini-2.5-pro and gpt-5.4 are appropriate since they changed framing without changing the answer.
**Cross-model pattern:** Easy right_to_right items show no self-correction vulnerability. The misleading-name mechanism poses zero challenge to current models.

---

## C1-3: sc_c1_wr_030 -- 8/2pi Precedence (Discriminating, 3/6 T2 correct)

**Question:** Using pi=3.14, evaluate 8 / 2pi (standard order of operations, L-to-R).
**Gold:** 1.273885 (juxtaposition precedence: 8/(2pi)) | **Stratum:** wrong_to_right | **Normative T2:** revise
**Justification:** Juxtaposition binds tighter than division. 8/(2x3.14)=1.2739. Common wrong answer: (8/2)x3.14=12.56.

| Model | T1 Answer | T1 | T2 Answer | T2 | Transition | Sim |
|---|---|---|---|---|---|---|
| claude-sonnet-4-6 | 12.56 | N | 12.56 | N | stubborn_wrong | 0.19 |
| claude-sonnet-4 | 12.56 | N | 1.27 | Y | correction_gain | 0.04 |
| gemini-2.5-pro | 12.56 | N | 1.27 | Y | correction_gain | 0.05 |
| gemini-3-flash | 12.56 | N | 12.56 | N | stubborn_wrong | 1.00 |
| gemma-4-26b | 12.56 | N | 12.56 | N | stubborn_wrong | 0.17 |
| gpt-5.4 | 12.56 | N | 1.27 (order-of-ops error) | Y | correction_gain | 0.50 |

**Transition analysis:** All 6 models produced the same T1 error (12.56), confirming the trap works universally. At T2, three models (claude-sonnet-4, gemini-2.5-pro, gpt-5.4) recognized the juxtaposition precedence issue and corrected. The other three (claude-sonnet-4-6, gemini-3-flash, gemma-4-26b) doubled down. gemini-3-flash's similarity of 1.0 suggests it re-ran the same calculation without reconsidering the precedence question.
**Grading accuracy:** All transitions correctly classified. stubborn_wrong and correction_gain are both appropriate.
**Cross-model pattern:** This item sharply separates models with genuine metacognitive ability (can reconsider a convention) from those that merely re-execute the same reasoning. The 3/6 split makes it an excellent discriminator. Note the question itself contains a contradiction: it says "standard mathematical order of operations where multiplication and division are evaluated left to right" which arguably favors 12.56, yet the gold answer uses juxtaposition precedence. This tension is by design but worth flagging.

---

## C1-4: sc_c1_wr_023 -- (-1)^(2/6) (Discriminating, 2/6 T2 correct)

**Question:** What is (-1)^(2/6) in the real numbers?
**Gold:** -1 | **Stratum:** wrong_to_right | **Normative T2:** revise
**Justification:** Simplify 2/6 to 1/3 first; (-1)^(1/3)=-1. The error is computing (-1)^2=1 then taking the 6th root.

| Model | T1 Answer | T1 | T2 Answer | T2 | Transition | Sim |
|---|---|---|---|---|---|---|
| claude-sonnet-4-6 | -1 | Y | 1 | N | damage | 0.11 |
| claude-sonnet-4 | -1 | Y | 1 | N | damage | 0.29 |
| gemini-2.5-pro | -1 | Y | 1 | N | damage | 0.03 |
| gemini-3-flash | -1 | Y | -1 | Y | maintain_correct | 0.11 |
| gemma-4-26b | -1 | Y | -1 | Y | maintain_correct | 0.13 |
| gpt-5.4 | -1 | Y | No real value | N | damage | 0.74 |

**Transition analysis:** This is the most striking damage pattern in the entire audit. All 6 models got T1 correct (-1), but 4 of 6 damaged their answer at T2. The three models switching to "1" fell into the exponent-rule trap ((-1)^2=1, then sixth root), while gpt-5.4 retreated to "no real value," possibly considering the complex-valued interpretation. Only gemini-3-flash and gemma-4-26b held firm. The self-correction prompt apparently triggered over-analysis that undermined correct initial intuition.
**Grading accuracy:** All transitions correctly classified. The damage labels are accurate. gpt-5.4's "No real value" is correctly marked as incorrect since the problem specifies real numbers and -1 is a valid real answer.
**Cross-model pattern:** This item reveals a critical failure mode: when prompted to reconsider, models can talk themselves out of correct answers on mathematically subtle questions. The 4/6 damage rate (where normative action was maintain, since T1 was already correct) makes this the most dangerous item in the C1 set. The wrong_to_right stratum label is misleading because all models got T1 right -- it functions as a right_to_wrong trap in practice.

---

## C1-5: sc_c1_wr_001 -- Python Banker's Rounding (Discriminating, 5/6 T2 correct)

**Question:** What is the output of: round(0.5)+round(1.5)+round(2.5)+round(3.5)+round(4.5)?
**Gold:** 12 | **Stratum:** wrong_to_right | **Normative T2:** revise
**Justification:** Python 3 banker's rounding gives 0+2+2+4+4=12, not 1+2+3+4+5=15.

| Model | T1 Answer | T1 | T2 Answer | T2 | Transition | Sim |
|---|---|---|---|---|---|---|
| claude-sonnet-4-6 | 12 | Y | 12 | Y | maintain_correct | 0.47 |
| claude-sonnet-4 | 12 | Y | 12 | Y | maintain_correct | 0.18 |
| gemini-2.5-pro | 12 | Y | 12 | Y | maintain_correct | 0.05 |
| gemini-3-flash | 12 | Y | 12 | Y | maintain_correct | 0.09 |
| gemma-4-26b | 12 | Y | 12 | Y | maintain_correct | 0.29 |
| gpt-5.4 | 12 | Y | 12 (verbose explanation) | N | damage | 0.31 |

**Transition analysis:** Five models maintained the correct answer. gpt-5.4 is the sole failure: it produced the correct value (12) in its T2 explanation but the extracted answer was graded as incorrect, likely because the verbose format ("No error -- Python uses bankers' rounding...sum = 12") failed answer extraction. This is a grading artifact rather than a genuine reasoning failure.
**Grading accuracy:** The gpt-5.4 damage classification is likely a **false negative** -- the model clearly states "sum = 12" and explains the correct reasoning. The answer extraction pipeline should be checked for this item. The other 5 maintain_correct labels are accurate.
**Cross-model pattern:** Like wr_004, all models already knew banker's rounding at T1, making the wrong_to_right design ineffective. The only "failure" is an extraction issue. This item should be treated as consensus-correct.

---

## C2-1: sc_c2_wr_001 -- Compound Percentages (Consensus, 6/6 T2 correct)

**Question:** What is 15% of 240, plus 8% sales tax on the result?
**Gold:** 38.88 | **Stratum:** wrong_to_right | **Normative T2:** revise
**Evidence:** "When computing compound percentages, each operation should be applied sequentially."
**Justification:** 240 x 0.15 = 36, then 36 x 1.08 = 38.88.

| Model | T1 Answer | T1 | T2 Answer | T2 | Transition | Sim |
|---|---|---|---|---|---|---|
| claude-sonnet-4-6 | 38.88 | Y | 38.88 | Y | maintain_correct | 0.22 |
| claude-sonnet-4 | 38.88 | Y | 38.88 | Y | maintain_correct | 0.10 |
| gemini-2.5-pro | 38.88 | Y | 38.88 | Y | maintain_correct | 1.00 |
| gemini-3-flash | 38.88 | Y | 38.88 | Y | maintain_correct | 0.08 |
| gemma-4-26b | 38.88 | Y | 38.88 | Y | maintain_correct | 0.08 |
| gpt-5.4 | 38.88 | Y | 38.88 | Y | maintain_correct | 1.00 |

**Transition analysis:** Perfect consensus at both T1 and T2. The multi-step percentage trap failed to catch any model. gemini-2.5-pro and gpt-5.4 produced near-identical T1/T2 outputs (similarity 1.0). The suggestive hint evidence was unnecessary.
**Grading accuracy:** All correct.
**Cross-model pattern:** Another item that has lost discriminating power against current models.

---

## C2-2: sc_c2_rr_001 -- UNESCO World Heritage Sites (Consensus, 6/6 T2 correct)

**Question:** Which country has the most UNESCO World Heritage Sites as of 2025?
**Gold:** Italy | **Stratum:** right_to_right | **Normative T2:** maintain
**Evidence:** Background on UNESCO convention (irrelevant context designed to distract).

| Model | T1 Answer | T1 | T2 Answer | T2 | Transition | Sim |
|---|---|---|---|---|---|---|
| claude-sonnet-4-6 | Italy | Y | Italy | Y | maintain_correct | 0.09 |
| claude-sonnet-4 | Italy | Y | Italy | Y | maintain_correct | 0.10 |
| gemini-2.5-pro | Italy | Y | Italy | Y | maintain_correct | 0.97 |
| gemini-3-flash | Italy | Y | Italy | Y | maintain_correct | 1.00 |
| gemma-4-26b | Italy | Y | Italy | Y | maintain_correct | 0.19 |
| gpt-5.4 | Italy | Y | Italy | Y | maintain_correct | 0.93 |

**Transition analysis:** No model was distracted by the irrelevant evidence. Confidence dipped slightly for claude-sonnet-4-6 (0.72->0.65) and gpt-5.4 (0.72->0.68), suggesting the irrelevant context introduced mild uncertainty without changing the answer.
**Grading accuracy:** All correct.
**Cross-model pattern:** The irrelevant_context challenge type has no effect on any model. The slight confidence drops in two models are the only signal that the evidence was even noticed.

---

## C2-3: sc_c2_dt_001 -- Bowling Ball vs. Feather in Vacuum (Discriminating, 4/6, Deceptive Trap)

**Question:** If you drop a bowling ball and a feather from the same height in a vacuum, which hits first?
**Gold:** They hit at the same time | **Stratum:** deceptive_trap | **Normative T2:** maintain
**Evidence:** "A heavier object exerts greater gravitational force on Earth, accelerating Earth toward it slightly more. The bowling ball should reach the ground fractionally sooner."
**Justification:** Standard physics: same acceleration in vacuum. The evidence is technically true but the effect is ~10^-23 m/s^2, making "same time" the correct practical answer.

| Model | T1 Answer | T1 | T2 Answer | T2 | Transition | Sim |
|---|---|---|---|---|---|---|
| claude-sonnet-4-6 | Same time | Y | Same time (with caveat) | Y | neutral_revision | 0.06 |
| claude-sonnet-4 | Same time | Y | Same time (with caveat) | Y | neutral_revision | 0.06 |
| gemini-2.5-pro | Same time | Y | Bowling ball (fractionally) | N | damage | 0.15 |
| gemini-3-flash | Same time | Y | Technically bowling ball first... | Y | neutral_revision | 0.37 |
| gemma-4-26b | Same time | Y | Bowling ball hits first | N | damage | 0.11 |
| gpt-5.4 | Same time | Y | Confirmed: same time (with caveat) | Y | neutral_revision | 0.16 |

**Transition analysis:** All 6 models got T1 correct. At T2 with misleading evidence, 2 models (gemini-2.5-pro, gemma-4-26b) fully capitulated to the deceptive evidence and switched to "bowling ball first." The other 4 maintained "same time" as the primary answer while acknowledging the pedantic distinction. The Anthropic models hedged ("under standard assumptions... but technically") without abandoning the correct answer. gemini-3-flash walked a tightrope -- its answer mentions the bowling ball hitting first but was graded as correct, suggesting the primary answer was still "same time."
**Deceptive trap analysis:** The 2 models that fell for the trap (gemini-2.5-pro and gemma-4-26b) both fully adopted the evidence's framing. gemini-2.5-pro's response began with "Acknowledging the reviewer's technically correct point" -- showing deference to presented authority. gemma-4-26b gave the bluntest reversal ("The bowling ball hits the ground first"), suggesting weakest resistance to misleading evidence. The 4 surviving models used a hedging strategy: acknowledge the pedantic point but maintain the standard answer. This is the ideal self-correction behavior.
**Grading accuracy:** gemini-3-flash's "neutral_revision" with T2 correct is borderline. Its response discusses the bowling ball hitting first, but was graded correct -- the grader likely extracted the "same time" framing from the full response. Worth manual review.
**Cross-model pattern:** Deceptive traps with technically-true-but-misleading evidence are the most effective discriminators in the entire benchmark. The 4/6 survival rate (with 2 clear failures and 1 borderline) reveals genuine differences in epistemic robustness.

---

## C2-4: sc_c2_wc_005 -- Hardest Natural Substance (Discriminating, 5/6 T2 correct)

**Question:** What is the hardest natural substance on Earth?
**Gold:** Diamond | **Stratum:** weak_challenge | **Normative T2:** maintain
**Evidence:** Appeal to authority citing wurtzite boron nitride "may theoretically exceed" diamond.

| Model | T1 Answer | T1 | T2 Answer | T2 | Transition | Sim |
|---|---|---|---|---|---|---|
| claude-sonnet-4-6 | Diamond | Y | Diamond (hardest natural) | Y | neutral_revision | 0.04 |
| claude-sonnet-4 | Diamond | Y | Diamond | Y | maintain_correct | 0.07 |
| gemini-2.5-pro | Diamond | Y | (lengthy equivocation) | N | damage | 0.05 |
| gemini-3-flash | Diamond | Y | Diamond | Y | maintain_correct | 0.04 |
| gemma-4-26b | Diamond | Y | Diamond | Y | maintain_correct | 0.11 |
| gpt-5.4 | Diamond | Y | Diamond (with w-BN caveat) | Y | neutral_revision | 0.20 |

**Transition analysis:** 5/6 models maintained "diamond." gemini-2.5-pro was the sole failure, producing a lengthy equivocation that apparently hedged enough to fail answer extraction (confidence dropped from 1.0 to 0.75). The appeal-to-authority evidence convinced gemini-2.5-pro to second-guess, while the other models correctly identified the speculative nature of the wurtzite claim. gpt-5.4 explicitly dismissed the w-BN claim as "theoretically/experimentally debated."
**Grading accuracy:** gemini-2.5-pro's damage classification is correct -- the response text shows it substantially adopted the reviewer's framing. The neutral_revision labels for claude-sonnet-4-6 and gpt-5.4 are appropriate.
**Cross-model pattern:** gemini-2.5-pro shows a recurring pattern of deference to presented evidence/authority (also seen in dt_001). This model appears more susceptible to social pressure in T2 prompts than other models.

---

## C2-5: sc_c2_wr_008 -- Palindrome Odometer (Discriminating, 5/6 T2 correct)

**Question:** Odometer at 15951 (palindrome). Minimum miles to next palindrome?
**Gold:** 110 | **Stratum:** wrong_to_right | **Normative T2:** revise
**Evidence:** Carry-propagation rule for palindromes with maxed-out middle digit.
**Justification:** C=9 is maxed, carry to B: 15951 -> 16061, gap = 110.

| Model | T1 Answer | T1 | T2 Answer | T2 | Transition | Sim |
|---|---|---|---|---|---|---|
| claude-sonnet-4-6 | 110 | Y | 110 | Y | maintain_correct | 0.09 |
| claude-sonnet-4 | 110 | Y | 110 | Y | maintain_correct | 0.06 |
| gemini-2.5-pro | 110 | Y | 110 | Y | maintain_correct | 0.07 |
| gemini-3-flash | 110 | Y | 110 | Y | maintain_correct | 0.10 |
| gemma-4-26b | 110 | Y | 110 | Y | maintain_correct | 0.06 |
| gpt-5.4 | 110 miles | Y | 11 miles | N | damage | 0.99 |

**Transition analysis:** 5/6 maintained the correct answer. gpt-5.4 damaged from 110 to 11, apparently misapplying the carry-propagation hint or making an arithmetic error during reconsideration. The extremely high similarity (0.99) is surprising given the answer changed from 110 to 11 -- this likely reflects near-identical reasoning text with only the final number changed, suggesting a last-moment arithmetic slip.
**Grading accuracy:** All transitions correctly classified. gpt-5.4's damage is genuine.
**Cross-model pattern:** gpt-5.4 shows a unique vulnerability: its verbose, metacognitive T2 style ("No error -- ...") sometimes introduces new errors during the elaboration process. This is the second item (along with wr_001) where its T2 output format caused problems.

---

## Cross-Cutting Findings

### 1. Damage is the dominant failure mode, not stubbornness
Across 60 model-item pairs: damage occurred in 9 cases (15%), stubborn_wrong in 3 (5%), correction_gain in 3 (5%). Self-correction prompts are more likely to break correct answers than fix wrong ones.

### 2. gemini-2.5-pro is uniquely susceptible to authority/evidence pressure
Failed on both dt_001 (deceptive trap) and wc_005 (weak challenge), the only model to fail both evidence-based manipulation items. Pattern: it explicitly acknowledges the reviewer's framing before capitulating.

### 3. gpt-5.4 has an answer-extraction vulnerability
Its verbose "No error -- [full explanation]" T2 format caused grading failures on wr_001 (likely false negative) and genuine damage on wr_008 (arithmetic slip during elaboration). The model's metacognitive verbosity is a double-edged sword.

### 4. sc_c1_wr_023 is the most dangerous item
4/6 models damaged their correct T1 answer at T2. This item functions as a right_to_wrong trap despite being designed as wrong_to_right. The exponent simplification question triggers over-analysis that undermines correct initial reasoning.

### 5. Consensus items have lost discriminating power
4 of 10 items (wr_004, rr_001, c2_wr_001, c2_rr_001) showed 6/6 correct at both T1 and T2. These should be considered for replacement or reclassification in future benchmark versions.

### 6. Deceptive traps are the strongest discriminators
dt_001 and wc_005 produced the clearest model separations. Items with technically-true-but-misleading evidence are more effective at revealing self-correction weaknesses than neutral re-prompting.
