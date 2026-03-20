# Kaggle Upload Runbook — MetaJudge Calibration Benchmark

**Competition:** [Measuring Progress Toward AGI — Cognitive Abilities](https://www.kaggle.com/competitions/kaggle-measuring-agi)  
**Track:** Metacognition (Confidence Calibration)  
**Deadline:** April 16, 2026 at 11:59 PM UTC  
**Last updated:** 2026-03-20

---

## Quick Reference

| Step | What | Command/Location |
|------|------|-----------------|
| 1 | Pre-flight checks | `pytest tests/ -v` + item count assert |
| 2 | Upload dataset | `kaggle datasets version -p ./kaggle-dataset/ -m "..."` |
| 3 | Upload notebook | Import lean notebook into Benchmarks task editor |
| 4 | Attach dataset | "+ Add Data" → `metajudge-benchmark` in notebook sidebar |
| 5 | Run sweep | Click "Run All" → Save & Run → "Add Models" |
| 6 | Download outputs | `kaggle kernels output <kernel-slug> -p outputs/sweeps/` |
| 7 | Log + commit | `log_run()` → optional results branch tag |

---

## 1. Pre-Upload Checklist

Run these checks before every Kaggle upload. Fix anything that fails before proceeding.

### 1.1 Verify tests pass

```bash
cd /path/to/metajudge-repo
python -m pytest tests/ -v
```

Expected: all green. The critical test targets are `tests/unit/test_scoring.py` and `tests/unit/test_dataset_checks.py`.

### 1.2 Verify dataset item count

```bash
python -c "
import json
items = json.load(open('data/metajudge_benchmark_v1.json'))
assert len(items) == 102, f'Expected 102 items, got {len(items)}'
print(f'OK — {len(items)} items')
"
```

### 1.3 Verify lean notebook runs locally

```bash
cd notebooks
jupyter nbconvert --to notebook --execute metajudge_submission_lean.ipynb \
  --output metajudge_submission_lean_executed.ipynb \
  --ExecutePreprocessor.timeout=120
```

This will fail on the `kaggle_benchmarks` import (expected outside Kaggle), but it validates everything up to Cell 2. If you want a fuller local test, mock the import or use the dev notebook instead.

### 1.4 Sync lean notebook with dev notebook logic

The lean notebook (`notebooks/metajudge_submission_lean.ipynb`) must stay in sync with the dev notebook (`notebooks/metajudge_submission.ipynb`). Before uploading, diff the scoring logic manually:

- Cell 5 (task definition) in lean == core eval logic in dev notebook
- Adjudication calls match: `adjudicate()`, `brier_item_score()`
- `CalibrationResponse` schema fields are identical in both notebooks

### 1.5 Confirm outputs from last sweep are saved

```bash
ls outputs/sweeps/
# Should show timestamped sweep directories
ls outputs/run_log.jsonl 2>/dev/null && echo "run_log exists" || echo "run_log missing"
```

If `outputs/` is empty and you have prior Kaggle results, download them first (see Section 5).

---

## 2. Kaggle Dataset Upload

The dataset (`metajudge-benchmark`) provides the 102-item benchmark and config file to the notebook at `/kaggle/input/metajudge-benchmark/`.

### 2.1 Prepare the dataset directory

```bash
mkdir -p kaggle-dataset
cp data/metajudge_benchmark_v1.json kaggle-dataset/
cp config/benchmark_config.yaml kaggle-dataset/
```

Create `kaggle-dataset/dataset-metadata.json` if it doesn't exist yet:

```json
{
  "title": "MetaJudge Benchmark V1",
  "id": "<your-kaggle-username>/metajudge-benchmark",
  "licenses": [{"name": "CC0-1.0"}],
  "description": "102-item V4 calibration dataset for the MetaJudge-AGI benchmark. Used by the MetaJudge metacognition task notebook.",
  "keywords": ["metacognition", "calibration", "agi", "benchmarks"]
}
```

Replace `<your-kaggle-username>` with your Kaggle username.

### 2.2 First-time creation

```bash
kaggle datasets create -p ./kaggle-dataset/
```

After creation, the dataset will be available at:  
`https://www.kaggle.com/datasets/<your-username>/metajudge-benchmark`

### 2.3 Updating an existing dataset

```bash
kaggle datasets version -p ./kaggle-dataset/ -m "V4 dataset with 102 items"
```

Use a descriptive message — it appears in the version history and helps you identify which sweep used which dataset version.

### 2.4 Verify the upload

```bash
kaggle datasets status <your-username>/metajudge-benchmark
```

Wait for status `ready` before attaching the dataset to a notebook run. Dataset processing typically takes 1–3 minutes.

### 2.5 Expected dataset contents

| File | Description |
|------|-------------|
| `metajudge_benchmark_v1.json` | 102-item V4 dataset. Fields: `item_id`, `question`, `gold_answer`, `aliases`, `rule`, `mechanism_primary`, `batch`, `final_tier`, `final_classification` |
| `benchmark_config.yaml` | Model panels (`smoke_flash`, `core_five`), scoring weights, benchmark metadata |

---

## 3. Kaggle Notebook Upload

The submission notebook is `notebooks/metajudge_submission_lean.ipynb` (9 cells).

> **Critical:** The notebook must be created or imported through `kaggle.com/benchmarks/tasks/new`, **not** the regular Notebooks page. `kaggle_benchmarks` is only importable in Benchmarks-context notebooks.

### 3.1 Create a new Benchmarks task notebook

1. Go to [kaggle.com/benchmarks/tasks/new](https://www.kaggle.com/benchmarks/tasks/new)
2. In the notebook editor: **File → Import Notebook**
3. Upload `notebooks/metajudge_submission_lean.ipynb`
4. If import fails due to metadata mismatch, copy-paste each cell manually

### 3.2 Required notebook settings

In the notebook's Settings panel (right sidebar):

| Setting | Value |
|---------|-------|
| Language | Python 3 |
| Accelerator | None (GPU not needed) |
| Internet | **On** (required for OpenRouter / external API calls if used) |
| Environment | Default (Kaggle Benchmarks pre-installs `kaggle_benchmarks`) |

These settings are already encoded in the notebook metadata:
```json
{
  "accelerator": "none",
  "isInternetEnabled": true,
  "isGpuEnabled": false
}
```

### 3.3 Attach the dataset

1. In the notebook sidebar, click **"+ Add Data"**
2. Search for `metajudge-benchmark`
3. Select your dataset — it mounts at `/kaggle/input/metajudge-benchmark/`

The lean notebook's Cell 3 will detect this path automatically:
```python
kaggle_path = "/kaggle/input/metajudge-benchmark/metajudge_benchmark_v1.json"
local_path  = "data/metajudge_benchmark_v1.json"
data_path   = kaggle_path if os.path.exists(kaggle_path) else local_path
```

### 3.4 Upload the metajudge package

The lean notebook imports from the `metajudge/` package (Cell 1):
```python
from metajudge.scoring.adjudication import adjudicate, brier_item_score, set_answer_key
from metajudge.utils.text import normalize_text
```

You have two options:

**Option A — Upload as a utility script dataset (recommended)**

```bash
mkdir -p kaggle-metajudge-pkg
cp -r metajudge/ kaggle-metajudge-pkg/
# Create dataset-metadata.json for kaggle-metajudge-pkg/
kaggle datasets create -p ./kaggle-metajudge-pkg/
```

Attach it in the notebook sidebar. The package will be available at `/kaggle/input/metajudge-pkg/metajudge/`.

Then add this to Cell 1 before the package imports:
```python
import sys
sys.path.insert(0, "/kaggle/input/metajudge-pkg")
```

**Option B — Inline the scoring logic**

Copy `metajudge/scoring/adjudication.py` and `metajudge/utils/text.py` directly into Cell 1 as self-contained code. Simpler but harder to maintain.

### 3.5 Set the OPENROUTER_API_KEY secret (if used)

If the notebook calls OpenRouter directly (not through `kaggle_benchmarks` SDK models):

1. Go to **Account → Settings → API Keys / Secrets** on Kaggle
2. Add a secret named `OPENROUTER_API_KEY`
3. In the notebook, access it:

```python
import os
from kaggle_secrets import UserSecretsClient
secrets = UserSecretsClient()
os.environ["OPENROUTER_API_KEY"] = secrets.get_secret("OPENROUTER_API_KEY")
```

> **Note:** For standard competition runs using `kbench.llm` / `kbench.llms[...]`, no API key is needed — Kaggle provides model access automatically.

---

## 4. Running the Submission

### 4.1 Smoke test first (smoke_flash panel)

Before running the full 5-model sweep, validate with a single model:

1. In Cell 7 (Multi-Model Sweep), temporarily set:
```python
SWEEP_MODELS = ["google/gemini-2.5-flash"]  # smoke_flash panel
```
2. Click **"Run All"**
3. Verify Cell 7 completes without errors and prints per-model scores
4. Check that `%choose metacog_calibration_v1_batch` in Cell 9 executes

Expected output from a clean smoke test:
```
=== Model Availability ===
  ✓ google/gemini-2.5-flash
Dataset loaded: 102 items
Smoke test passed — proceeding to full sweep
```

### 4.2 Full 5-model sweep (core_five panel)

Restore the full model list:
```python
SWEEP_MODELS = [
    "google/gemini-2.5-flash",
    "google/gemini-2.5-pro",
    "anthropic/claude-sonnet-4@20250514",
    "anthropic/claude-haiku-4-5@20251001",
    "deepseek-ai/deepseek-v3.1",
]
```

Click **"Save Version" → "Save & Run All"**. This creates a versioned notebook run and registers the Benchmarks Task once the final cell (`%choose`) executes.

### 4.3 Add models via the Task page (official path)

After the initial run creates the Task:

1. Go to your Task page at `kaggle.com/benchmarks/tasks/<task-id>`
2. Click **"+ Add Models"** (or "Evaluate More Models")
3. Select the remaining models from the list
4. Kaggle re-runs your notebook code with each model injected as `kbench.llm`

This is the preferred submission method — each model gets its own `*.run.json` and appears on the leaderboard.

### 4.4 Expected runtime and quota

| Panel | Models | Est. runtime | Est. cost |
|-------|--------|-------------|-----------|
| `smoke_flash` | 1 | ~5 min | ~$0.05 |
| `core_five` | 5 | ~20–30 min | ~$0.25 |

> **Quota:** $50/day, $500 total. At ~$0.25 per full 5-model sweep, you have headroom for ~200 full sweeps before hitting the total cap. The quota is not a practical constraint for this benchmark size.
>
> If you somehow exceed the daily limit, email `kaggle-benchmarks-agi-hackathon@google.com`.

### 4.5 Common failure modes

| Symptom | Cause | Fix |
|---------|-------|-----|
| `ModuleNotFoundError: No module named 'kaggle_benchmarks'` | Notebook created outside Benchmarks context | Re-create at `kaggle.com/benchmarks/tasks/new` |
| `AssertionError: Expected 102, got N` | Wrong dataset version attached | Re-check dataset attachment; verify `dataset-metadata.json` ID |
| `KeyError: 'model/name'` in Cell 7 | Model not available in current Kaggle environment | Remove model from `SWEEP_MODELS` or check model name spelling |
| Cell 7 hangs >45 min | Runaway eval loop or rate limit | Click Stop; check `n_jobs` setting; re-run with `smoke_flash` panel |
| `*.run.json` not produced | `%choose` cell not reached (earlier cell errored) | Check Cell 5/6 errors; ensure task returns `float` not `None` |
| `schema` errors with a model | Model doesn't support structured output (e.g., Gemma 3) | Remove that model from panel; avoid Gemma 3 models |
| Overconfident confidence values | Prompt wording issue | Check `CalibrationResponse` schema; confidence must be 0.0–1.0 |

---

## 5. Post-Run Artifact Collection

### 5.1 Download notebook outputs

```bash
# Replace <kernel-slug> with your notebook's URL slug
kaggle kernels output <your-username>/<kernel-slug> -p outputs/sweeps/kaggle_run_YYYYMMDD/
```

Or download manually:
1. Go to your notebook's **Output** tab on Kaggle
2. Download the output files (CSV, JSON, `*.run.json`)

### 5.2 Save to local outputs/ directory

```bash
mkdir -p outputs/sweeps/kaggle_run_$(date +%Y%m%d)
# Move downloaded files into this directory
mv ~/Downloads/output.zip outputs/sweeps/kaggle_run_$(date +%Y%m%d)/
cd outputs/sweeps/kaggle_run_$(date +%Y%m%d)/ && unzip output.zip
```

`outputs/` is git-ignored (`outputs/sweeps/` in `.gitignore`). These files stay local.

### 5.3 Update run_log.jsonl

Log each model run using the `metajudge.eval.logging` module:

```python
from metajudge.eval.logging import log_run

log_run(
    run_type="kaggle",
    model_name="google/gemini-2.5-flash",
    n_items=102,
    headline_score=0.742,         # 1 - mean Brier loss
    accuracy=0.683,
    mean_confidence=0.71,
    ece=0.088,
    overconfidence_rate=0.31,
    output_dir="outputs",
    dataset_path="data/metajudge_benchmark_v1.json",
    extra={"kaggle_run_id": "<run-id>", "notebook_version": 3},
)
```

The log writes to `outputs/run_log.jsonl`. One line per model per run.

### 5.4 Check success criteria

After a sweep, verify these thresholds:

```python
import json
import pandas as pd

records = [json.loads(l) for l in open("outputs/run_log.jsonl")]
df = pd.DataFrame(records)

# Discriminatory power check: score spread across models must be > 0.10
spread = df["headline_score"].max() - df["headline_score"].min()
assert spread > 0.10, f"Low discriminatory power: spread={spread:.3f}"

# No model should score < 0.40 (floor check)
assert df["headline_score"].min() > 0.40, "Floor failure — check adjudication"

print(df[["model","headline_score","accuracy","ece"]].sort_values("headline_score", ascending=False).to_string())
```

A valid submission needs visible score differentiation across the 5 models. If all models cluster within 0.05 of each other, the benchmark lacks discriminatory power — investigate item difficulty distribution.

---

## 6. Version Control

### 6.1 What to commit to main

| Artifact | Commit to main? |
|----------|----------------|
| `notebooks/metajudge_submission_lean.ipynb` | Yes |
| `data/metajudge_benchmark_v1.json` | Yes |
| `config/benchmark_config.yaml` | Yes |
| `kaggle-dataset/dataset-metadata.json` | Yes |
| `outputs/run_log.jsonl` | Yes (it's a log, not data) |
| `outputs/sweeps/` | **No** (git-ignored) |
| `outputs/audit/` | **No** (git-ignored) |

### 6.2 Sweep results branch (optional)

For a full sweep you want to preserve:

```bash
git checkout -b results/kaggle-sweep-YYYYMMDD
git add outputs/run_log.jsonl
git commit -m "results: kaggle sweep YYYY-MM-DD — core_five panel, 102 items"
git push origin results/kaggle-sweep-YYYYMMDD
# Do NOT merge to main
```

### 6.3 Milestone submission tags

Tag the repo state at each significant Kaggle submission:

```bash
# After a successful competition submission
git tag -a v1.0-submission-YYYYMMDD -m "Competition submission: 5-model sweep, headline score X.XXX"
git push origin v1.0-submission-YYYYMMDD
```

Recommended tags:
- `v1.0-smoke` — first successful Kaggle smoke test
- `v1.0-core-five` — first successful 5-model sweep
- `v1.0-final` — final competition submission (before April 16)

### 6.4 Never commit outputs/ to main

`outputs/sweeps/` and `outputs/audit/` are git-ignored for good reason — sweep CSVs and audit JSONs can be large and are fully reproducible from `run_log.jsonl` + the dataset. Confirm before committing:

```bash
git status --short | grep outputs/
# Should show nothing (or only outputs/run_log.jsonl)
```

---

## Appendix A: Lean Notebook Cell Map

| Cell | Purpose | Key output |
|------|---------|-----------|
| 1 (markdown) | Title, track, scoring description | — |
| 2 | Imports, `kaggle_benchmarks`, `metajudge` package | `kbench.llm` |
| 3 | `CalibrationResponse` dataclass schema | `CalibrationResponse` |
| 4 | Load dataset + answer key from `/kaggle/input/metajudge-benchmark/` | `dataset` (102-row DataFrame), `ANSWER_KEY` |
| 5 | Scoring self-test assertions | Pass/fail print |
| 6 | `@kbench.task` single-item task definition | `metacog_calibration_v1` |
| 7 | `@kbench.task` batch task (full 102-item sweep) | `metacog_calibration_v1_batch` |
| 8 | Multi-model sweep loop | `sweep_results` dict |
| 9 | `%choose metacog_calibration_v1_batch` | Registers task to leaderboard |

---

## Appendix B: Kaggle API Setup

If not already configured:

```bash
pip install kaggle
# Download kaggle.json from kaggle.com → Account → API → Create New Token
mkdir -p ~/.kaggle && mv ~/Downloads/kaggle.json ~/.kaggle/
chmod 600 ~/.kaggle/kaggle.json
kaggle datasets list  # verify auth
```

---

## Appendix C: dataset-metadata.json Template

```json
{
  "title": "MetaJudge Benchmark V1",
  "id": "YOUR_USERNAME/metajudge-benchmark",
  "licenses": [{"name": "CC0-1.0"}],
  "description": "102-item V4 calibration dataset for the MetaJudge-AGI Metacognition benchmark. Each item includes a factual question, gold answer, aliases, adjudication rule, difficulty tier, and mechanism classification. Used by the MetaJudge task notebook in the Measuring Progress Toward AGI competition.",
  "keywords": ["metacognition", "calibration", "agi-benchmark", "confidence", "brier-score"],
  "resources": [
    {
      "path": "metajudge_benchmark_v1.json",
      "description": "102-item calibration benchmark (V4). Fields: item_id, question, gold_answer, aliases, rule, mechanism_primary, batch, final_tier, final_classification."
    },
    {
      "path": "benchmark_config.yaml",
      "description": "Benchmark configuration: model panels (smoke_flash, core_five), scoring weights, family definitions."
    }
  ]
}
```
