r"""Test 6116 -- route #417 (expected FAIL): a bounded `for x in sorted(range(n))` (kept obligation) beside an unbounded `set(sorted(range(n)))` (obligation ERASED by the coercion) share one tag; under `no_exception \all`, f(10**20) raises OverflowError in CPython. PROVED at base 930d68ed5 and at r417's salvaged check (a present tag hid the erased twin).
"""
# pycsl-expected: FAIL
#@ requires n >= 0
#@ no_exception \all
def f(n: int) -> int:
    c = 0
    if n < 100:
        for x in sorted(range(n)):
            c = 1
    s = set(sorted(range(n)))
    return 0


if __name__ == "__main__":
    try:
        print(f(10**20))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
