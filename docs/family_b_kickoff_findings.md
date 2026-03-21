# Family B Kickoff Findings: Selective Abstention / Verification / Clarification
**Date:** 2026-03-21
**Sprint:** Family B Design + Pilot
**Branch:** `feat/family-b-selective-abstention`

---

## 1. What Family B Should Be

Family B measures whether an LLM makes the correct *next-action decision* when facing a query whose epistemic status varies: some questions have clear answers, some are ambiguous and need clarification, some require external verification, and some are genuinely unanswerable.

The four canonical actions are: **answer**, **clarify**, **verify**, **abstain**.

This is an Axis I (Epistemic Monitoring) task, weight 0.20 in the composite score. It directly complements calibration (Family A, weight 0.30) — where calibration asks "how well does the model know what it knows?", Family B asks "does the model act correctly on what it knows?"

Family B is NOT:
- A safety refusal benchmark (that's content policy, not epistemic monitoring)
- A difficulty test (hard but answerable questions should be answered, not abstained from)
- A multi-turn dialogue benchmark (single-turn action choice is the primary metric)

---

## 2. What Was Built on This Branch

### Documents
- `docs/family_b_literature_review.md` — 12-theme literature review covering abstention, selective prediction, clarification, and verification research (2024–2026)
- `docs/family_b_scoring_spec.md` — Complete scoring specification: utility matrix, UWAA, action F1, AUARC, multi-turn protocol, adjudication spec, success criteria B1–B5, anti-gaming measures
- `docs/family_b_dataset_design.md` — Dataset design memo: 48-item pilot, 16 subtypes across 4 action classes, foil item inventory, known limitations
- `docs/family_b_notebook_integration.md` — Notebook integration plan: cell placement, embedding strategy, inline scoring, compliance checklist

### Data
- `data/family_b_pilot_v2.json` — 48-item pilot dataset (revised post-probe: answer=13, clarify=9, verify=14, abstain=12)
- `data/family_b_rejection_log.json` — Items considered and rejected during authoring
- `data/family_b_probe_report.json` — Cross-model probe summary
- `data/probe_results/{deepseek,gemini,claude}_analysis.json` — Per-model probe analyses

### Code
- `metajudge/schemas/response_schemas.py` — Reconciled AbstentionResponse: `decision` now uses `Literal["answer", "clarify", "verify", "abstain"]` (was `"ask"`), added `clarification_request` and `verification_target` fields (was `missing_information`)
- `metajudge/scoring/abstention_metrics.py` — Rewritten with: 5x4 utility matrix, `compute_uwaa()`, `compute_action_f1()`, `compute_auarc()`, plus legacy helpers preserved
- `metajudge/tasks/abstention_verification.py` — Updated prompt template (4-action format), scoring uses `gold_action` from utility matrix
- `scripts/family_b_probe.py` — 3-model probe script (DeepSeek, Gemini, Claude)

### Tests
- `tests/test_family_b.py` — 34 tests: dataset validation (6), distribution (2), per-class field checks (5), scoring functions (12), schema validation (6), AUARC (2), UWAA (4)

---

## 3. What the Literature Changed

The literature review surveyed 12 research themes. Key findings that shaped the design:

### Shifted from binary to 4-action
The initial design (from SOUL.md and Recommendations memo) framed Family B as primarily "answer vs. abstain." The literature — particularly Wen et al.'s abstention taxonomy (arXiv 2407.18418), Deng et al.'s "learning to refuse" framework, and Feng et al.'s "don't hallucinate, abstain" (ACL 2024) — revealed that binary abstention is too coarse. Models need to distinguish between "I don't know" (abstain), "I need more context" (clarify), and "I should check this" (verify). This drove the 4-action ontology.

### Utility matrix over binary accuracy
Kamath et al.'s selective prediction framework and the coverage-risk tradeoff literature showed that binary accuracy (correct/incorrect action) misses important nuances. A model that always abstains gets 25% accuracy but is useless. The utility matrix encodes graduated rewards — correct answer on non-answer items gets partial credit (+0.5), cautious wrong actions get small credit (+0.3), over-abstention gets a penalty (−0.3). This was the single most important design decision.

### AUARC as a calibration check
The area-under-accuracy-rejection-curve metric from Geifman & El-Yaniv (ICML 2019) provides a threshold-free measure of confidence quality. This was added as Tier 3 to catch models that game the utility matrix by always outputting fixed confidence values.

### Foil items as anti-gaming
The adversarial evaluation literature (specifically work on shortcut learning and dataset artifacts) motivated the foil item design — items that superficially resemble one action class but belong to another. 12 of 48 pilot items are foils.

---

## 4. The Scoring and Schema Decision

### Schema reconciliation
The Recommendations memo specified `ask_clarifying_question` and the existing code used `"ask"`. We reconciled to short canonical labels: **answer, clarify, verify, abstain**. The Pydantic schema now has:
- `decision: Literal["answer", "clarify", "verify", "abstain"]`
- `clarification_request` (replaces `missing_information`) — for clarify actions
- `verification_target` (new) — for verify actions
- `abstention_reason` — for abstain actions (unchanged)

### Scoring stack
Three tiers, matching the scoring spec:

| Tier | Metric | Role | Range |
|------|--------|------|-------|
| 1 | **UWAA** (Utility-Weighted Action Accuracy) | Primary, headline | [0, 1] |
| 2 | **Per-class Action F1** | Diagnostic, bias detection | [0, 1] per class |
| 3 | **AUARC** | Confidence calibration quality | [0, 1] |

UWAA is the only metric that enters the composite score. F1 and AUARC are diagnostic.

---

## 5. The Pilot Dataset Composition

### Distribution (v2, post-probe revision)

| Action | Count | Subtypes |
|--------|-------|----------|
| answer | 13 | straightforward_factual (3), surface_similar_clarify (3), surface_similar_verify (3), foil_abstain (4) |
| clarify | 9 | missing_referent (2), missing_timeframe (1), missing_preference (3), missing_unit (3) |
| verify | 14 | time_sensitive (3), calculation (3), source_dependent (3), seemingly_static (3), reclassified_from_clarify (2) |
| abstain | 12 | false_premise (3), unknowable (3), subjective (3), incoherent (3) |
| **Total** | **48** | 16 subtypes |

### Balance rationale
The v2 distribution is not perfectly balanced (was 12/12/12/12 in v1). Post-probe revisions reclassified 3 clarify items to verify (abs_013→answer, abs_016→verify, abs_017→verify) because model probing revealed that the clarify/verify boundary was miscalibrated for time-sensitive items. This is documented in the probe report.

### Difficulty: easy=14, medium=28, hard=6

---

## 6. What the Model Probes Showed

Three models were probed on the v1 dataset (48 items, 12 per class):

| Metric | DeepSeek | Gemini Flash | Claude Haiku |
|--------|----------|--------------|-------------|
| Overall accuracy | 70.8% | 71.1%* | 66.7% |
| Macro F1 | 0.698 | 0.707 | 0.651 |
| Parse failures | 0/48 | 10/48 | 0/48 |
| Answer class accuracy | 91.7% | 100%* | 83.3% |
| Clarify class accuracy | 41.7% | 36.4%* | 33.3% |
| Verify class accuracy | 91.7% | 66.7%* | 83.3% |
| Abstain class accuracy | 58.3% | 85.7%* | 66.7% |

*Gemini figures computed on 38 valid items (10 parse failures excluded)

### Key findings

1. **Clarify is universally hard.** All three models had their worst performance on clarify items (33–42%). Models strongly prefer to answer or verify rather than ask for clarification. This is the most discriminating action class.

2. **Answer and verify are easy.** >80% accuracy across models. The foil items (abs_010–012) caught Claude but not DeepSeek.

3. **False premise items fool models.** abs_037–039 (false premise abstain items) were consistently misclassified as answer or verify. After revision, these became more clearly false-premise.

4. **Confidence is poorly calibrated.** Wrong predictions have similar confidence to correct ones (DeepSeek: 0.80 vs 0.77; Gemini: 0.99 vs 0.99; Claude: 0.79 vs 0.85). AUARC will have limited discriminative power.

5. **Gemini has a JSON compliance problem.** 10/48 parse failures due to markdown code block wrapping. The probe script's markdown stripper is not robust enough — the notebook integration must handle this.

6. **Cross-model accuracy spread:** 4.4% (66.7% to 71.1%). Estimated UWAA spread should be higher because the utility matrix amplifies action-class differences.

### Items revised post-probe (10 items)
- abs_013: clarify→answer (Mercury atomic number is unambiguous in isolation)
- abs_016: clarify→verify (population is time-sensitive, not ambiguous)
- abs_017: clarify→verify (UK PM is time-sensitive current info)
- abs_014, abs_015, abs_018, abs_022: reworded for clearer ambiguity
- abs_037, abs_038, abs_039: replaced with clearer false-premise items

---

## 7. What Should Be Merged Now

The following are ready for merge into main:

1. **All documents** — literature review, scoring spec, dataset design, notebook integration plan, this memo
2. **The pilot dataset** (`data/family_b_pilot_v2.json`) — 48 items, probed, revised
3. **The reconciled schema** — `AbstentionResponse` with canonical 4-action labels
4. **The scoring utilities** — UWAA, action F1, AUARC implementations
5. **The updated task module** — `abstention_verification.py` with new prompt format
6. **The tests** — 34 tests, all passing alongside the 212 existing tests
7. **The probe data** — analysis files and probe script

**Pre-merge checklist:**
- [x] All 246 tests pass (212 existing + 34 new)
- [x] No calibration files modified
- [x] `.env` in `.gitignore`
- [x] Existing `AbstentionResponse` consumers updated (test_schemas.py, test_scoring.py)
- [x] SOUL.md field names respected (gold_answer, aliases, rule)

---

## 8. What Should Remain Experimental

1. **Multi-turn protocol** — The scoring spec defines it (§5) but it requires a simulated user (separate LLM call). Not implemented; add after single-turn sweep validates the dataset.

2. **Dataset balance** — The 13/9/14/12 distribution is intentional post-revision but may need further rebalancing. The clarify class (9 items) is below the ideal 12. Adding 3 clarify items should be the first dataset expansion.

3. **AUARC metric** — Probe data shows poor confidence calibration across all models. AUARC may not discriminate well until stronger models are probed. Keep as diagnostic only; do not include in the composite score.

4. **Clarify/verify boundary** — Items like abs_017 (UK PM) sit at the boundary. The utility matrix gives +0.3 partial credit for adjacent non-answer actions, which mitigates this, but the boundary definition may need refinement after more model data.

5. **Probe script** — `scripts/family_b_probe.py` hardcodes workspace paths and API keys. Should be refactored to use relative paths and env vars before production use.

---

## 9. How This Integrates with the Benchmark and Notebook Path

### Benchmark integration
- Family B score (UWAA) feeds into `compute_composite_score()` with weight 0.20
- When only calibration is active: composite = calibration Brier score
- When both are active: composite = 0.60 × calibration + 0.40 × abstention (after normalization)
- The composite score module already handles this via weight normalization

### Notebook path
- 8 new cells (11–18) added after existing calibration cells
- Cell 11 embeds the 48-item dataset as JSON (r-string, matching Cell 3 pattern)
- Cell 13 duplicates scoring logic for Kaggle portability (matching Cell 4 pattern)
- Cell 14 defines `@kbench.task` per-item (matching Cell 5 pattern)
- Cell 18 computes combined composite and runs `%choose`

### Success criteria gating
Family B has its own B1–B5 criteria (analogous to C1–C5 for calibration). Both must pass (≥4/5) before the combined benchmark can be submitted. The criteria are:
- B1: UWAA spread ≥ 0.10 across model panel
- B2: Hard item resistance ≤ 80% action accuracy
- B3: Over-abstention rate spread ≥ 0.05
- B4: ≥3 action classes with F1 > 0.30 for best model
- B5: Foil items harder than non-foils by ≥0.05

---

## 10. What the Next Sprint Should Do

### Immediate (Sprint B+1)
1. **Run the full 5-model sweep** on the v2 dataset using the reconciled scoring pipeline. This validates B1–B5 criteria.
2. **Add 3 clarify items** to bring the class to 12 and improve balance.
3. **Build notebook Cells 11–18** following the integration plan.
4. **Fix Gemini parse failures** — add robust markdown-stripping to the notebook's response parser.

### Medium-term (Sprint B+2)
5. **Implement multi-turn evaluation** for clarify and verify items (simulated user protocol from scoring spec §5).
6. **Expand to 80 items** for production, maintaining the subtype taxonomy.
7. **Add clarify-quality scoring** — the scoring spec defines it (0.20 weight in clarify composite) but it needs a deterministic disambiguation checker.

### Before submission
8. **Freeze the dataset** after B1–B5 criteria are met on the expanded set.
9. **Update the writeup** — the 1500-word writeup needs a Family B section covering the utility-based scoring approach and why 4-action ontology was chosen over binary abstention.
10. **Final composite score validation** — verify that the combined calibration + abstention score discriminates meaningfully across the 5-model panel.

### Risks
- **Clarify class weakness:** If clarify items remain universally hard (~35% accuracy), the benchmark may not discriminate models on this axis. Mitigation: add easier clarify items with more obvious ambiguity.
- **Confidence calibration:** If models continue to show flat confidence distributions, AUARC adds no signal. Mitigation: keep AUARC diagnostic-only; don't weight it in the composite.
- **Budget:** The 48-item Family B sweep costs ~$0.24 per run. With multi-turn, ~$0.50. Total budget ($500) can support ~1000 sweeps — more than enough.

---

*Prepared by the integration agent. All artifacts on branch `feat/family-b-selective-abstention`.*
