# Prompt to drive the benchmark revision

You are updating the existing **MetaJudge-AGI** Kaggle benchmark architecture into a more defensible **epistemically robust metacognitive assessor of LLMs**.

You have been given a revision memo in Markdown. Use that memo as the governing design document. Do **not** restart from scratch, and do **not** discard the current wrapper-task architecture unless absolutely necessary. The objective is to preserve implementation momentum while tightening construct validity.

## Your mission
Revise the benchmark so that it measures **behaviorally grounded metacognitive performance** in two explicit domains:

1. **Epistemic monitoring**
2. **Cognitive control / regulation**

The output should remain compatible with the current Kaggle wrapper pattern: one exported `@kbench.task` that internally evaluates multiple families and returns a single composite float.

## Non-negotiable design requirements

1. **Keep calibration central.**
   - Preserve the calibration family as the anchor family.
   - Keep confidence scoring tied to correctness.
   - Maintain classical diagnostics such as Brier, ECE, AUROC, and overconfidence rate.

2. **Keep abstention, but make it cleaner.**
   - Use a constrained action ontology: `answer`, `ask_clarifying_question`, `abstain`, `verify_needed`.
   - Score as a decision policy, not just a text-generation task.

3. **Split self-correction into two modes.**
   - `intrinsic_self_correction`
   - `evidence_assisted_correction`
   - These must be distinguishable in the data model, score reports, and diagnostics.

4. **Replace source-awareness with grounding sensitivity.**
   - Do not score post hoc claims like `memory`, `inference`, or `guess` as if they were objective internal truths.
   - Instead score whether the model correctly responds to the presence or absence of supporting prompt evidence.

5. **Replace strategy narration with control-policy adaptation.**
   - Do not require agreement with a single hand-authored “expected strategy” label unless objectively necessary.
   - Score whether the model changes behavior appropriately under task perturbations.

6. **Favor behavioral evidence over introspective narration.**
   - Any free-text rationale field should be diagnostic by default unless there is a validated gold target.

7. **Preserve Kaggle practicality.**
   - Stay quota-aware.
   - Keep modular family evaluation.
   - Keep the wrapper-task structure.
   - Preserve the ability to stage rollout family by family.

## What to produce

Produce a concrete implementation update plan that includes all of the following:

### A. Revised benchmark specification
- Updated benchmark description
- Two top-level axes
- Final family list
- Per-family task signatures
- Revised schemas
- Revised composite weights

### B. Code-level migration plan
- Exact file/module renames or additions
- What existing code can remain unchanged
- What scoring functions must be modified
- What diagnostic metrics must be added
- What hidden metadata columns must be added to the CSVs

### C. Dataset revision plan
- Item types for each family
- Labeling rules
- Anti-gaming checks
- Human review requirements
- How to separate intrinsic vs evidence-assisted correction

### D. Execution plan
- Implementation order with the smallest viable slice first
- Acceptance criteria for each phase
- Risks and mitigations

## Output constraints

- Be concrete, technical, and implementation-oriented.
- Do not merely restate the memo.
- Convert it into executable design decisions.
- Explicitly mark which parts of the current production architecture are **kept**, **changed**, **replaced**, or **demoted to diagnostics**.
- Prefer tables and bulletized structure where helpful, but keep the writing crisp.
- Assume the team is about to start coding immediately after reading your response.

## Success condition
The revised plan should still feel like the same benchmark lineage, but it should now be substantially stronger as an **epistemically robust metacognitive assessor** rather than a loose collection of self-report-heavy tasks.
