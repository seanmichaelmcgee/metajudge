# MetaJudge Audit Framework

## Overview

MetaJudge uses a two-layer audit approach to ensure grading accuracy before
submission. The automated layer catches mechanical errors (grading engine bugs,
registry gaps, normalization math). The LLM layer catches semantic errors
(correct answers graded wrong due to phrasing, format, or alias gaps).

Both layers are required for submission readiness.

---

## Layer 1: Automated Re-Grading Audit

**Script:** `scripts/audit_benchmark_v32.py`

Runs the production grading engine (`grading_v2.py`) against every item in a
results directory and compares recorded grades to re-computed grades.

### What it catches

| Check | Description |
|-------|-------------|
| Correctness flips | Recorded correct but re-grades wrong (or vice versa) |
| Composite math | Anchor normalization produces values in [0,1], MetaScore = mean(norm_A, norm_B, norm_C) |
| File completeness | All 3 family CSVs + composite + summary present |
| Verbose T2 answers | Family C T2 answers >60 chars (potential parse failures) |
| Confirmation resolution | T2 answers processed through `resolve_t2_answer()` before grading |

### What it cannot catch

- Grading engine bugs that are **consistent** between run and audit (same engine, same result)
- Semantically correct answers that the engine doesn't recognize (alias gaps, phrasing)
- Gold answer errors (if the gold is wrong, both run and audit agree on "correct")

### Usage

```bash
python scripts/audit_benchmark_v32.py /path/to/results-dir/

# Audit all models:
for d in /path/to/results-*/; do
    python scripts/audit_benchmark_v32.py "$d"
done
```

### Output

- Console: structured audit report
- `<results_dir>/audit_report.md`: markdown report with per-family breakdown

---

## Layer 2: LLM Semantic Audit

**Prompt:** `docs/benchmark/llm_grading_audit_prompt.md`
**Extraction script:** `scripts/extract_wrong_for_llm_audit.py`

A long-context LLM reviews every item marked wrong and evaluates whether the
model's answer is semantically correct despite failing the automated grader.

### What it catches

| Check | Description |
|-------|-------------|
| Alias gaps | "The amounts are the same" for gold "They are equal" |
| Phrasing variants | "4% decrease" for gold "-4%" |
| Format issues | LaTeX, exponential notation, verbose wrappers |
| Gold answer errors | Model is more correct than the gold |
| Grading rule mismatches | Item uses wrong rule type |

### Workflow

```bash
# 1. Extract wrong-graded items to CSV
python scripts/extract_wrong_for_llm_audit.py /path/to/results-*/  > /tmp/audit_data.csv

# 2. Paste output into the DATA sections of docs/benchmark/llm_grading_audit_prompt.md

# 3. Submit to a long-context LLM (Claude Opus, Gemini Pro, etc.)

# 4. Review flagged items → fix registry/aliases → re-run automated audit
```

### Scope

With the v3.2 benchmark (4 models × 228 items):
- ~117 items marked wrong across all models
- Expected 5-15 items flagged as grading errors
- Items flagged HIGH severity require registry fixes before submission

---

## Audit History

| Date | Version | Scope | Script | Report |
|------|---------|-------|--------|--------|
| 2026-03-31 | v0.5.5.1 | Families A+B | `scripts/audit_family_ab_results.py` | `outputs/audit_family_ab_summary.md` |
| 2026-03-31 | v0.5.5.1 | A+B v1→v2 diff | `scripts/audit_v2_results_validation.py` | `outputs/audit_v2_validation_report.md` |
| 2026-04-01 | v0.7.0 | Family C | ad hoc | `outputs/audit_family_c_summary.md` |
| 2026-04-02 | v3.2 | All families (4 models) | `scripts/audit_benchmark_v32.py` | per-results-dir `audit_report.md` |

---

## Known Grading Failure Patterns (Fixed)

These patterns have been identified in prior audits and fixed in the grading
engine or registry. They are documented here for reference.

| # | Pattern | Fix | Where |
|---|---------|-----|-------|
| 1 | Verbose answer contains gold but fails alias match | Add `match_mode: "contains_any"` | Registry |
| 2 | Confirmation-without-restatement in T2 | `resolve_t2_answer()` with 19 phrase patterns | Package |
| 3 | Numeric tolerance too tight | Add `rel_tol` to registry entries | Registry |
| 4 | LaTeX notation (`\frac{}{}`, `\boxed{}`) | `_strip_latex()` in grading engine | Package |
| 5 | First-number extraction from verbose text | `_extract_final_answer_number()` | Package |
| 6 | Smart comma handling ("Nov 9, 1989") | Digit-only comma stripping | Package |
| 7 | Markdown formatting (`**bold**`) | `_strip_markdown()` in grading engine | Package |
