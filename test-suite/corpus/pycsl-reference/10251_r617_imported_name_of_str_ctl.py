r"""Test 10251 -- route #617 (expected PASS): CONTROL -- a Path passed to an IMPORTED parameter that
IS annotated `Path` (`name_of(p: Path) -> str`), and the `str` result compared with itself
(CPython True). The new imported-callee rule admits it. (No `assigns` claim: the injected stub
`name_of` declares no frame, so the typed / store models let it write the heap.)
"""
# pycsl-expected: PASS
from __future__ import annotations
from pathlib import Path
from multi_file_lib.r617_pathlib import name_of


#@ ensures \result == True
def f(s: str) -> bool:
    n = name_of(Path(s))
    return n == n


if __name__ == "__main__":
    r = f("a/b")
    print("VIOLATION contract" if r is not True else "result", r)
