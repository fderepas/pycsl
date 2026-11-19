r"""Test 2824 — route #267 CONTROL (expected PASS): a branch that is dead BEFORE the call (the
`requires x > 10` excludes `x == 5`) keeps its verdict even though it calls a `\trusted` callee:
the probe before the call is already unreachable, so the deadness is the program's own design,
not the callee's contract (the gate's dead-by-design philosophy). CPython: g(11) == 1.
"""
#@ \trusted
#@ ensures \result >= 0
#@ assigns \nothing
def oracle(x: int) -> int:
    return x * x

#@ requires x > 10
#@ ensures \result == 1
#@ assigns \nothing
def g(x: int) -> int:
    if x == 5:
        oracle(x)
        return 2
    return 1

if __name__ == "__main__":
    print(g(11))
