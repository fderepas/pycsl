r"""Test 2734 — route #260 CONTROL (expected PASS): a function with an undeclared `raise`
ValueError (an unconditioned `raises { ValueError }` arm is still emitted for it) and a normal
return keeps its verdict: the normal exit is reachable, so the vacuity gate does not fire.
The `requires` keeps every admitted argument on the returning path (the contract-truth plane's
rule: no contract promises a value where CPython raises). CPython: `pick(3) == 3`.
"""
#@ requires x >= 0
#@ ensures \result >= 0
#@ assigns \nothing
def pick(x: int) -> int:
    r = x
    if x < 0:
        raise ValueError("v")
    return r

if __name__ == "__main__":
    print(pick(3))
