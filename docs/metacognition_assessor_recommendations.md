# Recommended Changes to the MetaJudge-AGI Metacognition Architecture

**Prepared for:** MetaJudge-AGI implementation team  
**Date:** 2026-03-18  
**Status:** Architectural revision memo for implementation sprint

---

## Executive summary

The current production architecture is a **good benchmark scaffold** but not yet a clean metacognition benchmark. Its main strength is that it already separates several practically important behaviors: calibration, abstention, self-correction, source awareness, and strategy adaptation. Its main weakness is that some families rely too heavily on **self-reports about internal state** rather than on **behavioral evidence that the model monitored or regulated its own cognition**.

The recommended revision is **not** to discard the architecture. It is to **tighten the construct** and make the suite explicitly about **epistemically robust metacognitive behavior in LLMs**. In practice, that means:

1. Keep **calibration** as the anchor family.
2. Keep **selective abstention / verification** as a second core family.
3. Rework **self-correction** so it distinguishes **intrinsic correction** from **evidence-assisted correction**.
4. Demote or redesign **source awareness** so it measures **verifiable evidence attribution / grounding behavior**, not post hoc provenance narration.
5. Redesign **strategy adaptation** into **control-policy adaptation**, scored behaviorally rather than by agreement with a hand-authored “expected strategy.”
6. Report the benchmark on **two top-level axes**:
   - **Epistemic monitoring**
   - **Cognitive control / regulation**

This preserves the current wrapper-task implementation strategy while making the benchmark materially more defensible in light of both classical metacognition theory and recent LLM uncertainty / self-correction findings.

---

## The four core references I would use

These are the four references I would treat as the most decision-relevant for this benchmark revision.

### 1) Nelson & Narens (1990)
**Thomas O. Nelson and Louis Narens. _Metamemory: A Theoretical Framework and New Findings._ 1990.**

Why it matters here:
- This is the clearest classical account of metacognition as an interaction between a **meta-level** and an **object-level**.
- It distinguishes **monitoring** from **control** and therefore gives the benchmark its most defensible architectural split.
- It also cautions that subjective reports are only one route to operationalizing monitoring; control should usually be inferred from behavior.

Architectural consequence:
- The benchmark should be organized explicitly into **epistemic monitoring** and **cognitive control/regulation**, not treated as a flat bag of metacognitive behaviors.

### 2) Kadavath et al. (2022)
**Saurav Kadavath et al. _Language Models (Mostly) Know What They Know._ arXiv, 2022.**

Why it matters here:
- This is one of the foundational LLM papers for self-evaluation.
- It shows that models can produce useful estimates such as **P(True)** and **P(IK)** under the right setup.
- It supports the inclusion of calibration-like families, but also shows that some self-knowledge signals are more stable than others and may degrade out of distribution.

Architectural consequence:
- Keep calibration.
- Treat “I know / I do not know” style signals as potentially useful but not universally reliable.
- Prefer tasks where confidence is behaviorally tied to correctness or selective action.

### 3) Xiong et al. (ICLR 2024)
**Miao Xiong et al. _Can LLMs Express Their Uncertainty? An Empirical Evaluation of Confidence Elicitation in LLMs._ ICLR 2024.**

Why it matters here:
- It is one of the strongest empirical papers on **verbalized confidence** in black-box LLM settings.
- It shows that LLMs tend to be **overconfident when verbalizing confidence**.
- It also shows that prompting method, aggregation method, and sampling setup can change the quality of the uncertainty signal.

Architectural consequence:
- Confidence should be scored, but **free-text explanations of uncertainty should not be trusted as primary evidence of metacognition**.
- Calibration design should assume that verbalized confidence is gameable and prompt-sensitive.
- The benchmark should score **behavior under uncertainty**, not only statements about uncertainty.

### 4) Huang et al. (ICLR 2024)
**Jiaxin Huang et al. _Large Language Models Cannot Self-Correct Reasoning Yet._ ICLR 2024.**

Why it matters here:
- This is the most useful corrective paper for the current self-correction family.
- It argues that many apparent self-correction gains are artifacts of **oracle labels**, **unfair baselines**, or **extra responses**, and that intrinsic self-correction often underperforms careful baselines.

Architectural consequence:
- The benchmark must distinguish:
  - **intrinsic self-correction**
  - **weakly prompted review**
  - **evidence-assisted correction**
- “Correction” should not get credit merely because the second turn changed the answer.
- The suite should compare correction against strong non-correction baselines at equal budget.

### Supporting reference consulted but not treated as one of the four core anchors
**Jiahui Geng et al. _A Survey of Confidence Estimation and Calibration in Large Language Models._ NAACL 2024.**

Use:
- Good for terminology, method taxonomy, and evaluation pitfalls.
- I would use it as a secondary mapping document, not as the main source of architectural decisions.

---

## How the literature changes the critique of the current plan

The original critique remains basically correct, but the literature sharpens it in three important ways.

### 1) The monitoring / control split should be made explicit
The current plan informally mixes monitoring tasks (confidence, abstention, source reporting) with control tasks (self-correction, strategy adaptation). Nelson & Narens gives a cleaner framing: **monitoring supplies information about one’s cognitive state; control uses that information to change behavior**. The architecture should adopt that split formally.

### 2) Calibration is the most defensible family and should remain central
Kadavath and Xiong together support keeping calibration as the benchmark anchor. Calibration is not perfect metacognition, but it is the most behaviorally grounded and easiest-to-validate operational proxy in LLMs. This is the part of the architecture that is already closest to being scientifically defensible.

### 3) Self-reports about source and strategy are weaker than they look
The current source-awareness and strategy-adaptation families assume that a model can reliably narrate where an answer came from or which strategy it chose. That is much less well supported than confidence scoring. The LLM literature is stronger on uncertainty and weakly supported on faithful self-report. Those families should therefore move away from “tell us what happened internally” and toward “show us behavior that implies monitoring or control.”

### 4) Self-correction needs stricter evaluation boundaries
Huang et al. makes it unsafe to treat any two-turn improvement as evidence of metacognitive regulation. The architecture should separate true review from externally induced repair and should compare at equal inference budget.

---

## What should be kept from the current plan

The following parts of the existing architecture are good and should be preserved.

### Keep the overall wrapper pattern
The single exported `@kbench.task` wrapper that internally evaluates subtasks is sound and aligns with the verified SDK behavior.

### Keep per-family modularity
The separate files, cached family evaluation blocks, and family-level aggregation are excellent for testability and ablations.

### Keep calibration as the first implementation slice
This is still the correct first slice because it is the cleanest family, lowest-turn-cost, and best aligned with current literature.

### Keep the idea of multiple families
The benchmark should remain multi-family. No single cheap policy should dominate the score.

### Keep cost-awareness and the bundled dataset design
The planned evaluation size and quota sensitivity are practical and should remain part of the production plan.

---

## Recommended architectural changes

## 1. Reframe the benchmark claim

### Current implicit claim
“Metacognition benchmark for LLMs.”

### Recommended claim
**“Benchmark of epistemically robust metacognitive behavior in LLMs, with explicit separation of epistemic monitoring and cognitive control.”**

Why:
- This is more scientifically defensible.
- It avoids overstating what the benchmark measures.
- It still supports the competition’s practical goal of ranking systems by reflective reliability.

---

## 2. Replace the flat family list with two top-level axes

## Axis I — Epistemic Monitoring
These tasks ask whether the model tracks the reliability and status of its own cognition.

1. **Calibration** — keep as core
2. **Selective abstention / verification / clarification** — keep as core
3. **Evidence attribution / grounding sensitivity** — replace current source-awareness family with this

## Axis II — Cognitive Control / Regulation
These tasks ask whether the model uses monitoring information to change behavior productively.

4. **Self-correction** — split into intrinsic and evidence-assisted modes
5. **Control-policy adaptation** — behavioral replacement for current strategy-adaptation family

This gives the benchmark a clearer scientific story and cleaner score reporting.

---

## 3. Family-by-family revisions

## Family A — Confidence Calibration
### Recommendation
**Keep this family with only light revisions.**

### Why it is robust enough to keep
- It has the clearest objective target: correctness vs. confidence.
- It can be evaluated with standard measures such as Brier score, ECE, AUROC for failure prediction, selective risk, and overconfidence rate.
- It is well aligned with the most mature LLM metacognition-adjacent literature.

### Changes to make
1. Keep `answer` and `confidence` as the only scored outputs.
2. Move `reason_for_uncertainty` and `would_verify_if_possible` to **unscored diagnostics**.
3. Add hidden item groups for:
   - in-domain easy factual items
   - deceptive items
   - calibration stressors under distractors / misleading context
4. Report at least these diagnostics:
   - mean accuracy
   - Brier score
   - ECE
   - AUROC for failure prediction
   - overconfidence gap on wrong answers
5. Add **coverage-conditioned accuracy** so confidence is linked to selective answering utility.

### Revised schema
```python
@dataclass
class CalibrationResponse:
    answer: str
    confidence: float  # scored
    reason_for_uncertainty: str = ""   # diagnostic only
    would_verify_if_possible: bool = False  # diagnostic only
```

### Scoring recommendation
Keep the current confidence-aware scoring, but ensure the benchmark also records classical calibration diagnostics for offline analysis.

---

## Family B — Selective Abstention / Verification / Clarification
### Recommendation
**Keep this family, but tighten the action ontology and score it as selective prediction / decision policy.**

### Why
This is the best monitoring-to-action bridge in the current plan. It tests whether the model behaves differently when the question is answerable, underspecified, ambiguous, or not answerable from available information.

### Changes to make
1. Restrict the allowed actions to an ontology with cleaner evaluation:
   - `answer`
   - `ask_clarifying_question`
   - `abstain`
   - `verify_needed`
2. Ensure each item has a defensible optimal action, reviewed by humans.
3. Score not only utility but also:
   - answer accuracy on answered items
   - abstention precision on truly unsafe items
   - clarification precision on underspecified items
   - coverage / risk curves
4. Add explicit cost penalties for “safe but useless” policies that over-abstain.

### Revised schema
```python
@dataclass
class AbstentionResponse:
    decision: str
    answer: str = ""
    confidence: float = 0.0
    clarification_request: str = ""  # optional; diagnostic or weakly scored
    abstention_reason: str = ""      # diagnostic only
```

### Design note
This family should be treated as part of **epistemic monitoring**, not merely utility engineering.

---

## Family C — Self-Correction
### Recommendation
**Keep the family, but split it into two subfamilies and make the distinction explicit.**

### Subfamily C1 — Intrinsic self-correction
Turn 2 gives only a generic instruction to review or check the prior answer.

This tests whether the model can detect and repair an error with no new evidence.

### Subfamily C2 — Evidence-assisted correction
Turn 2 provides a weak contradiction, hint, or targeted evidence.

This tests whether the model uses external cues appropriately without blindly flipping.

### Why this change is necessary
Huang et al. shows that many apparent self-correction gains collapse once oracle signals and unfair baselines are removed. A single blended self-correction family will overstate what is being measured.

### Changes to make
1. Separate intrinsic from assisted correction in the dataset and scorebook.
2. Compare against same-budget baselines when possible.
3. Reward improvement **only when**:
   - incorrect becomes correct, or
   - confidence appropriately drops on unresolved review.
4. Penalize:
   - breaking a previously correct answer
   - flipping under weak challenge without sufficient evidence
   - high confidence after failed review
5. Make `suspected_error_type` and `what_changed` diagnostic only unless you have a validated gold label set.

### Revised schema
```python
@dataclass
class SelfCorrectionResponse:
    revised_answer: str
    revised_confidence: float
    revise_decision: str            # keep | revise | unresolved
    is_likely_wrong: bool = False   # diagnostic or lightly scored
    suspected_error_type: str = "" # diagnostic only
    what_changed: str = ""         # diagnostic only
```

### Scoring recommendation
Use separate scores for:
- **intrinsic correction gain**
- **evidence-assisted correction gain**
- **damage rate** (correct → incorrect after review)
- **confidence repair quality**

---

## Family D — Replace “Source Awareness” with “Evidence Attribution / Grounding Sensitivity”
### Recommendation
**Do not keep the current source-awareness family in its present form. Replace it.**

### Why the current version is weak
The current family assumes you can assign a single gold label such as `prompt`, `inference`, `memory`, `guess`, or `unresolved`, and then score whether the model names the same source. That is not a robust operationalization of metacognition. Much of it invites plausible post hoc narration.

### What to replace it with
A more valid family is:

**Evidence Attribution / Grounding Sensitivity**

This should test whether the model:
1. cites prompt-local evidence when prompt evidence exists,
2. refrains from pretending the prompt contains support when it does not,
3. distinguishes answering from quoting,
4. becomes less confident when required support is absent.

### Allowed item types
- passage-supported QA with extractable support span
- prompt-evidence contradiction items
- answerable-from-memory but not from prompt items
- support-required items where unsupported answers should trigger lower confidence or abstention

### Revised schema
```python
@dataclass
class GroundingResponse:
    answer: str
    confidence: float
    evidence_mode: str            # prompt_evidence | no_prompt_evidence | uncertain
    supporting_span: str = ""
```

### Scoring recommendation
Score behaviorally:
- answer correctness
- correct detection of whether prompt evidence exists
- support span validity when evidence is claimed
- abstention / confidence drop when support is absent

### Important claim change
This is no longer “the model knows the true source of its cognition.”
It is “the model behaves appropriately with respect to the presence or absence of supporting evidence.”
That is much stronger scientifically.

---

## Family E — Replace “Strategy Adaptation” with “Control-Policy Adaptation”
### Recommendation
**Keep the spirit, but redesign the family so that it scores adaptive control rather than author-agreement on a named strategy.**

### Why the current version is weak
The current family scores whether the model emits the “expected strategy.” That can become a benchmark of compliance with the author’s preferred label set rather than genuine regulation.

### What to measure instead
Measure whether the model changes its control policy when task structure changes in ways that should matter.

Examples:
- a problem becomes explicitly support-required
- a task is re-presented with a contradiction warning
- a problem is decomposed into subtasks
- a verify-first instruction becomes available
- a memory-demanding task is changed into a passage-grounded task

### Behavioral signal to score
- Did the model switch from direct answering to verify-first when appropriate?
- Did it ask for clarification when ambiguity was introduced?
- Did it reduce confidence and choose a safer action after a warning cue?
- Did accuracy improve or damage rate fall after the control shift?

### Revised schema
```python
@dataclass
class ControlPolicyResponse:
    control_action: str          # direct_answer | decompose | verify_first | ask_clarify | abstain
    answer: str
    confidence: float
    why_this_strategy: str = ""  # diagnostic only
```

### Scoring recommendation
Score:
- policy appropriateness under the item condition
- resulting accuracy / damage avoidance
- confidence adjustment quality

Do **not** require a single “gold strategy” narrative unless the task makes it objectively necessary.

---

## 4. Scoring and reporting revisions

## A. Do not rely on a single composite score for scientific interpretation
Keep the composite for Kaggle ranking, but always report:

### Monitoring axis
- calibration
- abstention / verification
- grounding sensitivity

### Control axis
- intrinsic self-correction
- evidence-assisted correction
- control-policy adaptation

## B. Add a damage-oriented view
For an epistemically robust assessor, some of the most important numbers are not just mean scores but **failure modes**:
- overconfident error rate
- unnecessary abstention rate
- correct-to-incorrect damage under review
- unsupported-evidence citation rate
- unsafe direct-answer rate under ambiguity

## C. Suggested initial weighting
For the Kaggle composite, I recommend a modest shift toward monitoring because that side is currently more valid and less gameable.

```python
WEIGHTS = {
    "calibration": 0.30,
    "abstention_verification": 0.20,
    "intrinsic_self_correction": 0.10,
    "evidence_assisted_correction": 0.15,
    "grounding_sensitivity": 0.10,
    "control_policy_adaptation": 0.15,
}
```

If the implementation team insists on exactly five top-level families, then merge the two correction subfamilies into one family but still report them separately in diagnostics.

---

## 5. Dataset authoring revisions

### General authoring rule
Each item should be built so that the **behavioral target is objectively defensible** and the self-report fields are auxiliary.

### Item design requirements
1. **Unambiguous gold answers** wherever correctness is scored.
2. **Human-reviewed optimal action labels** for abstention / verification items.
3. **Support-span-verifiable prompts** for grounding items.
4. **Budget-matched review conditions** for self-correction items.
5. **Perturbation pairs** for control-policy items so adaptation is behaviorally testable.

### Hidden metadata to add
- `item_family`
- `evaluation_axis`
- `support_present`
- `review_mode` (`intrinsic`, `weak_hint`, `evidence`)
- `risk_class`
- `optimal_control_action`
- `damage_sensitive`

These should not be exposed to the model.

---

## 6. Concrete code-level recommendations

## Keep
- top-level wrapper pattern
- per-family cached evaluation blocks
- DataFrame-defined inputs
- offline scoring modules
- first slice centered on calibration

## Change
1. Move all narrative self-report fields to diagnostic status unless directly validated.
2. Rename files/modules to reflect the revised construct.
3. Add explicit axis-level aggregation functions.
4. Add damage metrics to the scoring package.

### Suggested module map
```text
metajudge/
├── tasks/
│   ├── calibration.py
│   ├── abstention_verification.py
│   ├── self_correction.py
│   ├── grounding_sensitivity.py
│   └── control_policy.py
├── scoring/
│   ├── calibration_metrics.py
│   ├── abstention_metrics.py
│   ├── self_correction_metrics.py
│   ├── grounding_metrics.py
│   ├── control_policy_metrics.py
│   ├── aggregation.py
│   └── failure_modes.py
```

### Suggested aggregation additions
```python
def aggregate_monitoring_axis(subscores: dict) -> float:
    keys = ["calibration", "abstention_verification", "grounding_sensitivity"]
    return float(sum(subscores[k] for k in keys) / len(keys))


def aggregate_control_axis(subscores: dict) -> float:
    keys = ["intrinsic_self_correction", "evidence_assisted_correction", "control_policy_adaptation"]
    return float(sum(subscores[k] for k in keys) / len(keys))
```

---

## 7. Recommended implementation order

## Phase 1 — keep moving with the existing plan
1. Implement **Calibration** end to end.
2. Add offline diagnostics: Brier, ECE, AUROC, overconfidence gap.
3. Finalize the Kaggle wrapper with calibration-only pilot mode.

## Phase 2 — monitoring completion
4. Implement **Selective Abstention / Verification**.
5. Replace **Source Awareness** with **Grounding Sensitivity**.
6. Report a first combined **Monitoring Axis** score.

## Phase 3 — control completion
7. Split and implement **Self-Correction** into intrinsic and evidence-assisted modes.
8. Replace **Strategy Adaptation** with **Control-Policy Adaptation**.
9. Add damage metrics and budget-matched baselines.

## Phase 4 — benchmark hardening
10. Run adversarial and deceptive item audits.
11. Check whether a conservative “just abstain / lower confidence” policy can game the composite.
12. Tune weights only after failure-mode review.

---

## 8. Acceptance criteria for the revised benchmark

A reasonable v1 should satisfy all of the following:

1. **Construct clarity**
   - Public description uses “epistemically robust metacognitive behavior,” not unrestricted claims about internal metacognition.

2. **Behavioral grounding**
   - At least 80% of scored fields are behaviorally verifiable.
   - Narrative rationales are diagnostic by default.

3. **Calibration robustness**
   - Calibration is scored with both per-item utility and classical diagnostics.
   - Overconfident wrong answers are visibly penalized.

4. **Control validity**
   - Self-correction distinguishes intrinsic review from evidence-assisted correction.
   - Strategy / policy family does not depend on matching a single preferred verbal label.

5. **Anti-gaming resilience**
   - Over-abstention and blanket low-confidence policies do not dominate the composite.
   - Correct answers broken by review are explicitly penalized.

6. **Operational practicality**
   - The benchmark still runs inside Kaggle quota and retains the current modular implementation path.

---

## Bottom line

The current architecture is a **reasonable starting plan**, especially because it already treats calibration, abstention, correction, and adaptation as separate subproblems. The right move is **not** to start over. The right move is to **narrow the construct, keep calibration central, and redesign the weaker self-report-heavy families into behaviorally testable monitoring/control tasks**.

That produces a benchmark that is still competitively useful, still implementable in the current Kaggle architecture, and significantly more defensible as an **epistemically robust metacognitive assessor of LLMs**.

---

## References

### Core references
1. Nelson, T. O., & Narens, L. (1990). *Metamemory: A Theoretical Framework and New Findings*.
2. Kadavath, S. et al. (2022). *Language Models (Mostly) Know What They Know*.
3. Xiong, M. et al. (2024). *Can LLMs Express Their Uncertainty? An Empirical Evaluation of Confidence Elicitation in LLMs*. ICLR 2024.
4. Huang, J. et al. (2024). *Large Language Models Cannot Self-Correct Reasoning Yet*. ICLR 2024.

### Supporting reference consulted
- Geng, J. et al. (2024). *A Survey of Confidence Estimation and Calibration in Large Language Models*. NAACL 2024.
