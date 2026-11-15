r"""Test 9943 -- route #599 (expected FAIL: PROVED at L9, REFUSED PYCSL-R599-HANDLER-UNMODELLED-RAISER at HEAD): rt58 c09: the modelled `p.mkdir(..)` covers `except FileNotFoundError`, then `q.read_text()` (unmodelled) raises it only in CPython; returns 1 under `ensures \result == 0`
"""
# pycsl-expected: FAIL
from __future__ import annotations
from pathlib import Path


#@ ensures \result == 0
#@ assigns \nothing
def f(p: Path, q: Path) -> int:
    x = 0
    try:
        p.mkdir(parents=True, exist_ok=True)
        x = 1
        t = q.read_text()
    except FileNotFoundError:
        return x
    return 0


if __name__ == "__main__":
    import tempfile
    d = tempfile.mkdtemp()
    r = f(Path(d) / "a", Path(d) / "missing")
    print("VIOLATION contract" if r != 0 else "result", r)
