# Context Summary — Dataset Expansion Sprint (20 → 100 Items)

**Date:** 2026-03-18  
**Prior commit:** `cf99ad3` — Dataset sprint: 20-item pilot set + submission notebook + harvest pipeline  
**Competition deadline:** April 16, 2026  
**Goal:** Expand the calibration dataset from 20-item pilot to 100 production-quality items

---

## 1. What Exists Now

### 1.1 Committed pilot set (`data/calibration.csv`)
20 items, manually curated, with this difficulty distribution:

| Difficulty   | Count | Examples |
|-------------|-------|---------|
| easy        | 4     | Basic arithmetic (addition, multiplication, percentage, division) |
| medium      | 7     | Chemistry symbols, geography, anatomy, history, primes |
| hard        | 5     | Square root, periodic table, heart valves, multiplication, history |
| deceptive   | 3     | Antarctic desert, polar bear skin, bat-and-ball CRT |
| adversarial | 1     | US presidents assassinated |

### 1.2 Answer key (`data/calibration_answer_key.json`)
Each item has: `canonical_answer`, `accepted_aliases`, `answer_type`, `grader_rule`, `notes`.
Grader rules: `numeric_equivalence` (14 items), `alias_match` (6 items).

### 1.3 Provenance (`data/calibration_provenance.csv`)
Every item tracks: `source`, `item_family`, `difficulty`, `gold_answer`, `answer_type`, `aliases`, `note`.

### 1.4 Candidate pool (`data/harvest/unified_candidate_pool.json`)
**270 candidates** available for expansion:

| Source | Count |
|--------|-------|
| SimpleQA | 120 |
| TruthfulQA (rewritten) | 60 |
| Authored | 90 |

Distribution by difficulty:
- easy: 15
- medium: 111
- hard: 74
- deceptive: 60
- adversarial: 10

Distribution by item family:
- factual_recall: 40, arithmetic: 60, misconception: 51, geography: 20, numeric_estimation: 20, numeric: 20, history: 15, science: 15, language: 10, adversarial: 10, semantic_illusion: 6, cognitive_reflection: 3

### 1.5 Submission notebook (`notebooks/metajudge_submission.ipynb`)
8 cells. Uses `@dataclass` schema (verified working in Kaggle). Embeds dataset + answer key inline. Uses `chats.new()` for isolation. Batch eval with `evaluate()` + caching.

### 1.6 Codebase
- `metajudge/scoring/calibration_metrics.py` — Brier score, ECE, `calibration_aware_score`
- `metajudge/scoring/adjudication.py` — Deterministic grading (alias + numeric + yes/no)
- `metajudge/tasks/calibration.py` — Prompt builder + scoring pipeline
- `tests/unit/test_scoring.py` — 59 tests, all passing

---

## 2. Target Distribution for 100 Items

Per `dataset_construction_plan.md` §6, the recommended target:

| Difficulty   | Target | Currently Have | Need |
|-------------|--------|---------------|------|
| easy        | 15     | 4             | 11   |
| medium      | 35     | 7             | 28   |
| hard        | 25     | 5             | 20   |
| deceptive   | 15     | 3             | 12   |
| adversarial | 10     | 1             | 9    |
| **Total**   | **100**| **20**        | **80** |

### Domain coverage target (item families)
The pilot heavily skews toward arithmetic (8/20 items). Expansion should rebalance toward:
- arithmetic: ~15–20 (reduce share)
- factual_recall: ~20–25 (increase — leverage SimpleQA)
- science: ~10–15
- history/geography: ~10–15
- misconception: ~10–12 (leverage TruthfulQA)
- numeric_estimation: ~5–8
- adversarial: ~8–10
- cognitive_reflection: ~3–5
- language/semantic: ~3–5

---

## 3. Expansion Workflow

### 3.1 Candidate selection from pool
1. **Review** the 270 candidates in `unified_candidate_pool.json`
2. **Filter** for exact-match safety (already done by canonicalize.py, but human review needed)
3. **Select** 80 items to fill the target distribution above
4. **Verify** each gold answer is unambiguous and aliases are comprehensive
5. **Check** for duplicates / near-duplicates with pilot items

### 3.2 Quality gates per item (from `dataset_construction_plan.md` §8)
Each item must pass:
- [ ] Gold answer is 1–5 tokens
- [ ] Prompt explicitly requests bare answer format
- [ ] No punctuation dependence
- [ ] Numeric answers are digits
- [ ] Alias ledger covers plausible alternate renderings
- [ ] Item cannot be answered differently depending on date or context
- [ ] Deceptive items have documented common wrong answer and rationale
- [ ] Adversarial items have documented failure mode

### 3.3 Files to update
- `data/calibration.csv` — add 80 new rows (cal_021 through cal_100)
- `data/calibration_answer_key.json` — add specs for all new items
- `data/calibration_provenance.csv` — add provenance for all new items
- `notebooks/metajudge_submission.ipynb` — update embedded dataset + answer key

### 3.4 Multi-agent coordination plan
Suggested parallel subagent strategy:
1. **Selection agent**: Review pool, select 80 candidates, assign IDs
2. **Alias agent**: Build alias ledger for all selected items
3. **QA agent**: Verify gold answers, check for ambiguity, flag problems
4. **Integration agent**: Build final CSV, JSON, and provenance files
5. **Notebook agent**: Update submission notebook with expanded dataset

---

## 4. Key Constraints & Decisions

### Non-negotiable (from scoring_plan.md + dataset_construction_plan.md)
- Exact string matching only (no LLM judge in scoring loop)
- One canonical `gold_answer` per item in submission CSV
- Internal alias ledger for QC (not exposed to models)
- Headline metric: `mean(1 - (c - y)^2)` (strictly proper)
- No time-sensitive or current-events items
- No items requiring open-ended interpretation

### Competition rubric alignment
- **50%** Dataset quality & task construction
- **20%** Writeup (≤1,500 words)
- **15%** Discriminatory power across models
- **15%** Community votes

### What "done" looks like
- 100-item `calibration.csv` with balanced difficulty/domain distribution
- Complete answer key with aliases for all items
- Complete provenance CSV
- Updated submission notebook (embedded dataset, smoke-tested)
- All 59+ tests passing
- Git committed and pushed

---

## 5. Repository Structure Reference

```
metajudge-agi/
├── SOUL.md                         # Project north star
├── planning/
│   ├── v1_architecture.md          # Technical architecture
│   ├── scoring_plan.md             # Scoring methodology
│   ├── dataset_construction_plan.md # Dataset strategy
│   ├── expansion_sprint_context.md  # THIS FILE
│   └── archive/                    # Superseded docs
├── metajudge/
│   ├── scoring/
│   │   ├── calibration_metrics.py  # Brier, ECE, per-item score
│   │   ├── adjudication.py         # Deterministic grading
│   │   └── composite_score.py      # Multi-axis composite
│   ├── tasks/
│   │   └── calibration.py          # Task prompts + scoring
│   ├── schemas/
│   │   └── response_schemas.py     # Pydantic response schemas
│   └── utils/
│       └── text.py                 # normalize_text()
├── data/
│   ├── calibration.csv             # Submission dataset (20 items)
│   ├── calibration_answer_key.json # Alias ledger + grader rules
│   ├── calibration_provenance.csv  # Provenance tracking
│   └── harvest/                    # Candidate pool + extraction scripts
│       ├── unified_candidate_pool.json  # 270 candidates
│       ├── simpleqa_candidates.json     # 120 from SimpleQA
│       ├── truthfulqa_candidates.json   # 60 from TruthfulQA
│       ├── authored_candidates.json     # 90 authored
│       ├── filter_simpleqa.py
│       ├── build_candidates.py
│       └── canonicalize.py
├── notebooks/
│   ├── metajudge_submission.ipynb  # Kaggle submission notebook
│   └── metajudge_evidence.ipynb    # SDK verification notebook
├── tests/
│   └── unit/
│       ├── test_scoring.py         # 59 tests (scoring + adjudication)
│       └── test_schemas.py         # Schema validation tests
└── config/
    └── benchmark_config.yaml       # Configuration
```

---

## 6. Git History (key commits)

| Commit | Description |
|--------|-------------|
| `cf99ad3` | Dataset sprint: 20-item pilot + submission notebook + harvest pipeline |
| `942a884` | Scoring overhaul + adjudication layer + governance doc update |
| `be7e136` | Created scoring_guide.md documenting calibration_aware_score defect |
| `daa78ae` | Added dataset_wishlist.md with technical requirements |

---

## 7. Open Questions for Expansion Sprint

1. **SimpleQA items need prompt rewriting** — many say "answer in as few words as possible" instead of our standard "Answer with [format] only." Need systematic rewrite pass.
2. **TruthfulQA items need validation** — the rewritten items haven't been tested against actual models to verify they genuinely induce overconfidence.
3. **Adversarial coverage is thin** — only 10 candidates in pool. May need to author more.
4. **Should we run a model sweep on the pilot first?** Running the 20-item pilot on 2–3 models would validate discriminatory power before scaling to 100.
5. **Expansion notebook update complexity** — the embedded dataset in the notebook means every expansion requires rebuilding the notebook. Consider a file-reading approach for development, embedding for final submission.
