r"""Test 4396 -- gen #37 route #332 (expected FAIL): `no_exception AssertionError` is REFUSED by Module 4 (unknown exception name; base: same) — the named-set twin of the `\all` repair cannot reach the erasure.
"""
# pycsl-expected: FAIL
#@ ensures \result == 7
#@ assigns \nothing
#@ no_exception AssertionError
def g() -> int:
    x = 1
    assert x == 2
    return 7

if __name__ == "__main__":
    # CPython ground truth: this call RAISES (see the docstring); no handler, because a
    # handler that can catch AssertionError around an assert is refused (route 16).
    print(g())
