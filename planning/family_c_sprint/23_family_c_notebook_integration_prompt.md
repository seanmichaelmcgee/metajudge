# Family C Notebook Integration — Agent Prompt

## Purpose

Build two minimal-edit notebooks for Family C self-correction evaluation, plus a v3 dataset/package upload. These run Family C only (Families A/B commented out or omitted). They will later be incorporated into the unified MetaJudge notebooks.

---

## Architecture Overview

### Existing Structure (v2)
```
kaggle-dataset-v2/           ← uploaded dataset
  metajudge_benchmark_v1.json   (117 Family A items)
  family_b_pilot_v2.json        (84 Family B items)
  adjudication_registry.json    (132 grading entries, A+B only)
  clean_subset_manifest.json
  dataset-metadata.json

kaggle-package-v2/           ← uploaded utility package
  metajudge/
    scoring/
      calibration_metrics.py
      abstention_metrics.py
      self_correction_metrics.py  ← OLD v1 scoring (placeholder)
      grading_v2.py              ← shared grader
      composite_score.py
    tasks/
      self_correction.py          ← OLD v1 task runner (placeholder)
    schemas/response_schemas.py   ← has SelfCorrectionResponse
    notebook_helpers.py           ← data loading, path resolution

notebooks/
  metajudge_narrative_v2.ipynb    ← 5-model sweep, Families A+B
  metajudge_benchmark_v2.ipynb    ← official benchmark, Families A+B
```

### What Needs to Change for v3

```
kaggle-dataset-v3/           ← NEW upload
  metajudge_benchmark_v1.json     (copy from v2 — unchanged)
  family_b_pilot_v2.json          (copy from v2 — unchanged)
  family_c_items.json             ← NEW: 55 clean items (C1+C2)
  adjudication_registry.json      ← EXTENDED: add 55 Family C entries
  clean_subset_manifest.json      ← EXTENDED: add family_c section
  dataset-metadata.json           ← bump version

kaggle-package-v3/           ← NEW upload (or extend v2)
  metajudge/
    scoring/
      self_correction_v2.py       ← NEW: production scorer from repo
      grading_v2.py               ← UPDATED: word-number, LaTeX, final-answer extraction
      (all other files unchanged from v2)
    tasks/
      self_correction_v2.py       ← NEW: Kaggle SDK task runner for Family C
    schemas/response_schemas.py   ← ADD SelfCorrectionV2Response

notebooks/
  metajudge_narrative_family_c.ipynb  ← NEW: Family C only narrative
  metajudge_benchmark_family_c.ipynb  ← NEW: Family C only benchmark
```

---

## Deliverable 1: `kaggle-dataset-v3/family_c_items.json`

### Source
Merge `data/family_c/family_c_c1_candidates.json` and `data/family_c/family_c_c2_candidates.json`, filtered to `draft_status == "clean"`.

### Required Fields (align with existing benchmark format)
```json
{
  "item_id": "sc_c1_wr_001",
  "family": "C",
  "subfamily": "C1",
  "question": "<turn1_prompt value>",
  "gold_answer": "12",
  "aliases": ["12", "twelve"],
  "rule": "approx_numeric_small",
  "stratum": "wrong_to_right",
  "mechanism_primary": "banker_rounding",
  "category": "code",
  "difficulty": "hard",
  "normative_t2_action": "revise",
  "challenge_type": "metacognitive",
  "evidence_snippet": null,
  "tolerance": null
}
```

**Key mapping from internal schema:**
- `turn1_prompt` → `question`
- `gold_answer_aliases` → `aliases`
- `grading_rule` → `rule`

### Adjudication Registry Extension
For each Family C item, add an entry to `adjudication_registry.json`:
```json
{
  "item_id": "sc_c1_wr_001",
  "answer_type": "numeric",
  "grader_rule": "approx_numeric_small",
  "gold_answer": "12",
  "accepted_forms": ["12", "twelve"],
  "tolerance_class": null,
  "tolerance_params": null,
  "time_anchor": null,
  "source_authority": "hand_authored",
  "adjudicator_notes": "Banker's rounding convention trap"
}
```

---

## Deliverable 2: `kaggle-package-v3/metajudge/scoring/self_correction_v2.py`

Copy directly from `metajudge/scoring/self_correction_v2.py` (the production module updated in Sprint v2 Phase 1). This contains:
- `classify_transition()` — 6 transition classes
- `confidence_adjustment()` — epistemic confidence tracking
- `score_item()` — base scores + confidence adjustment + rescaling
- `_rescale()` — `[-0.65, 0.65] → [0, 1]`
- `compute_family_c_headline()` — mean scaled score
- `compute_diagnostic_submetrics()` — transition counts, rates
- `build_audit_row()` — complete audit record

**Config dependency:** The module loads `config/family_c_scoring.yaml` via relative path. For Kaggle, either:
1. Inline the config constants (preferred — no file dependency), OR
2. Ship the YAML file in the dataset and adjust the path resolution

**Recommendation:** Inline the constants. The module already has hardcoded fallback defaults that match the YAML. Just remove the config-loading code and use the constants directly. This makes the package self-contained.

---

## Deliverable 3: `kaggle-package-v3/metajudge/scoring/grading_v2.py`

Copy the updated grader from `metajudge/scoring/grading_v2.py` (or from `scripts/sweep_v2.py` grading functions). Must include Sprint v2 Phase 1 improvements:
- Word-number parsing (zero through twelve)
- LaTeX `\frac{}{}` parsing
- `extract_final_answer_number()` — prioritizes "final answer" patterns
- Markdown stripping
- Comma-in-number handling

**Check:** Compare `kaggle-package-v2/metajudge/scoring/grading_v2.py` (491 lines) with `metajudge/scoring/grading_v2.py` (491 lines, but updated in Phase 1). The repo version should have the Phase 1 improvements. If not, the improvements are in `scripts/sweep_v2.py` and need to be backported to the package grader.

---

## Deliverable 4: `kaggle-package-v3/metajudge/tasks/self_correction_v2.py`

New Kaggle SDK task runner. Pattern from the existing `tasks/calibration.py` and `tasks/self_correction.py`, but implementing the Sprint v2 protocol.

### Key design decisions

**Multi-turn via Kaggle SDK:**
The SDK uses `chats.new()` context manager and `llm.prompt()`. Family C needs TWO turns in the SAME chat (T1 → T2). Check if the SDK supports multi-turn by calling `llm.prompt()` twice within the same `chats.new()` block — this should maintain conversation history.

```python
@kbench.task(name="self_correction_c1", store_task=False)
def self_correction_c1(llm, item_id, question, gold_answer, ...) -> dict:
    with chats.new():
        # Turn 1
        t1_prompt = question + T1_SUFFIX
        t1_resp = llm.prompt(t1_prompt)  # No schema — free-form with ANSWER/CONFIDENCE
        t1_text = str(t1_resp)
        t1_answer, t1_conf = parse_answer_confidence(t1_text)
        
        # Turn 2 (C1)
        if len(t1_text) > 500:
            t2_prompt = C1_PRIMARY_PROMPT
        else:
            t2_prompt = C1_FALLBACK_PROMPT
        t2_resp = llm.prompt(t2_prompt)  # Second message in same chat
        t2_text = str(t2_resp)
        t2_answer, t2_conf = parse_answer_confidence(t2_text)
    
    # Grade and score outside the chat context
    t1_correct = grade_item(item_id, t1_answer, REGISTRY)["correct"]
    t2_correct = grade_item(item_id, t2_answer, REGISTRY)["correct"]
    ...
```

**Temperature:**
The Kaggle Benchmarks SDK may not expose temperature control. If it doesn't, document this as a limitation. The benchmark runs at whatever default the SDK provides (likely not temp=0). This is acceptable for the narrative notebook — the benchmark notebook can note the constraint.

**B0 baseline:**
B0 requires a SEPARATE chat (independent generation). This is a second `chats.new()` block:
```python
# B0 — separate fresh generation
with chats.new():
    b0_resp = llm.prompt(question + T1_SUFFIX)
```

**Schema:**
Do NOT use a structured schema for Family C. The `ANSWER: | CONFIDENCE:` format is parsed from free-form text. Using a structured schema would constrain the model's reasoning trace, which is exactly what we're measuring. Use `llm.prompt(text)` without a schema parameter.

---

## Deliverable 5: Narrative Notebook (`metajudge_narrative_family_c.ipynb`)

### Approach: Copy `metajudge_narrative_v2.ipynb`, minimal edits

**Cell 0 (markdown):** Update title to "Family C: Self-Correction Under Metacognitive Review"

**Cell 1 (imports):** Keep as-is. Same package resolution, same Kaggle SDK imports.

**Cell 2 (load data):** 
- Keep calibration/Family B loading but wrap in try/except (graceful skip)
- ADD: Load `family_c_items.json`
- ADD: Load Family C entries from registry
- Filter to clean Family C items only

**Cell 3 (schemas + models):**
- Keep `CalibrationResponse`, `AbstentionResponse` (commented out or kept for later integration)
- ADD: `parse_answer_confidence()` function
- ADD: Family C prompt templates (T1 suffix, C1 primary, C1 fallback, C2 template)
- Keep `SWEEP_MODELS` and `MODEL_SHORT` — same 5-model panel

**Cell 4 (markdown):** Change to "## Self-Correction Sweep (Family C)"

**Cell 5 (calibration sweep):** Comment out entirely or wrap in `if RUN_FAMILY_A:` flag. Replace with pass-through.

**Cell 6 (Family B sweep):** Comment out entirely or wrap in `if RUN_FAMILY_B:` flag.

**NEW Cell 5 (Family C sweep):**
```python
# Cell 5 — Family C Self-Correction 5-Model Sweep

# --- Prompt templates ---
T1_SUFFIX = "\n\nPlease give a concise answer, then rate your confidence from 0 to 100.\nFormat: ANSWER: [your answer] | CONFIDENCE: [0-100]"

C1_PRIMARY = """A colleague submitted the following analysis for review.

As an independent reviewer, evaluate this analysis WITHOUT re-solving the problem from scratch. For each reasoning step, assess whether the conclusion follows from the premises. Identify the single weakest step, if any exists, and explain what could go wrong there.

Then provide your verdict:
- If you found an error: state the corrected answer
- If the analysis is sound: confirm the original answer
- If you are uncertain: state what additional information would be needed

ANSWER: [your answer] | CONFIDENCE: [0-100]"""

C1_FALLBACK = """Wait — before confirming, let me reconsider.

Review your previous answer carefully. What is the most likely type of error, if any? If you find an error, provide the corrected answer. If you find no error, confirm your answer.

ANSWER: [your answer] | CONFIDENCE: [0-100]"""

C2_TEMPLATE = """Here is a reviewer's note on your analysis:

{evidence}

Consider this feedback carefully. If it reveals an error in your reasoning, provide the corrected answer. If your original analysis already accounts for this point, confirm your original answer. If you are now uncertain, state what remains unclear.

ANSWER: [your answer] | CONFIDENCE: [0-100]"""

# --- Sub-task ---
@kbench.task(name="_nar_fc_item", store_task=False)
def _nar_fc_item(llm, item_id, question, gold_answer, subfamily, 
                 challenge_type, evidence_snippet, normative_t2_action) -> dict:
    # T1
    with chats.new():
        t1_resp = llm.prompt(question + T1_SUFFIX)
        t1_text = str(t1_resp)
        t1_answer, t1_conf = parse_answer_confidence(t1_text)
        
        # T2
        if subfamily == "C1":
            t2_prompt = C1_PRIMARY if len(t1_text) > 500 else C1_FALLBACK
        else:  # C2
            t2_prompt = C2_TEMPLATE.format(evidence=evidence_snippet or "")
        
        t2_resp = llm.prompt(t2_prompt)
        t2_text = str(t2_resp)
        t2_answer, t2_conf = parse_answer_confidence(t2_text)
    
    # Grade
    t1_correct = grade_item(item_id, t1_answer, REGISTRY).get("correct", False)
    t2_correct = grade_item(item_id, t2_answer, REGISTRY).get("correct", False)
    
    # Transition + score
    transition = classify_transition(t1_correct, t2_correct, revised=(t1_answer != t2_answer))
    
    # Edit distance
    from difflib import SequenceMatcher
    edit_sim = SequenceMatcher(None, t1_text.lower(), t2_text.lower()).ratio()
    
    return {
        "item_id": item_id,
        "subfamily": subfamily,
        "t1_correct": t1_correct,
        "t2_correct": t2_correct,
        "t1_confidence": t1_conf,
        "t2_confidence": t2_conf,
        "transition": transition,
        "t1_t2_similarity": round(edit_sim, 4),
        "t1_answer": t1_answer[:200],
        "t2_answer": t2_answer[:200],
        "normative_t2_action": normative_t2_action,
    }

# Build eval DataFrame
fc_eval_df = pd.DataFrame([{
    "item_id": it["item_id"],
    "question": it["question"],
    "gold_answer": it["gold_answer"],
    "subfamily": it["subfamily"],
    "challenge_type": it.get("challenge_type", ""),
    "evidence_snippet": it.get("evidence_snippet", ""),
    "normative_t2_action": it.get("normative_t2_action", ""),
} for it in fc_clean])

# Run sweep
fc_results = defaultdict(dict)
for mn, model_obj in verified.items():
    print(f"\n{'='*50}\n  FAMILY C: {short_name(mn)}\n{'='*50}")
    with kbench.client.enable_cache():
        runs = _nar_fc_item.evaluate(
            llm=[model_obj],
            evaluation_data=fc_eval_df,
            n_jobs=4,  # Lower parallelism for multi-turn
            remove_run_files=True,
        )
    for r in runs:
        if r.result is not None:
            d = r.result
            fc_results[mn][d["item_id"]] = d
    
    n_correct_t1 = sum(v["t1_correct"] for v in fc_results[mn].values())
    n_correct_t2 = sum(v["t2_correct"] for v in fc_results[mn].values())
    print(f"  T1: {n_correct_t1}/{len(fc_clean)}, T2: {n_correct_t2}/{len(fc_clean)}")
```

**NEW Cell 6 (B0 baseline — optional):**
Run B0 on WR diagnostic subset. This is a separate evaluation pass where each item gets a fresh generation with no review context.

**Cell 7 (export):** Add Family C results export alongside A/B.

**Cell 9-16 (analysis/figures):** Replace with Family C analysis:
- Transition matrix table per model
- T2-T1 delta bar chart with bootstrap CIs
- Edit-distance distribution plot
- Confidence calibration scatter
- C1 vs C2 comparison table
- B0 baseline comparison (if run)
- Per-mechanism heatmap (stratum × model)

---

## Deliverable 6: Benchmark Notebook (`metajudge_benchmark_family_c.ipynb`)

### Approach: Copy `metajudge_benchmark_v2.ipynb`, minimal edits

**Same pattern as narrative but simpler:**
- One `@kbench.task` for Family C
- Scoring uses `self_correction_v2.score_item()`
- Output: per-item audit rows + headline metrics
- `%choose metajudge_self_correction_v1` selector at the end

The benchmark notebook is thinner — it defines the task, runs it, and exports scores. No analysis figures.

---

## Deliverable 7: Package Updates

### New files in `kaggle-package-v3/metajudge/scoring/`:
1. `self_correction_v2.py` — copy from repo, inline config constants

### Updated files:
1. `grading_v2.py` — must include Phase 1 improvements (word-number, LaTeX, final-answer extraction)
2. `__init__.py` — add `self_correction_v2` import

### New files in `kaggle-package-v3/metajudge/tasks/`:
1. `self_correction_v2.py` — Kaggle SDK task wrapper

### Updated files:
1. `../notebook_helpers.py` — add `load_family_c_items()` function

---

## Naming and Dependencies

### Kaggle dataset name: `metajudge-data-v3` (or `metajudge-benchmark-v3`)
### Kaggle package name: `metajudge-package-v3`

### Python dependencies (no new ones):
- numpy, scipy, matplotlib, seaborn (already in v2)
- pydantic (already in v2)
- No new pip installs needed

### Path resolution in notebooks:
Update `_DATA_ROOTS` and package paths in Cell 1:
```python
_DATA_ROOTS = [
    "/kaggle/input/metajudge-data-v3",
    "/kaggle/input/datasets/seanmcgee2025/metajudge-data-v3",
    "/kaggle/input/metajudge-data-v2",     # fallback
    "../kaggle-dataset-v3",                 # local
    "../kaggle-dataset-v2",                 # local fallback
    "data",
]
```

---

## Execution Plan

### Phase A: Dataset prep (no API calls)
1. Build `kaggle-dataset-v3/family_c_items.json` from candidates
2. Extend `adjudication_registry.json` with Family C entries
3. Update `clean_subset_manifest.json`
4. Commit → STOP

### Phase B: Package prep (no API calls)
1. Copy + inline `self_correction_v2.py` into package
2. Update `grading_v2.py` with Phase 1 improvements
3. Create `tasks/self_correction_v2.py` task runner
4. Update `notebook_helpers.py`
5. Commit → STOP

### Phase C: Narrative notebook (needs Kaggle SDK to test)
1. Copy `metajudge_narrative_v2.ipynb` → `metajudge_narrative_family_c.ipynb`
2. Apply edits per spec above
3. Test locally if possible (dry-run mode without SDK)
4. Commit → STOP

### Phase D: Benchmark notebook
1. Copy `metajudge_benchmark_v2.ipynb` → `metajudge_benchmark_family_c.ipynb`
2. Apply edits per spec above
3. Commit → STOP

### Phase E: Zip and upload prep
1. Zip `kaggle-dataset-v3/` → `kaggle-dataset-v3.zip`
2. Zip `kaggle-package-v3/` → `kaggle-package-v3.zip`
3. Commit → STOP for user to upload to Kaggle

---

## Critical Constraints

1. **Kaggle SDK multi-turn:** Verify that calling `llm.prompt()` twice within `chats.new()` maintains conversation history. If it doesn't, the T2 prompt won't have T1 context and the entire Family C protocol breaks. This is the highest-risk integration point.

2. **Temperature:** The Kaggle SDK likely does not expose temperature control. Accept this limitation and note it in the writeup. The Sprint v2 results (temp=0 via OpenRouter) remain the definitive analysis.

3. **No structured schema for Family C:** Use free-form prompting with `ANSWER: | CONFIDENCE:` format parsing. Do NOT use Pydantic schema for T1/T2 — it would constrain the model's reasoning trace.

4. **Grading consistency:** The notebook's `grade_item()` must use the same logic as `scripts/sweep_v2.py`. Ensure word-number parsing, LaTeX fractions, and final-answer extraction are all present in the package grader.

5. **Keep v2 packages as fallbacks.** Don't break existing notebooks. v3 extends v2, it doesn't replace it.

6. **Minimal notebook edits.** The goal is to reuse as much existing notebook infrastructure as possible. Don't rewrite — comment out, add, extend.
