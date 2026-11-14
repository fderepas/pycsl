r"""Test 9700 -- lvQ open-world external-effect model (expected PASS): `Path.mkdir(parents=True,
exist_ok=True)` is a law-free world write declaring every exception CPython can raise there (the
OSError family, ValueError for an embedded NUL); a postcondition that claims nothing about the world
(the function returns one of its two codes) PROVES. At base the call lowered to the receiver-less
`root_mkdir_0 ()` (a facade). Twin: 9701 (must FAIL).
"""
# pycsl-expected: PASS
from __future__ import annotations
import shutil
import tempfile
from pathlib import Path


#@ ensures \result == 0 or \result == 1
#@ assigns \nothing
def make(project_root: Path) -> int:
    root = project_root / ".cache"
    try:
        root.mkdir(parents=True, exist_ok=True)
    except OSError:
        return 1
    return 0


if __name__ == "__main__":
    d = tempfile.mkdtemp()
    r = make(Path(d))
    shutil.rmtree(d)
    print("VIOLATION contract" if r not in (0, 1) else "result", r)
