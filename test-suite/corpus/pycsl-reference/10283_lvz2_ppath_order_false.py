r"""Test 10283 -- lvZ2 restricted Path type separation (expected FAIL): `Path("a/b") < Path("a-b")`
orders by the parsed PARTS in CPython (True) while the strings order the other way
(`"a/b" < "a-b"` is False). The modelled values are the abstract `py_path`, which has NO order:
not provable either way (a Why3 type error or a refusal, fail-closed).
"""
# pycsl-expected: FAIL
from __future__ import annotations
from pathlib import Path


#@ requires a == "a/b" and b == "a-b"
#@ ensures \result == False
#@ assigns \nothing
def f(a: str, b: str) -> bool:
    p = Path(a)
    q = Path(b)
    return p < q


if __name__ == "__main__":
    r = f("a/b", "a-b")
    print("VIOLATION contract" if r is not False else "result", r)
