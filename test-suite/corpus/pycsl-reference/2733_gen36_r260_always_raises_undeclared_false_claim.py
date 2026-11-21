r"""Test 2733 — route #260 (expected FAIL): a function whose every path raises an exception
no `#@ raises` declares (and which is not `-> NoReturn`). Its normal-return postcondition
`\result == 1` was discharged by the added `raises { ValueError, KeyError }` alone, and the
non-vacuity gate saw no normal-exit goal and passed it. CPython: `pick(1)` raises ValueError.
Now the gate reports it VACUOUS.
"""
# pycsl-expected: FAIL
#@ ensures \result == 1
#@ assigns \nothing
def pick(x: int) -> int:
    r = 0
    if x >= 0:
        raise ValueError("v")
    else:
        raise KeyError("k")
    return r

if __name__ == "__main__":
    try:
        print(pick(1))
    except ValueError:
        print("raises ValueError")
