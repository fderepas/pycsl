r"""Test 2821 — route #267 (expected FAIL): an `\abstract` callee whose `ensures x != 5` is
unsatisfiable at x == 5, called only under `if x == 5:` — that branch is dead in the model, so
`\result == 1` PROVED although the branch returns 2. The all-exits vacuity gate saw the other,
consistent exit. CPython: g(5) == 2. Now the call-site probe reports g VACUOUS.
"""
# pycsl-expected: FAIL
#@ \abstract
#@ ensures x != 5
def oracle(x: int) -> int: ...

#@ ensures \result == 1
#@ assigns \nothing
def g(x: int) -> int:
    if x == 5:
        oracle(x)
        return 2
    return 1

if __name__ == "__main__":
    print(g(5))
