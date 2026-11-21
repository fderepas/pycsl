r"""Test 9963 -- route #599 advice control (expected PASS): rt58 c14b with the advice of PYCSL-R599-HANDLER-UNMODELLED-RAISER followed -- the operation the handler is not meant for (the `os.path.getsize` facade, here of `"."` so that the moved call returns normally on every argument) is MOVED OUT of the `try` body, so the handler is reached only from the modelled `Path.cwd()` (with x == 0); `\result == 0` holds on both paths
"""
# pycsl-expected: PASS
from __future__ import annotations
import os
from pathlib import Path


#@ ensures \result == 0
#@ assigns \nothing
def f(s: str) -> int:
    x = 0
    try:
        Path.cwd()
        x = 1
    except OSError:
        return x
    k = os.path.getsize(".")
    return 0


if __name__ == "__main__":
    import tempfile
    d = tempfile.mkdtemp()
    r = f(d)
    print("VIOLATION contract" if r != 0 else "result", r)
