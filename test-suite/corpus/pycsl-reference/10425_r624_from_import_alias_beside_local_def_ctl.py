r"""Test 10425 -- run #9 u70, route #624 (PASS control). `from qa70 import val1 as v1` beside a local
`def val1`: the alias keeps the two functions apart (`val v1` and the local `val1`), so `g() == 1 + 2`
proves; CPython agrees.
"""
# pycsl-expected: PASS
from qa70 import val1 as v1


#@ ensures \result == 2
#@ assigns \nothing
def val1() -> int:
    return 2


#@ ensures \result == 3
#@ assigns \nothing
def g() -> int:
    return v1() + val1()


if __name__ == "__main__":
    assert g() == 3
