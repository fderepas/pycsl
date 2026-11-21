r"""Test 10289 -- R614 unresolved aliases / unknown callees (lvZ2, run #8; expected FAIL): a parameter annotated through
`Fp = TypeAliasType("Fp", Path)` (red team rt70 t01, PRE-EXISTING: #336 erases it to `string`, and
`p == str(p)` PROVED); CPython: False.
REFUSED (`PYCSL-R614-PATH-STR-CONFLATED`), fail-closed.
"""
# pycsl-expected: FAIL
from __future__ import annotations
from pathlib import Path
from typing import TypeAliasType

Fp = TypeAliasType("Fp", Path)


#@ ensures \result == True
#@ assigns \nothing
def f(p: Fp) -> bool:
    return p == str(p)


if __name__ == "__main__":
    r = f(Path("a"))
    print("VIOLATION contract" if r is not True else "result", r)
