r"""Test 10291 -- R614 unresolved aliases / unknown callees (lvZ2, run #8; expected FAIL): ORDERING of two parameters
annotated through a `TypeAliasType` alias of Path (red team rt70 t04: decided as string order);
CPython orders by parts: `Path("a/b") < Path("a-b")` is True.
REFUSED (`PYCSL-R614-PATH-STR-CONFLATED`), fail-closed.
"""
# pycsl-expected: FAIL
from __future__ import annotations
from pathlib import Path
from typing import TypeAliasType

Fp = TypeAliasType("Fp", Path)


#@ requires str(p) == "a/b" and str(q) == "a-b"
#@ ensures \result == False
#@ assigns \nothing
def f(p: Fp, q: Fp) -> bool:
    return p < q


if __name__ == "__main__":
    r = f(Path("a/b"), Path("a-b"))
    print("VIOLATION contract" if r is not False else "result", r)
