r"""Test 9700 -- lvQ open-world external-effect model (expected PASS): `Path.mkdir(parents=True,
exist_ok=True)` is a law-free world write declaring every exception CPython can raise there (the
OSError family, ValueError for an embedded NUL); an honest contract that claims nothing about the
world PROVES. At base the call lowered to the receiver-less `root_mkdir_0 ()` (a facade).
"""
# pycsl-expected: PASS
from __future__ import annotations
import tempfile
from pathlib import Path


#@ ensures True
#@ assigns \nothing
def cache_root(project_root: Path) -> Path:
    root = project_root / ".cache"
    root.mkdir(parents=True, exist_ok=True)
    return root


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as d:
        print("result", cache_root(Path(d)))
