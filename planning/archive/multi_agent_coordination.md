# Multi-Agent Coordination Plan — Expansion Sprint V2

**Date:** 2026-03-18  
**Companion doc:** `planning/expansion_sprint_v2.md`  
**Governing:** `SOUL.md` > `scoring_plan.md` > `dataset_construction_plan.md`

---

## 0. Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    ORCHESTRATOR                          │
│  (Main agent — owns sprint state, sequencing, commits)  │
│                                                         │
│  Phase 1–2        Phase 3          Phase 4      Phase 5 │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────┐ │
│  │HARVESTER │──▶│FORMATTER │──▶│STRATEGIST│──▶│ORCH  │ │
│  │          │   │          │   │          │   │(self)│ │
│  └──────────┘   └──────────┘   └──────────┘   └──────┘ │
│       │              │              │                    │
│       │              │              ▼                    │
│       │              │        ┌──────────┐              │
│       │              │        │ AUDITOR  │              │
│       │              │        │(reviews  │              │
│       │              │        │ output)  │              │
│       │              │        └──────────┘              │
│       │              │                                   │
│       ▼              ▼                                   │
│  v2_raw_        v2_canon_       v2_selected_            │
│  candidates     candidates      100.json                │
│  .json          .json                                    │
└─────────────────────────────────────────────────────────┘
```

The sprint uses **4 specialist subagents** plus the **orchestrator** (you). Each agent has a defined role, input contract, output contract, and explicit handoff protocol. Agents operate sequentially — no parallel writes to the same file.

---

## 1. Agent Roles

### 1.1 HARVESTER — "Pull Info"

**Purpose:** Gather raw candidate questions from external sources and the existing pool.

**Responsibilities:**
- Download and filter HLE dataset (HuggingFace `cais/hle`)
- Download and filter FermiEval / Science Olympiad Fermi questions
- Check SimpleQA Verified availability and download if possible
- Author new multi-step reasoning, deceptive, and adversarial items
- Merge all candidates into a single raw pool

**Input contract:**
- This plan (`expansion_sprint_v2.md` §2 — source list and target yields)
- Existing pool at `data/harvest/unified_candidate_pool.json` (for dedup reference)
- Existing pilot set at `data/calibration.csv` (for dedup reference)

**Output contract:**
- `data/harvest/v2_raw_candidates.json` — array of objects, each with:
  ```json
  {
    "prompt": "...",
    "gold_answer": "...",
    "difficulty": "easy|medium|hard|deceptive|adversarial",
    "item_family": "...",
    "source": "hle|fermieval|simpleqa_verified|authored_v2|pool_upgrade",
    "answer_type": "integer|decimal|entity|yes_no|single_word",
    "plausible_wrong_answer": "..." ,
    "reasoning_chain": "...",
    "note": "...",
    "raw_id": "unique_within_batch"
  }
  ```
- Minimum 200 candidates
- Every deceptive/adversarial item MUST have `plausible_wrong_answer` populated
- Every hard item that requires multi-step reasoning MUST have `reasoning_chain` populated

**What this agent does NOT do:**
- Does not normalize prompts to final format (that's Formatter)
- Does not build the alias ledger (that's Formatter)
- Does not select the final 100 (that's Strategist)
- Does not assess items against the scoring plan (that's Strategist)

**Key instructions for the agent:**
- When filtering HLE: only keep items where `question_type == "short_answer"` or where the answer is ≤ 5 tokens
- When filtering HLE: skip any item with images or multimodal content
- When filtering Fermi questions: only keep items with a specific numeric ground truth (not "order of magnitude" estimates)
- When authoring items: follow the item-type specs in `expansion_sprint_v2.md` §2.2D
- When authoring items: document your reasoning chain for every item — why would a model get this wrong confidently?
- Preserve the `source` field accurately — never mislabel a source
- Do NOT rewrite prompts into final format yet — just ensure they're clear and complete

**Duration estimate:** 20–30 minutes

---

### 1.2 FORMATTER — "Canonicalize & Structure"

**Purpose:** Transform raw candidates into standardized, alias-covered, schema-compliant items.

**Responsibilities:**
- Normalize all prompts to standard MetaJudge format
- Normalize all gold answers (lowercase, strip whitespace, digits for numeric)
- Build comprehensive alias ledger for every item
- Assign `answer_type`, `grader_rule`, `format_instruction` per item
- Deduplicate against existing 20-item pilot
- Flag items that fail format gates (§3.1 of sprint plan)

**Input contract:**
- `data/harvest/v2_raw_candidates.json` (from Harvester)
- `data/calibration.csv` (existing pilot — for dedup)
- `data/calibration_answer_key.json` (existing answer key — for format reference)
- `planning/dataset_construction_plan.md` §8 (hard rules for item writing)
- `planning/scoring_plan.md` §4 (adjudication standard and grader hierarchy)

**Output contract:**
- `data/harvest/v2_canonicalized_candidates.json` — array of objects, each with:
  ```json
  {
    "prompt": "...(final format, ending with 'Answer with X only.')",
    "gold_answer": "...(normalized)",
    "difficulty": "...",
    "item_family": "...",
    "source": "...",
    "answer_type": "integer|decimal|entity|yes_no|single_word",
    "grader_rule": "numeric_equivalence|alias_match|yes_no_match",
    "format_instruction": "digits_only|country_name_only|yes_no|...",
    "plausible_wrong_answer": "...",
    "reasoning_chain": "...",
    "note": "...",
    "canonical_id": "v2_NNN",
    "format_pass": true|false,
    "format_issues": ["...", "..."]
  }
  ```
- `data/harvest/v2_alias_ledger.json` — keyed by `canonical_id`:
  ```json
  {
    "v2_001": {
      "canonical_answer": "...",
      "accepted_aliases": ["...", "..."],
      "rejected_near_misses": ["...", "..."],
      "alias_rationale": "..."
    }
  }
  ```
- Every item must have `format_pass` set to `true` or `false`
- Items with `format_pass: false` are still included (for Strategist to review) but flagged

**What this agent does NOT do:**
- Does not fetch new questions (that's Harvester)
- Does not select the final 100 (that's Strategist)
- Does not assess calibration signal quality (that's Strategist)
- Does not write to `data/calibration.csv` (that's Orchestrator)

**Key instructions for the agent:**
- Prompt normalization rules (from dataset_construction_plan.md §8.1):
  - End every prompt with a forcing instruction: "Answer with [format] only."
  - Use "digits only" for numeric answers
  - Use "the [noun] name only" for named entities
  - Use "yes or no only" for binary items
  - Use "one word only" for single-word answers
- Gold answer normalization:
  - Lowercase everything
  - Strip leading/trailing whitespace
  - Remove trailing periods
  - Digits only for numeric (no commas, no units)
  - No articles (a, an, the) at the start
- Alias construction rules:
  - Include common misspellings for names
  - Include with/without hyphens
  - Include singular and plural where applicable
  - Include common abbreviations
  - Include numeric variants (e.g., "twenty-seven" for 27)
  - Document WHY each alias is accepted or rejected
- Dedup rules:
  - Check prompt similarity against pilot set (semantic, not just exact)
  - Check gold_answer overlap — if two items have the same gold answer AND same domain, flag
- Flag (do not remove) items where:
  - Gold answer has >5 tokens
  - Prompt doesn't end with a forcing instruction (even after your rewrite attempt)
  - Answer has multiple equally natural forms that can't be collapsed
  - The item is clearly time-sensitive

**Duration estimate:** 15–20 minutes

---

### 1.3 STRATEGIST — "Assess, Select, Check Against Plan"

**Purpose:** Select the final 100 items from the canonicalized pool, ensuring the selection optimizes for calibration signal, domain balance, and competition rubric alignment.

**Responsibilities:**
- Select exactly 100 items matching the V2 difficulty distribution
- Verify domain balance and answer-type balance
- Verify every deceptive/adversarial item has documented calibration signal
- Apply discrimination gates (check for likely-memorized items)
- Cross-reference selection against scoring_plan.md and dataset_construction_plan.md
- Log every rejection with reason

**Input contract:**
- `data/harvest/v2_canonicalized_candidates.json` (from Formatter)
- `data/harvest/v2_alias_ledger.json` (from Formatter)
- `planning/expansion_sprint_v2.md` §1 (target distribution)
- `planning/scoring_plan.md` §7 (dataset implications) and §8 (frontier-readiness)
- `planning/dataset_construction_plan.md` §6 (composition) and §8 (hard rules)
- `SOUL.md` — final authority

**Output contract:**
- `data/harvest/v2_selected_100.json` — array of exactly 100 objects (same schema as canonicalized, plus `example_id: "cal_NNN"`)
- `data/harvest/v2_rejection_log.json` — array of rejected items:
  ```json
  {
    "canonical_id": "v2_NNN",
    "prompt_preview": "first 80 chars...",
    "rejection_reason": "...",
    "rejection_category": "format_fail|duplicate|ceiling_risk|contamination|domain_imbalance|answer_type_imbalance|weak_signal|ambiguous"
  }
  ```
- `data/harvest/v2_selection_summary.md` — human-readable summary:
  - Final distribution by difficulty, domain, answer_type, source
  - List of deceptive items with their plausible wrong answers
  - List of adversarial items with their confabulation triggers
  - Flags or concerns for Orchestrator review
  - Cross-reference against scoring_plan.md requirements

**What this agent does NOT do:**
- Does not fetch or author questions (that's Harvester)
- Does not normalize formatting (that's Formatter)
- Does not build final CSVs (that's Orchestrator)
- Does not update the notebook (that's Orchestrator)

**Key instructions for the agent:**
- Selection priorities (in order):
  1. Calibration signal quality — will this item differentiate models on confidence?
  2. Format compliance — does it pass all format gates?
  3. Answer unambiguity — is there exactly one defensible correct answer?
  4. Contamination resistance — is this item unlikely to be memorized?
  5. Domain balance — does adding this item improve coverage?
  6. Answer-type balance — does adding this item reduce yes/no skew?
- Hard constraints:
  - Yes/no items must be ≤ 20% of total (≤ 20 items)
  - No single item_family > 25% of total (≤ 25 items)
  - Every deceptive item must have `plausible_wrong_answer` that is NOT the gold answer
  - Every adversarial item must have a documented confabulation trigger
  - No items with `format_pass: false` in the final 100 (fix or reject)
- Soft targets:
  - 7+ distinct item_family values represented
  - At least 3 source types represented (authored, public dataset, rewritten)
  - At least 5 items requiring multi-step reasoning
- When in doubt about an item: **reject it and log the reason**. Better to have 95 excellent items than 100 with 5 weak ones.

**Duration estimate:** 15–20 minutes

---

### 1.4 AUDITOR — "Verify & Validate"

**Purpose:** Independent review of the Strategist's selection. Catches errors the Strategist might miss. Acts as a fresh pair of eyes before the Orchestrator commits.

**Responsibilities:**
- Verify the selected 100 items against ALL quality gates
- Spot-check alias coverage (sample 10–15 items, try to break them)
- Verify gold answers are factually correct (sample 15–20 items, verify via search)
- Check for subtle duplicates or near-duplicates within the 100
- Check for items that are actually easier than labeled
- Verify the selection summary matches the actual data
- Flag any SOUL.md violations

**Input contract:**
- `data/harvest/v2_selected_100.json` (from Strategist)
- `data/harvest/v2_alias_ledger.json` (from Formatter)
- `data/harvest/v2_selection_summary.md` (from Strategist)
- `SOUL.md`
- `planning/scoring_plan.md`
- `planning/dataset_construction_plan.md`

**Output contract:**
- `data/harvest/v2_audit_report.md` — structured report:
  ```markdown
  ## Audit Summary
  - Items reviewed: 100
  - Items flagged: N
  - Critical issues: N
  - Warnings: N

  ## Critical Issues (must fix before commit)
  1. [cal_NNN] ...

  ## Warnings (should fix, orchestrator discretion)
  1. [cal_NNN] ...

  ## Gold Answer Spot-Checks
  | Item | Gold Answer | Verified? | Source |
  |------|-----------|-----------|--------|
  | cal_NNN | ... | YES/NO/UNCERTAIN | ... |

  ## Alias Stress Tests
  | Item | Test Input | Expected | Actual | Pass? |
  |------|-----------|----------|--------|-------|
  | cal_NNN | ... | correct | ... | YES/NO |

  ## Distribution Verification
  (Confirm difficulty, domain, answer_type distributions match plan)

  ## SOUL.md Compliance
  - [ ] No new families added
  - [ ] No narrative fields scored
  - [ ] No dataset scope expansion beyond current phase
  - [ ] No quota-spending code without justification
  ```

**What this agent does NOT do:**
- Does not modify the selected items (flags only, Orchestrator fixes)
- Does not re-run the selection process
- Does not interact with other agents directly

**Key instructions for the agent:**
- **Be adversarial.** Your job is to find problems, not confirm everything is fine.
- For gold answer verification: use web search to independently verify at least 15 items, prioritizing:
  - All adversarial items (15)
  - 5 random deceptive items
  - Any item where the answer feels surprising or counter-intuitive
- For alias stress tests: for each sampled item, try 2–3 plausible model outputs and check if the grading system would handle them correctly
- For difficulty verification: flag any "hard" item that seems like straightforward recall, any "deceptive" item where the correct answer is widely known online
- If you find more than 5 critical issues: recommend the Orchestrator send items back to the Strategist for re-selection

**Duration estimate:** 15–20 minutes

---

## 2. Orchestrator Protocol

### 2.1 Role

The Orchestrator (main agent) owns:
- Sprint sequencing — which agent runs when
- File integrity — merging outputs into production files
- Git operations — all commits and pushes
- Decision authority — resolving agent disagreements
- Human communication — all status updates to the user

### 2.2 Execution sequence

```
Step 1: Orchestrator launches Harvester
   → Wait for v2_raw_candidates.json
   → Spot-check: ≥200 candidates? Sources diverse? Schema correct?
   → If issues: reply to Harvester with corrections
   → If good: proceed

Step 2: Orchestrator launches Formatter
   → Pass path to v2_raw_candidates.json
   → Wait for v2_canonicalized_candidates.json + v2_alias_ledger.json
   → Spot-check: format_pass rate? Alias coverage? Schema correct?
   → If issues: reply to Formatter with corrections
   → If good: proceed

Step 3: Orchestrator launches Strategist
   → Pass paths to canonicalized candidates + alias ledger
   → Wait for v2_selected_100.json + v2_rejection_log.json + v2_selection_summary.md
   → Spot-check: exactly 100? Distribution matches plan? All gates passed?
   → If issues: reply to Strategist with corrections
   → If good: proceed

Step 4: Orchestrator launches Auditor
   → Pass paths to selected 100 + alias ledger + selection summary
   → Wait for v2_audit_report.md
   → Review critical issues
   → If critical issues found: fix directly or send back to relevant agent
   → If clean: proceed to assembly

Step 5: Orchestrator assembles production files
   → Build calibration.csv (100 items)
   → Build calibration_answer_key.json (100 specs)
   → Build calibration_provenance.csv (100 records)
   → Update metajudge_submission.ipynb (embed dataset)
   → Run pytest — all tests must pass
   → Commit and push

Step 6: Report to user
   → Share final files
   → Summarize key decisions
   → Provide Kaggle upload instructions for 5-model sweep
```

### 2.3 Error handling

| Situation | Action |
|-----------|--------|
| Agent produces malformed JSON | Reply to agent with error details, ask to fix |
| Agent produces < minimum candidate count | Reply to agent, point to specific source gaps |
| Strategist can't fill a difficulty bucket | Orchestrator adjusts targets (±3 per bucket allowed) |
| Auditor finds > 5 critical issues | Send flagged items back to Strategist for replacement |
| Auditor finds gold answer is wrong | Orchestrator fixes directly using web search |
| Agent diverges from SOUL.md | Orchestrator overrides, documents divergence |
| Any file write conflict | Never happens — agents write to different files |

### 2.4 Budget guardrails

- No agent should make API calls to external LLM services
- No agent should run code that costs Kaggle quota
- All verification is done via web search and local computation
- Estimated total orchestrator cost: ~20–30 minutes of agent time across all phases

---

## 3. File Flow Diagram

```
Phase 1-2 (Harvester):
  READS:  unified_candidate_pool.json, calibration.csv
  WRITES: v2_raw_candidates.json

Phase 3 (Formatter):
  READS:  v2_raw_candidates.json, calibration.csv, calibration_answer_key.json
  WRITES: v2_canonicalized_candidates.json, v2_alias_ledger.json

Phase 4 (Strategist):
  READS:  v2_canonicalized_candidates.json, v2_alias_ledger.json
  WRITES: v2_selected_100.json, v2_rejection_log.json, v2_selection_summary.md

Phase 4b (Auditor):
  READS:  v2_selected_100.json, v2_alias_ledger.json, v2_selection_summary.md
  WRITES: v2_audit_report.md

Phase 5 (Orchestrator):
  READS:  v2_selected_100.json, v2_alias_ledger.json, v2_audit_report.md
  WRITES: calibration.csv, calibration_answer_key.json, calibration_provenance.csv,
          metajudge_submission.ipynb
```

All intermediate files live in `data/harvest/`. Production files live in `data/` and `notebooks/`.

No agent writes to another agent's output files. The Orchestrator is the only agent that writes to production files.

---

## 4. Agent Spawn Templates

### 4.1 Harvester spawn

```
task_name: "Harvest V2 candidates"
subagent_type: "research"
preload_skills: ["research-assistant"]
objective: |
  You are the Harvester agent for the MetaJudge-AGI expansion sprint.
  
  Read the sprint plan at /home/user/workspace/metajudge-agi/planning/expansion_sprint_v2.md (§2).
  Read the dataset construction plan at /home/user/workspace/metajudge-agi/planning/dataset_construction_plan.md.
  
  Your job: gather 200+ raw candidate questions from these sources:
  1. Humanity's Last Exam (HLE) — download from HuggingFace cais/hle, filter short-answer only
  2. FermiEval / Science Olympiad — github.com/landy8697/open-scioly-fermi/
  3. SimpleQA Verified — check availability, download if accessible
  4. Existing pool at /home/user/workspace/metajudge-agi/data/harvest/unified_candidate_pool.json — upgrade items that could be harder
  5. Author 40-50 new items: multi-step reasoning, modified misconceptions, adversarial confabulation
  
  For authored items, every deceptive/adversarial item MUST include plausible_wrong_answer and reasoning_chain.
  
  Output: /home/user/workspace/metajudge-agi/data/harvest/v2_raw_candidates.json
  Schema per item: {prompt, gold_answer, difficulty, item_family, source, answer_type, plausible_wrong_answer, reasoning_chain, note, raw_id}
  
  Dedup against the existing 20 pilot items in /home/user/workspace/metajudge-agi/data/calibration.csv.
```

### 4.2 Formatter spawn

```
task_name: "Canonicalize V2 candidates"
subagent_type: "general_purpose"
objective: |
  You are the Formatter agent for the MetaJudge-AGI expansion sprint.
  
  Read /home/user/workspace/metajudge-agi/planning/multi_agent_coordination.md §1.2 for your full spec.
  Read /home/user/workspace/metajudge-agi/planning/dataset_construction_plan.md §8 for hard rules.
  Read /home/user/workspace/metajudge-agi/planning/scoring_plan.md §4 for adjudication standard.
  Reference /home/user/workspace/metajudge-agi/data/calibration_answer_key.json for format examples.
  
  Input: /home/user/workspace/metajudge-agi/data/harvest/v2_raw_candidates.json
  
  Your job:
  1. Normalize all prompts to "Answer with [format] only." ending
  2. Normalize gold answers (lowercase, strip, digits for numeric)
  3. Build alias ledger for every item
  4. Assign answer_type, grader_rule, format_instruction
  5. Flag items failing format gates
  6. Dedup against pilot at /home/user/workspace/metajudge-agi/data/calibration.csv
  
  Outputs:
  - /home/user/workspace/metajudge-agi/data/harvest/v2_canonicalized_candidates.json
  - /home/user/workspace/metajudge-agi/data/harvest/v2_alias_ledger.json
```

### 4.3 Strategist spawn

```
task_name: "Select final 100 items"
subagent_type: "general_purpose"
objective: |
  You are the Strategist agent for the MetaJudge-AGI expansion sprint.
  
  Read /home/user/workspace/metajudge-agi/planning/multi_agent_coordination.md §1.3 for your full spec.
  Read /home/user/workspace/metajudge-agi/planning/expansion_sprint_v2.md §1 for target distribution.
  Read /home/user/workspace/metajudge-agi/SOUL.md — this is the final authority.
  
  Input:
  - /home/user/workspace/metajudge-agi/data/harvest/v2_canonicalized_candidates.json
  - /home/user/workspace/metajudge-agi/data/harvest/v2_alias_ledger.json
  
  Select exactly 100 items: 10 easy, 20 medium, 30 hard, 25 deceptive, 15 adversarial.
  Assign example_id as cal_001 through cal_100.
  
  Hard constraints:
  - yes/no items ≤ 20 items total
  - no single item_family > 25 items
  - every deceptive item needs plausible_wrong_answer
  - every adversarial item needs confabulation trigger
  - no items with format_pass: false
  
  Outputs:
  - /home/user/workspace/metajudge-agi/data/harvest/v2_selected_100.json
  - /home/user/workspace/metajudge-agi/data/harvest/v2_rejection_log.json
  - /home/user/workspace/metajudge-agi/data/harvest/v2_selection_summary.md
```

### 4.4 Auditor spawn

```
task_name: "Audit selected items"
subagent_type: "research"
preload_skills: ["research-assistant"]
objective: |
  You are the Auditor agent for the MetaJudge-AGI expansion sprint.
  
  Read /home/user/workspace/metajudge-agi/planning/multi_agent_coordination.md §1.4 for your full spec.
  Read /home/user/workspace/metajudge-agi/SOUL.md — check for violations.
  
  Input:
  - /home/user/workspace/metajudge-agi/data/harvest/v2_selected_100.json
  - /home/user/workspace/metajudge-agi/data/harvest/v2_alias_ledger.json
  - /home/user/workspace/metajudge-agi/data/harvest/v2_selection_summary.md
  
  Your job:
  1. Verify ALL 100 items pass format gates
  2. Spot-check aliases: pick 15 items, try to break the alias coverage
  3. Verify gold answers: search the web to verify at least 15 items (all adversarial + 5 deceptive)
  4. Check for near-duplicates within the 100
  5. Flag any item labeled "hard" that is actually easy recall
  6. Flag any deceptive item where the correction is a well-known internet meme
  7. Verify distribution matches the plan
  8. Check SOUL.md compliance
  
  Output: /home/user/workspace/metajudge-agi/data/harvest/v2_audit_report.md
  
  Be adversarial. Your job is to find problems, not confirm everything is fine.
```

---

## 5. Decision Authority Matrix

| Decision | Authority | Escalation |
|----------|-----------|------------|
| Item format (prompt wording, answer normalization) | Formatter | Orchestrator |
| Item selection / rejection | Strategist | Orchestrator |
| Gold answer correctness disputes | Auditor flags → Orchestrator resolves via search | Human (if ambiguous) |
| Difficulty label assignment | Strategist (based on Harvester's initial label) | Orchestrator |
| Alias coverage adequacy | Formatter creates → Auditor validates | Orchestrator |
| Distribution target adjustments (±3 per bucket) | Orchestrator | Human (if > ±3) |
| SOUL.md compliance | Auditor flags → Orchestrator enforces | Human (if genuine conflict) |
| Final commit / push | Orchestrator only | — |
| Kaggle upload | Human only | — |

---

## 6. Failure Modes & Recovery

| Failure Mode | Detection | Recovery |
|---|---|---|
| HLE dataset unavailable or wrong format | Harvester reports empty yield | Orchestrator adjusts: increase authored items, rely more on existing pool |
| Harvester produces < 200 candidates | Orchestrator counts on receipt | Reply to Harvester with specific gaps; if unfixable, proceed with reduced pool |
| Formatter breaks too many prompts (> 30% format_fail) | Orchestrator checks format_pass rate | Reply to Formatter with examples of good rewrites; worst case, Orchestrator fixes manually |
| Strategist can't fill adversarial bucket (15 items) | Strategist reports in selection_summary | Orchestrator allows ±3 adjustment; if still short, author additional items directly |
| Auditor finds gold answer is wrong | Audit report flags it | Orchestrator verifies via search; if confirmed wrong, fix or replace before commit |
| Auditor finds > 5 critical issues | Audit report summary | Orchestrator sends flagged items back to Strategist for replacement picks |
| Any agent writes to wrong file | Shouldn't happen — each agent writes to unique files | Orchestrator manually resolves |

---

## 7. Timing Estimates

| Phase | Agent | Est. Duration | Blocking? |
|-------|-------|---------------|-----------|
| 1–2 | Harvester | 20–30 min | Yes — all others wait |
| 3 | Formatter | 15–20 min | Yes — Strategist waits |
| 4 | Strategist | 15–20 min | Yes — Auditor waits |
| 4b | Auditor | 15–20 min | Yes — Assembly waits |
| 5 | Orchestrator | 10–15 min | — |
| **Total** | | **75–105 min** | |

**Note:** Phases cannot be parallelized because each depends on the previous output. The Auditor could theoretically run in parallel with assembly, but it's safer to wait for audit results before committing.

---

## 8. Post-Sprint Checklist

Before the Orchestrator declares the sprint complete:

- [ ] `data/calibration.csv` has exactly 100 rows (+ header)
- [ ] `data/calibration_answer_key.json` has entries for all 100 example_ids
- [ ] `data/calibration_provenance.csv` has entries for all 100 example_ids
- [ ] `notebooks/metajudge_submission.ipynb` embeds the full 100-item dataset
- [ ] `pytest tests/` — all tests pass
- [ ] Difficulty distribution matches V2 targets (±3 per bucket)
- [ ] Yes/no items ≤ 20% of total
- [ ] No single item_family > 25% of total
- [ ] Audit report has 0 unresolved critical issues
- [ ] All intermediate files in `data/harvest/` are committed
- [ ] Git status is clean, pushed to origin/main
- [ ] User has been briefed on key decisions and ready for Kaggle upload
