# Kaggle Upload & Submission Guide — MetaJudge Calibration Benchmark

**Last updated:** 2026-03-18  
**Competition:** [Measuring Progress Toward AGI — Cognitive Abilities](https://www.kaggle.com/competitions/kaggle-measuring-agi)  
**Deadline:** April 16, 2026 at 11:59 PM UTC  
**Track:** Metacognition

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Step-by-Step: Create and Run Your Task Notebook](#2-step-by-step-create-and-run-your-task-notebook)
3. [Dataset Handling: Embedding vs. Uploading](#3-dataset-handling-embedding-vs-uploading)
4. [Running on Multiple Models](#4-running-on-multiple-models)
5. [Building the Benchmark and Submitting](#5-building-the-benchmark-and-submitting)
6. [Writing the Writeup](#6-writing-the-writeup)
7. [Quotas and Cost Management](#7-quotas-and-cost-management)
8. [Common Mistakes and Troubleshooting](#8-common-mistakes-and-troubleshooting)
9. [Our Specific Workflow](#9-our-specific-workflow)

---

## 1. Architecture Overview

Kaggle Benchmarks uses a three-layer system:

```
You write a NOTEBOOK  →  it produces a TASK  →  tasks are grouped into a BENCHMARK
```

| Layer | What it is | How many |
|-------|-----------|---------|
| **Task Notebook** | A Kaggle notebook using the `kaggle_benchmarks` SDK. You write evaluation code here. | 1 notebook per task |
| **Task** | Created automatically when the notebook runs successfully and produces a `*.run.json` output file. | 1 per notebook |
| **Benchmark** | A named collection of 1+ tasks. This is what you submit. | 1 per submission |

**Critical constraint:** `kaggle_benchmarks` is ONLY importable inside notebooks created from the Benchmarks page — not in regular Kaggle notebooks.

---

## 2. Step-by-Step: Create and Run Your Task Notebook

### 2.1 Create a new Benchmarks task notebook

1. Go to [kaggle.com/benchmarks/tasks/new](https://www.kaggle.com/benchmarks/tasks/new)
   - This is the ONLY way to create a notebook where `kaggle_benchmarks` works
   - Do NOT create a regular notebook and try to import the SDK — it won't work
2. You'll get an empty notebook with the SDK pre-installed

### 2.2 Copy your code into the notebook

You have two options:

**Option A: Manual copy-paste (recommended for testing)**
- Open the test notebook (`notebooks/metajudge_pilot_sweep.ipynb`) in a text editor or Jupyter
- Copy each cell's source code into the Kaggle notebook, one cell at a time
- Run each cell sequentially

**Option B: Upload the .ipynb file**
- Go to [kaggle.com/benchmarks/tasks/new](https://www.kaggle.com/benchmarks/tasks/new)
- In the notebook editor, click `File → Import Notebook`
- Upload the `.ipynb` file
- **Caveat:** The notebook metadata must match Kaggle's expected format. If import fails, use Option A.

### 2.3 Run the notebook

- Click "Run All" or run cells sequentially
- The notebook must complete successfully and produce at least one `*.run.json` output
- This happens automatically when you call `my_task.run(...)` or `my_task.evaluate(...)`

### 2.4 Save the notebook

- Click "Save Version" → choose "Save & Run All"
- This runs the full notebook and saves outputs
- Once saved, the Task is created automatically

---

## 3. Dataset Handling: Embedding vs. Uploading

### Our approach: Embedded dataset (currently used)

The submission notebook embeds the full dataset and answer key as Python string literals directly in the code cells. This means:

- **No external dependencies** — the notebook is 100% self-contained
- **No dataset upload step** — simplest possible workflow
- **Portable** — anyone can fork and run it
- **Limitation** — gets unwieldy beyond ~100 items; not ideal for very large datasets

This is the right approach for our 20-item pilot and likely for our 100-item final set.

### Alternative: Upload as a Kaggle Dataset

If the dataset grows too large to embed, or if you want to version it separately:

#### Step 1: Create the dataset on Kaggle

1. Go to [kaggle.com/datasets](https://www.kaggle.com/datasets)
2. Click **"+ New Dataset"**
3. Fill in:
   - **Title:** e.g., "MetaJudge Calibration Dataset v1"
   - **Visibility:** Private (during development) or Public (for submission)
4. Upload files:
   - Drag and drop your CSV, JSON, and provenance files
   - Or upload a ZIP archive (Kaggle auto-extracts it)
   - Or specify a public URL to fetch from
   - Or link to a GitHub repository
5. Click "Create Dataset"

#### Step 2: Attach the dataset to your notebook

1. In your Kaggle Benchmarks notebook, click the **"+ Add Data"** button in the right sidebar
2. Search for your dataset by name
3. Select it — it will be mounted at `/kaggle/input/your-dataset-name/`
4. Access files in your code:

```python
import pandas as pd

# The path follows this pattern:
# /kaggle/input/{dataset-slug}/{filename}
dataset = pd.read_csv("/kaggle/input/metajudge-calibration-v1/calibration.csv")
```

#### Step 3: Versioning the dataset

- To update the dataset, go to its page → "New Version"
- Upload new files — this creates a version history
- Your notebook will use the latest version unless you pin a specific version

#### Important notes on Kaggle datasets:
- 200GB per dataset limit
- Max 50 top-level files (use subdirectories for more)
- A dataset can only come from ONE source type (local upload, GitHub, URL — can't mix)
- To combine multiple sources, create separate datasets and add them all to your notebook
- CSV files get automatic data type detection and previews
- ZIP archives are auto-extracted on Kaggle's side

### Alternative: Notebook output as dataset

You can also create a dataset from a notebook's output files:

1. Create a "data preparation" notebook that generates your CSV/JSON files
2. Save them to the notebook's output directory
3. On the notebook's Output tab, click "Create Dataset"
4. Attach that dataset to your benchmark notebook

This gives you a reproducible data pipeline but adds complexity.

---

## 4. Running on Multiple Models

The competition requires running on **at least 5 different models**.

### Available models (as of March 2026)

| Provider | Models |
|----------|--------|
| **Google** | gemini-2.5-flash, gemini-2.5-pro, gemini-2.5-flash-lite, gemini-2.0-flash-001, gemini-2.0-flash-lite, gemma-3-27b-it, gemma-3-12b-it, gemma-3-4b-it |
| **Anthropic** | claude-opus-4-20250514, claude-sonnet-4-20250514, claude-3-7-sonnet-20250219, claude-3-5-sonnet-20241022, claude-3-5-haiku-20241022 |
| **OpenAI** | o3-2025-04-16, o4-mini-2025-04-16, o1-2024-12-17, o1-mini-2024-09-12, gpt-4.1-2025-04-14, gpt-4o-2024-08-06, gpt-4o-mini-2024-07-18, gpt-3.5-turbo-0125 |
| **DeepSeek** | deepseek-r1, deepseek-v3 |
| **Mistral** | mistral-large-2411, mistral-small-2503, codestral-2501, pixtral-large-2411, pixtral-12b-2409, open-mixtral-8x22b-2404, ministral-8b-2410, ministral-3b-2410 |
| **xAI** | grok-2-1212, grok-2-vision-1212 |

**Limitations:**
- Gemma 3 does NOT support structured output (our `schema=CalibrationResponse` will fail)
- Gemma 3, Qwen3, GLM-5, and DeepSeek do NOT support image inputs (not relevant for us)

### Method 1: "Add Models" button (RECOMMENDED for submission)

This is the official approach:

1. Run your notebook once with the default model (creates the Task)
2. Go to your Task page on Kaggle
3. Click **"+ Add Models"** (or "Evaluate More Models")
4. Select additional models from the list
5. Kaggle runs your notebook code with each model swapped in
6. Results appear on the Task's leaderboard automatically

**Why this is preferred:**
- Each model run is a proper "Run" with its own `*.run.json`
- The leaderboard shows all model scores side-by-side
- This is what the judges evaluate for "discriminatory power"

### Method 2: In-notebook multi-model (for quick testing)

Use `kbench.llms[]` to access models programmatically:

```python
# Access a specific model
model = kbench.llms["google/gemini-2.5-pro"]

# Run your task with that model
score = my_task.run(model, dataset)

# Or compare multiple models
models = [
    kbench.llms["google/gemini-2.5-flash"],
    kbench.llms["anthropic/claude-sonnet-4-20250514"],
]
results = my_task.evaluate(llm=models, evaluation_data=df)
```

**Use this for:** quick diagnostic comparison during development.  
**Don't use this for:** the final submission (use Method 1 instead).

### Recommended 5-model sweep for our benchmark

Pick models that should show a gradient of calibration ability:

1. `google/gemini-2.5-flash` — default, should be our baseline
2. `google/gemini-2.5-pro` — stronger model, expect better calibration
3. `anthropic/claude-sonnet-4-20250514` — different provider, should be strong
4. `anthropic/claude-3-5-haiku-20241022` — smaller model, expect weaker calibration
5. `deepseek/deepseek-v3` — third provider, different architecture

Avoid Gemma 3 models — they don't support structured output.

---

## 5. Building the Benchmark and Submitting

### Step 1: Finalize your Task notebook

1. Make sure your notebook uses `%choose your_task_name` in the final cell
2. Run the notebook and save it
3. Verify the Task appears at [kaggle.com/benchmarks](https://www.kaggle.com/benchmarks)

### Step 2: Run on 5+ models

Use the "Add Models" button on the Task page (see Section 4).

### Step 3: Create the Benchmark

1. Go to [kaggle.com/benchmarks](https://www.kaggle.com/benchmarks)
2. Click "Create Benchmark"
3. Add your Task(s) to the Benchmark
4. Give it a name and description

### Step 4: Write the Writeup

1. Go to the competition's [Writeups tab](https://www.kaggle.com/competitions/kaggle-measuring-agi/writeups)
2. Create a new writeup (≤1,500 words)
3. Include: problem statement, task construction, dataset documentation, technical details, results, insights, citations
4. Attach your Benchmark via "Project Links" → "Benchmark"

### Step 5: Submit

Submit the Writeup before April 16, 2026 at 11:59 PM UTC.

---

## 6. Writing the Writeup

The writeup is worth **20%** of the total score. It must cover:

- **Problem statement:** What cognitive ability are you measuring? (Metacognition — specifically confidence calibration)
- **Task construction:** How the benchmark works, what the scoring function is, why it's valid
- **Dataset documentation:** Provenance, columns, data types, difficulty distribution, quality assurance process
- **Technical details:** Adjudication logic, Brier scoring derivation, chat isolation, prompt design
- **Results & insights:** What patterns emerged across models? Which models calibrate well?
- **Citations:** Brier (1950), Gneiting & Raftery (2007), SimpleQA, TruthfulQA

---

## 7. Quotas and Cost Management

| Limit | Value |
|-------|-------|
| Daily quota | $50/day |
| Monthly quota | $500/month |
| Overage | Email kaggle-benchmarks-agi-hackathon@google.com |

**Cost estimation for our benchmark:**
- 20 items × ~$0.0005/call ≈ $0.01 per model run
- 5 models × $0.01 = $0.05 total for the pilot
- 100 items × 5 models ≈ $0.25 total for the full set
- We are nowhere near the quota limits

**Cost management tips:**
- The test notebook uses `chats.new()` for each item, which keeps context windows small
- Use the pilot (20 items) for testing; only run the full 100 on the final version
- If you hit a rate limit, wait and retry

---

## 8. Common Mistakes and Troubleshooting

### Mistake 1: Creating a regular notebook instead of a Benchmarks notebook
**Symptom:** `ModuleNotFoundError: No module named 'kaggle_benchmarks'`  
**Fix:** Create your notebook at [kaggle.com/benchmarks/tasks/new](https://www.kaggle.com/benchmarks/tasks/new), not from the regular Notebooks page.

### Mistake 2: Not calling `.run()` in the notebook
**Symptom:** No Task created, no `*.run.json` in outputs  
**Fix:** Make sure at least one `my_task.run(...)` executes successfully.

### Mistake 3: Multiple tasks in one notebook
**Symptom:** Confusion about which task the notebook produces  
**Fix:** One notebook = one task. Create separate notebooks for separate tasks.

### Mistake 4: Using Gemma 3 with structured output
**Symptom:** Schema/structured output errors with Gemma models  
**Fix:** Gemma 3 doesn't support structured output. Use Gemini, Claude, OpenAI, or DeepSeek instead.

### Mistake 5: Fewer than 5 models
**Symptom:** Weak submission, possible disqualification  
**Fix:** Run on at least 5 models via the "Add Models" button.

### Mistake 6: Using `%choose` in a test notebook
**Symptom:** Accidentally designating a test run as the submission task  
**Fix:** Only use `%choose` in the final submission notebook, not in test/diagnostic notebooks.

### Mistake 7: Unescaped braces in f-strings
**Symptom:** `KeyError` or `ValueError` in prompt templates  
**Fix:** Use `{{` and `}}` for literal braces inside f-strings. E.g., `f"Return JSON: {{'score': <int>}}"`.

### Mistake 8: Token/context bloat across items
**Symptom:** Costs skyrocket, model gets confused by prior items  
**Fix:** Use `chats.new()` for each item to isolate conversations.

---

## 9. Our Specific Workflow

### Phase 1: Pilot sweep (current — 20 items)

1. **Copy-paste** `notebooks/metajudge_pilot_sweep.ipynb` into a new Benchmarks notebook
2. **Run** all cells — default model (gemini-2.5-flash) runs automatically
3. **Inspect** Cell 7 diagnostics: per-item results, difficulty aggregation, calibration stats
4. **Add models** via the Task page's "Add Models" button
5. **Compare** model scores for discriminatory power

### Phase 2: Fix issues found in pilot

- Items where the model answer is correct but our adjudication says wrong → fix alias ledger
- Items where all models get the same score → not discriminative, consider replacing
- Items with surprising confidence patterns → verify gold answers are unambiguous

### Phase 3: Expand to 100 items and re-sweep

1. Expand `calibration.csv` from 20 to 100 items using the candidate pool
2. Rebuild the submission notebook with the expanded dataset embedded
3. Run the full 100-item sweep on 5+ models
4. Verify discriminatory power (scores should spread across models)

### Phase 4: Final submission

1. Use `notebooks/metajudge_submission.ipynb` as the final submission notebook
2. Ensure it uses `%choose metacog_calibration_v1_batch` in the last cell
3. Run on 5+ models via "Add Models"
4. Write the 1,500-word writeup
5. Submit before April 16, 2026

---

## Appendix: Key Kaggle Benchmarks SDK Reference

```python
import kaggle_benchmarks as kbench

# Default LLM (assigned by Kaggle, usually gemini-2.5-flash)
kbench.llm

# Judge LLM (lighter model for LLM-as-judge patterns)
kbench.judge_llm

# Access specific models
model = kbench.llms["provider/model-name"]

# Define a task
@kbench.task(name="my_task")
def my_task(llm, param1, param2) -> float:
    ...

# Run once
result = my_task.run(llm=kbench.llm, param1="a", param2="b")

# Run on dataset
runs = my_task.evaluate(
    llm=[kbench.llm],          # list of models
    evaluation_data=df,         # pandas DataFrame — column names must match task params
    stop_condition=lambda r: len(r) == df.shape[0],
    max_attempts=1,
    n_jobs=3,                   # parallel workers
)
eval_df = runs.as_dataframe()

# Isolated conversation
with kbench.chats.new():
    response = llm.prompt("question", schema=MySchema)

# Structured output
response = llm.prompt("question", schema=MyDataclass)  # or Pydantic model, dict, int, bool

# Assertions
kbench.assertions.assert_true(condition, expectation="...")
kbench.assertions.assert_equal(expected, actual, expectation="...")
kbench.assertions.assert_contains_regex(pattern, text, expectation="...")

# Publish task to leaderboard (last cell)
%choose my_task_name

# Return types: bool, int, float, tuple[int,int], tuple[float,float], None
```
