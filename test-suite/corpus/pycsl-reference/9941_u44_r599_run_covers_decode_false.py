r"""Test 9941 -- route #599 (expected FAIL: PROVED at L9, REFUSED PYCSL-R599-HANDLER-UNMODELLED-RAISER at HEAD): rt58 c05: the modelled `subprocess.run` covers `except UnicodeDecodeError`, then the receiver-less facade `b.decode()` raises it only in CPython; `f("true", b"\xff")` returns 1 under `ensures \result == 0`
"""
# pycsl-expected: FAIL
from __future__ import annotations
import subprocess


#@ ensures \result == 0
#@ assigns \nothing
def f(cmd: str, b: bytes) -> int:
    x = 0
    try:
        r = subprocess.run([cmd], capture_output=True, text=True)
        x = 1
        t = b.decode()
    except UnicodeDecodeError:
        return x
    except OSError:
        return 0
    return 0


if __name__ == "__main__":
    r = f("true", b"\xff")
    print("VIOLATION contract" if r != 0 else "result", r)
