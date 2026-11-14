r"""Test 9707 -- lvQ open-world model (expected FAIL): `Path.cwd()` raises FileNotFoundError when
the working directory was removed, so the handler is reachable and `\result == 0` must NOT prove.
"""
# pycsl-expected: FAIL
from __future__ import annotations
import os
import tempfile
from pathlib import Path


#@ ensures \result == 0
#@ assigns \nothing
def here() -> int:
    try:
        Path.cwd()
    except FileNotFoundError:
        return 1
    return 0


if __name__ == "__main__":
    old = os.getcwd()
    d = tempfile.mkdtemp()
    os.chdir(d)
    os.rmdir(d)
    r = here()
    os.chdir(old)
    print("VIOLATION contract" if r != 0 else "result", r)
