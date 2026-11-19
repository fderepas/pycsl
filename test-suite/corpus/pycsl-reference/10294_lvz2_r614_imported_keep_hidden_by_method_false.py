r"""Test 10294 -- R614 unresolved aliases / unknown callees (lvZ2, run #8; expected FAIL): a `Path(<str>)` passed to the
IMPORTED `keep(x: str)` while a unit method is also named `keep` (red team rt70 m19: the method hid
the import from the check); CPython: False.
REFUSED (`PYCSL-R614-PATH-STR-CONFLATED`), fail-closed.
"""
# pycsl-expected: FAIL
from __future__ import annotations
from pathlib import Path
from multi_file_lib.lvz2r_tat import keep


class Box:
    #@ ensures \result == 0
    #@ assigns \nothing
    def keep(self) -> int:
        return 0


#@ ensures \result == True
#@ assigns \nothing
def f(s: str) -> bool:
    q = keep(Path(s))
    return q == str(Path(s))


if __name__ == "__main__":
    r = f("a")
    print("VIOLATION contract" if r is not True else "result", r)
