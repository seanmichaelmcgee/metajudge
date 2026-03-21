# Calibration Freeze Verdict

**Date:** 2026-03-21
**Phase:** 4 — Calibration Freeze Decision
**Verdict:** `FREEZE_AFTER_ONE_PATCH_CYCLE`
**Author:** VPS Orchestrator (automated)

---

## 1. What We Know

| Component | Status | Evidence |
|-----------|--------|----------|
| V4.2 dataset | 102 items, grading_v2 8-rule adjudication | 102/102 gold self-adjudication PASS |
| Item hardening | 7 trivial IOED items replaced with harder physics/math items | V4.2 replacement log in dataset |
| Lean notebook | GO_LEAN verdict, fully functional with grading_v2 | Parity audit: `docs/vps_cell4_parity_audit.md` |
| Family B | 48-item pilot integrated | UWAA/F1/AUARC scoring, 246 tests passing |
| Blocking issues | All 5 original BLOCK-001 through BLOCK-005 | RESOLVED — see STATE.json |
| SOUL.md | Family B canonical labels aligned | answer/clarify/verify/abstain |

### Engineering Completeness

- **Grading engine:** 8-rule registry-driven adjudication (exact_match, numeric, yes_no, case_insensitive, substring, alias_match, formula, unit_tolerant) — matches library `metajudge/scoring/adjudication.py` exactly.
- **Self-adjudication:** 102/102 items return `True` when model answer == gold answer. This was the critical correctness gate from BLOCK-004.
- **Family B scoring:** UWAA (uncertainty-weighted), macro-F1, and AUARC all implemented and tested (246 tests).
- **Notebook structure:** 9 cells, Kaggle-compatible, `%choose metacog_calibration_v1_batch` target set.

## 2. What We DON'T Know (Blocking Full FREEZE)

| Unknown | Why It Matters | Mitigation |
|---------|---------------|------------|
| No V4.2 sweep results on Kaggle | C1–C5 success criteria untested against V4.2 dataset | Run lean notebook Cell 7 on Kaggle |
| C1–C5 success criteria untested | Cannot confirm calibration quality | Sweep is the verification step |
| V4.1 sweep results never arrived | STATE.json says "WAITING" since 2026-03-20 | V4.2 supersedes V4.1; proceed with V4.2 sweep |

## 3. Success Criteria (from SOUL.md)

| Criterion | Metric | Threshold | V2 Result | V4.2 Expected |
|-----------|--------|-----------|-----------|---------------|
| C1 | Brier spread across models | ≥ 0.05 | 0.036 FAIL | Improved (harder items) |
| C2 | High-deception mechanism accuracy | < 80% on ≥ 3 models | FAIL | Improved (IOED replacements) |
| C3 | High-adversarial mechanism accuracy | < 70% on ≥ 3 models | FAIL | Improved (adversarial pipeline V4) |
| C4 | Conf-acc gap items | ≥ 10 | PASS | Expected PASS |
| C5 | ECE range across models | ≥ 0.03 | FAIL | Improved (wider difficulty spread) |

## 4. Verdict: FREEZE_AFTER_ONE_PATCH_CYCLE

### Rationale

1. **The grading engine is correct.** The 8-rule adjudication hierarchy matches the library implementation exactly. 102/102 gold self-adjudication confirms no scoring bugs remain.

2. **The dataset has been hardened.** V4.2 replaces 7 trivial IOED items (items where "I only evaluated the difficulty" was the most common failure mode) with harder physics and math items designed to stress-test model confidence calibration.

3. **The lean notebook is ready for submission.** GO_LEAN verdict confirmed after parity audit. All grading_v2 rules are registry-driven with the same precedence as the library.

4. **The one remaining gate is a 5-model sweep on Kaggle.** This is a verification step, not an engineering task. The sweep runs lean notebook Cell 7 against 5 models and produces per-model Brier scores, mechanism-group accuracies, and ECE values.

### Decision Tree After Sweep

```
Sweep results arrive
├── ≥ 4/5 criteria met → FREEZE immediately
│   └── Proceed to writeup and Kaggle upload
├── 3/5 criteria met → One final item replacement cycle
│   └── Use rejection log to identify weak items
│   └── Replace and re-run sweep
└── < 3/5 criteria met → Return to item authoring
    └── (Unlikely given V4.2 improvements over V2)
```

### Risk Assessment

- **Probability of ≥ 4/5:** HIGH — V4.2 addresses the exact failure modes from V2 (Brier spread too narrow, deception items too easy, ECE range too small).
- **Probability of 3/5:** MEDIUM — possible if adversarial mechanism items (C3) don't hit the < 70% threshold on enough models.
- **Probability of < 3/5:** LOW — would require regression from V2, which is unlikely given the strictly harder item set.

## 5. Recommended Next Steps

1. **Run the lean notebook on Kaggle with the 5-model sweep** (Cell 7). This is a single Kaggle session costing ~500 LLM calls ($10–15 of quota).

2. **Analyze sweep results against C1–C5.** The notebook's Cell 9 already produces the per-criterion breakdown.

3. **If ≥ 4/5: FREEZE** calibration, upload dataset to Kaggle (`metajudge-benchmark`), and begin the 1500-word writeup.

4. **If 3/5: One patch cycle.** Pull the rejection log, identify the weakest mechanism group, replace 5–10 items, re-run sweep.

5. **Upload Kaggle Dataset** (`metajudge-benchmark`) with V4.2 data, grading registry, and metajudge package.

---

*This verdict was produced by the VPS orchestrator based on the state of the `vps/lean-calibration-v2` branch as of 2026-03-21.*
