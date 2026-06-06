#!/usr/bin/env python3
"""PyCSL Dual-Oracle Compliance Test Suite Runner.

Usage:
    python3 run_suite.py                 # run all tests
    python3 run_suite.py --dynamic-only  # skip static oracle (faster)
    python3 run_suite.py --static-only   # skip dynamic oracle
    python3 run_suite.py FILE...         # run specific files
"""

import argparse
import glob
import os
import sys

_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_here, 'runner'))
sys.path.insert(0, os.path.join(_here, 'instrumenter'))
sys.path.insert(0, os.path.join(_here, '..'))

from runner.static_oracle import run_static, StaticResult
from runner.dynamic_oracle import run_dynamic, DynamicResult
from runner.evaluator import evaluate, classify
from runner.report import generate_report


def collect_test_files(paths=None):
    """Collect test .py files from corpus directories or explicit paths."""
    if paths:
        return [os.path.abspath(p) for p in paths if p.endswith('.py')]

    corpus_dirs = [
        os.path.join(_here, 'corpus', 'imported'),
        os.path.join(_here, 'corpus', 'edge_cases'),
        os.path.join(_here, 'corpus', 'negative'),
    ]

    files = []
    for d in corpus_dirs:
        if os.path.isdir(d):
            for f in sorted(os.listdir(d)):
                if f.endswith('.py'):
                    files.append(os.path.join(d, f))
    return files


def main():
    parser = argparse.ArgumentParser(description="PyCSL Compliance Test Suite")
    parser.add_argument('files', nargs='*', help='Specific test files to run')
    parser.add_argument('--dynamic-only', action='store_true',
                        help='Only run dynamic oracle')
    parser.add_argument('--static-only', action='store_true',
                        help='Only run static oracle')
    parser.add_argument('--timeout', type=int, default=30,
                        help='Per-test timeout in seconds')
    args = parser.parse_args()

    test_files = collect_test_files(args.files or None)
    if not test_files:
        print("No test files found. Add .py files to corpus/ directories.")
        sys.exit(1)

    print(f"[*] Running {len(test_files)} test(s)...")
    verdicts = []

    for filepath in test_files:
        fname = os.path.basename(filepath)
        print(f"\n  Testing: {fname}")

        # Determine if this is a negative test (expected to fail)
        is_negative = 'negative' in filepath

        # Static oracle
        if not args.dynamic_only:
            print(f"    Static oracle...", end=" ", flush=True)
            static = run_static(filepath, timeout=args.timeout)
            print(static.overall)
        else:
            static = StaticResult(filepath=filepath, overall="SKIP")

        # Dynamic oracle
        if not args.static_only:
            print(f"    Dynamic oracle...", end=" ", flush=True)
            dynamic = run_dynamic(filepath, timeout=args.timeout)
            print(dynamic.overall)
        else:
            dynamic = DynamicResult(filepath=filepath, overall="SKIP")

        verdict = evaluate(filepath, static, dynamic)
        verdicts.append(verdict)

    # Generate report
    report_dir = os.path.join(_here, 'reports')
    report_path = generate_report(verdicts, report_dir)

    # Exit code: 2 if any soundness bugs, 1 if errors, 0 otherwise
    has_soundness = any(v.classification == "SOUNDNESS_BUG" for v in verdicts)
    has_errors = any("ERROR" in v.classification for v in verdicts)

    if has_soundness:
        sys.exit(2)
    elif has_errors:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
