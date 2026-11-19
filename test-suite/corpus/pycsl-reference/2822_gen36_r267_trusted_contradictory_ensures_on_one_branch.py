r"""Test 2822 — route #267 (expected FAIL): a `\trusted` callee whose two `ensures` contradict
each other (`\result > x` and `\result < x`), reached only for x > 0; the caller's `\result == 1`
PROVED on the strength of that dead branch. CPython: g(5) == 5. Now reported VACUOUS.
"""
# pycsl-expected: FAIL
#@ \trusted
#@ ensures \result > x
#@ ensures \result < x
#@ assigns \nothing
def oracle(x: int) -> int:
    return x

#@ ensures \result == 1
#@ assigns \nothing
def g(x: int) -> int:
    if x > 0:
        y = oracle(x)
        return y
    return 1

if __name__ == "__main__":
    print(g(5))
