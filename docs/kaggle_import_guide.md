# MetaJudge Lean Notebook — Kaggle Import Availability Guide

## The Problem

The lean notebook (`metajudge_submission_lean.ipynb`) imports from the `metajudge` Python package. On Kaggle, this package is NOT pre-installed — you must make it available. Here's exactly how.

---

## What the Notebook Imports

### Calibration (Cells 1-8)
```python
from metajudge.scoring.adjudication import brier_item_score         # Cell 1
from metajudge.scoring.grading_v2 import grade_item, load_registry  # Cell 1
from metajudge.utils.text import normalize_text                     # Cell 1
```

### Family B (Cells 10-15)
```python
from metajudge.scoring.abstention_metrics import (                  # Cell 10
    decision_utility_single, compute_uwaa, compute_action_f1, compute_auarc
)
from metajudge.scoring.composite_score import compute_composite_score  # Cell 15
```

### Internal Dependency Chain
```
metajudge/scoring/grading_v2.py      → stdlib only (json, math, re, fractions)   ✅
metajudge/scoring/adjudication.py    → metajudge.utils.text (normalize_text, strip_wrapper)
metajudge/utils/text.py              → stdlib only (typing)                       ✅
metajudge/scoring/abstention_metrics.py → numpy                                  ✅ (pre-installed on Kaggle)
metajudge/scoring/composite_score.py    → numpy                                  ✅ (pre-installed on Kaggle)
```

**External dependencies beyond stdlib:** Only `numpy` — which is always available on Kaggle. No pip installs needed.

---

## How to Make It Available on Kaggle

### Option A: Upload as a Kaggle Dataset (Recommended)

This is the cleanest approach. Upload the `metajudge/` package directory as part of your Kaggle Dataset.

#### Step 1: Build the upload directory

```bash
# From repo root
mkdir -p kaggle-upload

# Copy the data files
cp data/metajudge_benchmark_v1.json kaggle-upload/
cp data/adjudication_registry.json kaggle-upload/
cp data/family_b_pilot_v2.json kaggle-upload/

# Copy the package (preserving directory structure)
cp -r metajudge/ kaggle-upload/metajudge/

# Verify the structure
find kaggle-upload/ -type f | sort
```

Expected structure:
```
kaggle-upload/
├── adjudication_registry.json     ← 102-entry grading registry
├── family_b_pilot_v2.json         ← 48-item Family B pilot
├── metajudge_benchmark_v1.json    ← 102-item V4.2 dataset
└── metajudge/                     ← Python package
    ├── __init__.py
    ├── scoring/
    │   ├── __init__.py
    │   ├── abstention_metrics.py
    │   ├── adjudication.py
    │   ├── calibration_metrics.py
    │   ├── composite_score.py
    │   ├── grading_v2.py
    │   └── ... (other scoring modules)
    └── utils/
        ├── __init__.py
        └── text.py
```

#### Step 2: Create dataset-metadata.json

```json
{
  "title": "MetaJudge Benchmark",
  "id": "YOUR_KAGGLE_USERNAME/metajudge-benchmark",
  "licenses": [{"name": "CC0-1.0"}],
  "description": "102-item V4.2 calibration + 48-item Family B pilot dataset with scoring package for the MetaJudge metacognition benchmark.",
  "keywords": ["metacognition", "calibration", "agi", "benchmarks"]
}
```

Save this as `kaggle-upload/dataset-metadata.json`.

#### Step 3: Upload to Kaggle

```bash
# First time:
kaggle datasets create -p ./kaggle-upload/

# Updating:
kaggle datasets version -p ./kaggle-upload/ -m "V4.2 dataset + grading_v2 + Family B pilot"
```

#### Step 4: Attach to notebook

In the Kaggle Benchmarks notebook editor:
1. Click **"+ Add Data"** in the right sidebar
2. Search for `metajudge-benchmark`
3. Select your dataset

This mounts everything at `/kaggle/input/metajudge-benchmark/`.

#### Step 5: Add sys.path to Cell 1

**This is the critical missing piece.** Cell 1 must add the Kaggle dataset path to Python's import path BEFORE any `metajudge` imports:

```python
# Cell 1 — Imports & Setup
import sys, os

# Make metajudge package importable from Kaggle dataset
kaggle_pkg = "/kaggle/input/metajudge-benchmark"
if os.path.exists(kaggle_pkg):
    sys.path.insert(0, kaggle_pkg)

import kaggle_benchmarks as kbench
from kaggle_benchmarks import assertions, chats
from dataclasses import dataclass
import json

# These now resolve from /kaggle/input/metajudge-benchmark/metajudge/
from metajudge.scoring.adjudication import brier_item_score
from metajudge.scoring.grading_v2 import grade_item, load_registry
from metajudge.utils.text import normalize_text

print(f"SDK imported: kaggle_benchmarks")
print(f"Default LLM: {kbench.llm}")
print("Environment OK")
```

---

### Option B: Utility Script (Alternative)

Kaggle also lets you attach "Utility Scripts" — another notebook whose code is importable. But this requires maintaining a separate notebook just for the package code and is harder to version. **Not recommended.**

---

## File Path Resolution on Kaggle

The lean notebook already handles dual paths (Kaggle vs local) in Cell 3:

```python
kaggle_path = "/kaggle/input/metajudge-benchmark/metajudge_benchmark_v1.json"
local_path = "data/metajudge_benchmark_v1.json"
data_path = kaggle_path if os.path.exists(kaggle_path) else local_path
```

The same pattern is used for:
- `adjudication_registry.json` (Cell 3)
- `family_b_pilot_v2.json` (Cell 10)

---

## Quick Verification Checklist

Before running on Kaggle, verify locally:

```bash
# 1. Check package structure is valid
python -c "import metajudge; print(metajudge.__version__)"

# 2. Check all notebook imports resolve
python -c "
from metajudge.scoring.adjudication import brier_item_score
from metajudge.scoring.grading_v2 import grade_item, load_registry
from metajudge.utils.text import normalize_text
from metajudge.scoring.abstention_metrics import decision_utility_single, compute_uwaa, compute_action_f1, compute_auarc
from metajudge.scoring.composite_score import compute_composite_score
print('All imports OK')
"

# 3. Check data files present
python -c "
import json
items = json.load(open('data/metajudge_benchmark_v1.json'))
registry = json.load(open('data/adjudication_registry.json'))
fb_items = json.load(open('data/family_b_pilot_v2.json'))
print(f'Dataset: {len(items)} items, Registry: {len(registry)} entries, Family B: {len(fb_items)} items')
"

# 4. Run tests
python -m pytest tests/ -v
```

---

## What Still Needs to Happen

1. **Patch Cell 1** — Add the `sys.path.insert()` block shown above
2. **Build kaggle-upload/** — Run the directory build commands
3. **Create/update the Kaggle Dataset** — Upload via `kaggle datasets create`
4. **Attach dataset to Benchmarks notebook** — "Add Data" sidebar
5. **Run smoke test** — Single model, verify all imports resolve, all 102 items score

---

## Summary: Minimum Files for Kaggle

| File | Source | Kaggle Path | Purpose |
|------|--------|-------------|---------|
| `metajudge_benchmark_v1.json` | `data/` | `/kaggle/input/metajudge-benchmark/` | 102-item V4.2 dataset |
| `adjudication_registry.json` | `data/` | `/kaggle/input/metajudge-benchmark/` | 102-entry grading registry |
| `family_b_pilot_v2.json` | `data/` | `/kaggle/input/metajudge-benchmark/` | 48-item Family B pilot |
| `metajudge/` directory | repo root | `/kaggle/input/metajudge-benchmark/metajudge/` | Scoring package (for Python imports) |
