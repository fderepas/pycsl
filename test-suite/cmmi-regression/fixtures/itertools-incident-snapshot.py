# Fixture — frozen snapshot of src/pycsl_lib/itertools.py:cycle
# as it appeared on 2026-05-31 13:47:22 (the GitHub Copilot Response
# capture that motivated missing-iter-feature.md).
#
# DO NOT EDIT. This is the canonical regression-test input for
# Phase D check 7 of cmmi-tailoring-plan-follow-up.md Item 2.
#
# The regression test (test_itertools_cycle_detection.py) runs
# `agent-stdlib-annotate --detect-gaps --scan-path <this file>`
# and asserts the iterator-semantics category contains `cycle`.

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/itertools.html#itertools.cycle
# cite:_note: cycle returns an infinite iterator; iterator-sequence semantics (indefinite cycling) cannot be expressed in the current contract surface. Stub models existence of a return value only.
#@ ensures True
def cycle(iterable: int) -> int:
    """Mock: make an iterator that cycles through iterable indefinitely."""
    return 0
