"""Run logging for MetaJudge evaluation experiments."""
import json
import hashlib
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


def get_git_commit() -> str:
    """Get current git commit SHA, or 'unknown' if not in a repo."""
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            stderr=subprocess.DEVNULL
        ).decode().strip()
    except Exception:
        return "unknown"


def dataset_hash(path: str | Path) -> str:
    """SHA256 hash of the dataset file (first 12 chars)."""
    h = hashlib.sha256(Path(path).read_bytes()).hexdigest()
    return h[:12]


def log_run(
    run_type: str,
    model_name: str,
    n_items: int,
    headline_score: float,
    accuracy: float,
    mean_confidence: float,
    ece: Optional[float] = None,
    overconfidence_rate: Optional[float] = None,
    output_dir: str | Path = "outputs",
    dataset_path: Optional[str] = None,
    extra: Optional[dict] = None,
) -> dict:
    """Log a single model run to outputs/run_log.jsonl.

    Returns the logged record.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "git_commit": get_git_commit(),
        "dataset_hash": dataset_hash(dataset_path) if dataset_path else None,
        "run_type": run_type,
        "model": model_name,
        "n_items": n_items,
        "headline_score": round(headline_score, 4),
        "accuracy": round(accuracy, 4),
        "mean_confidence": round(mean_confidence, 4),
        "ece": round(ece, 4) if ece is not None else None,
        "overconfidence_rate": round(overconfidence_rate, 4) if overconfidence_rate is not None else None,
    }
    if extra:
        record.update(extra)

    log_path = output_dir / "run_log.jsonl"
    with open(log_path, "a") as f:
        f.write(json.dumps(record) + "\n")

    return record
