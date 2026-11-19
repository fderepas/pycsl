r"""Test 10292 -- R614 unresolved aliases / unknown callees (lvZ2, run #8; expected FAIL): a Path returned by the IMPORTED
`mk(s) -> Fp`, `Fp` a `TypeAliasType` alias of Path in the dependency (red team rt70 m07);
CPython: False.
REFUSED (`PYCSL-R614-PATH-STR-CONFLATED`), fail-closed.
"""
# pycsl-expected: FAIL
from __future__ import annotations
from multi_file_lib.lvz2r_tat import mk


#@ ensures \result == True
#@ assigns \nothing
def f(s: str) -> bool:
    p = mk(s)
    return p == str(p)


if __name__ == "__main__":
    r = f("a")
    print("VIOLATION contract" if r is not True else "result", r)
