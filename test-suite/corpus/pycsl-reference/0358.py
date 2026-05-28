"""Test 0358 — no_exception preamble emission.

When a function declares `no_exception`, Module 6's preamble emits the
WhyML predicate library (`no_div_zero`, `in_bounds`, `non_neg_shift`).
This test exercises the preamble path only — the function body is a
constant so no VC injection is triggered.
"""
_ = 0  # anchor
#@ requires True
#@ ensures \result == 42
#@ assigns \nothing
#@ no_exception ZeroDivisionError
def constant_42() -> int:
    return 42


if __name__ == "__main__":
    assert constant_42() == 42
