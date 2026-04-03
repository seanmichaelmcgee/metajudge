# MetaJudge Benchmark Output Extraction Agent

## Your mission

Pull all notebook output files from Kaggle benchmark runs and organize them locally for scoring audit analysis. This is a data extraction task — no analysis, no code changes, just reliable file retrieval.

## Project context (minimal — just what you need)

MetaJudge-AGI is a Kaggle competition benchmark measuring metacognition in LLMs. It runs 4 task notebooks per model on the Kaggle Benchmarks platform. Each notebook produces output files (CSVs, JSONs, markdown reports) in `/kaggle/working/` that we need locally for scoring validation.

- **Competition:** https://www.kaggle.com/competitions/kaggle-measuring-agi
- **Repository:** https://github.com/seanmichaelmcgee/metajudge (branch: `claude/review-repo-update-docs-P0sGa`)
- **Benchmark:** https://www.kaggle.com/benchmarks/seanmcgee2025/metajudge-6

## Token budget

Be extremely token-lean. Short responses. No explanations unless troubleshooting. Do not read files unless necessary for debugging. Do not explore the repo beyond what's listed below.

## Key repo files for reference

- `scripts/extract_benchmark_outputs.py` — extraction script (ready to use, has notebook slug mappings)
- `outputs/benchmark_results_metajudge6.csv` — CSV of all benchmark scores (models × tasks × versions)
- `docs/scoring_audit_plan.md` — what the extracted data will be used for

## Kaggle credentials

Prompt the user for their Kaggle API key if `~/.kaggle/kaggle.json` does not exist. Set it up as:
```bash
mkdir -p ~/.kaggle
echo '{"username":"seanmcgee2025","key":"USER_PROVIDED_KEY"}' > ~/.kaggle/kaggle.json
chmod 600 ~/.kaggle/kaggle.json
```

## What to extract

For each notebook in the MetaJudge 6 benchmark, download ALL output files from `/kaggle/working/`:

**v62 notebooks (priority — these are the valid results):**
- `seanmcgee2025/metajudge-calibration-v62`
- `seanmcgee2025/metajudge-abstention-v62`
- `seanmcgee2025/metajudge-self-correction-c1-v62`
- `seanmcgee2025/metajudge-self-correction-c2-v62`

**v61 notebooks (secondary — known incomplete but useful for comparison):**
- `seanmcgee2025/metajudge-calibration-v61`
- `seanmcgee2025/metajudge-abstention-v61`
- `seanmcgee2025/metajudge-self-correction-c1-v61`
- `seanmcgee2025/metajudge-self-correction-c2-v61`

**Expected files per notebook run:**
- `*_item_audit_*.csv` — per-item grading results
- `*_full_responses_*.json` — full model responses + metadata
- `MetaJudge_*.md` — markdown audit report
- `*.run.json` — SDK runtime/cost data
- `*.task.json` — task metadata

## Where to place files

```
outputs/benchmark_runs/
  v62/
    calibration/    ← all output files from calibration v62 notebook
    abstention/     ← all output files from abstention v62 notebook
    sc_c1/          ← all output files from sc_c1 v62 notebook
    sc_c2/          ← all output files from sc_c2 v62 notebook
  v61/
    calibration/    ← all output files from calibration v61 notebook
    abstention/
    sc_c1/
    sc_c2/
```

## Method

Use the Kaggle CLI:
```bash
pip install kaggle
kaggle kernels output {notebook_slug} -p {output_dir}
```

**Known limitation:** `kaggle kernels output` may only pull the latest run's outputs. Each notebook runs multiple models via the benchmark platform — the latest run may have only one model's files. If this is the case:
1. Note which model's files were retrieved
2. Report the limitation
3. Ask the user if they want to manually download specific versions

## Troubleshooting

- **403 / proxy errors:** This environment may not have outbound Kaggle API access. If so, tell the user to run `scripts/extract_benchmark_outputs.py` locally.
- **Empty outputs:** Some runs failed (quota exhaustion). Missing files are expected for some models.
- **Emoji in filenames:** Model slugs may contain `🤖`. This is normal.

## Scope

ONLY extract files. Do not:
- Analyze the data
- Modify any code
- Read repo files beyond what's listed
- Create new scripts
- Make commits

Report what you extracted and stop.
