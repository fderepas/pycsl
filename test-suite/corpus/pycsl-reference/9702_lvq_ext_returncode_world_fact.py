r"""Test 9702 -- lvQ open-world model (expected FAIL): a `subprocess.run` result is a fresh law-free
handle; its `returncode` is an unconstrained int, so `\result == 0` (a world fact: `false` exits 1)
must NOT prove.
"""
# pycsl-expected: FAIL
from __future__ import annotations
import subprocess


#@ ensures \result == 0
#@ assigns \nothing
def rc(cmd: str) -> int:
    r = subprocess.run([cmd], capture_output=True, text=True)
    return r.returncode


if __name__ == "__main__":
    r = rc("false")
    print("VIOLATION contract" if r != 0 else "result", r)
