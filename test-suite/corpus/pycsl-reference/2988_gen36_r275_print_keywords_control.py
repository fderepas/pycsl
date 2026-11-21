r"""Test 2988 — route #275 control (expected PASS): `print`'s `sep`/`end` (str literals),
`flush` (bool literal) and `file=sys.stderr` neither raise nor reach user code, and print's
output is not modelled, so they are accepted and `no_exception \all` still proves.
"""
# pycsl-expected: PASS
import sys


#@ no_exception \all
#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    print("x", "y", sep=",", end="\n", file=sys.stderr, flush=True)
    return 0


if __name__ == "__main__":
    assert f() == 0
