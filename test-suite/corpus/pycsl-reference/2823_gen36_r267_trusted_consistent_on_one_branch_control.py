r"""Test 2823 — route #267 CONTROL (expected PASS): a `\trusted` callee with a satisfiable,
honest contract called on one branch keeps its verdict — the point after the call is reachable,
so the call-site probe does not fire. CPython: g(5) == 6, g(0) == 1.
"""
#@ \trusted
#@ requires x >= 0
#@ ensures \result >= x
#@ assigns \nothing
def oracle(x: int) -> int:
    return x

#@ requires x >= 0
#@ ensures \result >= 1
#@ assigns \nothing
def g(x: int) -> int:
    if x == 5:
        y = oracle(x)
        return y + 1
    return 1

if __name__ == "__main__":
    print(g(5), g(0))
