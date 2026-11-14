r"""Test 9710 -- lvQ open-world model (expected PASS): the `_why3_typecheck` shape -- a missing
program is caught, the return code selects the branch, the diagnostic is `stderr.strip() or
stdout.strip()` -- proves its honest postcondition (only the two results it can return).
"""
# pycsl-expected: PASS
from __future__ import annotations
import subprocess


#@ ensures \result == 0 or \result == 1 or \result == 2
#@ assigns \nothing
def check(path: str) -> int:
    try:
        r = subprocess.run(["cat", path], capture_output=True, text=True)
    except FileNotFoundError:
        return 2
    if r.returncode == 0:
        return 0
    d = r.stderr.strip() or r.stdout.strip()
    return 1


if __name__ == "__main__":
    r = check("/no/such/file/lvq9710")
    print("VIOLATION contract" if r not in (0, 1, 2) else "result", r)
