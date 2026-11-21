r"""Test 9705 -- lvQ open-world model (expected FAIL): `subprocess.run` of a missing program raises
FileNotFoundError, so the handler is reachable and `\result == 0` must NOT prove.
"""
# pycsl-expected: FAIL
from __future__ import annotations
import subprocess


#@ ensures \result == 0
#@ assigns \nothing
def probe(cmd: str) -> int:
    try:
        r = subprocess.run([cmd, "--version"], capture_output=True, text=True)
    except FileNotFoundError:
        return 1
    return 0


if __name__ == "__main__":
    r = probe("no-such-program-lvq-9705")
    print("VIOLATION contract" if r != 0 else "result", r)
