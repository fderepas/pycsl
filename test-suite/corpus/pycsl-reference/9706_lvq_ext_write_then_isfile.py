r"""Test 9706 -- lvQ open-world model (expected FAIL): a write does not make a later world read
true (another process may remove the file; the reads are law-free), so `\result == True` must NOT
prove (CPython: `p` a directory -> IsADirectoryError is caught, `is_file()` False).
"""
# pycsl-expected: FAIL
from __future__ import annotations
import tempfile
from pathlib import Path


#@ ensures \result == True
#@ assigns \nothing
def wrote(p: Path, s: str) -> bool:
    try:
        p.write_text(s)
    except OSError:
        pass
    return p.is_file()


if __name__ == "__main__":
    d = tempfile.mkdtemp()
    r = wrote(Path(d), "x")
    print("VIOLATION contract" if r is not True else "result", r)
