# Repo Team Handoff — Calibration Improvement Sprint

**From:** Research team  
**To:** Repo/execution team  
**Date:** March 19, 2026  
**Inputs:** `candidate_items_brief.md`, `candidate_items.json`  
**Branch:** Create `calibration-v3-sprint` off `main` at `a50276b`

---

## Team Prompt

> You are integrating 20–22 new calibration items into the MetaJudge benchmark notebook and supporting data files. The research team has delivered 30 candidate items (`candidate_items.json`) with a strategic brief (`candidate_items_brief.md`). Your job is to pre-test these against Flash, select the strongest ~20, remove ~20 universally-correct items from the current set, update all production artifacts, fix one known schema bug, and produce a notebook ready for a full 5-model sweep.
>
> **Read these files in order before starting work:**
>
> 1. `SOUL.md` — non-negotiables, sweep protocol, iteration protocol (§Iteration protocol, §Model sweep protocol)
> 2. `candidate_items_brief.md` — tiered item list, §6 implementation checklist, §5 removal candidates, §8 risk assessment
> 3. `candidate_items.json` — the 30 items with gold answers, aliases, and rationale fields
> 4. `planning/calibration_research_brief.md` — §10 schema unification plan (the field-name bug you must fix), §11 prompt modification recommendation
> 5. `notebooks/metajudge_submission.ipynb` — Cell 3 (embedded dataset + answer key), Cell 4 (scoring functions), Cell 5 (task definition)
> 6. `data/calibration_answer_key.json` — current production answer key
>
> **Constraints (from SOUL.md):**
> - 100-item total count (maintained exactly)
> - Single-turn Brier scoring — do not change the scoring function
> - Do not change the notebook cell structure (11 cells, v3)
> - Do not change the 5-model panel
> - $50/day quota — budget Flash pre-testing at ~30 calls ($0.30–0.60 total)
>
> **Success = a notebook that passes a full 5-model audit sweep (Cell 8) and meets ≥4/5 success criteria (Cell 9).**

---

## Verification Checklist

Items marked ⚠️ are NOT covered in the brief and need explicit attention.

### Phase 1 — Pre-Testing & Selection

| # | Check | Reference | Notes |
|---|-------|-----------|-------|
| 1 | Run all 30 candidates against `google/gemini-2.5-flash` | Brief §6 pre-testing protocol | Budget: ~30 calls. Use `chats.new()` isolation per item. Record: answer, confidence, is_correct |
| 2 | Classify results into slots per brief §6 thresholds | Brief §6 | Wrong + conf ≥0.75 → deceptive/adversarial. Correct + conf <0.85 → hard. Correct + conf ≥0.95 → reject |
| 3 | ⚠️ For borderline items, run against `deepseek-ai/deepseek-v3.1` as tiebreaker | — | DeepSeek was the weakest model in the March 19 sweep. If an item fools DeepSeek but not Flash, it may still be a useful hard-bucket item |
| 4 | ⚠️ Check no candidate duplicates an existing item conceptually | — | cand_a03 (Einstein Nobel citation) is adjacent to existing cal_090 (Einstein Nobel for relativity). Both can coexist if phrased differently, but verify the adjudication paths don't collide |
| 5 | ⚠️ Count final yes/no balance | Brief §8 risk assessment | Current: 24 yes/no items. If adding >6 yes/no candidates, convert weakest to open-ended per brief §8 mitigation |
| 6 | Select final ~20 items; assign to deceptive/adversarial/hard buckets | Brief §2–4 tier tables | Target: +8 deceptive, +8 adversarial, +4 hard (replacing 4 weak hard items) |

### Phase 2 — Schema Unification (Fix Before Integration)

| # | Check | Reference | Notes |
|---|-------|-----------|-------|
| 7 | Fix field names in `metajudge/metajudge/scoring/adjudication.py` | Research brief §10 | `canonical_answer` → `gold_answer`, `accepted_aliases` → `aliases` (lines 57, 59, 68, 78 + comment block lines 28–35) |
| 8 | Fix field names in notebook Cell 4 embedded `adjudicate()` | Research brief §10 | `spec["canonical"]` → `spec["gold_answer"]`, `spec["rule"]` → `spec["grader_rule"]` |
| 9 | ⚠️ Run `grep -rn "canonical_answer\|accepted_aliases\|\"canonical\"" .` across entire repo | — | Catch any test fixtures, config files, or docs that reference the old field names |
| 10 | Run `pytest tests/ -v` after changes | Research brief §10 validation | All 90 tests should still pass. Fix any that break due to renamed fields |

### Phase 3 — Dataset Integration

| # | Check | Reference | Notes |
|---|-------|-----------|-------|
| 11 | Strip non-production fields from accepted items | Brief §6 schema conversion | Remove `pattern`, `rationale`, `confidence_trap`, `difficulty` (difficulty goes in CSV only) |
| 12 | Add new CSV rows to Cell 3 `CALIBRATION_CSV` | Notebook Cell 3 | Match exact CSV format: `example_id,prompt,gold_answer,difficulty`. Use new IDs like `cal_101`–`cal_120` (or renumber if you prefer sequential) |
| 13 | Add new answer key entries to Cell 3 `ANSWER_KEY` | Notebook Cell 3 | Must use unified field names (post-fix): `gold_answer`, `aliases`, `grader_rule` |
| 14 | Update `data/calibration_answer_key.json` | Production data | Mirror the Cell 3 ANSWER_KEY entries exactly |
| 15 | Update `data/calibration.csv` if it exists | Production data | Mirror the Cell 3 CSV entries |
| 16 | Remove ~20 items from CSV and ANSWER_KEY simultaneously | Brief §6 removal candidates | The brief lists specific IDs. Remove from BOTH Cell 3 artifacts AND external files |
| 17 | ⚠️ Update `data/provenance.csv` | — | New items need provenance rows: source=`calibration_v3_sprint`, date=`2026-03-19`, author=`research_team` |
| 18 | ⚠️ Verify final item count = exactly 100 | — | `len(dataset)` in Cell 3 output must print 100 |
| 19 | ⚠️ Verify difficulty distribution matches target | — | Easy 5 / Medium 15 / Hard 30 / Deceptive 30 / Adversarial 20. Print `dataset['difficulty'].value_counts()` |

### Phase 4 — Adjudication Edge Cases

| # | Check | Reference | Notes |
|---|-------|-----------|-------|
| 20 | ⚠️ cand_a06 (Everest boiling point): tolerance handling | — | Gold = 70, aliases include 69 and 71. Verify `numeric_equivalence` grader handles this. If it uses `float(norm) == float(canonical)`, it won't match 69 or 71. You may need to add them as explicit aliases OR switch to a `numeric_tolerance` rule with ±2°C |
| 21 | ⚠️ cand_d03 (Elcano): accent handling | — | Gold answer includes accented form `juan sebastián elcano`. Verify `normalize_text()` handles Unicode accents. Current implementation lowercases + strips, which should work, but test explicitly |
| 22 | ⚠️ cand_d06 (oxygen): verify "o" isn't an alias | — | Alias list includes "o" for oxygen. Single-letter aliases risk false positives if a model returns just the letter. Consider removing "o" and keeping only "oxygen" |
| 23 | ⚠️ cand_h03 (Hawaiian alphabet): verify gold answer is defensible | — | 13 is the most common count (including ʻokina). Some sources say 12 (excluding ʻokina). If Flash pre-test reveals confusion, consider adding 12 as an alias or dropping the item |

### Phase 5 — Prompt Modification (Optional but Recommended)

| # | Check | Reference | Notes |
|---|-------|-----------|-------|
| 24 | Apply confidence anchoring instruction to Cell 5 prompt | Research brief §11 Recommendation A | Replace `"2. Provide a confidence score from 0.0 to 1.0."` with the expanded version that anchors 0.5 = random guess and 0.9+ = staking credibility |
| 25 | ⚠️ Test modified prompt on 10-item subsample before full sweep | Research brief §11 Recommendation B | 50 calls (5 models × 10 items). If overconfident error rate doesn't drop, revert |

### Phase 6 — Notebook Smoke Tests & Sweep

| # | Check | Reference | Notes |
|---|-------|-----------|-------|
| 26 | ⚠️ Update Cell 4 self-test assertions | — | Current self-test uses `cal_001` and `cal_017`. If either is removed, the self-test will break. Update to use items that remain in the dataset |
| 27 | ⚠️ Update Cell 5 smoke test | — | `_smoke = dataset.iloc[0]` pulls the first item. After reordering, verify this still works and the expected result is sensible |
| 28 | Run Cell 6 (single-model batch) to verify notebook runs end-to-end | Notebook Cell 6 | Should complete 100 items with no errors |
| 29 | Run Cell 7 (multi-model headline sweep) | SOUL.md §Model sweep protocol | All 5 models, headline scores. Budget: 500 calls |
| 30 | Run Cell 8 (audit sweep, `RUN_AUDIT=True`) | SOUL.md §Model sweep protocol | Per-item detail for all 5 models. Budget: 500 calls |
| 31 | Run Cell 9 (diagnostics + success criteria verdict) | SOUL.md §Model sweep protocol | Target: ≥4/5 criteria met → FREEZE |

### Phase 7 — Commit & Documentation

| # | Check | Reference | Notes |
|---|-------|-----------|-------|
| 32 | ⚠️ Commit with message referencing the sprint | SOUL.md §What agents should do | Example: `calibration-v3: replace 20 items, fix schema unification, update prompt anchoring` |
| 33 | ⚠️ Export audit CSV from Cell 9 | SOUL.md §Model sweep protocol | `audit_df.to_csv('metajudge_sweep_audit.csv')` |
| 34 | ⚠️ Update SOUL.md §Project history | — | Add entry for V3 sprint with results |
| 35 | If verdict = FREEZE, run Cell 10 (`%choose`) to submit | SOUL.md §Kaggle model workflow | Then use "Evaluate More Models" on the Task Detail page for official leaderboard |

---

## Recommended Actions (Priority Order)

1. **Fix the schema unification bug first** (checks 7–10). This is a latent integration bomb. It's 30 minutes of work and prevents mysterious KeyErrors during integration. Do it before touching any data files.

2. **Run Flash pre-tests** (checks 1–6). This is the single highest-value activity — it determines which items survive. Everything else depends on this output.

3. **Integrate items and update all artifacts** (checks 11–19). The most tedious phase. Must be done carefully because Cell 3 has the embedded dataset AND answer key as Python string literals, and both must stay in sync with the external JSON/CSV files.

4. **Handle adjudication edge cases** (checks 20–23). These are small but could cause false negatives in the sweep that waste time debugging.

5. **Apply prompt modification** (checks 24–25). Optional but the research brief makes a strong case. Test on a subsample first.

6. **Run the full sweep** (checks 26–31). This is the quality gate. If the verdict is NEEDS WORK, you go back to step 2 with the rejection log.

---

## Subagent Plan

I recommend **three subagents** running in a phased pipeline. Phases 1–2 can overlap; Phase 3 depends on Phase 1 output.

### Agent 1: Schema Fixer (30 min, parallelizable)

**Scope:** Checks 7–10 from the checklist.

**Prompt:**
> Fix the schema unification bug documented in `planning/calibration_research_brief.md` §10. Three components use different field names for the same data. Standardize everything on `gold_answer` + `aliases` + `grader_rule` from `data/calibration_answer_key.json`. Specific files to change:
>
> - `metajudge/metajudge/scoring/adjudication.py` (lines 57, 59, 68, 78, comment block 28–35)
> - `notebooks/metajudge_submission.ipynb` Cell 4 embedded `adjudicate()` — change `spec["canonical"]` → `spec["gold_answer"]`, `spec["rule"]` → `spec["grader_rule"]`
> - `planning/scoring_plan.md` §4.1 — update field name table
>
> After changes: run `grep -rn "canonical_answer\|accepted_aliases\|\"canonical\"" .` to catch stragglers. Run `pytest tests/ -v` and fix any test fixtures that reference old field names. Commit with message: `fix: unify schema field names (gold_answer + aliases + grader_rule)`.

**Why a separate agent:** This is a clean, isolated code change with no data dependencies. It can run immediately while Flash pre-testing happens in parallel. Having it done before integration prevents the latent bug from surfacing mid-sprint.

### Agent 2: Flash Pre-Tester (45 min, parallelizable with Agent 1)

**Scope:** Checks 1–6 from the checklist.

**Environment:** Local Python + Google Gemini API (NOT the Kaggle SDK). See `agent2_local_pretest_setup.md` for full setup instructions, API patterns, and the complete agent prompt. The Kaggle `kaggle_benchmarks` SDK only runs inside Kaggle notebooks, and giving a bot access to your Kaggle account likely violates their TOS.

**Prompt:**
> Pre-test 30 candidate items from `candidate_items.json` against `google/gemini-2.5-flash` on the Kaggle platform. For each item:
>
> 1. Use the calibration prompt from Cell 5 of `notebooks/metajudge_submission.ipynb`
> 2. Use `chats.new()` isolation per item
> 3. Use `schema=CalibrationResponse` from Cell 2
> 4. Record: `example_id`, `model_answer`, `confidence`, `is_correct` (use `adjudicate()` from Cell 4 with the candidate's gold answer and aliases)
>
> Classify each result:
> - Wrong answer + confidence ≥ 0.75 → **ACCEPT for deceptive/adversarial** (record as `slot: deceptive` or `slot: adversarial` per the item's `difficulty` field)
> - Correct + confidence < 0.85 → **CANDIDATE for hard** (run against DeepSeek as tiebreaker)
> - Correct + confidence ≥ 0.95 → **REJECT** (ceiling item)
>
> Output a JSON summary: `{item_id: {answer, confidence, is_correct, slot, notes}}`.
>
> Also check: (a) no candidate duplicates an existing item conceptually (compare prompts against Cell 3 CSV), (b) final yes/no count doesn't exceed 30/100 (current = 24, see `candidate_items_brief.md` §8).
>
> Budget: ~30–35 LLM calls (~$0.50). If you run DeepSeek tiebreakers, add ~10 calls ($0.30).

**Why a separate agent:** Flash pre-testing is the critical path — nothing else can proceed until you know which items survive. Running this in parallel with the schema fix saves 30 minutes.

### Agent 3: Dataset Integrator (60–90 min, depends on Agent 1 + Agent 2)

**Scope:** Checks 11–31 from the checklist (everything after pre-testing and schema fix).

**Prompt:**
> Using the pre-test results from Agent 2 and the schema-fixed codebase from Agent 1, integrate ~20 new items into the MetaJudge benchmark. Follow the implementation checklist in `candidate_items_brief.md` §6 exactly.
>
> **Step 1 — Item selection.** From Agent 2's output, select items for final inclusion per these targets: +8 deceptive (from ACCEPT results where original difficulty = deceptive), +8 adversarial (ACCEPT results where difficulty = adversarial), +4 hard (from hard candidates or demoted deceptive items that Flash got right but at low confidence). Total additions = 20.
>
> **Step 2 — Item removal.** Remove 20 items from the current dataset per `candidate_items_brief.md` §6 removal candidates: 5 from easy, 11 from medium, 4 from hard (weakest — all 5 models correct at 1.00 confidence in March 19 sweep). Verify removals in BOTH Cell 3 embedded data AND external files.
>
> **Step 3 — Integration.** For each new item:
> - Assign `cal_101` through `cal_120` IDs (or renumber)
> - Add CSV row to Cell 3 `CALIBRATION_CSV`
> - Add answer key entry to Cell 3 `ANSWER_KEY` using unified field names (`gold_answer`, `aliases`, `grader_rule`)
> - Strip `pattern`, `rationale`, `confidence_trap` fields — these are documentation only
> - Mirror to `data/calibration_answer_key.json` and `data/calibration.csv`
> - Add provenance row to `data/provenance.csv`
>
> **Step 4 — Edge cases.** Handle the adjudication issues flagged in the handoff checklist:
> - cand_a06 (Everest boiling point): ensure aliases 69, 70, 71 all match via `numeric_equivalence` — if the grader uses exact float match, add all three as explicit aliases
> - cand_d03 (Elcano): test `normalize_text()` handles accented characters
> - cand_d06 (oxygen): remove single-letter alias "o" to prevent false positives
> - cand_h03 (Hawaiian alphabet): if included, verify 13 is defensible or add 12 as alias
>
> **Step 5 — Prompt update.** Apply the confidence anchoring instruction from `planning/calibration_research_brief.md` §11 Recommendation A to Cell 5's calibration prompt. Test on a 10-item subsample (5 models × 10 items = 50 calls) before committing.
>
> **Step 6 — Smoke tests.** Update Cell 4 self-test if any referenced items were removed. Update Cell 5 smoke test if `dataset.iloc[0]` changed. Verify `len(dataset) == 100` and difficulty distribution matches 5/15/30/30/20.
>
> **Step 7 — Full sweep.** Run Cell 7 (headline), then Cell 8 (`RUN_AUDIT=True`), then Cell 9 (diagnostics + verdict). If ≥4/5 criteria met → commit with audit CSV and update SOUL.md §Project history. If <4/5 → document which criteria failed and which items underperformed, then flag for a second replacement pass.
>
> **Commit message format:** `calibration-v3: N items replaced, schema unified, prompt anchored. Sweep: X/5 criteria met.`

**Why a separate agent:** This is the heaviest workload and the most error-prone (keeping 4+ files in sync). A dedicated agent with a clear sequential checklist reduces the chance of forgetting a step. It also benefits from the clean inputs produced by Agents 1 and 2.

### Pipeline Diagram

```
Time →
────────────────────────────────────────────────────────

Agent 1 (Schema Fix)     ████████░░░░░░░░░░░░░░░░░░░░
                          30 min
                                  ↘
Agent 2 (Flash Pre-Test)  ████████████████░░░░░░░░░░░░
                          45 min       ↘
                                        ↘
Agent 3 (Integration)     ░░░░░░░░░░░░░░░████████████████████████
                                         60-90 min (includes sweep)

Total wall-clock time: ~2.5 hours (if Agents 1+2 run in parallel)
Sequential fallback:    ~3 hours
```

### Quota Budget

| Activity | Calls | Est. Cost |
|----------|-------|-----------|
| Agent 2: Flash pre-test (30 items) | 30 | ~$0.50 |
| Agent 2: DeepSeek tiebreakers (~10 items) | 10 | ~$0.30 |
| Agent 3: Prompt subsample test (5 models × 10 items) | 50 | ~$2.00 |
| Agent 3: Full headline sweep (5 models × 100 items) | 500 | ~$15.00 |
| Agent 3: Audit sweep (5 models × 100 items) | 500 | ~$15.00 |
| **Total** | **~1,090** | **~$33** |

This fits within the $50/day limit with $17 of headroom for retries or a second pass.

---

## What's Already Covered in the Brief (Don't Duplicate)

These items are fully addressed in `candidate_items_brief.md` and don't need repo-team re-derivation:

- Gold answer verification sources (brief §7)
- Tier rankings and expected discrimination strength (brief §2–4)
- Items explicitly excluded and why (brief §5)
- Specific removal candidates from current dataset (brief §6)
- Target distribution math (brief §6)
- Yes/no balance risk and mitigation (brief §8)

---

## Decision Points for the Repo Team

These require human judgment — the agents should flag them rather than decide unilaterally:

1. **If fewer than 16 items pass Flash pre-test:** Do you author new items from the research brief's category list (§6 Directions 1–5), or pull from the rejection log (`data/harvest/v2_rejection_log.json`, 123 candidates)?

2. **If the audit sweep verdict is MARGINAL (3/5):** Do you commit and iterate, or do a targeted replacement of the weakest 5 new items?

3. **Prompt modification:** The confidence anchoring instruction (research brief §11) is recommended but changes the measurement conditions. If you want clean comparability with the March 19 sweep, skip it for the first V3 sweep and apply it as a separate commit afterward.

4. **Item renumbering:** The brief suggests `cal_101`–`cal_120` for new items (preserving old IDs for removed items so audit trails remain readable). Alternatively, renumber the entire set `cal_001`–`cal_100` for clean sequential ordering. The tradeoff is audit trail continuity vs. cleanliness.
