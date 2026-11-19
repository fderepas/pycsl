r"""Test 8925 -- lvD string literal into an int-hash local (expected FAIL): false twin of 8923. The
hash constant carries no claim about `None`-ness beyond what CPython says: after `name = "_"`,
`name is None` is False, so `\result == True` (claiming it is None) must NOT prove.
"""
# pycsl-expected: FAIL
from __future__ import annotations


#@ ensures \result == True
#@ assigns \nothing
def star(x) -> bool:
    name = x
    if x is None:
        name = "_"
        return name is None
    return True


if __name__ == "__main__":
    r = star(None)
    print("VIOLATION contract" if r is not True else "result", r)
