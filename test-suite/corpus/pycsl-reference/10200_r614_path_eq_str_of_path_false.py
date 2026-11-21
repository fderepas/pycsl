r"""Test 10200 -- route #614 (expected FAIL): a modelled `Path(<str>)` compared with its own `str`
(rt65 a01). The model represents a Path as a Why3 string and `str(<string>)` is the identity, so
`p == str(p)` lowered to `str_eq_op !p !p` and `\result == True` PROVED at 4d753c2f1; CPython
`PosixPath('a') == 'a'` is False. REFUSED (`PYCSL-R614-PATH-STR-CONFLATED`).
"""
# pycsl-expected: FAIL
from __future__ import annotations
from pathlib import Path


#@ ensures \result == True
#@ assigns \nothing
def f(s: str) -> bool:
    p = Path(s)
    return p == str(p)


if __name__ == "__main__":
    r = f("a")
    print("VIOLATION contract" if r is not True else "result", r)
