# MetaJudge Grading Audit — LLM Semantic Review

## Your Role

You are an independent grading auditor for MetaJudge, a metacognition benchmark
for large language models. Your task is to review every item marked as
**incorrectly answered** across 4 model runs and determine whether the grading
is justified or whether the model's answer is actually correct despite being
marked wrong.

This is a **false-negative audit**: we are looking for cases where the model
gave a semantically correct answer that the automated grading engine failed to
recognize. False positives (marked correct when actually wrong) are less likely
and lower priority, but flag any you notice.

## Context

The benchmark evaluates 4 models across 3 families:
- **Family A (Calibration)**: 105 items — model answers a question and states confidence
- **Family B (Abstention)**: 72 items — model chooses an action (answer/clarify/verify/abstain)
- **Family C (Self-Correction)**: 51 items — model answers (T1), then reviews and may revise (T2)

The automated grading engine uses:
- 8 grading rules (exact match, numeric tolerance, alias matching, etc.)
- An adjudication registry with gold answers and accepted aliases per item
- `contains_any` match mode for some items (substring matching)
- Confirmation-without-restatement detection for Family C T2 answers

## Known failure patterns (from prior audits)

These are the grading errors we have already identified and fixed. They may
still appear in these results since the runs used earlier grading versions.
**Do not re-flag these — they are known.** Instead, look for NEW patterns.

1. **Verbose answers containing the gold but failing alias match** — e.g.,
   "The amounts are the same" for gold="They are equal" where alias "the same"
   exists but `contains_any` mode was not set. (Fixed: v41_crt_009)

2. **Confirmation-without-restatement** — Model says "I confirm my previous
   answer" or "My original analysis already accounts for..." without restating
   the answer value. The T2 answer text doesn't contain the gold string.
   (Fixed: `resolve_t2_answer()` with expanded phrase list)

3. **Numeric tolerance too tight** — e.g., gold=1.273885, model says 1.27
   (correct to 2 sig figs). (Fixed: rel_tol=0.005 for affected items)

4. **LaTeX/exponential notation** — `\frac{5}{11}` or `2^{81}` not parsed.
   (Fixed: `_strip_latex()` in grading engine)

5. **First-number extraction** — "0.1 + 0.2 = 0.3" extracts 0.1 instead of
   0.3. (Fixed: `_extract_final_answer_number()`)

## What to review

For each item marked wrong, evaluate:

1. **Is the model's answer semantically equivalent to the gold answer?**
   Consider: synonyms, rephrasings, equivalent numeric forms, correct answers
   expressed differently than the gold.

2. **Is the gold answer itself correct?** If the model's answer is actually
   more accurate than the gold, flag it.

3. **Is the grading rule appropriate?** If the item uses `exact_match` but
   should use `alias_plus_normalization`, flag it.

4. **For Family B**: When the model chose "answer" and was marked wrong, is
   the model's answer actually correct? Also: if the model chose a non-answer
   action (clarify/verify/abstain), was that action reasonable given the
   question?

5. **For Family C**: Review BOTH T1 and T2. If T2 is marked wrong but the
   model confirmed its (correct) T1 answer in review prose, flag it as a
   confirmation-without-restatement issue.

## Output format

For each item you flag, provide:

```
ITEM: <item_id>
MODEL: <model_name>
FAMILY: A/B/C
TURN: T1/T2 (Family C only)
GOLD: <gold_answer>
MODEL_ANSWER: <model's answer>
RECORDED: wrong
VERDICT: CORRECT / BORDERLINE / WRONG (confirmed)
REASON: <1-2 sentence explanation>
SEVERITY: HIGH (changes a score) / LOW (cosmetic)
```

At the end, provide a summary:

```
SUMMARY:
  Total items reviewed: <N>
  Confirmed wrong (grading correct): <N>
  Flagged as CORRECT (grading error): <N>
  Flagged as BORDERLINE: <N>
  Items where gold answer is suspect: <N>
```

## Data

The following CSV data contains every item marked as wrong across 4 model runs.
Review each one.

### Family A — Calibration (items marked wrong)

```csv
model,item_id,question,gold_answer,model_answer,confidence,grading_rule
[DATA WILL BE INSERTED HERE — see generation script below]
```

### Family B — Abstention (items where decision=answer and marked wrong)

```csv
model,item_id,question,gold_answer,gold_action,model_decision,model_answer,grading_rule
[DATA WILL BE INSERTED HERE]
```

### Family C — Self-Correction (T1 or T2 marked wrong)

```csv
model,item_id,turn,question,gold_answer,model_answer,grading_rule
[DATA WILL BE INSERTED HERE]
```

---

## How to generate the data CSVs

Run the following script to extract all wrong-graded items into a single
CSV suitable for pasting into the prompt above:

```python
# scripts/extract_wrong_for_llm_audit.py
import csv, json, os, sys

RESULTS_DIRS = sys.argv[1:]  # Pass one or more results directories
REGISTRY_PATH = "kaggle-dataset-v3/adjudication_registry.json"
SOURCE_A = "kaggle-dataset-v3/metajudge_benchmark_v1.json"
SOURCE_B = "kaggle-dataset-v3/family_b_pilot_v2.json"
SOURCE_C = "kaggle-dataset-v3/family_c_items.json"

with open(REGISTRY_PATH) as f:
    registry = {r["item_id"]: r for r in json.load(f)}
with open(SOURCE_A) as f:
    items_a = {it["item_id"]: it for it in json.load(f)}
with open(SOURCE_B) as f:
    items_b = {it["item_id"]: it for it in json.load(f)}
with open(SOURCE_C) as f:
    items_c = {it["item_id"]: it for it in json.load(f)}

print("=== FAMILY A ===")
print("model,item_id,question,gold_answer,model_answer,confidence,grading_rule")
for rdir in RESULTS_DIRS:
    model = os.path.basename(rdir.rstrip("/"))
    path = os.path.join(rdir, "calibration_item_audit.csv")
    if not os.path.exists(path): continue
    for row in csv.DictReader(open(path)):
        if row["is_correct"] == "False":
            iid = row["item_id"]
            q = items_a.get(iid, {}).get("question", "")[:150]
            rule = registry.get(iid, {}).get("grader_rule", "?")
            print(f'{model},{iid},"{q}","{row["gold_answer"]}","{row["model_answer"][:100]}",{row["confidence"]},{rule}')

print("\n=== FAMILY B (answer+wrong only) ===")
print("model,item_id,question,gold_answer,gold_action,model_decision,model_answer,grading_rule")
for rdir in RESULTS_DIRS:
    model = os.path.basename(rdir.rstrip("/"))
    path = os.path.join(rdir, "family_b_item_audit.csv")
    if not os.path.exists(path): continue
    for row in csv.DictReader(open(path)):
        if row["model_decision"] == "answer" and row["is_correct"] == "False":
            iid = row["item_id"]
            q = items_b.get(iid, {}).get("question", "")[:150]
            rule = registry.get(iid, {}).get("grader_rule", "?")
            print(f'{model},{iid},"{q}","{row["gold_answer"]}",{row["gold_action"]},{row["model_decision"]},"{row["model_answer"][:100]}",{rule}')

print("\n=== FAMILY C (T1 or T2 wrong) ===")
print("model,item_id,turn,question,gold_answer,model_answer,grading_rule")
for rdir in RESULTS_DIRS:
    model = os.path.basename(rdir.rstrip("/"))
    path = os.path.join(rdir, "family_c_item_audit.csv")
    if not os.path.exists(path): continue
    for row in csv.DictReader(open(path)):
        iid = row["item_id"]
        q = items_c.get(iid, {}).get("question", "")[:150]
        rule = registry.get(iid, {}).get("grader_rule", "?")
        if row["t1_correct"] == "False":
            print(f'{model},{iid},T1,"{q}","{registry.get(iid,{}).get("gold_answer","?")}","{row["t1_answer"][:100]}",{rule}')
        if row["t2_correct"] == "False":
            print(f'{model},{iid},T2,"{q}","{registry.get(iid,{}).get("gold_answer","?")}","{row["t2_answer"][:100]}",{rule}')
```

Run as:
```bash
python scripts/extract_wrong_for_llm_audit.py \
    /path/to/results-flash2.5 \
    /path/to/results-gemini2.5-pro \
    /path/to/results-sonnet4 \
    /path/to/results-flash-3.1-lite
```

Then paste the output into the DATA sections of this prompt and submit to a
long-context model (Claude Opus, Gemini 1.5 Pro, etc.).

---

## Scope expectations

- **~117 wrong-graded items** across 4 models (35 Family A + 59 Family B + 23 Family C)
- Most will be genuinely wrong (models do get items wrong)
- We expect **5-15 flagged items** based on prior audit patterns
- Any item flagged by 2+ reviewers should be investigated immediately
- Items flagged as CORRECT with HIGH severity require registry or alias fixes before submission
