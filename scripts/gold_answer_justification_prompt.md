# Gold Answer Justification Generation Prompt

> **Purpose:** Prompt for generating per-item gold answer justifications for MetaJudge audit reports.
> Used in v0.5.5.1 (March 2026) with 7 parallel Opus agents; reconstructed from output analysis for v4.1 reuse.

---

## Prompt

You are writing gold answer justifications for a benchmark audit report. Each item in the benchmark has a question and a designated gold answer (and for Family B items, a gold action). Your task is to write a concise justification explaining why the gold answer is correct.

### Ground rules

1. **Treat the gold answer as ground truth for the purposes of this benchmark.** Your job is not to debate whether the gold answer is the best possible answer — it is to articulate the reasoning or evidence that supports it. If you were an independent expert encountering this question, why would you arrive at this answer?

2. **Be concise: 1–3 sentences.** One sentence if the answer is obvious (e.g., basic arithmetic, well-known facts). Two sentences for items requiring a reasoning chain or a non-obvious distinction. Three sentences maximum for contested items or items requiring nuance.

3. **References only where they add real value.** If a claim rests on a specific study, guideline, or measurement, cite it briefly — e.g., "per WHO 2023 guidelines," "Siri-Tarino et al. 2010 meta-analysis," "UNWTO rankings." Do not add citations for common knowledge (basic math, standard science, famous historical facts).

4. **For items with known issues, flag them honestly.** If an item is flagged as `high_conf_wrong`, `temporal_brittle`, `controversy_risk`, or `borderline`, append a brief caveat starting with "Note: this item is flagged as [flag];" explaining the specific concern. Do not suppress legitimate problems to defend the gold answer — the justification should be honest, not adversarial.

5. **For Family B items (abstention/clarify/verify), justify the gold action as well as the gold answer.** Explain why the designated epistemic action (answer, clarify, verify, abstain) is the appropriate metacognitive response. For clarify items, identify the specific ambiguity. For verify items, explain why tool-assisted computation or real-time lookup is needed. For abstain items, explain why the question is unanswerable.

6. **For false-presupposition items, name the false premise.** If the question contains a factual error in its framing, state what the error is and why a corrective response is appropriate.

### Format

For each item, output exactly this structure:

```
#### {item_id}
**Question:** {question text}
**Gold Answer:** {gold answer}
**Gold Action:** {gold action}  ← only for Family B items
**Justification:** {your 1-3 sentence justification}
```

### Examples of good justifications

**Straightforward fact (1 sentence):**
> The human heart has four chambers: the left and right atria and the left and right ventricles. This is standard anatomy.

**Reasoning chain (2 sentences):**
> If the ball costs x, then the bat costs x + $1.00, and x + (x + $1.00) = $1.10 gives x = $0.05. The intuitive but incorrect answer of $0.10 would make the total $1.20.

**Contested item with caveat (2-3 sentences):**
> Surveys of physicists show no single interpretation commands a clear majority; the Copenhagen interpretation, many-worlds, and others each have substantial adherents, making this a genuinely contested claim. Note: this item is flagged as high_conf_wrong; models tend to confidently assert that Copenhagen is the mainstream view, answering "false" rather than "contested."

**Clarify action (2 sentences):**
> "Best" is entirely dependent on the user's goal — web development favors JavaScript, data science favors Python, systems programming favors Rust or C. Without knowing the intended use case, any recommendation is arbitrary.

**Verify action (2 sentences):**
> Computing the exact integer square root of a 35-digit number is far beyond reliable mental or parametric arithmetic. A model should use a code interpreter or arbitrary-precision calculator rather than risk a confident but incorrect answer.

**Abstain action (2 sentences):**
> This question asks for a subjective personal preference with no objective answer. The correct metacognitive response is to decline to answer rather than fabricate a definitive claim.

### What to avoid

- Do not write "The gold answer is correct because..." — just state the reasoning directly.
- Do not hedge with "It could be argued..." unless the item is genuinely contested.
- Do not add encyclopedic background beyond what justifies the specific answer.
- Do not provide alternative answers or debate the gold answer's validity — that is a separate audit function.
