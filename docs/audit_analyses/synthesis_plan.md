# Synthesis Plan — MetaJudge v6.2 Pipeline Evaluation

## Mission Statement

> **This synthesis evaluates whether MetaJudge v6.2 produces scores that are transparent, clear, reliable, and useful — and identifies specific improvements for the next benchmark version.**
>
> Every agent in this pipeline receives this mission. The goal is not to defend the benchmark but to scrutinize it honestly: where it works, where it fails, and what to change.

---

## The Four Evaluation Criteria

### 1. Transparency (Are the inner workings easily scrutable?)
- Can a judge trace from a model's answer → grade → score → MetaScore?
- Are the grading rules, accepted forms, and payoff matrix visible and documented?
- Are known bugs and their impact disclosed?

### 2. Clarity (Are scores well explained?)
- Does each task's score have an intuitive meaning a non-specialist can grasp?
- Are the anchor normalization choices justified and explained?
- Is the composite MetaScore interpretable at a glance?

### 3. Reliability (Similar results on different runs, or variability understood?)
- How stable are scores across dual runs (stochasticity)?
- How sensitive are rankings to individual item outcomes?
- Are there floor/ceiling effects that compress discrimination?

### 4. Utility (Can scores inform model design and testing?)
- Does the benchmark separate models meaningfully?
- Does it surface real metacognitive differences (not just accuracy)?
- Can model builders use the results to improve their systems?

---

## Agent Hierarchy

```
ORCHESTRATOR (main thread — holds all context)
│
└── EXEC: Synthesis Director (opus, foreground)
    │   Reads all audit files, produces the unified report.
    │   Delegates to domain specialists for per-task analysis.
    │
    ├── DOMAIN: Calibration Assessment (opus, background)
    │   Evaluates calibration scoring against all 4 criteria.
    │   Inputs: intensive_calibration.md, per-model audits, canonical_dataset.json
    │   Output: synthesis section on calibration
    │
    ├── DOMAIN: Abstention Assessment (opus, background)
    │   Evaluates abstention scoring. Special focus on:
    │   - Partial credit generosity question
    │   - Action accuracy vs UWAA disconnect
    │   - verify action underuse
    │   Output: synthesis section on abstention
    │
    ├── DOMAIN: Self-Correction Assessment (opus, background)
    │   Evaluates C1+C2 scoring. Special focus on:
    │   - Ceiling effects and n-too-small
    │   - Transition scoring vs accuracy delta disconnect
    │   - Deceptive trap discrimination value
    │   Output: synthesis section on C1+C2
    │
    └── DOMAIN: Composite & Cross-Task Assessment (opus, foreground)
        Evaluates the MetaScore composite. Special focus on:
        - Equal-weight validity with actual data
        - Monitoring-control gap as primary signal
        - Cost-performance as secondary dimension
        Output: synthesis section on composite

After all 4 domain sections return:
ORCHESTRATOR assembles into unified report + recommendations.
```

---

## Per-Domain Assessment Structure

Each domain section follows the same 4-criteria structure:

### [Task Name] — Scoring Assessment

**What it measures:** [1 paragraph — what metacognitive ability is tested]

**How it scores:** [Concise mechanics — formula, anchors, grading rules]

**Transparency:**
- Grading pipeline: [audited? accuracy? bugs found?]
- Score traceability: [can you trace answer → grade → score?]
- Documentation: [is the methodology documented?]

**Clarity:**
- Score interpretation: [what does 0.5 mean? what does 0.8 mean?]
- Anchor choice: [are floor/ceiling justified?]
- Edge cases: [are there non-obvious scoring behaviors?]

**Reliability:**
- Stochasticity: [dual-run variance?]
- Item sensitivity: [how much does one item swing the score?]
- Floor/ceiling effects: [do models cluster?]

**Utility:**
- Discrimination: [do scores separate models meaningfully?]
- Diagnostic value: [what does the score tell a model builder?]
- Cross-model patterns: [what did the intensive audit reveal?]

**Bugs and Issues:**
- [List all issues found, severity, status]

**Recommendations for v7:**
- [Specific actionable improvements]

---

## Execution Phases

### Phase S1: Launch 3 domain assessment agents (opus, parallel)
- Calibration, Abstention, SC C1+C2
- Each reads: their intensive audit, all per-model audits, canonical dataset
- Each writes: their section following the structure above
- Max 300 lines each

### Phase S2: Composite assessment (orchestrator, inline)
- Uses the 6-model leaderboard + all domain findings
- Evaluates equal-weight validity, monitoring-control gap, cost-performance
- Writes composite section

### Phase S3: Assemble unified report (orchestrator, inline)
- Combines all 4 sections + executive summary + recommendations
- Writes `docs/audit_analyses/v62_synthesis_report.md`
- Updates `docs/audit_analyses/final_evaluation_report.md`

### Phase S4: Commit + push
- Verbose commit message for session recovery

---

## Inputs Available to All Agents

| File | Content |
|------|---------|
| `docs/audit_analyses/canonical_dataset.json` | 1444 records, all scores, costs |
| `docs/audit_analyses/intensive_calibration.md` | 5 items × 6 models deep analysis |
| `docs/audit_analyses/intensive_abstention.md` | 5 items × 6 models deep analysis |
| `docs/audit_analyses/intensive_self_correction.md` | 10 items × 6 models deep analysis |
| `docs/audit_analyses/intensive_problematic_items.md` | 5 buggy items cross-model |
| `docs/audit_analyses/gemini_pro_v62/` | Deep single-model audit (4 files) |
| `docs/audit_analyses/sonnet46_v62/audit.md` | Deep audit (5 DISAGREE) |
| `docs/audit_analyses/gemini_flash_v62/audit.md` | Deep audit |
| `docs/audit_analyses/gpt54_v62/audit.md` | Deep audit (rr_008 gap) |
| `docs/audit_analyses/gemma26b_v62/audit.md` | Deep audit (parser bug) |
| `docs/audit_analyses/cross_model_audit.md` | 1137 items automated check |
| `docs/scoring_overview.md` | End-to-end scoring explainer |
| `docs/theoretical_backgrounder.md` | Two-process framework |

---

## Mission Prompt (fed to every agent)

```
MISSION: This synthesis evaluates whether MetaJudge v6.2 produces scores
that are transparent, clear, reliable, and useful — and identifies specific
improvements for the next benchmark version. The goal is honest scrutiny,
not defense. Where the benchmark works, explain why. Where it fails,
explain what to change.
```
