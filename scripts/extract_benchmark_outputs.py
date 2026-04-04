#!/usr/bin/env python3
"""Extract benchmark notebook outputs from Kaggle.

Downloads all output files for MetaJudge 6 benchmark runs.
Requires Kaggle credentials (~/.kaggle/kaggle.json or KAGGLE_USERNAME/KAGGLE_KEY env vars).

Usage:
    python scripts/extract_benchmark_outputs.py

Or to extract a single notebook:
    python scripts/extract_benchmark_outputs.py --slug seanmcgee2025/metajudge-calibration-v62
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

# All notebook slugs for the MetaJudge 6 benchmark
# Format: {task_version: notebook_slug}
NOTEBOOK_SLUGS = {
    "calibration_v61": "seanmcgee2025/metajudge-calibration-v61",
    "abstention_v61": "seanmcgee2025/metajudge-abstention-v61",
    "sc_c1_v61": "seanmcgee2025/metajudge-self-correction-c1-v61",
    "sc_c2_v61": "seanmcgee2025/metajudge-self-correction-c2-v61",
    "calibration_v62": "seanmcgee2025/metajudge-calibration-v62",
    "abstention_v62": "seanmcgee2025/metajudge-abstention-v62",
    "sc_c1_v62": "seanmcgee2025/metajudge-self-correction-c1-v62",
    "sc_c2_v62": "seanmcgee2025/metajudge-self-correction-c2-v62",
}

OUTPUT_BASE = Path("outputs/benchmark_runs")


def extract_notebook(slug, output_dir):
    """Download outputs for a single notebook using kaggle CLI."""
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"Extracting: {slug}")
    print(f"  → {output_dir}")

    try:
        result = subprocess.run(
            ["kaggle", "kernels", "output", slug, "-p", str(output_dir)],
            capture_output=True, text=True, timeout=120
        )
        if result.returncode == 0:
            files = list(output_dir.iterdir())
            print(f"  ✓ Downloaded {len(files)} files")
            for f in sorted(files):
                print(f"    {f.name} ({f.stat().st_size / 1024:.1f} KB)")
            return True
        else:
            print(f"  ✗ Failed: {result.stderr.strip()[:200]}")
            return False
    except subprocess.TimeoutExpired:
        print(f"  ✗ Timeout (120s)")
        return False
    except FileNotFoundError:
        print(f"  ✗ kaggle CLI not found. Install: pip install kaggle")
        return False


def extract_all():
    """Download outputs for all benchmark notebooks."""
    print("MetaJudge 6 — Benchmark Output Extraction")
    print(f"Output directory: {OUTPUT_BASE}")

    results = {}
    for task_ver, slug in NOTEBOOK_SLUGS.items():
        output_dir = OUTPUT_BASE / task_ver
        success = extract_notebook(slug, output_dir)
        results[task_ver] = success

    # Summary
    print(f"\n{'='*60}")
    print("Summary:")
    for task_ver, success in results.items():
        print(f"  {'✓' if success else '✗'} {task_ver}")

    succeeded = sum(results.values())
    print(f"\n{succeeded}/{len(results)} notebooks extracted successfully.")

    if succeeded < len(results):
        print("\nFor failed extractions, try:")
        print("  1. Check credentials: kaggle config view")
        print("  2. Download manually from Kaggle UI")
        print("  3. Ensure notebook slugs are correct")


def main():
    parser = argparse.ArgumentParser(description="Extract MetaJudge benchmark outputs")
    parser.add_argument("--slug", help="Extract a single notebook by slug")
    parser.add_argument("--output-dir", default=str(OUTPUT_BASE),
                        help="Base output directory")
    args = parser.parse_args()

    global OUTPUT_BASE
    OUTPUT_BASE = Path(args.output_dir)

    if args.slug:
        # Single notebook
        name = args.slug.split("/")[-1]
        extract_notebook(args.slug, OUTPUT_BASE / name)
    else:
        # All notebooks
        extract_all()


if __name__ == "__main__":
    main()
