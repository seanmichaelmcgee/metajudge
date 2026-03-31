# Follow-Up: Two Additions to the Family C Literature Report

You produced the document "Self-correction as metacognitive control: from error-related negativity to LLM revision benchmarks." The narrative arc and theoretical grounding are strong. Two additions are needed before this document can serve as the foundation for downstream design and competition writeup work.

**Before responding, you must read the following files from the MetaJudge repository.** These contain the empirical data and formatting precedent you need. Do not work from memory or inference — the specific numbers matter.

---

## Files to read

### For Addition 1 (structured source inventory):
Read **`docs/metacognition_literature_report.md`** — specifically the section titled "Comprehensive Source Inventory Organized by Domain" (approximately lines 205–295). This contains the Family B source inventory formatted as structured tables with columns: Authors | Year | Title | Venue | Key Contribution. Your source inventory must match this format exactly.

### For Addition 2 (empirical engagement):
Read these files in order:

1. **`outputs/family_c/sweep_analysis_v062.md`** — the corrected 5-model sweep analysis. Key data:
   - Table in §2.1: per-model T1 accuracy, T2 accuracy, R→R, W→R, R→W, W→W counts, SC rates, damage rates
   - §6: model rankings and metacognitive susceptibility profiles
   - §7: discernibility analysis showing which items differentiate models

2. **`outputs/family_c/power_analysis_v062.md`** — statistical power analysis. Key data:
   - §1: Wilson 95% CIs for SC rates (CI widths of 40–70%, pairwise comparisons indefensible)
   - §2: Bootstrap CIs for T2-T1 delta (DeepSeek +8.9pp is the only significant result)
   - §3: McNemar pairwise tests (0/6 pairs significant)
   - §5: Rescaling compression analysis (3/6 transitions clamp to 1.0 under current scoring)
   - §6: Recommendations on what is defensible vs. exploratory at n=45

3. **`planning/family_c_sprint/checkpoint_status_v062.md`** — current dataset state. Key data:
   - 45 clean items in sweep, 61 total clean, 54 total including quarantine
   - WR item difficulty problem: 12/16 WR items have T1 accuracy ≥80%
   - Batch 1 frontier validation: all 3 hardening candidates quarantined (too easy for frontier models)

4. **`config/family_c_scoring.yaml`** — the implemented scoring parameters. Note the C1 damage:gain ratio is 2:1 (|-0.40|/0.20) and C2 standard is 1:1 (|-0.25|/0.25), with C2-misleading at 2:1. The rescaling range [-0.55, 0.30] causes top-clamping.

5. **`planning/family_c_sprint/state_memo_next_phase.md`** — corrected model performance table and remaining grading edge cases.

---

## Addition 1: Restructure the source inventory into structured tables

The current source inventory (Part IV) lists references in paragraph blocks by domain. Restructure into the table format used in the Family B report.

For each domain, produce a table with these columns:

| Authors | Year | Title | Venue | Key Contribution |

Group into the same 7 domains currently used (Foundational psychology, Modern cognitive science, LLM self-correction core, Sycophancy and adversarial dynamics, Decision theory and psychometrics, Existing benchmarks, Metacognition-LLM bridge papers).

Requirements:
- Every reference currently cited in the document must appear in exactly one table
- Include full venue information (journal name, volume, pages OR conference name and year)
- The "Key Contribution" column should be a single phrase capturing what the paper contributes to the Family C argument specifically (not a generic description)
- If the current document cites a paper but gives insufficient bibliographic detail, fill in the correct venue/year from your knowledge — do not leave blanks
- Also add Wang, Wu, Ye et al. (AAAI 2025) — "Decoupling metacognition from cognition" — which is currently missing from the report. This paper provides SDT-based metrics for separating metacognitive ability from cognitive ability in LLMs, and was a centrepiece of the Family B grounding. It belongs in Domain 7 (bridge papers) and should also be referenced in the Part III bridging constructs section, specifically in the "Error detection without external feedback" construct — the DMC framework addresses the confound that a model scoring well on correction might simply be a better reasoner rather than a better metacognitive corrector.

---

## Addition 2: New section — "Theoretical predictions meet empirical data"

Insert a new section between Part III (bridging constructs) and Part IV (source inventory). Title it:

**"Part III-B: What the theory predicts and what the v0.6.2 sweep shows"**

This section should take each of the five bridging constructs from Part III and evaluate them against the actual empirical findings from the sweep data. The goal is to show the literature *predicting* (or failing to predict) what the data shows. This is what transforms the document from a purely theoretical review into an empirically anchored one.

Structure it as five subsections, one per construct:

### 1. Error detection without external feedback (C1)
- **Theory predicts:** Near-zero accuracy improvement from generic review (Huang et al.); detection is the bottleneck (Tyen et al.); models with stronger internal conflict should show more correction.
- **Data shows:** [Reference the sweep analysis — which models self-corrected on C1 items specifically? What were the C1 SC rates? How does Grok's complete rigidity map to the theory?]

### 2. Evidence-calibrated revision (C2)
- **Theory predicts:** Weak evidence should produce modest updating; misleading evidence should trigger sycophantic flipping in susceptible models; C2 should outperform C1 on matched items.
- **Data shows:** [Reference the sweep analysis — C2 vs C1 item-level patterns, any evidence of differential sycophancy across models]

### 3. Damage avoidance
- **Theory predicts:** Prospect theory (λ ≈ 2) predicts conservative revision; damage should be rare but non-zero; models under sycophantic pressure should show more damage.
- **Data shows:** [1 genuine damage event in 180 trials. Connect to the scoring analysis: C1 damage:gain is 2:1, matching prospect theory. C2 standard is only 1:1 — flag this as a potential scoring issue. Reference the rescaling compression finding.]

### 4. Confidence repair
- **Theory predicts:** Successful revision should be accompanied by appropriate confidence increase (Nelson & Narens monitoring update); damage should be accompanied by confidence decrease if monitoring is functional.
- **Data shows:** [Reference whatever confidence dynamics data exists in the sweep — if the sweep JSONL files contain confidence data, summarize the patterns. If not, note this as a data gap.]

### 5. Appropriate search termination ("unresolved")
- **Theory predicts:** FOK-like responses should appear on genuinely ambiguous items; the 0.15 confidence-drop threshold may be too low given LLM confidence reliability (Jacobson & Truax RCI analysis).
- **Data shows:** [Reference the unresolved items in the sweep — sc_c1_ur_001, sc_c1_ur_002, sc_c2_ur_001, sc_c2_ur_002. How did models behave on these? Did any model show the FOK-like pattern?]

Close with a summary paragraph stating which predictions held, which didn't, and what this means for Family C's discriminatory validity at the current item count.

**Important:** Use specific numbers from the repo files. Not "models showed positive deltas" but "DeepSeek showed +8.9pp (bootstrap 95% CI: +2.2 to +17.8, p < 0.05), the only statistically significant T2-T1 improvement." Not "damage was rare" but "1 genuine correct→wrong event across 4 models × 45 items = 180 trials (0.56%), consistent with prospect-theory predictions of conservative revision but insufficient for statistical characterization of damage rates."

---

## Output format

Produce the complete revised document incorporating both additions. Keep the existing Parts I, II, and III exactly as they are (they are strong). Insert Part III-B after Part III. Replace Part IV with the restructured table-format source inventory. Keep the existing conclusion.

The target length for the revised document is 500–700 lines (currently 141 — the additions should roughly triple it, primarily from the structured tables and the empirical engagement section).
