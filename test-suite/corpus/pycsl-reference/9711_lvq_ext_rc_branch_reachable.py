r"""Test 9711 -- lvQ open-world model (expected FAIL): twin of 9710 -- the non-zero return-code
branch is reachable (`cat` of a missing file exits 1), so `\result == 0` must NOT prove.
"""
# pycsl-expected: FAIL
from __future__ import annotations
import subprocess


#@ ensures \result == 0
#@ assigns \nothing
def check(path: str) -> int:
    try:
        r = subprocess.run(["cat", path], capture_output=True, text=True)
    except FileNotFoundError:
        return 0
    if r.returncode == 0:
        return 0
    return 1


if __name__ == "__main__":
    r = check("/no/such/file/lvq9711")
    print("VIOLATION contract" if r != 0 else "result", r)
