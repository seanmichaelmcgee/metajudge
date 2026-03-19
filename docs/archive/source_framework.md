# Framework for Building Metacognition Benchmarks for the Kaggle **Measuring Progress Toward AGI – Cognitive Abilities** Competition

## 1. Purpose and competition fit

This document outlines a practical and competition-aligned framework for building a **metacognition benchmark suite** for the newly launched Kaggle competition **Measuring Progress Toward AGI – Cognitive Abilities**. The goal is not merely to test whether a model can answer questions correctly. The goal is to test whether a model can **monitor, evaluate, and regulate its own cognition** while solving tasks.

Within the competition framing from Google DeepMind, metacognition is one of the target faculties alongside learning, attention, executive functions, and social cognition. DeepMind’s cognitive framework defines metacognition as a system’s knowledge of its own cognitive processes and its ability to **monitor and control** those processes. That framing is critical, because it tells us that a benchmark for metacognition should not primarily reward polished explanation, verbose self-reflection, or chain-of-thought style formatting. Instead, it should reward **behavioral evidence** that the model:

- knows when it is uncertain,
- can estimate its own likelihood of being correct,
- can identify likely errors,
- can distinguish memory from inference or guessing,
- can choose better strategies when the present strategy is failing,
- and can decide whether to answer, defer, request more information, or revise.

For this competition, the benchmark submission is expected to be an actual **Kaggle Benchmark with underlying tasks authored by the participant**, not just a conceptual writeup. That makes implementation design central. The benchmark therefore needs to be:

1. conceptually rigorous,
2. behaviorally measurable,
3. reproducible in Kaggle,
4. resistant to shallow gaming,
5. and intelligible to judges reviewing the benchmark design.

The framework below is written to support all five of those needs.

---

## 2. Working definition of metacognition for this competition

For benchmarking purposes, metacognition should be defined operationally as:

> **The model’s ability to represent, monitor, and regulate the reliability of its own cognition during task performance.**

That definition can be decomposed into three evaluation layers.

### 2.1 Metacognitive knowledge

This concerns what the model appears to know about its own performance characteristics or cognitive state. In benchmark terms, this includes whether the model can indicate:

- whether it remembers versus infers,
- whether it is relying on incomplete evidence,
- whether the task is within its present competence,
- whether its current strategy is fragile,
- and whether there are identifiable reasons to distrust the answer.

### 2.2 Metacognitive monitoring

This concerns online assessment of its own thinking. In benchmark terms, this includes whether the model can:

- provide calibrated confidence,
- detect its own probable mistakes,
- revise its confidence as new evidence appears,
- recognize conflict between earlier and later outputs,
- and flag uncertainty before the final answer is scored.

### 2.3 Metacognitive control

This concerns using monitoring information to alter behavior. In benchmark terms, this includes whether the model can:

- abstain when appropriate,
- ask for clarification or additional evidence,
- switch strategies when its first method fails,
- perform targeted correction rather than generic restatement,
- and allocate effort differently depending on difficulty.

A good metacognition benchmark should test all three layers. A weak benchmark will only test one, most commonly self-reported confidence.

---

## 3. High-level benchmark philosophy

The benchmark should be built around one central design principle:

> **Do not score metacognition by what the model says about itself alone; score it by the consequences of self-monitoring on task behavior.**

This principle matters because frontier models can imitate reflective language without demonstrating genuine self-monitoring. A model may say “I’m not fully certain” on difficult prompts because it has learned the surface convention that hard problems deserve hedging. That is not enough.

Accordingly, the benchmark should emphasize:

- **behavior under uncertainty**, not only verbal introspection,
- **multi-step interactions**, not only one-shot responses,
- **decision quality**, not only answer quality,
- **strategy adaptation**, not only post hoc explanation,
- and **cross-task robustness**, not narrow optimization to a fixed template.

This suggests a suite of tasks rather than a single task type.

---

## 4. Recommended benchmark architecture

The proposed benchmark should be organized as a **suite of complementary task families**, each probing a different aspect of metacognition. The suite should be modular, so that each task family contributes a subscore and the overall benchmark produces both:

- a **headline metacognition score**, and
- a **profile across subdimensions**.

### 4.1 Recommended sub-benchmarks

A strong first version would include five sub-benchmarks:

1. **Confidence Calibration**
2. **Selective Abstention and Deferral**
3. **Error Detection and Targeted Self-Correction**
4. **Source Awareness and Epistemic Attribution**
5. **Strategy Selection and Adaptive Revision**

This mapping is attractive because each module is legible, measurable, and closely aligned with the DeepMind framework.

### 4.2 Why a suite is better than a single benchmark type

A single metacognition task can usually be gamed. For example:

- if only confidence is scored, the model may learn generic hedging;
- if only self-correction is scored, the model may always revise even when revision hurts accuracy;
- if only abstention is rewarded, the model may become overly conservative;
- if only source labeling is used, the model may memorize label conventions.

A suite forces broader competence and makes tradeoffs visible. It also allows competition judges to see whether a model is good at one component of metacognition but poor at others.

---

## 5. Core task-family designs

## 5.1 Task Family A: Confidence Calibration

### 5.1.1 Objective

Measure whether the model’s stated confidence corresponds to actual correctness.

### 5.1.2 Why this matters

Calibration is the most direct measurable indicator that a system can monitor the reliability of its own outputs. A model that is often correct but badly calibrated is less useful in real deployments than one that knows when its outputs are risky.

### 5.1.3 Task format

Each item should contain:

- a prompt,
- a required answer,
- a required numeric confidence estimate, ideally on a 0 to 100 or 0.0 to 1.0 scale,
- and a structured justification field that is not directly scored for eloquence but can be analyzed for diagnostics.

Suggested structured response schema:

```json
{
  "answer": "...",
  "confidence": 0.73,
  "reason_for_uncertainty": "...",
  "would_verify_if_possible": true
}
```

### 5.1.4 Data design

The dataset should include a controlled mix of:

- easy items,
- moderately difficult novel items,
- deceptive items that resemble familiar templates but differ in key ways,
- and intentionally ambiguous items where the best behavior may involve lower confidence.

Difficulty labels should be hidden from the model but maintained in metadata for analysis.

### 5.1.5 Scoring

Use a combination of:

- correctness,
- Brier score or log-loss style confidence scoring,
- expected calibration error,
- and overconfidence penalties.

Important principle: **confident wrong answers should be penalized much more heavily than low-confidence wrong answers**.

### 5.1.6 Failure modes to watch

- generic mid-range confidence on everything,
- superficial confidence tied to prompt length or style,
- confidence copied from lexical cues rather than true uncertainty,
- and response-format hacking.

---

## 5.2 Task Family B: Selective Abstention and Deferral

### 5.2.1 Objective

Measure whether the model can decide not to answer, or request clarification, when uncertainty is sufficiently high.

### 5.2.2 Why this matters

Metacognition is not just “estimating confidence.” It is also using that confidence to regulate action. Abstention is one of the clearest action-level expressions of metacognitive control.

### 5.2.3 Task format

Each item should force one of several mutually exclusive choices:

- answer now,
- ask for one missing piece of information,
- abstain,
- or request external verification.

Suggested structured response schema:

```json
{
  "decision": "answer|ask|abstain|verify",
  "answer": "...",
  "confidence": 0.41,
  "missing_information": "...",
  "abstention_reason": "..."
}
```

### 5.2.4 Data design

Include three item classes:

1. **Answerable items** where abstention should be penalized.
2. **Under-specified items** where a clarification request should outperform guessing.
3. **Unreliably answerable items** where abstention or verification should be rewarded.

This prevents the benchmark from rewarding universal conservatism.

### 5.2.5 Scoring

Use a decision-theoretic reward matrix. Example:

- correct answer when answerable: strong positive reward,
- abstain on answerable item: modest penalty,
- guess incorrectly on under-specified item: stronger penalty,
- request the right clarification on under-specified item: positive reward,
- abstain on unreliable or adversarial item: positive reward,
- confident hallucination on impossible item: largest penalty.

This can be summarized as a **risk-aware utility score**.

### 5.2.6 Key implementation detail

The benchmark should not always accept abstention. Instead, it should score whether abstention behavior is **appropriately selective**.

---

## 5.3 Task Family C: Error Detection and Targeted Self-Correction

### 5.3.1 Objective

Measure whether the model can identify probable errors in its own prior answer and improve the answer in a targeted way.

### 5.3.2 Why this matters

Many systems can produce a second answer that differs from the first. That is not the same as metacognitive correction. The benchmark should reward the ability to identify *what is likely wrong* and revise accordingly.

### 5.3.3 Task format

Use a two-stage or three-stage interaction:

1. Model gives initial answer and confidence.
2. Model is shown either:
   - its own previous answer only,
   - a weak challenge,
   - a contradiction,
   - or a request to inspect for likely error.
3. Model must either:
   - keep the answer,
   - revise the answer,
   - revise confidence,
   - or identify unresolved uncertainty.

Suggested schema for stage two:

```json
{
  "is_likely_wrong": true,
  "suspected_error_type": "arithmetic|misread|unsupported_inference|memory_failure|other",
  "revised_answer": "...",
  "revised_confidence": 0.58,
  "what_changed": "..."
}
```

### 5.3.4 Scoring

Reward should depend on:

- whether the revision improves correctness,
- whether the error type diagnosis is plausible,
- whether confidence moves in the right direction,
- whether the model avoids gratuitous revision when the original answer was already correct.

This last part is essential. Otherwise the benchmark may reward compulsive second-guessing.

### 5.3.5 Anti-gaming requirement

The correction prompt should vary substantially in wording and structure so models cannot simply learn that “on second pass, change the answer.”

---

## 5.4 Task Family D: Source Awareness and Epistemic Attribution

### 5.4.1 Objective

Measure whether the model can distinguish among remembered information, direct evidence in the prompt, inferred conclusions, and guesses.

### 5.4.2 Why this matters

This is one of the most compelling metacognitive properties in current AI systems. Users often need to know not merely *what* the model answered, but *where the answer came from*.

### 5.4.3 Task format

The model must answer a question and label the answer source using a constrained set, for example:

- directly stated in prompt,
- inferred from prompt,
- recalled from prior knowledge,
- estimated or guessed,
- or unresolved.

Suggested schema:

```json
{
  "answer": "...",
  "source_label": "prompt|inference|memory|guess|unresolved",
  "confidence": 0.66,
  "supporting_span": "..."
}
```

### 5.4.4 Data design

Construct items where different source labels are genuinely correct:

- some answers are explicitly stated,
- some require inference from prompt contents,
- some rely on background knowledge,
- some are intentionally unsupported,
- and some contain distractors that encourage false source claims.

### 5.4.5 Scoring

Use separate scores for:

- answer correctness,
- source-label correctness,
- justification alignment,
- and unsupported certainty penalties.

This can reveal whether a model is correct for the wrong epistemic reason.

---

## 5.5 Task Family E: Strategy Selection and Adaptive Revision

### 5.5.1 Objective

Measure whether the model can choose among alternative approaches and shift strategy when the first one proves unreliable.

### 5.5.2 Why this matters

Metacognitive control is not only about abstaining. It is also about deciding how to think. In humans, strategy adaptation is a central sign of mature metacognition. In AI evaluation, it provides a bridge between metacognition and executive function while remaining distinct.

### 5.5.3 Task format

Design problems with at least two plausible solution strategies, where one is better under specific conditions. The model should be asked to:

- choose a strategy before solving,
- state why that strategy was chosen,
- execute the task,
- and optionally revise strategy after feedback.

Possible strategy categories:

- direct recall,
- stepwise reasoning,
- verification-first,
- decomposition into subproblems,
- or decline pending evidence.

Suggested schema:

```json
{
  "chosen_strategy": "recall|stepwise|decompose|verify_first|decline",
  "why_this_strategy": "...",
  "answer": "...",
  "confidence": 0.62,
  "would_change_strategy_after_feedback": true
}
```

### 5.5.4 Scoring

Reward:

- appropriate strategy selection,
- successful completion,
- rational adaptation after challenge,
- and reduced error after switching strategy.

Penalize:

- always selecting the same strategy,
- strategy labels that do not match actual behavior,
- and spurious “verification-first” declarations without meaningful change.

---

## 6. Task formatting recommendations

Because Kaggle Benchmarks supports structured output, multi-turn interaction, tools, dataset evaluation, and model-based judgments, the benchmark should use **structured schemas** rather than unstructured prose wherever feasible.

### 6.1 Why structured outputs matter

Structured outputs make the benchmark:

- easier to grade automatically,
- harder to game through verbosity,
- easier to analyze dimension by dimension,
- and more reproducible across models.

### 6.2 Recommended response fields

Across most tasks, the following response fields should be standardized when relevant:

- `answer`
- `confidence`
- `decision`
- `source_label`
- `suspected_error_type`
- `chosen_strategy`
- `revised_answer`
- `revised_confidence`
- `justification`

Not every field belongs in every task, but schema consistency across task families will simplify downstream analysis.

### 6.3 Hidden metadata fields

Each task item should also carry hidden evaluator metadata, such as:

- gold answer,
- ambiguity class,
- intended optimal action,
- source type,
- difficulty label,
- adversarial category,
- expected strategy family,
- and penalty schedule.

These hidden fields should not be exposed to the model.

---

## 7. Scoring framework

The benchmark should not use a single simplistic pass/fail metric. Metacognition is multi-dimensional. The scoring system should therefore combine several components.

## 7.1 Recommended top-level score composition

A strong initial composition would be:

- **25% Confidence calibration**
- **20% Selective abstention / deferral quality**
- **20% Error detection and correction**
- **15% Source-awareness accuracy**
- **20% Strategy adaptation quality**

These exact weights can be tuned after pilot runs, but the larger point is that metacognitive control and monitoring should both matter.

## 7.2 Component-level metrics

### Calibration metrics

Use:

- Brier score,
- expected calibration error,
- accuracy by confidence bucket,
- and overconfidence rate.

### Decision metrics for abstention tasks

Use:

- utility-based reward,
- risk-coverage curves,
- abstention precision,
- and false-answer-under-uncertainty rate.

### Self-correction metrics

Use:

- percentage of revisions that improve correctness,
- percentage of unnecessary revisions on already-correct answers,
- confidence change directionality,
- and correction efficiency.

### Source-awareness metrics

Use:

- answer correctness,
- source-label accuracy,
- unsupported-source claims,
- and prompt-span evidence alignment.

### Strategy metrics

Use:

- strategy-selection accuracy,
- improvement after strategy change,
- behavioral consistency between declared and observed strategy,
- and diversity-adjusted strategy use.

## 7.3 Composite score design principles

The composite score should satisfy four principles:

1. **Overconfident error must hurt a lot.**
2. **Appropriate abstention must help, but not too much.**
3. **Second-pass revision must help only when it improves performance.**
4. **No single cheap behavior should dominate the benchmark.**

---

## 8. Anti-gaming design

This section is especially important. A metacognition benchmark is highly vulnerable to superficial optimization.

## 8.1 Main gaming risks

### 8.1.1 Hedging-language gaming

The model learns generic uncertainty phrases and uses them decoratively.

### 8.1.2 Middle-confidence collapse

The model outputs mid-range confidence for most tasks to reduce penalty.

### 8.1.3 Universal abstention

The model becomes overly conservative if abstention is rewarded without opportunity cost.

### 8.1.4 Always-revise behavior

The model learns that the benchmark likes second-pass changes and changes answers even when it should not.

### 8.1.5 Strategy-label theater

The model claims different strategies while behavior remains unchanged.

### 8.1.6 Template memorization

The model learns recurring prompt structures and uses benchmark-specific cues instead of metacognitive behavior.

## 8.2 Anti-gaming countermeasures

### 8.2.1 Behavior-first scoring

Whenever possible, score outcomes and decision consequences, not stylistic features of explanations.

### 8.2.2 Hidden optimal-action classes

Mix tasks where answer, clarification, abstention, or revision are respectively optimal. This prevents a single global policy from dominating.

### 8.2.3 Prompt and format variation

Vary wording, layout, order of fields, and interaction style across items. The model should not reliably infer scoring from superficial prompt shape.

### 8.2.4 Decoy confidence cues

Include tasks whose surface appearance does not match true difficulty. This helps distinguish true calibration from heuristic confidence assignment.

### 8.2.5 Symmetric correction setup

Include both:

- wrong-first-answer cases where revision should help,
- and correct-first-answer cases where unwarranted revision should hurt.

### 8.2.6 Source-label adversarial items

Design tasks where the answer is correct but the source label is easy to get wrong. This tests epistemic awareness separately from answer success.

### 8.2.7 Cross-template evaluation splits

Use multiple templates and reserve some prompt structures as hidden evaluation variants.

### 8.2.8 Limit reward for verbosity

Do not directly reward long justification text. Use structured fields and targeted assertions instead.

---

## 9. Integration with Kaggle Benchmarks

The benchmark should be designed from the start to fit Kaggle’s benchmark system rather than retrofitted afterward.

## 9.1 Why Kaggle Benchmarks is a good fit

Kaggle Benchmarks is well suited here because it supports:

- custom task definitions through `@kbench.task`,
- structured outputs through schemas,
- dataset evaluation across many rows,
- reproducible run capture,
- multi-turn chat interactions,
- tool use,
- and model-based assertions using a separate judge model.

Those capabilities are unusually well matched to metacognition, which often requires more than single-turn string matching.

## 9.2 Recommended implementation pattern

The implementation should be organized into the following layers:

### Layer 1: Item dataset

A tabular dataset, ideally a DataFrame-backed CSV or parquet table, with one row per task item and metadata columns for hidden grading.

### Layer 2: Task functions

One `@kbench.task` function per task family, or per narrower task type when needed.

### Layer 3: Shared schemas

Define dataclasses or pydantic models for structured responses such as:

- calibration response,
- abstention decision response,
- self-correction response,
- source attribution response,
- strategy selection response.

### Layer 4: Assertion and scoring utilities

Create reusable functions for:

- numeric confidence validation,
- calibration scoring,
- utility-matrix decision scoring,
- source-label scoring,
- behavior-consistency checks,
- and custom assertions for benchmark recording.

### Layer 5: Aggregation notebook

A notebook section that computes sub-benchmark and overall scores from run outputs and verifies expected leaderboard rendering.

## 9.3 Practical Kaggle task design advice

### Use structured outputs aggressively

Because Kaggle Benchmarks supports schemas, require models to return structured objects instead of free-form reflection. This makes the benchmark much more robust.

### Keep first parameter as `llm`

Every task function should follow Kaggle’s expected design with `llm` as the first argument.

### Use `.evaluate()` over datasets

This is the correct pattern for obtaining aggregate benchmark metrics across many items.

### Use pass/fail assertions for local guarantees and returned numeric values for scoring

Where possible, each task should both:

- record meaningful assertion outcomes for interpretability,
- and return a numeric or boolean signal that can be aggregated.

### Consider a judge LLM only for narrow rubric checks

Kaggle allows model-based judging through `assess_response_with_judge`, but metacognition scoring should not rely too heavily on another model’s subjective reading. Use a judge model sparingly, for example:

- to assess whether a strategy explanation matches the selected strategy,
- or whether a free-text uncertainty rationale matches a rubric.

Wherever feasible, prefer deterministic scoring from structured fields and gold metadata.

---

## 10. Proposed benchmark proposal for this competition

This is the concrete proposal I would recommend submitting in first-pass form.

## 10.1 Benchmark name

**MetaJudge-AGI: A Behavioral Benchmark for Metacognition in Frontier Models**

## 10.2 Benchmark thesis

MetaJudge-AGI evaluates whether frontier models can accurately assess and regulate the reliability of their own cognition, not merely produce correct answers. The benchmark measures five dimensions: calibration, abstention, self-correction, source awareness, and strategy adaptation.

## 10.3 Benchmark structure

- **Module A:** Calibrated answering
- **Module B:** Ask / answer / abstain decisions
- **Module C:** Targeted self-correction after challenge
- **Module D:** Source attribution under mixed evidence conditions
- **Module E:** Strategy selection and revision

## 10.4 Example task blueprint

### Example blueprint 1: Ambiguous factual prompt

The model receives an under-specified question with insufficient context. It must choose whether to answer, ask, abstain, or verify.

This tests whether the model recognizes incompleteness before hallucinating.

### Example blueprint 2: Trap question with strong familiarity cues

The problem looks like a memorized template but contains one altered condition. The model must answer and provide confidence.

This tests whether confidence tracks true rather than superficial familiarity.

### Example blueprint 3: Self-review after contradiction

The model answers, then receives a targeted contradiction or weak evidence that its answer may be wrong. It must decide whether to revise.

This tests error monitoring and control, not just re-answering.

### Example blueprint 4: Answer-source disambiguation

The model must answer and then identify whether the answer came from prompt evidence, inference, background memory, or guessing.

This tests epistemic self-awareness.

### Example blueprint 5: Strategy-precommitment problem

The model must choose a strategy before solving and then indicate whether feedback should cause strategy revision.

This tests metacognitive control and planned adaptation.

---

## 11. Suggested major tasks and subtasks for development

This section is intended as a project-management guide.

## Task 1: Finalize the benchmark specification

### Subtasks

- Write a one-page benchmark charter.
- Freeze the operational definition of metacognition.
- Finalize the five sub-benchmarks.
- Define scoring weights and acceptable alternatives.
- Decide where deterministic grading ends and judge-model grading begins.

### Deliverable

A concise design specification that all later dataset and code work adheres to.

## Task 2: Build the task taxonomy and metadata schema

### Subtasks

- Create the item-type taxonomy.
- Define metadata columns for all task families.
- Define adversarial classes.
- Define ambiguity classes.
- Define gold optimal actions and source types.
- Define difficulty labels for post hoc analysis.

### Deliverable

A canonical item schema document and starter dataset template.

## Task 3: Author datasets for each module

### Subtasks

- Draft initial items manually.
- Ensure every module has easy, medium, hard, deceptive, and adversarial items.
- Create items where answering is optimal.
- Create items where abstention is optimal.
- Create items where clarification is optimal.
- Create items where correction should help.
- Create items where correction should not help.
- Create source-awareness items with mixed provenance.

### Deliverable

Versioned datasets for each module, with hidden gold metadata.

## Task 4: Define response schemas

### Subtasks

- Implement dataclasses or pydantic models.
- Standardize confidence fields and valid ranges.
- Standardize allowed labels for source, strategy, and error-type fields.
- Add validation for malformed outputs.

### Deliverable

Reusable response-schema Python module.

## Task 5: Implement Kaggle task functions

### Subtasks

- Write one task function per module.
- Add row-wise evaluation support using `.evaluate()`.
- Capture multi-turn interaction where needed.
- Add deterministic assertions for formatting and field validity.
- Return numeric or boolean outcomes suitable for aggregation.

### Deliverable

A working Kaggle notebook that executes the full benchmark suite.

## Task 6: Implement scoring utilities

### Subtasks

- Implement calibration metrics.
- Implement abstention utility scoring.
- Implement self-correction deltas.
- Implement source-label scoring.
- Implement strategy-consistency checks.
- Implement aggregate composite score computation.

### Deliverable

A scoring library with test coverage.

## Task 7: Add anti-gaming protections

### Subtasks

- Create paraphrased prompt variants.
- Add decoy familiarity cues.
- Add control items where default strategies should fail.
- Ensure that no single action policy dominates.
- Add hidden evaluation variants if competition format allows.

### Deliverable

A hardened benchmark less vulnerable to surface-level optimization.

## Task 8: Pilot benchmark across available Kaggle models

### Subtasks

- Run the benchmark on multiple models using Kaggle’s “Evaluate More Models” workflow.
- Inspect subscore variation.
- Identify modules with poor discrimination.
- Check whether models exploit formatting weaknesses.
- Tune weights only after empirical inspection.

### Deliverable

A pilot analysis notebook and a refined benchmark v1.1.

## Task 9: Prepare competition-facing writeup

### Subtasks

- Describe the benchmark motivation.
- Explain why the design captures metacognition rather than style.
- Document data construction.
- Explain scoring clearly.
- Explain anti-gaming measures.
- Show illustrative examples.
- Discuss limitations honestly.

### Deliverable

A polished writeup aligned with competition expectations.

---

## 12. Example pseudocode sketch for Kaggle Benchmarks

The exact SDK details may evolve, but a rough implementation shape should look like this:

```python
import pandas as pd
import kaggle_benchmarks as kbench
from dataclasses import dataclass

@dataclass
class CalibrationResponse:
    answer: str
    confidence: float
    reason_for_uncertainty: str
    would_verify_if_possible: bool

@kbench.task(name="metacog_calibration")
def metacog_calibration(llm, prompt: str, gold_answer: str) -> float:
    response = llm.prompt(prompt, schema=CalibrationResponse)

    kbench.assertions.assert_true(
        0.0 <= response.confidence <= 1.0,
        expectation="Confidence must be between 0 and 1."
    )

    is_correct = normalize(response.answer) == normalize(gold_answer)
    score = calibration_aware_score(
        is_correct=is_correct,
        confidence=response.confidence,
    )
    return score

runs = metacog_calibration.evaluate(
    llm=[kbench.llm],
    evaluation_data=my_dataframe,
)
```

A second module could use multi-turn chat and a correction schema. A third could use a judge model only for limited rubric checks.

---

## 13. When to use a judge model and when not to

A separate judge model is useful, but should be constrained.

## 13.1 Good uses

- checking whether a free-text rationale matches a declared strategy,
- checking whether an abstention reason meaningfully references missing information,
- checking whether a self-correction explanation is targeted rather than generic.

## 13.2 Bad uses

- deciding overall correctness when correctness is objectively gradable,
- deciding calibration quality from prose,
- deciding source awareness when gold source metadata exists,
- or scoring the entire benchmark holistically.

The more the benchmark depends on another model’s subjective impression, the weaker and less reproducible it becomes.

---

## 14. Validation plan

Before final submission, the benchmark should be validated along four axes.

## 14.1 Construct validity

Does the benchmark actually measure metacognition rather than raw reasoning, verbosity, or instruction following?

## 14.2 Discriminative validity

Do different models separate meaningfully on different sub-benchmarks?

## 14.3 Robustness

Do small prompt variations preserve ranking and interpretation?

## 14.4 Anti-gaming robustness

Do known cheap strategies fail to dominate the benchmark?

A brief ablation section in the writeup would strengthen the submission substantially.

---

## 15. Main risks and limitations

A strong submission should acknowledge limitations.

### Limitation 1: Metacognition is only partially observable

We infer metacognition from behavior. We do not directly observe internal self-modeling.

### Limitation 2: Some modules overlap with other faculties

Strategy adaptation touches executive function; source awareness touches memory and reasoning. This is acceptable if the writeup explains that the benchmark isolates the *metacognitive component* of those behaviors.

### Limitation 3: Current models may produce reflective language without stable self-monitoring

The benchmark should explicitly state that it prioritizes consequence-sensitive behavior over introspective style.

### Limitation 4: Judge-model components may introduce evaluator bias

This is why deterministic scoring should dominate.

---

## 16. Final recommendation

If I were building for this competition now, I would avoid trying to make one giant abstract benchmark for “metacognition” in a vague sense. I would instead submit a **behavioral metacognition suite** centered on:

- calibrated confidence,
- selective abstention,
- targeted self-correction,
- source awareness,
- and strategy adaptation.

That suite is close to the competition’s stated goals, technically compatible with Kaggle Benchmarks, legible to judges, and much harder to game than a single self-reflection benchmark.

The strongest version of the submission would present metacognition not as “the model talks about its thinking,” but as:

> **the model manages epistemic risk while solving tasks.**

That framing is concrete, modern, benchmarkable, and likely to be persuasive in this competition.

---

## 17. Source notes for the framework

This framework was grounded in:

- the Kaggle competition page for **Measuring Progress Toward AGI – Cognitive Abilities**,
- Google DeepMind’s **Measuring Progress Toward AGI: A Cognitive Framework**,
- Kaggle’s Community Benchmarks / Benchmarks SDK documentation,
- and the `kaggle-benchmarks` quick start and user guide.

Primary sources:

- Kaggle competition: https://www.kaggle.com/competitions/kaggle-measuring-agi
- DeepMind framework blog: https://blog.google/innovation-and-ai/models-and-research/google-deepmind/measuring-agi-cognitive-framework/
- DeepMind framework PDF: https://storage.googleapis.com/deepmind-media/DeepMind.com/Blog/measuring-progress-toward-agi/measuring-progress-toward-agi-a-cognitive-framework.pdf
- Kaggle Benchmarks docs: https://www.kaggle.com/docs/benchmarks
- Kaggle Benchmarks repo: https://github.com/Kaggle/kaggle-benchmarks

