"""
MetaJudge-AGI: A Behavioral Benchmark for Metacognition in Frontier Models
============================================================================

A benchmark suite for the Kaggle "Measuring Progress Toward AGI - Cognitive Abilities"
competition, focused on evaluating metacognition through behavioral evidence.

Five sub-benchmarks:
- Confidence Calibration (Framework §5.1)
- Selective Abstention and Deferral (Framework §5.2)
- Error Detection and Targeted Self-Correction (Framework §5.3)
- Source Awareness and Epistemic Attribution (Framework §5.4)
- Strategy Selection and Adaptive Revision (Framework §5.5)

Design principle: Score metacognition by the consequences of self-monitoring
on task behavior, not by what the model says about itself.
"""

__version__ = "0.5.4"
__benchmark_name__ = "metacognition_behavioral_suite_v1"
