# Benchmark Output Extraction — Reproducibility Notes

**Date:** 2026-04-03  
**Branch:** `claude/review-repo-update-docs-P0sGa`  
**Extracted by:** Perplexity Computer (AI agent)

---

## Overview

This document describes the step-by-step process used to extract MetaJudge 6 benchmark notebook outputs from Kaggle and commit them to `outputs/benchmark_runs/`. It is intended for reproducibility if extraction needs to be repeated.

---

## Prerequisites

- Kaggle account: `seanmcgee2025`
- Kaggle legacy API key (from [kaggle.com/settings/account](https://www.kaggle.com/settings/account) → **Create New Token**)
- Python 3.x + `pip`

> **Token type matters:** Use the legacy `kaggle.json` download (produces a plain hex key). The newer scoped `KGAT_` tokens do **not** include `kernels.get` permission by default and will return `403 Permission Denied` on `kaggle kernels output`.

---

## Step 1 — Install Kaggle CLI

```bash
pip install kaggle
```

Verify:

```bash
kaggle --version
# Kaggle CLI 2.0.0
```

---

## Step 2 — Configure Credentials

Place your `kaggle.json` at `~/.kaggle/kaggle.json` and restrict permissions:

```bash
mkdir -p ~/.kaggle
cp /path/to/kaggle.json ~/.kaggle/kaggle.json
chmod 600 ~/.kaggle/kaggle.json
```

The file format should be:

```json
{"username":"seanmcgee2025","key":"<your-legacy-api-key>"}
```

Verify auth works:

```bash
kaggle kernels list -s "metajudge"
# Should return a list of your notebooks
```

---

## Step 3 — Create Output Directory Structure

```bash
mkdir -p outputs/benchmark_runs/v62/{calibration,abstention,sc_c1,sc_c2}
mkdir -p outputs/benchmark_runs/v61/{calibration,abstention,sc_c1,sc_c2}
```

---

## Step 4 — Extract Notebook Outputs

Use `kaggle kernels output <slug> -p <output_dir>` for each notebook.

> **Known slug quirk:** The `sc_c2` v6.2 notebook has a typo in its Kaggle slug — `metajudege` (extra 'e') — which does not match the intended name `metajudge`. This was discovered by inspecting the notebook's edit URL on kaggle.com.

### v6.2 Notebooks (priority — valid results)

```bash
kaggle kernels output seanmcgee2025/metajudge-calibration-v6-2      -p outputs/benchmark_runs/v62/calibration
kaggle kernels output seanmcgee2025/metajudge-abstention-v6-2        -p outputs/benchmark_runs/v62/abstention
kaggle kernels output seanmcgee2025/metajudge-self-correction-c1-v6-2 -p outputs/benchmark_runs/v62/sc_c1
kaggle kernels output seanmcgee2025/metajudege-self-correction-c2-v6-2 -p outputs/benchmark_runs/v62/sc_c2
#                                   ^^^^^^^^^ note typo — extra 'e'
```

### v6.1 Notebooks (secondary — known incomplete)

```bash
kaggle kernels output seanmcgee2025/metajudge-calibration-v6-1       -p outputs/benchmark_runs/v61/calibration
kaggle kernels output seanmcgee2025/metajudge-abstention-v61          -p outputs/benchmark_runs/v61/abstention
kaggle kernels output seanmcgee2025/metajudge-self-correction-c1-v61  -p outputs/benchmark_runs/v61/sc_c1
kaggle kernels output seanmcgee2025/metajudge-self-correction-c2-v61  -p outputs/benchmark_runs/v61/sc_c2
```

Alternatively, use the existing extraction script (after correcting the sc_c2 slug):

```bash
python scripts/extract_benchmark_outputs.py
```

---

## Step 5 — Verify Extracted Files

Each notebook directory should contain 6 files:

| File pattern | Description |
|---|---|
| `MetaJudge_*.md` | Markdown audit report |
| `*_full_responses_*.json` | Full model responses + metadata |
| `*_item_audit_*.csv` | Per-item grading results |
| `*.run.json` | SDK runtime and cost data |
| `*.task.json` | Task metadata |
| `*.log` | Kernel execution log |

---

## Extraction Results (2026-04-03)

| Notebook | Slug used | Files | Model (latest run) |
|---|---|---|---|
| v62/calibration | `metajudge-calibration-v6-2` | 6 | anthropic claude-sonnet-4@20250514 |
| v62/abstention | `metajudge-abstention-v6-2` | 6 | google gemma-4-31b |
| v62/sc_c1 | `metajudge-self-correction-c1-v6-2` | 6 | google gemma-4-31b |
| v62/sc_c2 | `metajudege-self-correction-c2-v6-2` ⚠️ | 6 | anthropic claude-sonnet-4@20250514 |
| v61/calibration | `metajudge-calibration-v6-1` | 6 | openai gpt-5.4-2026-03-05 |
| v61/abstention | `metajudge-abstention-v61` | 6 | google gemma-4-26b-a4b |
| v61/sc_c1 | `metajudge-self-correction-c1-v61` | 6 | google gemma-4-26b-a4b |
| v61/sc_c2 | `metajudge-self-correction-c2-v61` | 6 | google gemma-4-26b-a4b |

⚠️ Typo in Kaggle slug — see note in Step 4.

---

## Known Limitations

- `kaggle kernels output` only retrieves the **latest run's** outputs. Each notebook is run once per model by the benchmark platform — only the most recent model's files are accessible this way.
- Some runs may be missing if they failed due to quota exhaustion on the Kaggle side.
- The `.run.json` files can be large (~400 KB–1 MB each) due to full API call logs.

---

## Recommended Fix

Update `scripts/extract_benchmark_outputs.py` to correct the `sc_c2_v62` slug:

```python
# Current (wrong):
"sc_c2_v62": "seanmcgee2025/metajudge-self-correction-c2-v62",

# Correct:
"sc_c2_v62": "seanmcgee2025/metajudege-self-correction-c2-v62",
```

Consider also renaming the Kaggle notebook to remove the typo for future runs.
