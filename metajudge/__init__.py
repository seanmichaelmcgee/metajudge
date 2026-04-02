"""
MetaJudge-AGI: A Behavioral Benchmark for Metacognition in Frontier Models
============================================================================

A benchmark suite for the Kaggle "Measuring Progress Toward AGI - Cognitive Abilities"
competition, focused on evaluating metacognition through behavioral evidence.

Three families:
- Confidence Calibration (Family A) — Brier scoring, 8-rule grading engine
- Selective Abstention (Family B) — UWAA, utility matrix
- Self-Correction (Family C) — Transition scoring, C1 intrinsic + C2 evidence-assisted

Design principle: Score metacognition by the consequences of self-monitoring
on task behavior, not by what the model says about itself.
"""

__version__ = "4.1"
__benchmark_name__ = "metacognition_behavioral_suite_v4"
