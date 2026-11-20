r"""Test 10290 -- R614 unresolved aliases / unknown callees (lvZ2, run #8; expected FAIL): the `typing.TypeAliasType(..)` spelling
of 10289 (red team rt70 t03); CPython: False.
REFUSED (`PYCSL-R614-PATH-STR-CONFLATED`), fail-closed.
"""
# pycsl-expected: FAIL
from __future__ import annotations
import typing
from pathlib import Path

Fp = typing.TypeAliasType("Fp", Path)


#@ ensures \result == True
#@ assigns \nothing
def f(p: Fp) -> bool:
    return p == str(p)


if __name__ == "__main__":
    r = f(Path("a"))
    print("VIOLATION contract" if r is not True else "result", r)
