"""Tests for the metajudge.eval package — logging, diagnostics, export."""
import json
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from metajudge.eval.diagnostics import (
    _json_safe,
    compute_discrimination,
    compute_model_summary,
    compute_success_criteria,
    export_artifacts,
)
from metajudge.eval.export import headline_results_to_df, sweep_results_to_audit_df
from metajudge.eval.logging import log_run


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def synthetic_audit_df():
    """Create a synthetic audit DataFrame with 21 rows across 3 models."""
    items = [
        ("q01", "RLHF"),
        ("q02", "IOED"),
        ("q03", "Compositional"),
        ("q04", "AmbiguityMetacognition"),
        ("q05", "Anchoring"),
        ("q06", "Prototype"),
        ("q07", "ModifiedCRT"),
    ]
    rows = []
    for model_idx, model in enumerate(["model_a", "model_b", "model_c"]):
        for i, (item_id, mech) in enumerate(items):
            # Vary correctness and confidence across models to create disagreements
            if model_idx == 0:
                is_correct = i % 2 == 0
                confidence = 0.9 if is_correct else 0.85
            elif model_idx == 1:
                is_correct = i % 3 != 0
                confidence = 0.7
            else:
                is_correct = i < 4
                confidence = 0.6 if is_correct else 0.3
            outcome = 1.0 if is_correct else 0.0
            brier = 1.0 - (confidence - outcome) ** 2
            rows.append({
                "model": model,
                "item_id": item_id,
                "mechanism_primary": mech,
                "model_answer": f"answer_{model}_{item_id}",
                "confidence": confidence,
                "is_correct": is_correct,
                "brier_score": round(brier, 4),
            })
    return pd.DataFrame(rows)


@pytest.fixture
def synthetic_sweep_results():
    """Create a sweep_results dict as produced by notebook Cell 8."""
    return {
        "model_a": [
            {"item_id": "q1", "mechanism_primary": "RLHF", "model_answer": "ans_a1",
             "confidence": 0.9, "is_correct": True, "brier_score": 0.99},
            {"item_id": "q2", "mechanism_primary": "IOED", "model_answer": "ans_a2",
             "confidence": 0.8, "is_correct": False, "brier_score": 0.36},
        ],
        "model_b": [
            {"item_id": "q1", "mechanism_primary": "RLHF", "model_answer": "ans_b1",
             "confidence": 0.5, "is_correct": False, "brier_score": 0.75},
            {"item_id": "q2", "mechanism_primary": "IOED", "model_answer": "ans_b2",
             "confidence": 0.6, "is_correct": True, "brier_score": 0.84},
        ],
    }


# ---------------------------------------------------------------------------
# _json_safe
# ---------------------------------------------------------------------------

class TestJsonSafe:
    def test_numpy_bool(self):
        assert _json_safe(np.bool_(True)) is True
        assert _json_safe(np.bool_(False)) is False

    def test_numpy_int(self):
        assert _json_safe(np.int64(42)) == 42
        assert isinstance(_json_safe(np.int64(42)), int)

    def test_numpy_float(self):
        result = _json_safe(np.float64(3.14))
        assert isinstance(result, float)
        assert abs(result - 3.14) < 1e-9

    def test_numpy_array(self):
        assert _json_safe(np.array([1, 2, 3])) == [1, 2, 3]

    def test_pandas_timestamp(self):
        ts = pd.Timestamp("2026-03-20T12:00:00")
        result = _json_safe(ts)
        assert "2026-03-20" in result

    def test_fallback_str(self):
        assert _json_safe({"key": "val"}) == "{'key': 'val'}"


# ---------------------------------------------------------------------------
# compute_model_summary
# ---------------------------------------------------------------------------

class TestComputeModelSummary:
    def test_returns_one_row_per_model(self, synthetic_audit_df):
        summary = compute_model_summary(synthetic_audit_df)
        assert len(summary) == 3

    def test_expected_columns(self, synthetic_audit_df):
        summary = compute_model_summary(synthetic_audit_df)
        expected = {
            "model", "n_items", "correct", "accuracy", "headline_score",
            "mean_confidence", "ece", "overconfidence_rate", "overconfident_wrong",
        }
        assert set(summary.columns) == expected

    def test_n_items_per_model(self, synthetic_audit_df):
        summary = compute_model_summary(synthetic_audit_df)
        assert all(summary["n_items"] == 7)

    def test_accuracy_in_range(self, synthetic_audit_df):
        summary = compute_model_summary(synthetic_audit_df)
        assert all(0 <= a <= 1 for a in summary["accuracy"])


# ---------------------------------------------------------------------------
# compute_discrimination
# ---------------------------------------------------------------------------

class TestComputeDiscrimination:
    def test_finds_disagreement_items(self, synthetic_audit_df):
        disc = compute_discrimination(synthetic_audit_df)
        assert len(disc) > 0

    def test_expected_columns(self, synthetic_audit_df):
        disc = compute_discrimination(synthetic_audit_df)
        expected = {"item_id", "n_models", "n_correct", "n_wrong",
                    "models_correct", "models_wrong"}
        assert set(disc.columns) == expected

    def test_no_unanimous_items_in_result(self, synthetic_audit_df):
        disc = compute_discrimination(synthetic_audit_df)
        for _, row in disc.iterrows():
            assert 0 < row["n_correct"] < row["n_models"]

    def test_empty_on_unanimous(self):
        df = pd.DataFrame([
            {"model": "a", "item_id": "q1", "is_correct": True, "confidence": 0.9, "brier_score": 0.99},
            {"model": "b", "item_id": "q1", "is_correct": True, "confidence": 0.8, "brier_score": 0.96},
        ])
        disc = compute_discrimination(df)
        assert len(disc) == 0


# ---------------------------------------------------------------------------
# compute_success_criteria
# ---------------------------------------------------------------------------

class TestComputeSuccessCriteria:
    def test_returns_proper_structure(self, synthetic_audit_df):
        verdict = compute_success_criteria(synthetic_audit_df)
        assert "criteria" in verdict
        assert "verdict" in verdict
        assert "total_pass" in verdict
        assert "total_criteria" in verdict
        assert verdict["total_criteria"] == 5

    def test_all_criteria_present(self, synthetic_audit_df):
        verdict = compute_success_criteria(synthetic_audit_df)
        for key in ["C1", "C2", "C3", "C4", "C5"]:
            assert key in verdict["criteria"]
            crit = verdict["criteria"][key]
            assert "name" in crit
            assert "threshold" in crit
            assert "measured" in crit
            assert "pass" in crit

    def test_verdict_is_valid(self, synthetic_audit_df):
        verdict = compute_success_criteria(synthetic_audit_df)
        assert verdict["verdict"] in ("FREEZE", "REPLACE", "NEEDS_WORK")

    def test_total_pass_consistent(self, synthetic_audit_df):
        verdict = compute_success_criteria(synthetic_audit_df)
        n_pass = sum(1 for c in verdict["criteria"].values() if c["pass"])
        assert verdict["total_pass"] == n_pass


# ---------------------------------------------------------------------------
# export_artifacts
# ---------------------------------------------------------------------------

class TestExportArtifacts:
    def test_writes_files(self, synthetic_audit_df):
        with tempfile.TemporaryDirectory() as tmpdir:
            paths = export_artifacts(synthetic_audit_df, output_dir=tmpdir, tag="test")
            assert "per_item_audit" in paths
            assert "model_summary" in paths
            assert "verdict" in paths
            for path in paths.values():
                assert Path(path).exists()

    def test_audit_csv_shape(self, synthetic_audit_df):
        with tempfile.TemporaryDirectory() as tmpdir:
            paths = export_artifacts(synthetic_audit_df, output_dir=tmpdir, tag="test")
            loaded = pd.read_csv(paths["per_item_audit"])
            assert len(loaded) == len(synthetic_audit_df)

    def test_verdict_json_valid(self, synthetic_audit_df):
        with tempfile.TemporaryDirectory() as tmpdir:
            paths = export_artifacts(synthetic_audit_df, output_dir=tmpdir, tag="test")
            with open(paths["verdict"]) as f:
                verdict = json.load(f)
            assert "criteria" in verdict
            assert verdict["total_criteria"] == 5


# ---------------------------------------------------------------------------
# sweep_results_to_audit_df
# ---------------------------------------------------------------------------

class TestSweepResultsToAuditDf:
    def test_correct_row_count(self, synthetic_sweep_results):
        df = sweep_results_to_audit_df(synthetic_sweep_results)
        assert len(df) == 4

    def test_has_model_column(self, synthetic_sweep_results):
        df = sweep_results_to_audit_df(synthetic_sweep_results)
        assert "model" in df.columns
        assert set(df["model"]) == {"model_a", "model_b"}

    def test_preserves_fields(self, synthetic_sweep_results):
        df = sweep_results_to_audit_df(synthetic_sweep_results)
        assert "item_id" in df.columns
        assert "brier_score" in df.columns
        assert "is_correct" in df.columns


# ---------------------------------------------------------------------------
# headline_results_to_df
# ---------------------------------------------------------------------------

class TestHeadlineResultsToDf:
    def test_converts_dict_to_df(self):
        results = {
            "model_a": {"headline_score": 0.85, "n_items": 102},
            "model_b": {"headline_score": 0.78, "n_items": 102},
        }
        df = headline_results_to_df(results)
        assert len(df) == 2
        assert "model" in df.columns
        assert "headline_score" in df.columns


# ---------------------------------------------------------------------------
# log_run
# ---------------------------------------------------------------------------

class TestLogRun:
    def test_writes_jsonl(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            record = log_run(
                run_type="test",
                model_name="test_model",
                n_items=10,
                headline_score=0.85,
                accuracy=0.7,
                mean_confidence=0.75,
                output_dir=tmpdir,
            )
            assert record["model"] == "test_model"
            assert record["headline_score"] == 0.85

            log_path = Path(tmpdir) / "run_log.jsonl"
            assert log_path.exists()
            with open(log_path) as f:
                line = json.loads(f.readline())
            assert line["run_type"] == "test"

    def test_appends_multiple(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            log_run("test", "m1", 10, 0.8, 0.7, 0.75, output_dir=tmpdir)
            log_run("test", "m2", 10, 0.9, 0.8, 0.85, output_dir=tmpdir)
            log_path = Path(tmpdir) / "run_log.jsonl"
            lines = log_path.read_text().strip().split("\n")
            assert len(lines) == 2

    def test_optional_fields(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            record = log_run(
                run_type="test",
                model_name="m1",
                n_items=10,
                headline_score=0.8,
                accuracy=0.7,
                mean_confidence=0.75,
                ece=0.05,
                overconfidence_rate=0.1,
                output_dir=tmpdir,
                extra={"custom_key": "custom_val"},
            )
            assert record["ece"] == 0.05
            assert record["overconfidence_rate"] == 0.1
            assert record["custom_key"] == "custom_val"
