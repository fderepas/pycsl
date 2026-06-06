"""Report generator — produces JSON and console summaries."""

import json
import os
from typing import List
from datetime import datetime


def generate_report(verdicts: list, report_dir: str) -> str:
    """Generate a JSON report and print a console summary.
    
    Returns the path to the JSON report.
    """
    # Console summary
    counts = {}
    for v in verdicts:
        counts[v.classification] = counts.get(v.classification, 0) + 1

    total = len(verdicts)
    print("\n" + "=" * 70)
    print("  PyCSL DUAL-ORACLE COMPLIANCE TEST REPORT")
    print("=" * 70)
    print(f"  Total tests: {total}")
    print()

    order = ["SUCCESS", "EXPECTED_FAIL", "FALSE_POSITIVE",
             "SOUNDNESS_BUG", "STATIC_PASS", "STATIC_FAIL",
             "DYNAMIC_PASS", "DYNAMIC_FAIL",
             "STATIC_ERROR", "DYNAMIC_ERROR",
             "BOTH_ERROR", "SKIP", "UNKNOWN"]
    for cls in order:
        if cls in counts:
            marker = "✓" if cls in ("SUCCESS", "EXPECTED_FAIL",
                                     "STATIC_PASS", "DYNAMIC_PASS") else "✗"
            if cls in ("SKIP", "FALSE_POSITIVE"):
                marker = "○"
            print(f"  {marker} {cls:20s} {counts[cls]:3d}")

    soundness_bugs = [v for v in verdicts if v.classification == "SOUNDNESS_BUG"]
    if soundness_bugs:
        print()
        print("  ⚠ SOUNDNESS BUGS DETECTED:")
        for v in soundness_bugs:
            print(f"    - {v.filepath}: {v.detail}")

    print("=" * 70)

    # Detailed per-file results
    print("\nPer-file results:")
    for v in verdicts:
        sym = {"SUCCESS": "✓", "EXPECTED_FAIL": "~", "FALSE_POSITIVE": "?",
               "SOUNDNESS_BUG": "!", "SKIP": "○",
               "STATIC_PASS": "✓", "DYNAMIC_PASS": "✓",
               "STATIC_FAIL": "✗", "DYNAMIC_FAIL": "✗"
               }.get(v.classification, "✗")
        fname = os.path.basename(v.filepath)
        static = v.static_result
        dynamic = v.dynamic_result
        print(f"  {sym} {fname:45s}  static={static:5s}  dynamic={dynamic:5s}  → {v.classification}")

    # JSON report
    os.makedirs(report_dir, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = os.path.join(report_dir, f"report_{ts}.json")

    report_data = {
        "timestamp": datetime.now().isoformat(),
        "total": total,
        "summary": counts,
        "verdicts": [
            {
                "filepath": v.filepath,
                "static": v.static_result,
                "dynamic": v.dynamic_result,
                "classification": v.classification,
                "detail": v.detail,
            }
            for v in verdicts
        ]
    }

    with open(report_path, 'w') as f:
        json.dump(report_data, f, indent=2)

    print(f"\nJSON report: {report_path}")
    return report_path
