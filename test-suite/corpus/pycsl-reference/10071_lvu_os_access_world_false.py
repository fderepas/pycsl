r"""Test 10071 -- lvU `os.access` (expected FAIL): the answer is a WORLD fact the model does not
know, so `\result == 1` is false (CPython: `can_run("/nonexistent")` is 0). Control: 10070.
"""
# pycsl-expected: FAIL
import os


#@ ensures \result == 1
#@ assigns \nothing
def can_run(p: str) -> int:
    if os.access(p, os.X_OK):
        return 1
    return 0


if __name__ == "__main__":
    r = can_run("/nonexistent")
    print("VIOLATION contract" if r != 1 else "result", r)
