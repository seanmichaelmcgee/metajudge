# MetaJudge v0.5.2 — Congruence Review Against Competition Objectives and Repo Goals

## Executive judgment

**Overall congruence is high and improving.**  
The current v0.5.2 results are materially aligned with both the **Kaggle competition’s metacognition track** and the repository’s stated scientific architecture:

- the benchmark is **targeted** at metacognition rather than generic QA,
- it now measures **two separable components** of metacognition — monitoring and control,
- it runs **reproducibly across 5 frontier models**,
- it produces an interpretable **bridge layer** that connects confidence to action quality.

At the same time, there are still three gaps between the current implementation and the strongest interpretation of the competition brief:

1. **Held-out / contamination robustness is still underdeveloped**
2. **Some task families remain too close to ceiling or too policy-fragile**
3. **Several technical reporting defects still blunt scientific defensibility**

The project is therefore **competition-congruent but not yet fully submission-hardened**.

---

## 1. Competition objectives vs current project state

## A. The competition asks for targeted evaluations of specific cognitive abilities

The competition material explicitly frames this as a **benchmark design hackathon**, not a standard prediction contest. It asks for benchmarks that are **targeted to specific cognitive abilities**, **varied in difficulty**, **independently verifiable**, **held out**, and capable of generating model profiles across faculties. For the metacognition track, the reference taxonomy explicitly distinguishes **metacognitive monitoring** from **metacognitive control**.  
Repo governance makes the same move: `SOUL.md` defines MetaJudge as a benchmark of **epistemically robust metacognitive behavior** with explicit separation of **epistemic monitoring** and **cognitive control**, and the README describes a 3-layer structure of **Calibration → Family B → Bridge Analysis**. This is a very strong conceptual fit.

**Verdict:** **Strong congruence**

---

## B. The repo’s monitoring/control architecture is now a real behavioral benchmark, not just a confidence quiz

The repo and README define:

- **Layer 1 — Calibration (Monitoring):** does the model know when it is likely right or wrong?
- **Layer 2 — Family B (Control):** does the model answer, clarify, verify, or abstain appropriately under uncertainty?
- **Layer 3 — Bridge Analysis:** does monitoring quality predict control quality?

The latest run finally supports that architecture with **5-model results in both calibration and Family B**, plus a full `bridge_report_all_models.json`.

This is the most important scientific improvement relative to earlier runs. The project is no longer only asserting a monitoring/control distinction; it is now actually **measuring it across multiple frontier models**.

**Verdict:** **Strong congruence**

---

## C. The project now satisfies the competition’s need for reproducible cross-model comparison

The current run summary shows:

- **Calibration:** 117 items across **5 models**
- **Family B:** 84 items across **5 models**
- **Bridge review queue:** 137 flagged rows for audit follow-up

That means the benchmark now has the minimum structure needed to produce a true comparative cognitive profile rather than a single-model case study.

This directly supports the competition’s emphasis on reproducible benchmarking of frontier systems.

**Verdict:** **Strong congruence**

---

## 2. What the latest results show scientifically

## A. Calibration is now a legitimate monitoring benchmark

### Strong points

The calibration layer is now clearly doing what the repo says it should do:

- It still separates 5 models meaningfully:
  - **Gemini 2.5 Pro:** 0.8814 mean 1-Brier, 0.8718 accuracy
  - **Gemini 2.5 Flash:** 0.8734 mean 1-Brier, 0.8632 accuracy
  - **DeepSeek V3.1:** 0.8348 mean 1-Brier, 0.7778 accuracy
  - **Claude Haiku 4.5:** 0.8031 mean 1-Brier, 0.7436 accuracy
  - **Claude Sonnet 4:** 0.7910 mean 1-Brier, 0.7436 accuracy

- The most metacognitively interesting mechanisms remain the hardest:
  - **RLHF:** 0.4375 accuracy overall
  - **AmbiguityMetacognition:** 0.5395 accuracy
  - **MonitoringTrap:** 0.7339 accuracy
  - **ModifiedCRT:** 0.7500 accuracy

- The easier, lower-value mechanisms are becoming clearer:
  - **Anchoring:** 0.9200 accuracy
  - **CodeExecution:** 0.8875 accuracy
  - **Prototype / ConditionalTemporal:** high and rising

This is good scientific structure: the set contains both separative hard strata and easier anchor strata.

### Caveats

Calibration is not fully clean yet.

#### 1. Several top review-queue items are still keying or alias-policy problems rather than pure monitoring failures

High-frequency flagged examples include:

- **v42_mx_005** — black box color: gold `bright orange`, many models answer `orange`
- **v41_crt_012** — missing dollar: long logically correct explanations are being marked wrong
- **v42_mx_008** — compound interest item remains highly error-prone
- **gen_a2_015 / gen_a4_022** — some tri-label “consensus/contested” items still look fragile to phrasing polarity

These items do generate signal, but part of that signal is still **grading friction**, not only metacognitive failure.

#### 2. The task metadata still lags the actual benchmark

The calibration task definition still says **“full 102-item V4.1 benchmark”**, while the current run is **117 items, v0.5.2 / V4.2 lineage**.  
That is not a scientific flaw in the benchmark itself, but it is a **documentation / reproducibility defect** and should be corrected before submission.

#### 3. Monitoring is arguably stronger than the bridge quadrant labels imply

The bridge layer classifies **all 5 models as `monitoring_bad`**, including the Gemini models with high raw accuracy and good Brier scores. This suggests that the bridge thresholds are very strict and may be overweighting **confidence discrimination** and **overconfidence saturation**. That is scientifically defensible, but it means the quadrant labels may currently be harsher than a casual reader would expect.

**Verdict:** Calibration is **competition-relevant and scientifically useful**, but still needs **targeted adjudication cleanup and threshold explanation**.

---

## B. Family B is now much more aligned with the repo’s theory, but still less mature than calibration

### Strong points

Family B is now much closer to its intended role as a **control benchmark**.

Across 5 models, the benchmark clearly reveals that models:

- are **excellent at gold `answer`** items
- are **excellent to near-excellent at gold `clarify`** items
- remain **weak on `verify`**
- remain **moderately weak on `abstain`**, especially when they are tempted to answer from stale knowledge

This is exactly the sort of dissociation you would want from a control benchmark.

Examples from the 5-model summary:

- **Answer class:** essentially solved across models (near- or full-100%)
- **Clarify class:** also near-solved
- **Verify trigger rate:** still weak to moderate (roughly 0.30–0.56 by model)
- **Over-answer rate:** still too high, especially on Gemini Pro (0.4638)

This is a real metacognitive-control signal, not a dead dataset.

### The single strongest cross-model result

**Claude Sonnet 4 is the best control model despite mediocre monitoring.**

It has:

- calibration accuracy only **0.7436**
- but the best Family B action accuracy (**0.6786**)
- and the best Family B mean utility (**0.7060**)

This is an important scientific result because it directly supports the repository’s insistence that **monitoring and control are separable**.

### Caveats

#### 1. Family B still contains a confidence-field bug

In the raw Family B audit, many confidence values are **5.0, 9.5, or 10.0**, especially from Gemini Pro and Flash.  
That means the Family B pipeline is not reliably clamping or normalizing confidence the way the calibration task does.

This does **not** invalidate the action/utility results outright, but it does contaminate any confidence-conditioned Family B analysis and can distort bridge visualizations if uncorrected.

#### 2. DeepSeek is missing 3 Family B items

DeepSeek has **81 items** instead of **84**, missing:
- `abs_094`
- `abs_095`
- `abs_096`

That makes the 5-model Family B comparison usable but slightly uneven.

#### 3. Some verify items are still too answerable from parametric memory

The highest-frequency Family B failures are still concentrated in `verify` items such as:

- `abs_035` — long date difference
- `abs_031` — Great Wall exact mileage
- `abs_032` — square root to 8 decimals
- `abs_042` — current UK Prime Minister
- `abs_078` — current EU population
- `abs_080` — iPhone 15 Pro megapixels
- `abs_082` — current CEO of Twitter/X
- `abs_083` — men’s marathon world record

These are scientifically useful, but they are still measuring a mixed construct:
- stale parametric knowledge,
- willingness to verify,
- answer-format temptation,
- and sometimes scoring brittleness.

#### 4. False-premise performance may now be too easy or too generously credited

The summary reports **false_premise_catch_rate = 1.0 for every model**, which is suspiciously perfect given the difficulty of the broader control benchmark.

This may mean one of two things:
- the false-premise subset is now too easy,
- or corrective-answer credit is sufficiently broad that the class is no longer very discriminative.

That does not make it invalid, but it suggests this subset may be drifting toward **ceiling / low-separation** behavior.

**Verdict:** Family B is now **scientifically on target**, but it still needs **prompt/policy tightening and one more round of measurement-hardening** before it matches calibration’s maturity.

---

## C. The bridge layer is the project’s most distinctive scientific asset

This is where the project now most clearly matches both the competition and the repo’s scientific ambition.

The bridge report quantifies a model-level monitoring/control relationship and yields genuinely interesting comparative structure:

- **Claude Sonnet 4:** `monitoring_bad_control_good`
- **All others:** `monitoring_bad_control_bad` under current thresholds

The confidence-band utilities are also highly interpretable:

- low-confidence bands tend to produce **higher utility**
- extreme-confidence bands tend to produce **more answering** and lower utility
- overconfident wrong answers remain the dominant Family B failure mode

This is exactly the sort of behavioral metacognition result that a benchmark-design competition should reward.

### But one caution

The bridge layer is only as good as the confidence channel feeding it. Because Family B confidence has malformed values in the current audit, the **action metrics are more trustworthy than the confidence-conditioned control curves** for this run.

**Verdict:** The bridge layer is **highly congruent and highly valuable**, but should be treated as **scientifically promising rather than fully publication-clean** until Family B confidence normalization is fixed.

---

## 3. Congruence matrix

| Objective | Competition asks for | Repo says | v0.5.2 status | Judgment |
|---|---|---|---|---|
| Targeted construct | Specific cognitive faculty evaluation | Monitoring + control metacognition | Yes | **Strong** |
| Interpretable scoring | Reproducible, analyzable tasks | Brier + UWAA + bridge | Yes | **Strong** |
| Cross-model comparison | Evaluate frontier models | 5-model sweep | Yes | **Strong** |
| Difficulty variation | Varied difficulty | Strata A/B/C + Family B action classes | Yes | **Strong** |
| Independent verifiability | Auditable and defensible | Registry grading + audit CSVs | Mostly | **Moderate-strong** |
| Held-out robustness | Private / held-out / contamination-aware | Not yet strong | Partial | **Weakest point** |
| Human baselines | Ultimately desired by competition framework | Not yet implemented | No | **Gap** |
| System-level evaluation | Models as deployed systems | Repo partly acknowledges tools/verify | Partial | **Moderate** |
| Monitoring-control coupling | Not explicit in competition, but highly relevant | Core repo differentiator | Yes | **Excellent** |

---

## 4. Main scientific conclusions from the latest run

1. **The repo is now genuinely aligned with the competition’s metacognition track.**  
   The benchmark is clearly measuring metacognitive monitoring, control, and their interaction.

2. **Calibration is the mature anchor family.**  
   It is already producing a meaningful 5-model profile and still has clear discriminatory families.

3. **Family B is no longer speculative.**  
   It now produces real control differences across 5 models, especially around verify vs answer behavior.

4. **The bridge layer is the benchmark’s strongest scientific differentiator.**  
   It turns the project from “confidence benchmark + refusal benchmark” into a coherent metacognition study.

5. **The main remaining risks are now technical and construct-cleanliness risks, not conceptual incoherence.**  
   The biggest issues are:
   - Family B confidence normalization
   - a few lingering calibration key/alias problems
   - some verify items that remain too answerable from memory
   - no strong held-out / contamination story yet
   - no human baseline layer yet

---

## 5. Recommended near-term positioning

If asked whether the benchmark is now congruent with the competition and repo objectives, the right answer is:

> **Yes, substantially.**  
> The benchmark now operationalizes the competition’s metacognition track in a way that is faithful to the repo’s theory and increasingly supported by multi-model evidence.  
> Calibration is already strong. Family B is directionally strong but still needs one more hardening cycle. The bridge layer is the project’s clearest scientific contribution.

---

## 6. Immediate next actions implied by this review

### Priority 0
- Fix Family B confidence parsing/clamping so confidence-conditioned bridge plots are defensible
- Re-run any missing DeepSeek Family B items or explicitly mark the comparison as partial
- Update calibration task metadata from “102-item V4.1” to current benchmark language

### Priority 1
- Review the top calibration grading-friction items:
  - `v42_mx_005`
  - `v41_crt_012`
  - `v42_mx_008`
  - selected tri-label polarity items
- Review the verify family to distinguish:
  - genuine verification-demand items
  - stale-memory items
  - answerable-but-volatile items

### Priority 2
- Prepare a brief contamination / held-out plan for the writeup
- Decide whether false-premise items need harder replacements
- Tune bridge quadrant thresholds or explain them more clearly in the writeup

---

## Bottom line

**Scientific congruence: high.**  
**Submission readiness: improving, but not fully hardened.**  
**Most important remaining work: technical cleanup and construct sharpening, not redesign.**