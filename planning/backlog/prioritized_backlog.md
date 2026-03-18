# Prioritized Task Backlog — MetaJudge-AGI

## Priority Levels
- **P0 (Critical):** Blocks all downstream work
- **P1 (High):** Blocks a specific phase
- **P2 (Medium):** Important but not blocking
- **P3 (Low):** Nice to have, can defer

---

## P0 — Critical (Must Do First)

### B-001: Freeze response schemas
- **Phase:** 1
- **Agent:** Schema
- **Source:** Framework §5.1-5.5, §6.2-6.3
- **Status:** DONE (stubs created, needs review and freeze)
- **Description:** Finalize all five task-family schemas and metadata schema. After freeze, changes require Orchestrator approval.

### B-002: Write benchmark charter
- **Phase:** 1
- **Agent:** Documentation
- **Source:** Framework §2, §10.2
- **Description:** One-page document freezing operational definition of metacognition, five sub-benchmarks, scoring philosophy.

### B-003: Verify Kaggle SDK API surface
- **Phase:** 1 (start early), 6 (finalize)
- **Agent:** Integration
- **Source:** Notebook Sketch §Important verification notes
- **Description:** Confirm @kbench.task, .evaluate(), structured output, multi-turn, judge model, export mechanism.
- **BLOCKING:** Phase 6 completion

### B-004: Author initial dataset (minimum 500 items)
- **Phase:** 2
- **Agent:** Dataset
- **Source:** Implementation Plan §Phase 2
- **Description:** 100+ items per task family. All difficulty tiers. Metadata complete.

---

## P1 — High Priority

### B-005: Implement complete calibration metrics
- **Phase:** 4
- **Agent:** Scoring
- **Source:** Framework §7.2
- **Status:** DONE (stubs created, needs testing)

### B-006: Implement complete abstention utility scoring
- **Phase:** 4
- **Agent:** Scoring
- **Source:** Framework §5.2.5, §7.2
- **Status:** DONE (stubs created, needs testing)

### B-007: Implement self-correction metrics
- **Phase:** 4
- **Agent:** Scoring
- **Source:** Framework §5.3.4, §7.2
- **Status:** DONE (stubs created, needs testing)

### B-008: Implement source-awareness metrics
- **Phase:** 4
- **Agent:** Scoring
- **Source:** Framework §5.4.5, §7.2
- **Status:** DONE (stubs created, needs testing)

### B-009: Implement strategy metrics
- **Phase:** 4
- **Agent:** Scoring
- **Source:** Framework §5.5.4, §7.2
- **Status:** DONE (stubs created, needs testing)

### B-010: Implement composite score with principle verification
- **Phase:** 4
- **Agent:** Scoring
- **Source:** Framework §7.1, §7.3
- **Status:** DONE (stubs created, needs testing)

### B-011: Build @kbench.task wrappers for all five families
- **Phase:** 6
- **Agent:** Integration
- **Source:** Framework §9.2, Notebook Sketch Cells 17-23

### B-012: Implement prompt paraphrase generation
- **Phase:** 5
- **Agent:** Anti-Gaming
- **Source:** Framework §8.2.3

### B-013: Create public/private/pilot dataset splits
- **Phase:** 2
- **Agent:** Dataset
- **Source:** Framework §8.2.7, Notebook Sketch Cell 8

---

## P2 — Medium Priority

### B-014: Write task authoring guide
- **Phase:** 2
- **Agent:** Documentation
- **Source:** Notebook Sketch §Recommended follow-on files #2

### B-015: Implement judge-model rubric checks (limited scope)
- **Phase:** 3
- **Agent:** Integration
- **Source:** Framework §13
- **Description:** Only for strategy explanation matching and abstention reason quality.

### B-016: Add decoy confidence cues to dataset
- **Phase:** 5
- **Agent:** Anti-Gaming
- **Source:** Framework §8.2.4

### B-017: Implement family consistency analysis
- **Phase:** 5
- **Agent:** Anti-Gaming
- **Source:** Notebook Sketch Cell 25

### B-018: Build pilot analysis notebook
- **Phase:** 7
- **Agent:** QA / Scoring
- **Source:** Framework §14, Implementation Plan §Phase 7

### B-019: Write competition writeup
- **Phase:** 8
- **Agent:** Documentation
- **Source:** Framework §10, §11 Task 9

### B-020: Implement risk-coverage curve analysis
- **Phase:** 4
- **Agent:** Scoring
- **Source:** Framework §7.2

### B-021: Add source-label adversarial items
- **Phase:** 5
- **Agent:** Anti-Gaming
- **Source:** Framework §8.2.6

### B-022: Verify model availability in competition environment
- **Phase:** 6
- **Agent:** Integration
- **Source:** Notebook Sketch §Important verification notes #2

---

## P3 — Low Priority / Deferrable

### B-023: Implement visualization for calibration curves
- **Phase:** 7
- **Agent:** Scoring
- **Description:** Nice diagnostic tool for pilot analysis.

### B-024: Write limitations document
- **Phase:** 8
- **Agent:** Documentation
- **Source:** Framework §15

### B-025: Build CI/CD pipeline
- **Phase:** Ongoing
- **Agent:** Environment
- **Description:** Automated testing on commit. Low priority for competition timeline.

### B-026: Implement behavioral consistency check for strategy tasks
- **Phase:** 4
- **Agent:** Scoring
- **Source:** Framework §5.5.4
- **Description:** Requires judge-model or heuristic. Placeholder exists.

---

## Backlog Summary

| Priority | Count | Status |
|----------|-------|--------|
| P0       | 4     | 1 done, 3 pending |
| P1       | 9     | 6 stub-done, 3 pending |
| P2       | 9     | All pending |
| P3       | 4     | All pending |
| **Total** | **26** | |
