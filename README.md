# MetaJudge-AGI

**A Behavioral Benchmark for Metacognition in Frontier Models**

Competition: [Kaggle — Measuring Progress Toward AGI: Cognitive Abilities](https://www.kaggle.com/competitions/kaggle-measuring-agi)

## Overview

MetaJudge-AGI evaluates whether frontier models can accurately assess and regulate the reliability of their own cognition — not merely produce correct answers. The benchmark measures five dimensions of metacognition through behavioral evidence:

| Module | What It Tests | Framework Section |
|--------|---------------|-------------------|
| A. Confidence Calibration | Stated confidence vs actual correctness | §5.1 |
| B. Selective Abstention | Knowing when not to answer | §5.2 |
| C. Error Detection & Self-Correction | Identifying and fixing own errors | §5.3 |
| D. Source Awareness | Distinguishing memory, inference, guessing | §5.4 |
| E. Strategy Adaptation | Choosing and changing solution approaches | §5.5 |

## Design Principle

> Score metacognition by the consequences of self-monitoring on task behavior, not by what the model says about itself.

## Repository Structure

```
metajudge-agi/
├── metajudge/                  # Core Python package
│   ├── tasks/                  # Task family implementations (A-E)
│   ├── scoring/                # Metrics for each dimension
│   ├── schemas/                # Pydantic response schemas
│   ├── evaluation/             # Runner and Kaggle integration
│   ├── anti_gaming/            # Anti-gaming countermeasures
│   └── utils/                  # Shared utilities
├── data/                       # Task datasets
│   ├── raw_tasks/              # Hand-authored items
│   ├── processed_tasks/        # Validated and enriched items
│   ├── splits/                 # Public/private/pilot splits
│   └── prototypes/             # Development examples
├── notebooks/                  # Kaggle submission notebook
├── config/                     # Benchmark configuration
├── scripts/                    # Automation scripts
├── tests/                      # Unit and integration tests
├── planning/                   # Project management artifacts
│   ├── backlog/                # Task backlog
│   ├── decisions/              # Architecture decisions
│   └── verification/           # Unknowns and risk log
├── docs/                       # Documentation
└── logs/                       # Execution logs
```

## Scoring

Composite score = weighted combination of five sub-benchmarks:

- **25%** Confidence Calibration (Brier score, ECE, overconfidence penalty)
- **20%** Selective Abstention (utility-based reward, risk-coverage)
- **20%** Error Detection & Self-Correction (revision quality, confidence direction)
- **15%** Source Awareness (source-label accuracy, span alignment)
- **20%** Strategy Adaptation (selection accuracy, improvement after change)

## Anti-Gaming

Eight countermeasures from Framework §8: behavior-first scoring, hidden optimal-action classes, prompt variation, decoy confidence cues, symmetric correction, source-label adversarial items, cross-template splits, verbosity independence.

## Status

- [x] Framework specification
- [x] Implementation plan
- [x] Notebook sketch
- [x] Repository bootstrap
- [x] Schema definitions
- [x] Scoring module stubs
- [x] Task module stubs
- [ ] Full dataset authoring (500-1500 items)
- [ ] Complete scoring implementation
- [ ] Kaggle SDK integration verification
- [ ] Anti-gaming hardening
- [ ] Pilot evaluation
- [ ] Final submission

## Source Documents

1. `metacognition_kaggle_benchmark_framework.md` — Conceptual framework
2. `metacognition_kaggle_implementation_plan.md` — Implementation timeline
3. `kaggle_metacognition_notebook_sketch.md` — Notebook scaffold

## License

MIT
