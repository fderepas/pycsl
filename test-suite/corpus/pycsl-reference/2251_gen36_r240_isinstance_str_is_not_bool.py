r"""Test 2251 — route #240 (expected PASS): CONTROL. A subject with a concrete NON-int tag still
decides `isinstance(<str>, bool)` FALSE (a str is neither an int nor a bool), so `\result == 0`
PROVES (CPython: 0 for any str `s`). Only an int / undecided subject's bool test became opaque.
"""
# pycsl-expected: PASS


#@ ensures \result == 0
#@ assigns \nothing
def f(s: str) -> int:
    if isinstance(s, bool):
        return 1
    return 0
