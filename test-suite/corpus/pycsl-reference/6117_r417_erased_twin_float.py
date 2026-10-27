r"""Test 6117 -- route #417 (expected FAIL): a guarded `float(n)` (kept obligation) beside `isinstance(float(n), float)` (obligation ERASED) share one tag; under `no_exception \all`, f(10**400) raises OverflowError in CPython. PROVED at base 930d68ed5 and at r417's salvaged check.
"""
# pycsl-expected: FAIL
#@ no_exception \all
def f(n: int) -> int:
    if -100 < n and n < 100:
        a = float(n)
    if isinstance(float(n), float):
        return 1
    return 0


if __name__ == "__main__":
    try:
        print(f(10**400))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
