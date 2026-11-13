r"""Test 9703 -- lvQ open-world model (expected PASS): two reads of the SAME process local's field
are equal (a `val function` of the handle; the CompletedProcess never escapes, so this is exact).
"""
# pycsl-expected: PASS
from __future__ import annotations
import subprocess


#@ ensures \result == True
#@ assigns \nothing
def same(cmd: str) -> bool:
    r = subprocess.run([cmd], capture_output=True, text=True)
    return r.returncode == r.returncode and r.stdout == r.stdout


if __name__ == "__main__":
    r = same("true")
    print("VIOLATION contract" if r is not True else "result", r)
