r"""Test 10295 -- R614 unresolved aliases / unknown callees (lvZ2, run #8; expected FAIL): a `Path(<str>)` passed to an
imported `keep(x: str)` through a DOTTED package callee (red team rt70 m20: a two-dot callee was
never keyed); CPython: False.
REFUSED (`PYCSL-R614-PATH-STR-CONFLATED`), fail-closed.
"""
# pycsl-expected: FAIL
from __future__ import annotations
from pathlib import Path
import multi_file_lib.lvz2r_tat


#@ ensures \result == True
#@ assigns \nothing
def f(s: str) -> bool:
    q = multi_file_lib.lvz2r_tat.keep(Path(s))
    return q == str(Path(s))


if __name__ == "__main__":
    r = f("a")
    print("VIOLATION contract" if r is not True else "result", r)
