# Decision Log

Chronological record of orchestrator decisions. Each entry explains what was
decided, why, and what alternatives were considered.

---

## 2026-03-20 06:20 — Session 1: VPS Bootstrap

### Decision 1: Patch notebook, do not regenerate

**Context:** The bootstrap report (prior session) identified that the submission
notebook embeds stale V2 data (100 cal_* items) but the V4 pipeline produced
102 gen_* survivors. The notebook's scoring pipeline, SDK integration, and
`%choose` cell are all structurally sound.

**Decision:** Patch Cells 0, 3, 5, 8, 9 of the existing notebook. Do not regenerate.

**Rationale:**
- SOUL.md §5: "Do not redesign from scratch. The wrapper-task architecture is verified and works."
- Only Cell 3 (data) needs full replacement; other cells need minor fixes
- Regeneration introduces regression risk in verified SDK integration
- The notebook has been tested in live Kaggle environment — that verification is valuable

**Alternatives considered:**
- Full notebook regeneration — rejected (violates SOUL.md §5, unnecessary risk)
- External data loading (Kaggle input) — rejected for V1 (102 items is small, embed is portable)

---

### Decision 2: Use combined_discrimination_matrix.json as batch 1 full-text source

**Context:** combined_survivors.json truncates 13/19 batch 1 questions at exactly
120 characters. phase2_final_results.json is also truncated. The CDM has full text
for all 102 items.

**Decision:** Reconstruct the canonical frozen benchmark by:
1. Starting with combined_survivors.json as structural base
2. Replacing all 19 batch 1 question fields from CDM
3. Exporting as data/metajudge_benchmark_v1.json

**Rationale:**
- CDM is the only file with verified full text for batch 1 survivors
- Batches 2-4 in survivors are byte-for-byte identical to source files
- This is the minimum-churn path to a clean canonical dataset

---

### Decision 3: Work on feature branch, PR for human review

**Context:** User explicitly requested feature branch + PR workflow.

**Decision:** All work goes to `orchestrator/vps-bootstrap` branch. PR opened
when ready. User reviews and merges manually.

**Rationale:** Preserves human oversight. No direct commits to main.

---

### Decision 4: Agent architecture — Opus for strategy, Sonnet for execution

**Context:** Need to balance quality and cost across agent roles.

**Decision:** Use Opus for Executive Analyst and Quality Auditor (strategic reasoning).
Use Sonnet for all execution agents (document generation, code, git, data).

**Rationale:** Opus reasoning capability is needed for compliance checks and
strategic decisions. Execution tasks are well-defined and don't need it.

## D-005: Fix adjudicate() gold_answer check + yes_no handler (2026-03-20)

**Context:** Claude Code Auditor CI report on PR #5 identified that notebook Cell 4 `adjudicate()` diverges from the library's `metajudge/scoring/adjudication.py`. The library's `_grade_alias_match()` checks `spec["gold_answer"]` before iterating aliases; the notebook only iterated aliases.

**Impact analysis:**
- 24/102 items have empty `aliases[]` (19 batch-1, 5 batch-2) — always return False
- 21 items use `rule="yes_no"` with no handler in the notebook — fall through to False for non-literal matches
- Old function: 27/102 (26.5%) would incorrectly return False with correct answers
- Bug was latent in V2 (V2 items always included gold_answer in aliases list)

**Decision:** Patch Cell 4 to match library grading hierarchy:
1. `_grade_alias_match()`: gold_answer first, then aliases
2. Numeric equivalence (rule == "numeric")
3. `_grade_yes_no()`: yes/no form normalization (rule == "yes_no")

Also: add V4 validation to `run_checks.py` (6 FAIL-level + 2 WARN-level checks) so CI validates the canonical dataset.

**Verification:** 102/102 self-adjudication pass, 240/240 alias variations pass, all 21 yes_no items handle variants.

**Commit:** aeca6da
**Alternative rejected:** Populating empty aliases arrays — would require manual review of 24 items and wouldn't fix the yes_no handler gap.
