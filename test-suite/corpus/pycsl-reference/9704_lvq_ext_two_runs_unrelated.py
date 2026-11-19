r"""Test 9704 -- lvQ open-world model (expected FAIL): two runs of the same command are unrelated
(the world can change between them: each `subprocess.run` is a fresh handle), so equal stdout
must NOT prove (CPython: `date +%N` differs).
"""
# pycsl-expected: FAIL
from __future__ import annotations
import subprocess


#@ ensures \result == True
#@ assigns \nothing
def twice(cmd: str, arg: str) -> bool:
    a = subprocess.run([cmd, arg], capture_output=True, text=True)
    b = subprocess.run([cmd, arg], capture_output=True, text=True)
    return a.stdout == b.stdout


if __name__ == "__main__":
    r = twice("date", "+%N")
    print("VIOLATION contract" if r is not True else "result", r)
