# Family C Sprint: Risks, Failure Modes, and Decision Gates

**Purpose:** Enumerate risks, identify failure modes, and define the decision
framework for proceeding, pausing, or pivoting.

---

## 1. Measurement Risks

### 1.1 Risk: C1 Shows No Discrimination

**Description:** All models score near-zero on C1 (intrinsic self-correction).
Huang et al. predict this is plausible — intrinsic self-correction may simply
not work for current LLMs.

**Probability:** Medium-high (40-60%)

**Impact:** C1 becomes a floor-effect measure with no benchmark utility.

**Mitigation:**
- Accept this as a valid finding ("current models cannot self-correct without
  evidence") rather than a benchmark failure
- C1 still has value as a baseline: if future models break above the floor,
  that's a meaningful signal
- C2 carries the discrimination burden; ensure C2 item set is strong enough
- Decision: if C1 has zero variance across all 5 models, keep it in the
  benchmark at reduced weight (0.05 instead of 0.10) and note it as a
  documented floor effect

### 1.2 Risk: Obedience Confound

**Description:** Models that score well on C2 are simply more compliant —
they change answers whenever asked, and the C2 evidence happens to be correct
often enough to produce a positive score.

**Probability:** Medium (30-40%)

**Impact:** Family C measures compliance, not metacognition.

**Mitigation:**
- Include right-to-right and weak-challenge items where compliance hurts
- Track revision rate separately from revision quality
- If a model's revision rate > 80% AND damage rate > 20%, flag it as
  compliance-driven, not metacognitive
- Weak-challenge stratum is the primary diagnostic for this risk

### 1.3 Risk: Confidence Is Decorative

**Description:** Models adjust confidence in formulaic ways that don't reflect
actual uncertainty tracking (e.g., always lower by 0.1 on turn 2).

**Probability:** Medium (30-50%)

**Impact:** Confidence adjustment score becomes noise, not signal.

**Mitigation:**
- Track variance in confidence adjustments per model
- If confidence adjustment is near-constant across items, the confidence
  component adds no information and should be down-weighted
- Compare confidence dynamics to Family A calibration quality as a sanity check
- Decision: if confidence adjustment variance < 0.02 for all models, reduce
  confidence_adjustment weight in scoring

### 1.4 Risk: Grading Ambiguity

**Description:** Answer grading on turn 2 is harder than turn 1 because
revised answers may be partially correct, differently formatted, or annotated
with caveats.

**Probability:** Medium (30-40%)

**Impact:** Noisy scoring, quarantined items, reduced clean-set size.

**Mitigation:**
- Use same grading pipeline as A/B (grading_v2.py with 8 adjudication rules)
- Design items with unambiguous gold answers (numeric or short factual)
- Avoid open-ended questions where partial credit would be needed
- Generous quarantine: when in doubt, quarantine

---

## 2. Design Risks

### 2.1 Risk: Item Pool Too Small for Stable Scores

**Description:** With only 15 C1 items and 20 C2 items, individual item
variance may dominate the family score, making it unreliable.

**Probability:** Medium (30-40%)

**Impact:** Unstable scores, wide confidence intervals, unreliable model ordering.

**Mitigation:**
- Report bootstrap CIs alongside headline scores
- If CIs are too wide (±0.15 or more), defer promotion and expand item pool
- The seed phase is explicitly designed to test this — if 35 items isn't
  enough, expand to 60-80 before promotion

### 2.2 Risk: Challenge Prompts Leak the Answer

**Description:** In C2 items, the evidence or challenge prompt inadvertently
reveals the correct answer, making correction trivial.

**Probability:** Low-medium (20-30%)

**Impact:** C2 scores are inflated; correction measures reading, not metacognition.

**Mitigation:**
- Evidence must be suggestive, not conclusive (design principle)
- Review each C2 item: could a model answer correctly just from the evidence
  without having seen the question? If yes, the evidence is too strong.
- Include items where the evidence is misleading (weak-challenge stratum)
- Audit: if C2 correction rate is > 90%, evidence may be too revealing

### 2.3 Risk: Prompt Format Sensitivity

**Description:** Scores are sensitive to exact wording of the turn-2 prompt.
Different challenge templates produce different model orderings.

**Probability:** Medium (30-50%)

**Impact:** Benchmark results are fragile and unreproducible.

**Mitigation:**
- Use multiple challenge templates per stratum (generic, inspect, reconsider for C1)
- Assign templates to items, not to models — all models see the same template
  for the same item
- If time permits in expansion phase, run a subset with alternative templates
  to test robustness
- Decision: if model ordering changes substantially with template variation,
  fix templates before promotion

---

## 3. Implementation Risks

### 3.1 Risk: SDK Multi-Turn Bugs

**Description:** The Kaggle SDK's conversation history management has edge
cases that corrupt turn-2 context.

**Probability:** Low (10-20%)

**Impact:** Invalid data from turn-2 responses.

**Mitigation:**
- Phase 0 dry run explicitly tests multi-turn conversation handling
- Log both turn-1 and turn-2 raw responses for manual inspection
- Verify turn-2 responses reference turn-1 content (sanity check)

### 3.2 Risk: Schema Enforcement Failures

**Description:** Some models fail to produce valid structured output on the
`SelfCorrectionResponse` schema, especially the `is_likely_wrong` boolean.

**Probability:** Low-medium (15-25%)

**Impact:** Missing data for some model × item combinations.

**Mitigation:**
- The SDK handles schema enforcement automatically for most models
- Gemma 3 doesn't support structured output — exclude if in panel
- Current panel (gemini, claude, deepseek) all support structured output
- Set `max_attempts=1` and handle None results gracefully
- Track failure rate per model; if > 10%, investigate prompt/schema

### 3.3 Risk: Budget Overrun

**Description:** Two-turn items cost ~2x single-turn. 5 models × 35 items ×
2 turns = 350 API calls.

**Probability:** Low (5-10%)

**Impact:** Exceed $50/day or $500/month budget.

**Mitigation:**
- Estimated cost: ~175K tokens total, well within budget
- Use `kbench.client.enable_cache()` to avoid re-running identical calls
- Run smoke test on cheapest model first
- Monitor cost after Phase 1 before proceeding to Phase 2

---

## 4. Scientific Risks

### 4.1 Risk: Overclaiming Self-Correction Capability

**Description:** We report "Model X can self-correct" when it actually just
benefits from the second-chance effect (more compute time = better answer).

**Probability:** Medium (25-35%)

**Impact:** Scientifically misleading claims, credibility damage.

**Mitigation:**
- C1/C2 separation is the primary safeguard
- Never report "self-correction" based on C2 alone
- Always report C1 and C2 separately in any publication or leaderboard
- Include null hypothesis framing: "C1 improvement rate of X% compared to
  a second-attempt baseline of Y%"

### 4.2 Risk: Model Contamination

**Description:** Models may have been trained on items similar to our seed set,
inflating scores for those models.

**Probability:** Low for seed set (items are novel), Medium for expansion

**Impact:** Unfair benchmark, model-specific score inflation.

**Mitigation:**
- Author original items rather than pulling from public datasets
- Avoid well-known trick questions that are likely in training data
- Monitor for suspiciously perfect performance on specific items
- Track item-level scores across models; contaminated items show bimodal patterns

### 4.3 Risk: Gaming via Review-Prompt Pattern Matching

**Description:** Models learn to always revise when they see "review" or
"reconsider" in the prompt, regardless of content.

**Probability:** Medium (25-40%)

**Impact:** Scores reflect prompt-following, not metacognition.

**Mitigation:**
- Right-to-right items catch this: always-revise → damage
- Vary challenge templates to prevent pattern matching
- Anti-gaming countermeasure from config: `symmetric_correction_setup`
- The scoring design explicitly penalizes indiscriminate revision

---

## 5. Decision Gates (Summary)

### Gate 0: Pre-Evaluation Readiness

**Trigger:** Before running any models.
**Criteria:**
- [ ] Seed items authored and reviewed (35 items)
- [ ] Scoring pipeline tested with synthetic data
- [ ] Grading pipeline handles expected answer formats
- [ ] SDK multi-turn pattern verified in dry run
- [ ] Data files in correct format and location

**If not met:** Fix issues before proceeding. No evaluation without passing Gate 0.

### Gate 1: Seed-Set Approval

**Trigger:** After Phase 2 (5-model panel run on seed set).
**Criteria:**
- [ ] ≥ 25 clean items after audit
- [ ] Score range ≥ 0.10 for at least one subfamily
- [ ] Damage rate > 0 for ≥ 2 models
- [ ] No systematic grading failures
- [ ] Budget within limits

**If met:** Proceed to item expansion (Phase 2 of dataset plan).
**If not met:** Diagnose failure mode:
  - If grading issues → fix grading, re-run
  - If no discrimination → review item design, consider harder items
  - If budget issues → reduce panel to 3 models

### Gate 2: Clean-Set Promotion

**Trigger:** After expansion to 60-80 items.
**Criteria:**
- [ ] ≥ 50 clean items
- [ ] Significant pairwise model differences (bootstrap)
- [ ] Rank correlation with A < 0.9
- [ ] Stable damage rate patterns
- [ ] Scores in useful range

**If met:** Family C earns reporting status; include in narrative notebook.
**If not met:** Family C remains analysis-only; revisit item design.

### Gate 3: Official Benchmark Inclusion

**Trigger:** After Gate 2 + narrative documentation.
**Criteria:**
- [ ] Gates 1 and 2 passed
- [ ] Composite score with C does not degrade A/B discrimination
- [ ] No unresolved grading ambiguities
- [ ] Documentation complete
- [ ] Scoring weights confirmed

**If met:** Update official benchmark notebook, `%choose` task, and leaderboard.
**If not met:** Family C remains in narrative notebook only.

---

## 6. Escalation Triggers

Stop and surface to user if:

1. **C1 shows literally zero variance across all 5 models** — discuss whether
   to keep C1 or defer it entirely
2. **Damage rate is zero across all models and all items** — the right-to-right
   items may need to be redesigned to be more challenging
3. **C2 correction rate > 90%** — evidence may be too revealing; redesign
   followup_evidence for affected items
4. **More than 40% of items quarantined** — seed set quality is insufficient;
   need to re-author items
5. **SDK multi-turn handling produces invalid data** — may need to restructure
   the conversation pattern or contact SDK maintainers
