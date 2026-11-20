r"""Test 10281 -- lvZ2 restricted Path type separation (expected FAIL): a modelled `Path(<str>)`
passed to the IMPORTED `keep(x: str) -> str` while a local class method is also named `keep`
(red team rt70 m19, INTRODUCED by batch C: the string lowering decided `q == str(Path(s))`);
CPython: False. The modelled value is the abstract `py_path`: a Why3 TYPE ERROR (fail-closed).
"""
# pycsl-expected: FAIL
from __future__ import annotations
from pathlib import Path
from multi_file_lib.lvz2_pathlib import keep


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
