# Family C Notebook Integration — Revised Plan (v3)

## Context

Plan 23 specified separate Family C-only notebooks. Phases A (dataset-v3) and
B (package-v3) are done. Phase C (narrative notebook) caused three agent teams
to time out trying to create the narrative notebook from scratch.

**Revised approach:** Add Family C *into* the existing v2 notebooks (which
already have Families A+B), producing unified v3 notebooks. This avoids
duplicating infrastructure and matches the always-intended design of a single
multi-family benchmark.

---

## What already exists (from Phases A + B)

| Artifact | Status | Location |
|----------|--------|----------|
| Family C items (55 clean) | Done | `kaggle-dataset-v3/family_c_items.json` |
| Extended registry (187 entries) | Done | `kaggle-dataset-v3/adjudication_registry.json` |
| Updated manifest | Done | `kaggle-dataset-v3/clean_subset_manifest.json` |
| `self_correction_v2.py` (scoring) | Done | `kaggle-package-v3/metajudge/scoring/` |
| `self_correction_v2.py` (tasks) | Done | `kaggle-package-v3/metajudge/tasks/` |
| `notebook_helpers.py` (v3 roots, `load_family_c_items()`) | Done | `kaggle-package-v3/metajudge/` |
| Prompt templates + `parse_answer_confidence()` | Done | `kaggle-package-v3/metajudge/tasks/self_correction_v2.py` |

## What the existing v2 narrative notebook looks like

18 cells, ~750 lines:

| Cell | Type | Content | Lines |
|------|------|---------|-------|
| 0 | md | Title + audit notes | ~40 |
| 1 | code | Imports, path resolution, package imports | ~60 |
| 2 | code | Load data (A+B), registry, manifest, clean filters | ~36 |
| 3 | code | Response schemas (Cal, Abstention), model config, helpers | ~52 |
| 4 | md | "## Calibration Sweep (Family A)" header | 3 |
| 5 | code | Calibration 5-model sweep (`@kbench.task`) | ~89 |
| 6 | code | Family B 5-model sweep (`@kbench.task`) | ~121 |
| 7 | code | Export A+B CSV audit files | ~50 |
| 8 | md | "## Results" header | 5 |
| 9 | code | Calibration leaderboard + reliability diagram (Fig 1) | ~55 |
| 10 | md | Interpretation + Family B header | 5 |
| 11 | code | Family B leaderboard + action distribution (Fig 2) | ~53 |
| 12 | md | Composite MetaScore formula (60/40) | 7 |
| 13 | code | Compute composite MetaScore | ~28 |
| 14 | md | Statistical analysis header | 5 |
| 15 | code | Pairwise bootstrap CIs + forest plot (Fig 3) | ~60 |
| 16 | code | Mechanism heatmap (Fig 4) + bridge analysis | ~49 |
| 17 | md | Findings + limitations + next steps | ~27 |

---

## Composite weighting — placeholder for now

`compute_composite_score()` already accepts arbitrary subscores and
renormalizes by the weight of keys present. The DEFAULT_WEIGHTS in
`composite_score.py` already include:

```python
DEFAULT_WEIGHTS = {
    "calibration": 0.30,
    "abstention_verification": 0.20,
    "intrinsic_self_correction": 0.10,
    "evidence_assisted_correction": 0.15,
    "grounding_sensitivity": 0.10,      # V2 — absent, auto-excluded
    "control_policy_adaptation": 0.15,  # V2 — absent, auto-excluded
}
```

With Families A+B+C present and D+E absent, the function will renormalize
over the four available keys (0.30 + 0.20 + 0.10 + 0.15 = 0.75), giving
effective weights of:

| Family | Raw | Effective |
|--------|-----|-----------|
| Calibration (A) | 0.30 | 40.0% |
| Abstention (B) | 0.20 | 26.7% |
| Intrinsic SC (C1) | 0.10 | 13.3% |
| Evidence SC (C2) | 0.15 | 20.0% |

This is a reasonable placeholder: monitoring-heavy (67% monitoring vs 33%
control), Family C split favors evidence-assisted (as designed). No code
change needed — just pass the right keys to `compute_composite_score()`.

Weight optimization is a separate later task.

---

## Revised Phase C: Narrative notebook — 5 sub-phases

### Overview

Instead of creating a new notebook, we copy `metajudge_narrative_v2.ipynb` →
`metajudge_narrative_v3.ipynb` and make **additive edits only**: keep all A+B
cells, add Family C cells after them.

Each sub-phase is independently committable. If an agent times out on one
sub-phase, the prior sub-phases are preserved.

---

### Phase C0 — Scaffold + setup edits (~10 min)

**Actions:**
1. `cp notebooks/metajudge_narrative_v2.ipynb notebooks/metajudge_narrative_v3.ipynb`
2. Edit **cell 0** (markdown): Update title to "v3 — Families A+B+C", add
   Family C row to the axis table, update version to v0.7.0.
3. Edit **cell 1** (imports): Add v3 path fallbacks, add Family C imports:
   ```python
   from metajudge.tasks.self_correction_v2 import (
       T1_SUFFIX, C1_T2_PRIMARY, C1_T2_FALLBACK, C2_T2_TEMPLATE,
       C1_PRIMARY_MIN_LENGTH, parse_answer_confidence,
       compute_edit_similarity, score_family_c_item,
   )
   from metajudge.scoring.self_correction_v2 import classify_transition
   ```
4. Edit **cell 2** (data loading): Add Family C loading after A+B:
   ```python
   # Family C items (55)
   fc_path = os.path.join(DATA_ROOT, "family_c_items.json")
   if os.path.exists(fc_path):
       with open(fc_path) as f:
           fc_items = json.load(f)
       fc_excluded = set(manifest.get("family_c", {}).get("excluded_items", []))
       fc_clean = [it for it in fc_items if it["item_id"] not in fc_excluded]
       fc_answer_key = {it["item_id"]: it for it in fc_items}
       print(f"Family C:    {len(fc_items)} total -> {len(fc_clean)} clean")
   else:
       fc_items, fc_clean, fc_answer_key = [], [], {}
       print("Family C:    not found (v2 dataset)")
   ```

**Commit:** "Phase C0: scaffold v3 narrative notebook with Family C data loading"

**Why this is safe:** No new cells, no sweep logic, no analysis. Just plumbing.

---

### Phase C1 — Family C sweep cell (~20 min)

**Actions:**
1. Insert a **new markdown cell** after cell 6 (Family B sweep):
   "## Self-Correction Sweep (Family C)"
2. Insert a **new code cell** — the Family C sweep. This is the core logic:

   ```python
   # Cell — Family C Self-Correction 5-Model Sweep

   fc_results = defaultdict(dict)

   @kbench.task(name="_nar_fc_item", store_task=False)
   def _nar_fc_item(llm, item_id, question, gold_answer, subfamily,
                    evidence_snippet, normative_t2_action) -> dict:
       with chats.new():
           # Turn 1
           t1_resp = llm.prompt(question + T1_SUFFIX)
           t1_text = str(t1_resp)
           t1_answer, t1_conf = parse_answer_confidence(t1_text)

           # Turn 2
           if subfamily == "C1":
               t2_prompt = (C1_T2_PRIMARY if len(t1_text) > C1_PRIMARY_MIN_LENGTH
                            else C1_T2_FALLBACK)
           else:
               t2_prompt = C2_T2_TEMPLATE.format(
                   evidence=evidence_snippet or "")
           t2_resp = llm.prompt(t2_prompt)
           t2_text = str(t2_resp)
           t2_answer, t2_conf = parse_answer_confidence(t2_text)

       # Grade
       t1_correct = grade_item(item_id, t1_answer, REGISTRY).get("correct", False)
       t2_correct = grade_item(item_id, t2_answer, REGISTRY).get("correct", False)
       transition = classify_transition(t1_correct, t2_correct,
                                        revised=(t1_answer.strip().lower()
                                                 != t2_answer.strip().lower()))
       edit_sim = compute_edit_similarity(t1_text, t2_text)

       return {
           "item_id": item_id, "subfamily": subfamily,
           "t1_correct": t1_correct, "t2_correct": t2_correct,
           "t1_confidence": t1_conf, "t2_confidence": t2_conf,
           "transition": transition,
           "t1_t2_similarity": round(edit_sim, 4),
           "t1_answer": t1_answer[:200], "t2_answer": t2_answer[:200],
           "normative_t2_action": normative_t2_action,
       }

   # Build evaluation DataFrame
   fc_eval_df = pd.DataFrame([{
       "item_id": it["item_id"],
       "question": it["question"],
       "gold_answer": it["gold_answer"],
       "subfamily": it["subfamily"],
       "evidence_snippet": it.get("evidence_snippet", ""),
       "normative_t2_action": it.get("normative_t2_action", ""),
   } for it in fc_clean])

   # Run sweep
   for mn, model_obj in verified.items():
       print(f"\n{'='*50}\n  FAMILY C: {short_name(mn)}\n{'='*50}")
       with kbench.client.enable_cache():
           runs = _nar_fc_item.evaluate(
               llm=[model_obj], evaluation_data=fc_eval_df,
               n_jobs=4, remove_run_files=True,
           )
       for r in runs:
           if r.result is not None:
               fc_results[mn][r.result["item_id"]] = r.result
       n_t1 = sum(v["t1_correct"] for v in fc_results[mn].values())
       n_t2 = sum(v["t2_correct"] for v in fc_results[mn].values())
       print(f"  T1: {n_t1}/{len(fc_clean)}, T2: {n_t2}/{len(fc_clean)}")
   ```

**Commit:** "Phase C1: add Family C sweep cell to v3 narrative notebook"

**Why this is bounded:** One cell, ~70 lines. All helpers already exist in
the package. The agent only needs to insert this cell at the right position
in the ipynb JSON.

---

### Phase C2 — Export + composite update (~15 min)

**Actions:**
1. Edit the **existing export cell** (was cell 7, now shifted) to add Family C
   CSV export after A+B exports:
   ```python
   # Family C audit CSV
   fc_rows = []
   for mn, items in fc_results.items():
       for iid, v in items.items():
           gold = fc_answer_key.get(iid, {})
           fc_rows.append({
               "model_name": mn, "item_id": iid,
               "subfamily": v["subfamily"],
               "question": gold.get("question", ""),
               "gold_answer": gold.get("gold_answer", ""),
               "t1_answer": v["t1_answer"],
               "t2_answer": v["t2_answer"],
               "t1_correct": v["t1_correct"],
               "t2_correct": v["t2_correct"],
               "t1_confidence": v["t1_confidence"],
               "t2_confidence": v["t2_confidence"],
               "transition": v["transition"],
               "t1_t2_similarity": v["t1_t2_similarity"],
           })
   if fc_rows:
       fc_csv_path = os.path.join(OUTPUT_DIR, "family_c_item_audit.csv")
       with open(fc_csv_path, "w", newline="") as f:
           w = csv.DictWriter(f, fieldnames=list(fc_rows[0].keys()))
           w.writeheader()
           w.writerows(fc_rows)
       print(f"Exported: {fc_csv_path} ({len(fc_rows)} rows)")
   ```

2. Edit the **composite MetaScore cell** (was cell 13) to include Family C:
   ```python
   # Compute C1/C2 mean scaled scores per model
   for mn in model_order:
       fc_items_mn = fc_results.get(mn, {})
       if fc_items_mn:
           c1_scores = [score_family_c_item(
               item_id=v["item_id"], subfamily=v["subfamily"],
               stratum=fc_answer_key[v["item_id"]].get("stratum", ""),
               normative_t2_action=v["normative_t2_action"],
               t1_answer=v["t1_answer"], t1_confidence=v["t1_confidence"],
               t1_correct=v["t1_correct"],
               t2_answer=v["t2_answer"], t2_confidence=v["t2_confidence"],
               t2_correct=v["t2_correct"],
           )["scaled_score"] for v in fc_items_mn.values()
               if v["subfamily"] == "C1"]
           c2_scores = [score_family_c_item(
               ...same pattern...
           )["scaled_score"] for v in fc_items_mn.values()
               if v["subfamily"] == "C2"]
           subscores["intrinsic_self_correction"] = float(np.mean(c1_scores)) if c1_scores else float("nan")
           subscores["evidence_assisted_correction"] = float(np.mean(c2_scores)) if c2_scores else float("nan")
       meta = compute_composite_score(subscores)  # auto-renormalizes
   ```

3. Update the **composite markdown cell** (was cell 12) to show the 4-family
   formula.

**Commit:** "Phase C2: add Family C export + update composite MetaScore to A+B+C"

---

### Phase C3 — Family C analysis cells (~20 min)

**Actions:**
Insert new cells after the existing Family B analysis (after what was cell 11).

1. **New markdown cell:** "### Family C Leaderboard (Self-Correction)"

2. **New code cell — Family C leaderboard + transition summary (~50 lines):**
   - Per-model table: T1 Acc, T2 Acc, T2-T1 Delta, W→R count, R→W count,
     SC Rate, Damage Rate
   - Transition matrix per model (printed)

3. **New code cell — Family C figures (~60 lines):**
   - **Figure 5:** T2-T1 accuracy delta bar chart (one bar per model, with
     bootstrap CI error bars)
   - **Figure 6:** Stratum × Model heatmap (T2 accuracy by stratum,
     analogous to Fig 4's mechanism heatmap)

**Commit:** "Phase C3: add Family C analysis cells (leaderboard, transition matrix, figures)"

---

### Phase C4 — Update statistical analysis + conclusions (~10 min)

**Actions:**
1. Edit the **pairwise bootstrap cell** (was cell 15) to add Family C
   pairwise comparisons (T2-T1 delta CIs between models).

2. Edit the **conclusions cell** (was cell 17) to add Family C findings:
   - Which model is the strongest self-corrector
   - Edit-distance → revision strategy insight
   - Confidence uniformly high finding
   - Updated limitations (FC sample size, multi-turn SDK constraint)
   - Remove "Next Steps" bullet about Family C being unimplemented

**Commit:** "Phase C4: update statistical analysis and conclusions for A+B+C"

---

## Revised Phase D: Benchmark notebook — 3 sub-phases

Same principle: copy v2 → v3, additive edits.

### Phase D0 — Scaffold
1. `cp notebooks/metajudge_benchmark_v2.ipynb notebooks/metajudge_benchmark_v3.ipynb`
2. Update cell 0 markdown (title, version, 3-family table)
3. Update cell 1 imports (add v3 paths, FC imports)
4. Update cell 4 data loading (add FC items)

### Phase D1 — Family C task cell
1. Insert new code cell after cell 6 (Family B task) with the Family C
   `@kbench.task` definition (same logic as narrative sweep cell but
   simpler — single model, no loop)

### Phase D2 — Composite + audit
1. Update cell 7 (composite task) to include Family C scores
2. Update cell 9 (audit export) to include Family C CSV
3. Update cell 10 (scoring methodology) markdown
4. Update `%choose` selector name if needed

---

## Summary: 9 sub-phases, each independently committable

| Phase | Notebook | What | Est. lines changed | Risk |
|-------|----------|------|-------------------|------|
| C0 | Narrative | Scaffold + setup | ~30 | Low |
| C1 | Narrative | FC sweep cell | ~70 (1 new cell) | Medium |
| C2 | Narrative | Export + composite | ~60 | Low |
| C3 | Narrative | FC analysis cells | ~110 (2-3 new cells) | Medium |
| C4 | Narrative | Stats + conclusions | ~30 | Low |
| D0 | Benchmark | Scaffold + setup | ~25 | Low |
| D1 | Benchmark | FC task cell | ~60 (1 new cell) | Medium |
| D2 | Benchmark | Composite + audit | ~40 | Low |

Total: ~425 lines of changes across 9 commits. No single sub-phase exceeds
~110 lines.

---

## Key differences from Plan 23

| Plan 23 | This plan |
|---------|-----------|
| Separate FC-only notebooks | Add FC into existing v2 notebooks → v3 |
| Create from scratch | Copy v2 → v3, additive edits |
| Monolithic Phase C | 5 sub-phases (C0-C4) |
| Monolithic Phase D | 3 sub-phases (D0-D2) |
| Separate composite formula | Use existing `compute_composite_score()` with auto-renormalization |
| Weight optimization inline | Defer weight optimization to separate task |
| Phase E (zip) unchanged | Phase E (zip) unchanged |
