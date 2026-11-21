r"""Test 10073 -- lvU `os.access` (expected FAIL): `os.access` raises ValueError on a path with an
embedded NUL (CPython: `can_run("a\x00b")` raises), so `no_exception \all` is false. Measured
verdict: refused by the `no_exception` callee census (route #161: a world query is not admitted
under a claim), as lvQ's 9708. Control: 10070.
"""
# pycsl-expected: FAIL
import os


#@ assigns \nothing
#@ no_exception \all
def can_run(p: str) -> int:
    if os.access(p, os.X_OK):
        return 1
    return 0


if __name__ == "__main__":
    try:
        print("result", can_run("a\x00b"))
    except ValueError:
        print("VIOLATION ValueError")
