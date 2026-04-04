#!/usr/bin/env python3
"""Generate a per-model .docx audit report from MetaJudge v6.1 notebook outputs.

Thin CLI wrapper around metajudge.reporting.audit_docx.generate_audit_report().

Usage:
    python scripts/generate_audit_docx.py \
      --task calibration \
      --audit-csv /path/to/calibration_item_audit_flash2.5_v6.1.csv \
      --responses-json /path/to/calibration_full_responses_flash2.5_v6.1.json \
      --items-json /path/to/metajudge_benchmark_v1.json \
      --registry-json /path/to/adjudication_registry.json \
      --output MetaJudge_Calibration_Flash2.5.docx \
      [--run-json /path/to/run.json] \
      [--justifications-md /path/to/metajudge_v51_gold_answer_justifications.md]

Supports all 4 task types: calibration, abstention, sc_c1, sc_c2.
"""

import argparse
import sys
from pathlib import Path

# Allow running from repo root without PYTHONPATH
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from metajudge.reporting.audit_docx import generate_audit_report


def parse_args():
    p = argparse.ArgumentParser(description="Generate MetaJudge v6.1 audit .docx")
    p.add_argument("--task", required=True,
                   choices=["calibration", "abstention", "sc_c1", "sc_c2"],
                   help="Task type")
    p.add_argument("--audit-csv", required=True, help="Item-level audit CSV")
    p.add_argument("--responses-json", required=True, help="Full responses JSON")
    p.add_argument("--items-json", required=True, help="Benchmark items JSON")
    p.add_argument("--registry-json", required=True, help="Adjudication registry JSON")
    p.add_argument("--output", required=True, help="Output .docx path")
    p.add_argument("--run-json", default=None, help="SDK run.json (optional, for runtime/cost)")
    p.add_argument("--justifications-md", default=None,
                   help="Gold answer justifications markdown (optional)")
    return p.parse_args()


def main():
    args = parse_args()
    print(f"Generating audit report for task: {args.task}")

    output = generate_audit_report(
        task=args.task,
        audit_csv_path=args.audit_csv,
        responses_json_path=args.responses_json,
        items_json_path=args.items_json,
        registry_json_path=args.registry_json,
        output_path=args.output,
        justifications_md_path=args.justifications_md,
        run_json_path=args.run_json,
    )
    print(f"Saved: {output}")


if __name__ == "__main__":
    main()
