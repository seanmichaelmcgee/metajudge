# MetaJudge v4.1 — Build Prompt

## Overview

Build MetaJudge v4.1: a 4-task Kaggle Benchmark evaluating LLM metacognition across three families. Each family is its own task notebook returning an **anchor-normalized float**. The platform averages the 4 task scores into the leaderboard MetaScore — no composite notebook needed.

**Repo:** `github.com/seanmichaelmcgee/metajudge` (private)
**Branch from:** `main`
**Reference notebooks:**
- `metaj-bench0551-v2-try2.ipynb` — working v2 benchmark (Families A+B only), use as task pattern template
- `metajudge_benchmark_v3_2.ipynb` on `claude/benchmark-v32-build` — v3.2 prototype with Family C
**Kaggle datasets:** `metajudge-data-v3`, `metajudge-package-v3`

---

## Architecture

4 task notebooks. Each independently evaluates one model via `kbench.llm`. Each returns one `float` — the anchor-normalized family score. The Kaggle benchmark UI groups them; the platform averages the 4 floats into the leaderboard ranking.

| # | Notebook | Task name | Family | Items | Returns |
|---|----------|-----------|--------|-------|---------|
| 1 | `metajudge_calibration.ipynb` | `metajudge_calibration` | A | 105 | `float` (normalized 1-Brier) |
| 2 | `metajudge_abstention.ipynb` | `metajudge_abstention` | B | 72 | `float` (normalized UWAA) |
| 3 | `metajudge_sc_c1.ipynb` | `metajudge_sc_c1` | C1 | 28 | `float` (normalized C1 delta) |
| 4 | `metajudge_sc_c2.ipynb` | `metajudge_sc_c2` | C2 | 23 | `float` (normalized C2 delta) |

**Why this works:** The platform computes a simple average of per-task float scores for the leaderboard aggregate. If each task returns its anchor-normalized score, the platform average IS the equal-weight MetaScore:

```
Platform MetaScore = (norm_A + norm_B + norm_C1 + norm_C2) / 4
```

This is mathematically equivalent to an equal-weight composite of anchor-normalized family scores, which is justified by Dawes (1979) and Davis-Stober (2011).

**Important:** Each notebook runs independently per model. There is no shared filesystem between notebooks. Each notebook must load its own data, run its own evaluation, and return its own score.

---

## Common Cells (identical in all 4 notebooks)

### Cell 1 — Imports & Path Setup

Copy from `metajudge_benchmark_v3_2.ipynb` Cell 1. Includes:
- Path resolution for Kaggle dataset inputs (with fallback chain)
- `import kaggle_benchmarks as kbench`
- `from kaggle_benchmarks import chats, assertions`
- `from metajudge.scoring.grading_v2 import grade_item, load_registry`
- `from metajudge.scoring.abstention_metrics import score_family_b_item_v2, compute_uwaa`
- Family C imports (only needed in C1/C2 notebooks, but harmless to include everywhere):
  `T1_SUFFIX`, `C1_T2_PRIMARY`, `C1_T2_FALLBACK`, `C2_T2_TEMPLATE`,
  `C1_PRIMARY_MIN_LENGTH`, `parse_answer_confidence`, `compute_edit_similarity`,
  `resolve_t2_answer`, `classify_transition`
- `OUTPUT_DIR` definition:
  ```python
  OUTPUT_DIR = "/kaggle/working" if os.path.exists("/kaggle/working") else "outputs"
  os.makedirs(OUTPUT_DIR, exist_ok=True)
  ```

### Cell 2 — Scoring Formulas & Anchor Normalization

```python
import numpy as np

def brier_item_score(is_correct: bool, confidence: float) -> float:
    y = 1.0 if is_correct else 0.0
    return 1.0 - (confidence - y) ** 2

# --- Anchor-Based Normalization ---
# Each family score rescaled to [0, 1] using fixed theoretical anchors.
# Equal weighting justified by Dawes (1979) and Davis-Stober (2011).
# Anchor normalization follows BIG-Bench (Srivastava et al. 2023).

ANCHOR_A_FLOOR = 0.75   # 1-Brier at 50% confidence (verified: see below)
ANCHOR_A_CEIL  = 1.00   # Perfect calibration
ANCHOR_B_FLOOR = 0.60   # Empirical: random uniform actions → UWAA ≈ 0.60
ANCHOR_B_CEIL  = 1.00   # Perfect abstention
ANCHOR_C1_FLOOR = ???   # SEE §ANCHOR INVESTIGATION — agent must determine
ANCHOR_C1_CEIL  = ???   # SEE §ANCHOR INVESTIGATION — agent must determine
ANCHOR_C2_FLOOR = ???   # SEE §ANCHOR INVESTIGATION — agent must determine
ANCHOR_C2_CEIL  = ???   # SEE §ANCHOR INVESTIGATION — agent must determine

def normalize(score, floor, ceil):
    return max(0.0, min(1.0, (score - floor) / (ceil - floor)))
```

### Cell 3 — Response Schemas

Copy from v3.2 Cell 3. `CalibrationResponse` and `AbstentionResponse` dataclasses. Only needed in notebooks 1 and 2, but harmless to include everywhere.

### Cell 4 — Load Datasets & Registry

Copy from v3.2 Cell 4. Loads all items, applies clean subset manifest exclusions, loads REGISTRY. Each notebook loads everything even if it only uses one family.

---

## Notebook 1: `metajudge_calibration.ipynb`

### Cell 5 — Per-Item Task (helper)

```python
@kbench.task(name="_cal_item", store_task=False)
def _cal_item(llm, item_id, question, gold_answer) -> dict:
    # [copy from v3.2 Cell 5 metacog_calibration body]
    ...
    return {"item_id": ..., "brier_score": ..., "is_correct": ..., ...}
```

### Cell 6 — Main Task

```python
@kbench.task(name="metajudge_calibration")
def metajudge_calibration(llm) -> float:
    cal_eval = cal_df[["item_id", "question", "gold_answer"]].copy()

    cal_runs = _cal_item.evaluate(
        llm=[llm], evaluation_data=cal_eval,
        n_jobs=8, remove_run_files=True,
        stop_condition=lambda runs: len(runs) == len(cal_eval),
        max_attempts=1,
    )

    records = [r.result for r in cal_runs if r.result is not None]
    CAL_AUDIT = pd.DataFrame(records)

    raw_score = float(CAL_AUDIT["brier_score"].mean())
    normalized = normalize(raw_score, ANCHOR_A_FLOOR, ANCHOR_A_CEIL)

    # Display
    acc = CAL_AUDIT["is_correct"].mean()
    print(f"Calibration: 1-Brier={raw_score:.4f} Acc={acc:.1%} Normalized={normalized:.3f} [{len(CAL_AUDIT)} items]")

    # Export CSV audit
    CAL_AUDIT.to_csv(os.path.join(OUTPUT_DIR, "calibration_item_audit.csv"), index=False)

    # Export JSON full responses
    import json
    with open(os.path.join(OUTPUT_DIR, "calibration_full_responses.json"), "w") as f:
        json.dump(records, f, indent=2, default=str)

    return normalized
```

### Cell 7 — Run + %choose

```python
metajudge_calibration.run(kbench.llm)
%choose metajudge_calibration
```

### Cell 8 — Methodology Markdown

Brief markdown explaining: what calibration measures, the Brier scoring rule, the anchor normalization, item count, and reference to Nelson & Narens monitoring construct.

---

## Notebook 2: `metajudge_abstention.ipynb`

Same pattern as Notebook 1. Key differences:
- Helper task: `_abs_item` with `store_task=False`
- Main task: `metajudge_abstention` returns `normalize(uwaa, ANCHOR_B_FLOOR, ANCHOR_B_CEIL)`
- Uses `score_family_b_item_v2()` for utility scoring (handles corrective answers, acceptable alternatives)
- Exports: `family_b_item_audit.csv` + `family_b_full_responses.json`

Copy the abstention task logic from v3.2 Cell 6 / v2 Cell 6.

---

## Notebook 3: `metajudge_sc_c1.ipynb`

### Cell 5 — Per-Item Task (helper)

```python
@kbench.task(name="_sc_item", store_task=False)
def _sc_item(llm, item_id, question, gold_answer, subfamily,
             evidence_snippet, normative_t2_action) -> dict:
    # [copy from v3.2 Cell 7 metacog_self_correction body]
    ...
```

### Cell 6 — Main Task

```python
@kbench.task(name="metajudge_sc_c1")
def metajudge_sc_c1(llm) -> float:
    c1_df = fc_df[fc_df["subfamily"] == "C1"][
        ["item_id", "question", "gold_answer", "subfamily",
         "evidence_snippet", "normative_t2_action"]
    ].copy().fillna("")

    # Run 1 (scored)
    runs_1 = _sc_item.evaluate(
        llm=[llm], evaluation_data=c1_df,
        n_jobs=4, remove_run_files=True,
        stop_condition=lambda runs: len(runs) == len(c1_df),
        max_attempts=1,
    )
    records_1 = [r.result for r in runs_1 if r.result is not None]

    # Run 2 (stochasticity check — display only, not scored)
    runs_2 = _sc_item.evaluate(
        llm=[llm], evaluation_data=c1_df,
        n_jobs=4, remove_run_files=True,
        stop_condition=lambda runs: len(runs) == len(c1_df),
        max_attempts=1,
    )
    records_2 = [r.result for r in runs_2 if r.result is not None]

    # Compute score from Run 1
    audit = pd.DataFrame(records_1)
    t1c = audit["t1_correct"].sum()
    t2c = audit["t2_correct"].sum()
    delta = float((t2c - t1c) / len(audit))
    normalized = normalize(delta, ANCHOR_C1_FLOOR, ANCHOR_C1_CEIL)

    # Stochasticity comparison (display only)
    audit_2 = pd.DataFrame(records_2)
    t1c_2 = audit_2["t1_correct"].sum()
    t2c_2 = audit_2["t2_correct"].sum()
    delta_2 = float((t2c_2 - t1c_2) / len(audit_2))
    trans_diffs = sum(1 for r1, r2 in zip(
        sorted(records_1, key=lambda r: r["item_id"]),
        sorted(records_2, key=lambda r: r["item_id"]))
        if r1["transition"] != r2["transition"])

    print(f"C1: Δ={delta:+.4f} Norm={normalized:.3f} [{len(audit)} items]")
    print(f"  Stochasticity: Run 1 Δ={delta:+.4f}, Run 2 Δ={delta_2:+.4f}")
    print(f"  Transition stability: {len(audit)-trans_diffs}/{len(audit)} items stable")

    # Export CSV + JSON
    audit.to_csv(os.path.join(OUTPUT_DIR, "family_c1_item_audit.csv"), index=False)
    import json
    with open(os.path.join(OUTPUT_DIR, "family_c1_full_responses.json"), "w") as f:
        json.dump({"run_1": records_1, "run_2": records_2}, f, indent=2, default=str)

    return normalized
```

### Cell 7 — Run + %choose

```python
metajudge_sc_c1.run(kbench.llm)
%choose metajudge_sc_c1
```

---

## Notebook 4: `metajudge_sc_c2.ipynb`

Identical structure to Notebook 3. Key differences:
- Filter: `fc_df["subfamily"] == "C2"` (23 items)
- Task name: `metajudge_sc_c2`
- Uses `ANCHOR_C2_FLOOR` and `ANCHOR_C2_CEIL`
- Exports: `family_c2_item_audit.csv` + `family_c2_full_responses.json`

---

## CRITICAL: Grading Fix — v41_crt_009

**Item:** `v41_crt_009`
**Problem:** Model answers "The same amount", gold is "They are equal". Semantically equivalent but grader marks wrong.
**Impact:** Costs 1 accuracy point AND produces Brier = 0.0 (worst possible) at confidence 1.0. Confirmed in Flash 2.5 benchmark run.

**Fix:** Add accepted forms to `adjudication_registry.json`:

```json
{
  "item_id": "v41_crt_009",
  "accepted_forms": ["they are equal", "the same amount", "equal", "the same"]
}
```

**Rebuild** the `metajudge-data-v3` Kaggle dataset after this fix.

---

## CRITICAL: Investigate Family C Anchor Values

### The Problem

The current C anchors are `[-1.0, +1.0]` — the full theoretical range. No model has ever scored outside approximately `[-0.08, +0.04]`. This means ALL models' C scores normalize to a narrow band around 0.49–0.51, **destroying Family C's discriminative contribution to the composite.**

With current anchors [-1.0, +1.0]:
- Flash C1 delta: 0.000 → normalized: 0.500
- Sonnet C1 delta: +0.036 → normalized: 0.518
- **Difference: 0.018** (invisible on leaderboard)

With tighter anchors [-0.15, +0.15]:
- Flash: 0.000 → normalized: 0.500
- Sonnet: +0.036 → normalized: 0.620
- **Difference: 0.120** (6.7× more discriminating)

**Since the platform averages the 4 task scores, the C anchors directly control how much weight self-correction gets in the final leaderboard ranking.** Getting this wrong means Family C contributes nothing despite being the benchmark's most distinctive measurement.

### What to Investigate

The agent must determine empirically grounded anchor values for C1 and C2 separately. The anchors must:

1. **Cover any plausible model performance** — no model should clip at 0.0 or 1.0
2. **Maximize discrimination** — the normalized range should span a meaningful portion of [0, 1]
3. **Be defensible without reference to the current model panel** — based on theoretical or literature-grounded bounds, not fitted to our 5 models

### Data to Examine

| Source | Location | What it contains |
|--------|----------|-----------------|
| Triplicate (5 models × 3 runs) | `family_c_all_runs.csv` | Per-model-item-run correctness + transitions |
| Triplicate results memo | `docs/stats/family_c_triplicate_results.md` | Summary stats, per-run deltas, ICC |
| Stability run (3 models × 3 runs) | `family_c_stability.csv` | Pre-grading-fix but useful for range |
| v0.7.0 run (5 models × 55 items) | results in repo | First full run, widest observed range |
| Benchmark Flash run | `calibration_item_audit.csv` etc. in Kaggle outputs | v3.2 benchmark results |
| Literature review | `docs/family_c_literature_report.md` | Self-correction rates from published research |

### Observed Ranges Across All Runs

From all available data (v0.7.0 through triplicate):

**C1 (intrinsic review, 28 items):**
- Best single run: +0.036 (Sonnet, multiple runs)
- Worst single run: −0.107 (Pro, v0.7.0)
- Typical range: −0.07 to +0.04

**C2 (evidence-assisted, 23 items):**
- Best single run: 0.000 (Sonnet triplicate)
- Worst single run: −0.087 (Flash, v0.7.1 complete run)
- Typical range: −0.09 to 0.00
- C2 hurts almost everyone — 4/5 models go negative on C2 consistently

### Recommended Investigation Steps

1. Collect all per-model per-run C1 and C2 deltas from the data files listed above
2. Compute the observed min, max, mean, and SD across all models and runs
3. Set floor = observed_min − 2×SD (covers future worse models with margin)
4. Set ceiling = observed_max + 2×SD (covers future better models with margin)
5. Verify no current model clips at 0.0 or 1.0 with the proposed anchors
6. Compute the normalized spread (max_norm − min_norm) and confirm it exceeds 0.10
7. Document the reasoning and the exact values chosen

### Fallback

If the investigation is inconclusive, use these conservative values that are tighter than [-1, +1] but still have headroom:
- C1: `[-0.20, +0.10]` (range 0.30)
- C2: `[-0.15, +0.05]` (range 0.20)

These are based on the observation that C1 deltas cluster in [-0.11, +0.04] and C2 deltas cluster in [-0.09, 0.00]. But the agent should derive better values from the data.

---

## Family B UWAA Gap Investigation

Both Flash and Sonnet showed ~0.028 lower UWAA in the benchmark notebook vs the narrative notebook. This is systematic, not stochastic — same magnitude, same direction, two different models.

**Investigate:**
1. Compare the abstention prompt text between the narrative notebook (`metajudge_narrative_v3.ipynb` Cell 6) and the benchmark notebook (v3.2 Cell 6). Any wording differences?
2. Check if the `AbstentionResponse` schema parsing handles the `decision` field identically in both paths
3. Check if the `fb_df` column selection differs (extra columns passed as kwargs could cause issues — we saw this with the `family` column error on Family C)
4. Compare action distributions: are models choosing different actions in the benchmark vs narrative?

The fix may be as simple as aligning the prompt text. Document any differences found.

---

## Exports Per Notebook

Each notebook produces:

| File | Format | Content |
|------|--------|---------|
| `{family}_item_audit.csv` | CSV | Per-item scores, grading, answers (truncated to 200 chars) |
| `{family}_full_responses.json` | JSON | Full untruncated model responses for deep audit |

The C1 and C2 JSON files additionally contain both stochasticity runs:
```json
{
  "run_1": [...],
  "run_2": [...]
}
```

---

## Known Bugs to Fix

1. **`import numpy as np as _np_fc`** — syntax error in v3.2 Cell 7. Remove entirely; numpy is imported in Cell 2.

2. **`.fillna("")`** — required on Family C DataFrames after column selection. `evidence_snippet` is NaN for C1 items. Without this, the task function receives NaN and may fail or produce incorrect results.

3. **`OUTPUT_DIR` must be defined before any cell that uses it.** In v3.2 it was used in Cell 10 but defined in Cell 11. Define it in Cell 1.

---

## Methodology Markdown (per notebook)

Each notebook should end with a brief methodology markdown cell. Templates:

**Calibration:**
> Axis I — Confidence Calibration (Monitoring). Per-item: score = 1 − (confidence − outcome)². 
> Strictly proper scoring rule (Brier 1950). 105 clean items. Correctness graded by deterministic 
> 8-rule engine with tolerance-aware numeric, alias, tri-label, code-output, and fraction grading. 
> No LLM judge. Normalized to [0, 1] using anchor floor 0.75 (random baseline) and ceiling 1.0.

**Abstention:**
> Axis II — Selective Abstention (Monitoring). Per-item utility from 5×4 payoff matrix mapping 
> (model action × gold action) → [−1, +1]. UWAA = (mean utility + 1) / 2. 72 clean items. 
> Normalized to [0, 1] using anchor floor 0.60 (empirical random baseline) and ceiling 1.0.

**C1:**
> Axis III — Intrinsic Self-Correction (Control). Two-turn protocol: T1 answer → third-person 
> review prompt → T2 revision. T2-T1 accuracy delta measures net correction. 28 clean C1 items. 
> Dual-run stochasticity check displayed in output. Normalized using empirically grounded anchors.

**C2:**
> Axis IV — Evidence-Assisted Self-Correction (Control). Two-turn protocol: T1 answer → reviewer 
> note with evidence snippet → T2 revision. 23 clean C2 items. Tests whether external evidence 
> improves or damages performance. Dual-run stochasticity check displayed in output.

---

## Scoring Rationale (for reference — not a notebook cell)

The platform averages the 4 normalized task scores. This equals:

```
MetaScore = (norm_A + norm_B + norm_C1 + norm_C2) / 4
```

Equal weighting is provably optimal at small n (Davis-Stober 2011; Dawes 1979). Anchor normalization follows BIG-Bench (Srivastava et al. 2023) and Open LLM Leaderboard v2 (Beeching et al. 2024).

The two-axis decomposition from Nelson & Narens (1990) maps as:
- **Monitoring** = (norm_A + norm_B) / 2
- **Control** = (norm_C1 + norm_C2) / 2

This is visible in the per-task leaderboard scores: judges can compare a model's monitoring tasks (A, B) against its control tasks (C1, C2) directly.

---

## Verification Checklist Before Submission

- [ ] Each notebook runs end-to-end on Flash 2.5 without errors
- [ ] Each returns a float in [0, 1]
- [ ] CSV audit files have correct column names and no truncation artifacts
- [ ] JSON full response files contain untruncated text
- [ ] C1 and C2 stochasticity tables display in notebook output
- [ ] v41_crt_009 grading fix is in the registry and dataset
- [ ] C anchor values are documented with derivation
- [ ] Family B prompt text matches narrative notebook (or gap is documented)
- [ ] `.fillna("")` is applied on all FC DataFrames
- [ ] `OUTPUT_DIR` is defined in Cell 1
- [ ] `%choose` in final cell matches the task name
- [ ] Each notebook has a methodology markdown cell
