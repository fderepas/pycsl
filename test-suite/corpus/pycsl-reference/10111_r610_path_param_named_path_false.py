r"""Test 10111 -- route #610 (rt61 M1, expected FAIL): a PARAMETER named `Path` shadows `from pathlib import Path`: `Path.cwd()` is the user method. The model of the module call
applies only when the head name is the module import, bound nowhere in the function and not
rebound at module level; here it is not, so the file is REFUSED
(`PYCSL-R610-EXT-MODULE-NAME-SHADOWED`) rather than lowered as the module call.
"""
# pycsl-expected: FAIL
from __future__ import annotations
from pathlib import Path


class P:
    #@ assigns \nothing
    def __init__(self) -> None:
        self.n: int = 0

    #@ assigns self.n
    def cwd(self) -> str:
        self.n = self.n + 1
        return "/"


#@ ensures Path.n == \old(Path.n)
def where(Path: P) -> int:
    try:
        Path.cwd()
    except OSError:
        return 0
    return 1


if __name__ == "__main__":
    p = P()
    where(p)
    print("VIOLATION contract" if p.n != 0 else "result", p.n)
