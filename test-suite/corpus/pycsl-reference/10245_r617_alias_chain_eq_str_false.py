r"""Test 10245 -- route #617 (expected FAIL): an alias CHAIN (`A = Path`, `B: TypeAlias = A`;
lvZ probe q05, PRE-EXISTING: #31 resolved `B` to Path and erased the parameter to `string`);
`p == str(p)` PROVED `\result == True`, CPython False. REFUSED (`PYCSL-R614-PATH-STR-CONFLATED`:
aliases are resolved to a fixpoint).
"""
# pycsl-expected: FAIL
from __future__ import annotations
from pathlib import Path
from typing import TypeAlias

A = Path
B: TypeAlias = A


#@ ensures \result == True
#@ assigns \nothing
def f(p: B) -> bool:
    return p == str(p)


if __name__ == "__main__":
    r = f(Path("a"))
    print("VIOLATION contract" if r is not True else "result", r)
