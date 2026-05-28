"""Test 0386 — strict-no-exception-propagation: unannotated callee fails.

Under `--strict-no-exception-propagation`, calling an unresolved /
abstract function from a `no_exception`-enabled context becomes a
hard VC: the abstract callee is conservatively assumed to be able to
raise the listed exceptions, so the call site asserts ``false``.
"""
# pycsl-flags: --strict-no-exception-propagation
# pycsl-expected: FAIL
_ = 0  # anchor
#@ requires n != 0
#@ ensures \result == external_helper(n)
#@ assigns \nothing
#@ no_exception ZeroDivisionError
def caller(n: int) -> int:
    return external_helper(n)


if __name__ == "__main__":
    pass
