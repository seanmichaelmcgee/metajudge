"""MetaJudge-AGI Scoring Package.

Sub-modules:
- calibration_metrics: Brier score, ECE, overconfidence (Framework §5.1.5, §7.2)
- abstention_metrics: Utility matrix, risk-coverage (Framework §5.2.5, §7.2)
- self_correction_metrics: Revision quality, confidence direction (Framework §5.3.4, §7.2)
- source_awareness_metrics: Source-label accuracy, span alignment (Framework §5.4.5, §7.2)
- strategy_metrics: Strategy accuracy, diversity, adaptation (Framework §5.5.4, §7.2)
- composite_score: Weighted aggregation (Framework §7.1, §7.3)
"""
