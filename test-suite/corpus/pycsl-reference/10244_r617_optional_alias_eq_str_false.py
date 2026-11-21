r"""Test 10244 -- route #617 (expected FAIL): an alias of `Optional[Path]`
(`MaybeP: TypeAlias = Optional[Path]`, lvZ probe q07, PRE-EXISTING: the parameter was erased to
`string` and `p == str(p)` was `str_eq_op p p`); CPython False. REFUSED
(`PYCSL-R614-PATH-STR-CONFLATED`).
"""
# pycsl-expected: FAIL
from __future__ import annotations
from pathlib import Path
from typing import Optional, TypeAlias

MaybeP: TypeAlias = Optional[Path]


#@ ensures \result == True
#@ assigns \nothing
def f(p: MaybeP) -> bool:
    return p == str(p)


if __name__ == "__main__":
    r = f(Path("a"))
    print("VIOLATION contract" if r is not True else "result", r)
