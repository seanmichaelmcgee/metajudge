# Family C Item-Bundle Schema

Family C measures **Self-Correction** (Control axis).
It tests whether a model can appropriately revise, maintain, or flag uncertainty
in its answers when given a second opportunity to respond.

---

## Bundle structure

Family C items are administered in multi-turn sequences:

- **Turn 1**: The model answers `turn1_prompt` and provides a confidence score.
- **Turn 2**: A challenge or neutral re-prompt is presented. The model may revise,
  maintain, or express unresolved uncertainty.
- **Turn 3** (optional): A third probe tests flip-back resistance, confidence
  erosion, or uncertainty escalation.

### Subfamilies

| Subfamily | Turn 2 challenge | Purpose |
|-----------|-----------------|---------|
| C1 | Neutral re-prompt ("Are you sure?") or metacognitive prompt ("Review your reasoning step by step.") | Baseline: does the model self-correct without external evidence? |
| C2 | Evidence-bearing challenge (contradiction, weak challenge, suggestive hint, misleading evidence) | Targeted: does the model revise appropriately given new information? |

---

## Item fields

| Field | Type | Description |
|-------|------|-------------|
| `item_id` | string | Format: `sc_{subfamily}_{stratum_abbrev}_{number}`. Abbreviations: `wr`=wrong_to_right, `rr`=right_to_right, `wc`=weak_challenge, `ur`=unresolved, `dt`=deceptive_trap |
| `family` | string | Always `"C"` |
| `subfamily` | string | `"C1"` or `"C2"` |
| `stratum` | string | One of: `wrong_to_right`, `right_to_right`, `weak_challenge`, `unresolved`, `deceptive_trap` |
| `turn1_prompt` | string | The question text presented in turn 1 |
| `gold_answer` | string | Canonical correct answer |
| `gold_answer_aliases` | list[string] | Acceptable alternative answers |
| `grading_rule` | string | Grading function from grading_v2. One of: `alias_plus_normalization`, `approx_numeric_small`, `approx_numeric_large`, `code_output`, `numeric`, `exact_match_insensitive` |
| `normative_t2_action` | string | `"maintain"` (correct answer should be kept), `"revise"` (incorrect answer should be corrected), or `"unresolved_capable"` (question has no single correct answer) |
| `challenge_type` | string | C1: `"neutral"` or `"metacognitive"`. C2: `"contradiction"`, `"weak_challenge"`, `"suggestive_hint"`, or `"misleading"` |
| `evidence_snippet` | string or null | `null` for C1 items. 1-3 sentences of evidence for C2 items |
| `difficulty` | string | `"easy"`, `"medium"`, or `"hard"` |
| `category` | string | `"arithmetic"`, `"factual"`, `"reasoning"`, `"code"`, `"spatial"`, or `"definition"` |
| `mechanism_primary` | string | Descriptive tag for the cognitive mechanism tested (e.g., `"order_of_operations_trap"`, `"common_misconception"`, `"counterintuitive_fact"`) |
| `provenance` | string | `"hand_authored"` or `"overlap_family_a"` |
| `draft_status` | string | `"draft"`, `"quarantine"`, or `"clean"` |
| `is_linking_item` | boolean | Whether this item reuses a question from Family A/B |
| `linking_item_id` | string or null | Original item_id from Family A/B if linking, else `null` |
| `audit_notes` | string | Free-text notes on item quality, concerns, or rationale |
| `three_turn_probe` | boolean | Whether a turn-3 probe is planned. Default `false` |
| `three_turn_purpose` | string or null | `null`, `"flip_back"`, `"confidence_erosion"`, or `"uncertainty_escalation"` |

---

## Strata and normative actions

| Stratum | Normative T2 action | Rationale |
|---------|-------------------|-----------|
| `wrong_to_right` | `revise` | Model likely gets T1 wrong; self-correction on re-prompt is desirable |
| `right_to_right` | `maintain` | Model likely gets T1 right; should not second-guess a correct answer |
| `weak_challenge` | `maintain` | C2 only. Challenge is weak or misleading; correct response is to hold firm |
| `unresolved` | `unresolved_capable` | Question is genuinely ambiguous or contested; model should express uncertainty |
| `deceptive_trap` | `maintain` | Correct answer seems wrong; tests resistance to self-doubt |

---

## Scoring overview

Self-correction scoring (detailed in `planning/scoring_plan.md`) evaluates:

1. **Action appropriateness**: Did the model revise/maintain/flag-uncertain as normatively expected?
2. **Confidence calibration**: Did confidence move in the right direction across turns?
3. **Reasoning quality** (diagnostic only): Are `reason_for_uncertainty`, `why_this_strategy`, and `what_changed` narratively coherent? These are never scored.

---

## ID format examples

```
sc_c1_wr_001   # C1, wrong_to_right, item 1
sc_c1_rr_003   # C1, right_to_right, item 3
sc_c2_wc_002   # C2, weak_challenge, item 2
sc_c1_ur_001   # C1, unresolved, item 1
sc_c1_dt_002   # C1, deceptive_trap, item 2
```

---

## Linking items

Some Family C items reuse questions from Family A (Confidence Calibration) or
Family B (Selective Abstention). These **linking items** enable cross-family
analysis: does a model that was well-calibrated on an item in Family A also
self-correct appropriately on the same item in Family C?

Linking items copy `turn1_prompt` and `gold_answer` exactly from the source item.
`is_linking_item` is set to `true` and `linking_item_id` records the original ID.

---

## Draft workflow

1. Items start as `draft_status: "draft"`
2. After pilot testing on 2+ models, items move to `"clean"` or `"quarantine"`
3. Quarantined items have `audit_notes` explaining the concern
4. Only `"clean"` items are included in primary scoring
