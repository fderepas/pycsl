r"""Test 8924 -- lvD string literal into an int-hash local (expected FAIL): false twin of 8923. With
`x = None` the result is "*_", so `\result == "*a"` must NOT prove: the hash constant renders through
the content-free `int_to_string`, which equates it with no literal.
"""
# pycsl-expected: FAIL
from __future__ import annotations


#@ ensures \result == "*a"
#@ assigns \nothing
def star(x) -> str:
    name = x
    if name is None:
        name = "_"
    return f"*{name}"


if __name__ == "__main__":
    r = star(None)
    print("VIOLATION contract" if r != "*a" else "result", r)
