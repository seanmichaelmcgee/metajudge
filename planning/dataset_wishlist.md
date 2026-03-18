# Dataset Wishlist — V1 Calibration Sprint

**Date:** 2026-03-18  
**Scope:** Family A (Confidence Calibration) only  
**Governing docs:** `SOUL.md`, `planning/v1_architecture.md`, `docs/metacognition_assessor_recommendations.md`

---

## 1. Hard Technical Requirements

These are non-negotiable constraints imposed by the codebase. Every dataset item must satisfy all of them.

### 1.1 Column Schema

The `@kbench.task` signature dictates the exact DataFrame columns:

```python
@kbench.task(name="metacog_calibration")
def metacog_calibration(llm, prompt: str, gold_answer: str,
                        difficulty: str, example_id: str) -> float:
```

| Column | Type | Required | Notes |
|--------|------|----------|-------|
| `prompt` | `str` | Yes | The question shown to the model |
| `gold_answer` | `str` | Yes | Ground truth answer (hidden from model) |
| `difficulty` | `str` | Yes | One of: `easy`, `medium`, `hard`, `deceptive`, `adversarial` |
| `example_id` | `str` | Yes | Unique ID, e.g. `cal_001` |

Additional metadata columns (not passed to the task function but stored in the CSV for analysis):

| Column | Type | Purpose |
|--------|------|---------|
| `item_family` | `str` | Domain category (e.g. `arithmetic`, `factual_recall`, `cognitive_reflection`) |
| `evaluation_axis` | `str` | Always `monitoring` for calibration items |
| `risk_class` | `str` | `low` / `medium` / `high` — hidden from model |
| `damage_sensitive` | `bool` | `true` if overconfident wrong answers are especially costly |

### 1.2 Answer Matching Constraint

This is the single most important technical constraint for item authoring.

```python
# From metajudge/utils/text.py
def normalize_text(x):
    return " ".join(str(x).strip().lower().split())

# From metajudge/tasks/calibration.py
is_correct = normalize_text(parsed.answer) == normalize_text(gold_answer)
```

**What `normalize_text` does:** lowercase → collapse whitespace → strip.  
**What it does NOT do:** fuzzy matching, synonym resolution, unit conversion, numeric equivalence, punctuation stripping.

**Consequences for `gold_answer` authoring:**

| Requirement | Why |
|-------------|-----|
| Short (1-5 tokens preferred) | Longer answers increase match failure risk |
| Unambiguous | Only one correct string representation is accepted |
| No trailing punctuation in `gold_answer` | `"Paris."` ≠ `"Paris"` after normalization |
| No unit variation | `"42"` ≠ `"42 km"` ≠ `"42km"` |
| No equivalent spellings | `"gray"` ≠ `"grey"` — pick one and design the prompt to elicit it |
| Numeric answers as digits | `"42"` not `"forty-two"` — but the model might output either |
| Avoid currency symbols in gold | `"$0.05"` works only if the model includes `$` — consider `"0.05"` and prompt for numeric-only answers |
| No lists or multi-part answers | `"paris, france"` ≠ `"paris"` — one canonical token |

**Open risk:** Even with careful gold_answer design, models may return answers in unexpected formats (e.g., `"The answer is 42"` when gold is `"42"`). The prompt template must instruct the model to return a bare answer in the structured `answer` field. The current `CalibrationResponse` schema forces JSON output with an `answer` key, which helps, but the model may still embed preamble in the value.

### 1.3 Difficulty Distribution

From `v1_architecture.md` §4:

| Difficulty | Pilot (20) | Full (100) | Purpose |
|------------|-----------|-----------|---------|
| `easy` | 4 | 20 | Baseline — models should get right with high confidence |
| `medium` | 7 | 35 | Standard evaluation — moderate knowledge required |
| `hard` | 5 | 25 | Discriminates strong from average models |
| `deceptive` | 3 | 15 | Looks easy but isn't (cognitive reflection, common misconceptions) |
| `adversarial` | 1 | 5 | Stress test — designed to elicit overconfidence on wrong answers |

### 1.4 Scoring Behavior

Understanding how `calibration_aware_score()` works is necessary to author items that discriminate between models:

```python
def calibration_aware_score(is_correct, confidence):
    if is_correct:
        return 0.5 + 0.5 * confidence   # Range: [0.5, 1.0]
    else:
        return 0.5 * (1.0 - confidence)  # Range: [0.0, 0.5]
```

| Scenario | Score | Dataset implication |
|----------|-------|---------------------|
| Correct + high confidence (0.95) | 0.975 | Easy items should produce this — validates baseline |
| Correct + low confidence (0.3) | 0.65 | Hard items might produce this — model knows but is uncertain |
| Wrong + low confidence (0.2) | 0.40 | Acceptable — model was uncertain and wrong |
| Wrong + high confidence (0.9) | 0.05 | Heavy penalty — this is what deceptive/adversarial items should trigger in weaker models |

**Design target:** A well-calibrated model scores ≈ 0.80-0.85 on the full set. A model that defaults to 0.5 confidence on everything scores ≈ 0.50 regardless of accuracy. A chronically overconfident model scores < 0.60 if it gets hard items wrong.

### 1.5 File Format

Output must be `data/calibration.csv` (plain CSV, UTF-8, no BOM). The task function reads this via `kbench` DataFrame semantics — column names must match exactly.

---

## 2. Key Dataset Attributes

### 2.1 What Makes a Good Calibration Item

A calibration benchmark tests whether the model's stated confidence matches its actual likelihood of being correct. The dataset needs items that spread models across the confidence-accuracy plane. Specifically:

| Attribute | Description |
|-----------|-------------|
| **Verifiable ground truth** | Every item must have an objectively correct answer that can be string-matched. No opinion questions, no judgment calls. |
| **Difficulty variation** | Easy items the model should nail with high confidence, hard items where even strong models might be uncertain, deceptive items that tempt confident wrong answers. |
| **Domain breadth** | Items should span multiple knowledge domains to avoid measuring domain expertise rather than metacognition. |
| **Short, unambiguous prompts** | The prompt should not be a reading comprehension task. Calibration measures confidence tracking, not comprehension. |
| **Known difficulty stratification** | The author should have a hypothesis about which difficulty tier each item belongs to, validated (ideally) by pilot testing. |

### 2.2 Item Type Categories

These are the domain categories (`item_family`) that should be represented:

| Category | Difficulty Range | Example |
|----------|-----------------|---------|
| **Factual recall** | easy–medium | "What is the chemical symbol for gold?" → `"au"` |
| **Arithmetic / numeric** | medium–hard | "What is the square root of 1764?" → `"42"` |
| **Cognitive reflection** | deceptive | Bat-and-ball, lily pad doubling, etc. — classic CRT items |
| **Common misconceptions** | deceptive | "What color is a polar bear's skin?" → `"black"` |
| **Obscure but answerable facts** | hard | Facts that exist but most models may not encode reliably |
| **Adversarial / near-unknowable** | adversarial | Questions with a definite answer but strong temptation to confabulate |
| **Numeric estimation** | medium–hard | "How many countries are in Africa?" → `"54"` (models often get close but not exact) |

### 2.3 What the Dataset Should NOT Contain

| Exclusion | Reason |
|-----------|--------|
| Open-ended or opinion-based questions | No gold answer possible |
| Questions with multiple valid answer formats | Breaks exact match (`"Mount Everest"` vs `"Everest"` vs `"Sagarmatha"`) |
| Questions requiring current/recent knowledge | Model training cutoffs vary; not testing metacognition |
| Questions with long or complex gold answers | Increases match failure risk |
| Questions where difficulty depends on language/culture | Should be answerable across English-trained models |
| Duplicate or near-duplicate items | Wastes budget, inflates easy-item bias |

---

## 3. Open Questions

These are unresolved issues that must be answered before or during dataset authoring. They are listed roughly in priority order.

### 3.1 Answer Format Robustness

**Question:** How reliably does the `CalibrationResponse` JSON schema force the model to put only the bare answer in the `answer` field?

**Why it matters:** If the model writes `"The answer is 42"` in the `answer` field, `normalize_text` will not match `"42"`. The JSON schema should constrain this, but we have no empirical data from the SDK's `llm.prompt(schema=...)` behavior on diverse question types.

**Next step:** In the 20-item pilot, deliberately include items where models are likely to produce verbose answers (e.g., sentence-form answers). Check the raw `answer` field values. If > 10% of items have format mismatch, either (a) tighten the prompt, (b) add post-processing to the scoring pipeline, or (c) redesign `gold_answer` to be more forgiving.

### 3.2 Difficulty Calibration of the Calibration Items

**Question:** How do we validate that items labeled `easy` are actually easy and items labeled `hard` are actually hard — before spending quota?

**Why it matters:** If difficulty labels are wrong, the benchmark measures nothing useful. An item labeled `deceptive` that every model gets right doesn't test overconfidence.

**Possible approaches:**
- **Heuristic authoring:** Author difficulty based on human judgment (fast, cheap, error-prone).
- **Pre-pilot on free APIs:** Run items through freely available models (e.g., local inference or free-tier APIs) to validate difficulty before spending Kaggle quota.
- **Iterative pilot:** Use the 20-item pilot run itself as the validation step. Re-label difficulty based on observed accuracy. Risk: wastes one quota run.

**Next step:** Decide which approach before authoring the full 100-item set. The 20-item pilot should inform difficulty labeling for the remaining 80.

### 3.3 Domain Breadth vs. Depth

**Question:** How many distinct domains should the 100-item set cover? How many items per domain?

**Why it matters:** Too few domains → we measure domain expertise, not metacognition. Too many domains with 1-2 items each → no statistical power per domain, and `item_family` metadata becomes noise.

**Constraint:** 100 items across 5 difficulty tiers. If we want ~3 items per domain-difficulty cell, we can cover roughly 6-7 domains.

**Candidate domain list (7 domains):**

| Domain | Items (approx) | Rationale |
|--------|----------------|-----------|
| Arithmetic / math | 15 | Objectively verifiable, wide difficulty range |
| Geography / capitals | 12 | Classic factual recall, easy to hard |
| Science (chemistry, physics, biology) | 15 | Broad, verifiable, spans difficulty |
| History (dates, events) | 12 | Factual, but some obscure facts are genuinely hard |
| Language / linguistics | 10 | Word origins, grammar rules — verifiable |
| Logic / cognitive reflection | 15 | Deceptive items, classic CRT, reasoning traps |
| Numeric estimation / counts | 10 | "How many X are there?" — tests calibration directly |
| **Buffer / adversarial** | 11 | Cross-domain adversarial items |

**Next step:** Finalize domain list. Ensure at least 2-3 items per domain × difficulty combination where possible.

### 3.4 Deceptive Items: Source and Validation

**Question:** Where do we source deceptive/adversarial items, and how do we ensure they actually fool models?

**Why it matters:** Deceptive items are the most valuable for discriminating well-calibrated from poorly-calibrated models. But they're hard to author: a question that fools GPT-4 may not fool Claude, and vice versa. Items from published CRT (Cognitive Reflection Tests) may already be in training data.

**Known good sources:**
- Frederick (2005) CRT items — but likely memorized by frontier models
- Semantic illusions ("How many animals did Moses take on the Ark?" → `"0"`, it was Noah)
- Numerical intuition traps (birthday paradox, Monty Hall)
- Common factual misconceptions (Great Wall visible from space → `"no"`)

**Risk:** If deceptive items are memorized, frontier models will get them right with high confidence, making them indistinguishable from easy items. Need novel or modified deceptive items.

**Next step:** Author 5-8 candidate deceptive items. Run them through 2+ models (if possible pre-pilot) to check if they actually produce overconfident wrong answers.

### 3.5 Reproducibility Across Model Generations

**Question:** Will the dataset remain valid as models improve?

**Why it matters:** If every model aces the calibration set within 6 months, the benchmark has no shelf life. The Kaggle competition cares about current discrimination, but the writeup will be stronger if we address longevity.

**Mitigation strategies:**
- Include a spectrum: some items only hard-difficulty models get wrong, some items frontier models still struggle with.
- `damage_sensitive` flag and `risk_class` metadata allow post-hoc analysis even if overall accuracy converges.
- The adversarial tier is specifically designed for items that resist memorization.

**Not a V1 blocker** but should be mentioned in the writeup.

### 3.6 Anti-Gaming: The Low-Confidence Hedge

**Question:** Can a model game the benchmark by always reporting ~0.5 confidence?

**Scoring analysis:**
- If the model reports 0.5 confidence and is correct: score = 0.75
- If the model reports 0.5 confidence and is wrong: score = 0.25
- Expected score at 70% accuracy with constant 0.5 confidence: 0.70 × 0.75 + 0.30 × 0.25 = 0.60

Compare to a well-calibrated model at 70% accuracy:
- Correct items at 0.85 avg confidence: score ≈ 0.925
- Wrong items at 0.35 avg confidence: score ≈ 0.325
- Expected: 0.70 × 0.925 + 0.30 × 0.325 ≈ 0.745

**Conclusion:** The scoring function already penalizes the hedge strategy. A constant-confidence model scores ~0.60 vs. ~0.75 for a calibrated model at the same accuracy. This gap is sufficient, but the dataset should include enough easy items (where calibrated models can confidently score ~0.975) to widen it.

**Not a dataset change** — this is a scoring validation. Documented here because dataset difficulty distribution affects the gap.

### 3.7 The `$0.05` Problem: Currency and Symbol Matching

**Question:** How should we handle gold answers that contain symbols, currency, or special characters?

**Example from prototypes:** `cal_003` has `gold_answer: "$0.05"`. If the model returns `"0.05"`, `"$0.05"`, `"5 cents"`, or `"five cents"`, only exact post-normalization match wins.

**Options:**
1. **Strip all non-alphanumeric from gold_answer** (would require modifying `normalize_text`)
2. **Author gold_answer as the most likely model output** (e.g., `"0.05"` and prompt for numeric-only)
3. **Accept the risk** and check empirically in the pilot

**Next step:** Decide before authoring. Recommendation: author gold answers as bare numbers/words without symbols, and add a line to the prompt template instructing the model to answer with the bare value only. This avoids changing `normalize_text` (which is tested and stable).

---

## 4. Summary: Authoring Checklist

Before writing each item, verify:

- [ ] `gold_answer` is short (1-5 tokens), unambiguous, and survives `normalize_text`
- [ ] `gold_answer` contains no trailing punctuation, currency symbols, or unit variations
- [ ] `difficulty` label has a clear rationale (documented per-item or per-batch)
- [ ] `example_id` follows the `cal_NNN` pattern and is unique
- [ ] `item_family` is assigned from the approved domain list
- [ ] `prompt` does not leak the answer or hint at the difficulty
- [ ] For `deceptive` items: the item has a plausible wrong answer that models are likely to give confidently
- [ ] For `adversarial` items: the item is designed to resist memorization (novel phrasing, uncommon facts)
- [ ] For `easy` items: the item should be answerable by any model with > 0.9 confidence — this validates baseline scoring

---

## 5. Next Steps (Ordered)

1. **Decide on gold_answer format policy** (§3.7) — bare values vs. symbols
2. **Finalize domain list** (§3.3) — confirm 7 domains or adjust
3. **Author 20-item pilot set** → `data/calibration.csv`
4. **Run pilot in Kaggle** — check answer format issues (§3.1), validate difficulty labels (§3.2)
5. **Analyze pilot results** — re-label difficulty, adjust prompt template if needed
6. **Author remaining 80 items** informed by pilot
7. **Run full 100-item set** — compute diagnostics, iterate if needed
