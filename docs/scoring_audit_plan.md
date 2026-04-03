# Scoring Audit & Data Extraction Plan

## Data landscape

**15 models** with complete v61 runs (4 tasks each = 60 scored results).
**4 models** with complete v62 runs (Flash, Sonnet 4, Haiku, Gemma-31b).
**4 models** with both v61 and v62 for version comparison.

## Phase 1: Data extraction — pull all notebook outputs

### 1a. Install and configure kagglehub
```bash
pip install kagglehub
```
Configure Kaggle credentials (`~/.kaggle/kaggle.json`).

### 1b. Build extraction script
`scripts/extract_benchmark_outputs.py` — pulls all output files for each notebook:

For each model × task × version combination that has a score:
1. Identify the notebook slug (e.g., `seanmcgee2025/metajudge-calibration-v62`)
2. Use `kagglehub.notebook_output_download()` to pull outputs
3. Organize into `outputs/benchmark_v61/{model}/` and `outputs/benchmark_v62/{model}/`

**Expected files per run:**
- `*_item_audit_*.csv` — per-item grading results
- `*_full_responses_*.json` — full model responses + metadata
- `MetaJudge_*.md` — audit report
- `*.run.json` — SDK runtime data
- `*.task.json` — task metadata

**Limitation:** kagglehub may only pull latest version. If version-specific
downloads don't work, we fall back to manual download from the Kaggle UI
for the specific `scriptVersionId`.

### 1c. Verify extraction
- Count files per model × task
- Spot-check: do CSV item counts match expected (105/72/28/23)?
- Parse JSON metadata to confirm model names and timestamps

**Commit, stop, wait**

## Phase 2: Preliminary analysis from benchmark CSV

Even before item-level data, the benchmark CSV gives us composite scores.
Build `scripts/analyze_benchmark_scores.py`:

### 2a. v61 leaderboard (15 models)
- Compute MetaScore = mean(cal, abs, c1, c2) per model
- Rank models
- Flag suspicious scores (0.0, 1.0, or scores based on partial items)

### 2b. v62 leaderboard (4 models)
- Same computation
- Compare to v61 for the 4 overlapping models

### 2c. Discrimination analysis (from composite scores)
- Score spread: what's the range of MetaScores?
- Per-task spread: which task discriminates most?
- Rank correlation between tasks (do good calibrators also abstain well?)
- Identify ceiling/floor effects (tasks where all models cluster)

### 2d. Red flags from the CSV
Looking at the v61 data, several scores look suspicious:
- `gpt-5.4`: abstention=1.0 (perfect), sc_c1=0.0, sc_c2=0.0 — possible structured output failure
- `claude-opus`: sc_c2=0.0 — possible failure
- Many models have sc_c1 ≈ 0.257 or 0.4 — possible ceiling/floor effect
- `gemini-2.5-pro`: abstention=0.248 — very low, possible structured output issue

**Commit, stop, wait**

## Phase 3: Item-level scoring audit (once outputs extracted)

### 3a. Grading accuracy audit
For each model × task:
- Re-grade all items using the local grading engine
- Compare to the CSV is_correct field
- Flag any mismatches (grading engine bug or data corruption)

### 3b. Calibration validity
- Plot 1-Brier distribution across models — is there meaningful spread?
- Check: are models with high accuracy also well-calibrated? (they should be correlated but not identical)
- Overconfidence analysis: which models say 0.95+ when wrong?

### 3c. Abstention validity
- Action distribution per model — are some models always answering? Always abstaining?
- False-presupposition handling — do models recognize false premises?
- Utility distribution — are negative utilities coming from wrong answers or wrong actions?

### 3d. Self-correction validity
- Transition distribution per model — what % maintain, what % damage?
- T1 accuracy vs T2 accuracy — does T2 ever improve on T1?
- Deceptive trap performance — do models fall for misleading evidence in C2?
- C1 vs C2 correlation — does having evidence help?

### 3e. Composite validity
- Does the MetaScore rank order make intuitive sense?
- Are there models where task scores are wildly inconsistent?
- Equal-weight sensitivity — would different weights change rankings?

**Commit, stop, wait**

## Phase 4: Discrimination analysis (item-level)

### 4a. Item discrimination
- Per item: what % of models get it right?
- Identify non-discriminating items (100% or 0% correct)
- Identify high-discrimination items (50/50 split)

### 4b. Model separation
- For each task: can we statistically separate any model pairs?
- Bootstrap CIs on per-task scores
- Friedman test across models

### 4c. Version stability (v61 vs v62)
- For the 4 overlapping models: how much do scores change?
- Are rank orderings preserved?
- Which task shows most version sensitivity?

**Commit, stop, wait**

## Dependencies

- Phase 2 can start immediately (we have the CSV)
- Phase 1 runs in parallel (kagglehub extraction)
- Phases 3-4 depend on Phase 1 (need item-level data)

## Output

All analysis scripts and results go in `outputs/scoring_audit/`.
Summary findings in `outputs/scoring_audit/audit_findings.md`.
