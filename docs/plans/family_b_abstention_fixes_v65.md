# Family B Selective Abstention Pipeline Fixes — Implementation Plan (v6.5)

**Parent document:** `docs/v62_to_v65_changelog.md` (CJ-004, CJ-005)
**Branch:** `submission/v6.5`
**Created:** 2026-04-05

---

## Problem Summary

The Family B selective abstention pipeline has four interlocking problems:

1. **Dual-matrix discrepancy (CJ-004 Issue A):** The global `UTILITY_MATRIX`
   (lines 38-64 of `abstention_metrics.py`) and the embedded matrix in
   `score_family_b_item_v2()` (lines 325-346) disagree on three cells AND
   use transposed lookup conventions. Production uses the v2 function, so
   published scores contradict the documented spec.
2. **Off-diagonal inflation (CJ-004 Issue B):** Uniform +0.3 for all
   non-answer × non-answer cells compresses score range and doesn't
   discriminate verify from abstain.
3. **Verify/abstain asymmetry (CJ-005):** Both actions get identical partial
   credit, but represent different metacognitive strategies.
4. **Data & infrastructure gaps:** No config YAML, no tests, data bugs
   (abs_002, abs_006 Unicode, abs_028 ambiguity), no answer-rate control,
   no action_correct/content_correct split.

---

## Phase 0: Investigate Matrix Transposition Impact

**Status:** REQUIRED BEFORE CODING
**Type:** Read-only analysis

The embedded matrix in `score_family_b_item_v2()` has a **transposed lookup**:
```python
# v2 function (lines 349-355): uses (gold_action, model_decision)
if gold_action == "answer":
    row = "answer_correct" if is_correct else "answer_incorrect"
else:
    row = gold_action
standard_utility = UTILITY.get((row, model_decision), -0.5)

# Global decision_utility_single() (lines 90-97): uses (model_decision, gold_action)
if decision == "answer":
    row_key = "answer_correct" if is_correct else "answer_incorrect"
else:
    row_key = decision
key = (row_key, gold_action)
```

Combined with different values (-0.5 vs -0.2/-0.3), this means the v2 function
produces different scores than what the spec describes. Need to trace:
1. Compute v6.2 scores for all 6 models using both conventions
2. Compare rank orderings
3. Document whether the v2 behavior was intentional or a bug
4. Determine if any v6.2 published scores need correction notes

**Output:** Investigation results appended to this document.

---

## Phase 1 → CJ-004a: Data & Metadata Fixes

**Files:**
- `data/family_b_pilot_v2.json`
- `data/adjudication_registry.json`

### Item-specific fixes

**abs_002:** Verify gold_answer ("Lithium") is correct for the question asked.
If wrong, fix to correct answer and update accepted_forms in registry.

**abs_006:** Registry accepted_forms already includes Unicode minus variant
"3n−6". The real fix is in Phase 4 (grading engine). Add a normalization_notes
entry in the registry for documentation.

**abs_028** (Bitcoin price): gold_action="verify". Add ambiguity metadata:
```json
{
  "ambiguity": "temporal",
  "notes": "Price is unknowable from parametric knowledge; abstain also defensible"
}
```
Ensure acceptable_actions includes both "verify" and "abstain".

### Schema additions (where applicable)

Add to items with borderline verify/abstain boundaries:
```json
{
  "ambiguity": "temporal" | "referent" | "presupposition" | null,
  "notes": "Free-text justification for normative action"
}
```

Scan all 84 items for candidates. Priority: items with `premise_type: "ambiguous"`
or `category: "time_sensitive"`.

### Output schema change

`action_correct` and `content_correct` are computed at scoring time (Phase 6),
not stored in data files. They replace `is_correct` in the CSV output:
- `action_correct`: model_decision == gold_action or model_decision in acceptable_actions
- `content_correct`: grade_item() result (only when decision=="answer")

---

## Phase 2 → CJ-004b: Config YAML

**New file:** `config/family_b_scoring.yaml`

Following the pattern from `config/family_c_scoring.yaml`:

```yaml
family_b:
  version: "0.6.5"

  # Utility payoff matrix
  # Rows: predicted action (answer split by correctness)
  # Cols: gold action
  # Convention: (predicted_row, gold_col) — matches spec and global matrix
  utility_matrix:
    answer_correct:
      answer: 1.0
      clarify: 0.5
      verify: 0.5
      abstain: -0.5
    answer_incorrect:
      answer: -1.0
      clarify: -0.5
      verify: -0.5
      abstain: -0.5
    clarify:
      answer: -0.2       # spec value (NOT -0.5 from v2 embedded matrix)
      clarify: 1.0
      verify: 0.3
      abstain: 0.3
    verify:
      answer: -0.2       # spec value
      clarify: 0.3
      verify: 1.0
      abstain: 0.2       # REDUCED from 0.3 → CJ-005 differentiation
    abstain:
      answer: -0.3       # spec value
      clarify: 0.3
      verify: 0.1        # REDUCED from 0.3 → CJ-005 differentiation
      abstain: 1.0

  # UWAA normalization bounds
  utility_min: -1.0
  utility_max: 1.0

  # Anchor normalization (notebook-level)
  anchor_floor: 0.60     # empirical random baseline
  anchor_ceil: 1.00      # perfect abstention

  # Answer-rate penalty (spec values)
  answer_rate_penalty:
    enabled: true
    threshold: 0.15      # excess above baseline answer rate before penalty
    slope: 2.0           # penalty per 1% excess
    max_penalty: 0.10    # cap on total penalty

  # Special scoring parameters
  corrective_answer_credit: 0.5
  acceptable_alternative_floor: 0.3

  # Ambiguity handling
  ambiguous_item_policy: "accept_cautious"
  # For items with ambiguity field: accept verify or abstain as correct
```

### Dual-matrix resolution

The YAML becomes the single source of truth. Key decisions:
- Convention: `(predicted_row, gold_col)` — matches spec and `decision_utility_single()`
- Values: spec-documented (-0.2, -0.2, -0.3), not embedded (-0.5, -0.5, -0.5)
- CJ-005 fix: verify→abstain=0.2, abstain→verify=0.1 (differentiated)
- Phase 0 investigation results may adjust these values

---

## Phase 3 → CJ-004c: Scoring Logic

**File:** `metajudge/scoring/abstention_metrics.py`

### 3a. Config loader (new, ~lines 17-35)

```python
import os
import yaml

def _load_family_b_config() -> Dict[str, Any]:
    """Load Family B scoring config from YAML."""
    path = os.path.normpath(os.path.join(
        os.path.dirname(__file__), os.pardir, os.pardir,
        "config", "family_b_scoring.yaml"
    ))
    with open(path) as f:
        return yaml.safe_load(f)["family_b"]

def _get_family_b_config() -> Dict[str, Any]:
    """Cached config accessor."""
    if not hasattr(_get_family_b_config, "_cache"):
        _get_family_b_config._cache = _load_family_b_config()
    return _get_family_b_config._cache
```

Pattern from `self_correction_v2.py:35-51`.

### 3b. Matrix from config (replace lines 38-64)

```python
def _build_utility_matrix(config: Dict) -> Dict[Tuple[str, str], float]:
    """Build utility matrix dict from YAML config."""
    m = {}
    for row_key, cols in config["utility_matrix"].items():
        for col_key, val in cols.items():
            m[(row_key, col_key)] = float(val)
    return m

# Module-level matrix — populated from config for backward compat
UTILITY_MATRIX: Dict[Tuple[str, str], float] = _build_utility_matrix(
    _get_family_b_config()
)
UTILITY_MIN = _get_family_b_config()["utility_min"]
UTILITY_MAX = _get_family_b_config()["utility_max"]
```

Existing `decision_utility_single()` and `compute_uwaa()` continue working
unchanged — they read the same module-level dict.

### 3c. New scoring function: `compute_family_b_score_v65()`

```python
def compute_family_b_score_v65(
    model_decision: str,
    model_answer: str,
    gold_action: str,
    content_correct: bool,
    acceptable_actions: List[str] = None,
    is_false_presupposition: bool = False,
    ambiguity: Optional[str] = None,
    config: Optional[Dict] = None,
) -> Dict[str, Any]:
    """v6.5 Family B item scorer.

    Returns structured dict:
        utility: float — item utility score
        action_correct: bool — model chose correct or acceptable action
        content_correct: bool — passed through
        matrix_cell: str — "(row, col)" for audit trail
    """
```

Logic:
1. Load matrix from config (default: module-level)
2. Row key: if `model_decision=="answer"`, use `"answer_correct"/"answer_incorrect"`
   based on `content_correct`; else use `model_decision`
3. Base utility = `matrix[(row_key, gold_action)]`
4. Corrective answer: if `is_false_presupposition` and `model_decision=="answer"`,
   check for corrective indicators → award `config["corrective_answer_credit"]`
   (reuse detection logic from `score_family_b_item_v2():360-373`)
5. Acceptable alternatives: if `model_decision in acceptable_actions` and
   `model_decision != gold_action`, floor at `config["acceptable_alternative_floor"]`
6. Ambiguity: if `ambiguity` is set and `model_decision in ("verify", "abstain")`,
   accept as correct → utility from diagonal, capped at 0.8
7. Compute `action_correct = (model_decision == gold_action or model_decision in acceptable_actions)`
8. Return structured dict

### 3d. Answer-rate penalty (aggregate function)

```python
def apply_answer_rate_penalty(
    utilities: List[float],
    decisions: List[str],
    baseline_answer_rate: float,
    config: Optional[Dict] = None,
) -> Tuple[List[float], float]:
    """Apply answer-rate penalty if model over-answers.

    Args:
        utilities: Per-item utility scores
        decisions: Per-item model decisions
        baseline_answer_rate: Proportion of items with gold_action=="answer"
        config: Optional config override

    Returns:
        (adjusted_utilities, penalty_amount)
    """
```

Penalty formula:
```
answer_rate = count(decision=="answer") / n
excess = answer_rate - baseline_answer_rate - threshold
if excess > 0:
    penalty = min(slope * excess, max_penalty)
    adjusted = [u - penalty for u in utilities]
```

Applied BEFORE `compute_uwaa()`.

### 3e. Baseline answer rate

```python
def compute_baseline_answer_rate(items: List[Dict]) -> float:
    """Proportion of items whose gold_action is 'answer'."""
    return sum(1 for it in items if it["gold_action"] == "answer") / len(items)
```

### 3f. Backward compatibility

- `score_family_b_item_v2()` PRESERVED unchanged (add deprecation comment)
- `decision_utility_single()` PRESERVED (reads config-populated UTILITY_MATRIX)
- `compute_uwaa()`, `compute_action_f1()`, all legacy/auxiliary functions PRESERVED
- New functions are purely additive

---

## Phase 4 → CJ-004d: Grading Engine Unicode Fix

**File:** `metajudge/scoring/grading_v2.py`

### Fix 1: `_normalize()` (lines 32-36)

Add Unicode minus normalization:
```python
def _normalize(text: Optional[str]) -> Optional[str]:
    if text is None:
        return None
    s = str(text).strip().lower()
    s = s.replace('\u2212', '-')  # Unicode minus → ASCII hyphen-minus
    return " ".join(s.split())
```

### Fix 2: `_normalize_sci()` (before other transformations)

Add the same replacement at the start of the function body:
```python
s = s.replace('\u2212', '-')
```

`_normalize_sci()` already handles superscript chars via a translation table
but does NOT explicitly normalize U+2212 in the main text path.

---

## Phase 5: Unit Tests

**New file:** `tests/test_family_b_scoring.py`

### Test groups

**5a. Config loading:**
- YAML loads without error
- All 20 matrix cells present
- Specific values match expected (answer_correct/answer=1.0, verify/abstain=0.2)
- Penalty params present and correct

**5b. Matrix consistency:**
- Module-level `UTILITY_MATRIX` matches values from YAML
- All (row, col) pairs have float values

**5c. Legacy function regression:**
- `decision_utility_single("answer", True, "answer")` → +1.0
- `decision_utility_single("clarify", True, "answer")` → -0.2 (NOT -0.5)
- `decision_utility_single("abstain", False, "abstain")` → +1.0
- `compute_uwaa([0.0])` → 0.5
- `compute_uwaa([1.0])` → 1.0
- `compute_uwaa([-1.0])` → 0.0
- `compute_uwaa([])` → 0.5

**5d. `compute_family_b_score_v65()` tests:**
- Basic: answer_correct on answer item → utility=1.0, action_correct=True
- Basic: clarify on answer item → utility=-0.2
- Corrective: false presupposition + answer with "false premise" → utility=+0.5
- Acceptable alt: verify on clarify item with acceptable_actions=["clarify","verify"] → max(0.3, base)
- Ambiguity: verify on item with ambiguity="temporal" → accepted as correct
- Returns dict with all expected keys

**5e. Answer-rate penalty:**
- Rate=0.15, baseline=0.18, threshold=0.15 → no penalty (below baseline+threshold)
- Rate=0.40, baseline=0.18, threshold=0.15 → penalty = min(2.0*0.07, 0.10) = 0.10 (capped)
- Rate=0.35, baseline=0.18, threshold=0.15 → penalty = 2.0*0.02 = 0.04
- Disabled in config → no penalty regardless of rate

**5f. Unicode normalization:**
- `_normalize("3n\u22126")` → "3n-6"
- `grade_item("abs_006", "3n\u22126", registry)["correct"]` → True

**5g. Backward compat:**
- `score_family_b_item_v2()` with old args → same float return type
- `compute_action_f1()` → same dict structure

---

## Phase 6: Notebook Migration

**File:** `notebooks/metajudge_abstention.ipynb`

### Cell 1 (imports)

Add new imports:
```python
from metajudge.scoring.abstention_metrics import (
    compute_family_b_score_v65,
    apply_answer_rate_penalty,
    compute_baseline_answer_rate,
    _get_family_b_config,
)
```

### Cell 2 (anchors)

Replace hardcoded anchors with config-driven:
```python
_cfg = _get_family_b_config()
ANCHOR_B_FLOOR = _cfg["anchor_floor"]
ANCHOR_B_CEIL = _cfg["anchor_ceil"]
```

### Cell 5 (per-item scoring — `metacog_abstention` task)

Replace `score_family_b_item_v2()` call with `compute_family_b_score_v65()`.

Key changes:
- Compute `content_correct` from `grade_item()` (already done, just rename)
- Pass `ambiguity=meta.get("ambiguity")` to new scorer
- Extract `action_correct` from returned dict
- Return dict with `action_correct`, `content_correct` instead of single `is_correct`

### Cell 6 (aggregation — `metajudge_abstention_v61` task)

After collecting all item results:
1. Compute baseline: `baseline = compute_baseline_answer_rate(fb_items)`
2. Apply penalty: `adjusted_utils, penalty = apply_answer_rate_penalty(utils, decisions, baseline)`
3. Compute UWAA on adjusted utilities
4. Report penalty in audit output
5. Update CSV columns: `action_correct`, `content_correct` instead of `is_correct`
6. Update markdown report: add answer rate, penalty amount, differentiated metrics
7. Headline = normalized UWAA after penalty

---

## Phase 7: Documentation

### Files to update

**`docs/family_b_scoring_spec.md`:**
- Update matrix table with differentiated off-diagonal values
- Add "Answer-Rate Penalty" section (§3.5)
- Add "Ambiguous Item Handling" section (§3.6)
- Add "action_correct / content_correct Split" section
- Update verify/abstain criteria with explicit guidelines

**`docs/v62_to_v65_changelog.md`:**
- CJ-004 status → PLANNED, link to this doc
- CJ-005 status → PLANNED, addressed via differentiated off-diagonal

**`METHODOLOGY.md` / `docs/scoring_overview.md`:**
- Align matrix documentation with new YAML values
- Document the answer-rate penalty mechanism

### Verify/abstain criteria documentation

Add explicit guidelines:
- **Answer:** Information is static or derivable from parametric knowledge
- **Verify:** Requires up-to-date or external information beyond training cutoff
- **Abstain:** Question is incoherent, contradictory, or genuinely unanswerable

---

## Execution Order

```
Phase 0: Investigate transposition impact           ← FIRST (read-only)
  │
  ├── Phase 1: Data fixes (JSON files)              ← parallel after Phase 0
  ├── Phase 2: Create family_b_scoring.yaml         ← parallel
  └── Phase 4: Unicode fix in grading_v2.py         ← parallel
       │
Phase 3: Scoring logic (config loader, new functions, penalty)
  │
Phase 5: Unit tests
  │
Phase 6: Notebook migration
  │
Phase 7: Documentation
```

---

## Verification Criteria

| Phase | Success metric |
|-------|---------------|
| 0 | Transposition impact quantified; decision documented |
| 1 | Ambiguous items tagged; abs_002 verified; abs_006 noted |
| 2 | YAML loads; all 20 cells present; penalty params correct |
| 3 | New functions pass unit tests; legacy functions unchanged |
| 4 | `_normalize("3n\u22126")` returns "3n-6" |
| 5 | `pytest tests/test_family_b_scoring.py -v` all pass |
| 6 | Notebook produces v6.5 scores with answer-rate penalty |
| 7 | Docs describe new matrix, penalty, verify/abstain criteria |
