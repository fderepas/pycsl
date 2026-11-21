r"""Test 7024 -- route #452 (expected PASS): CONTROL -- `71 in b"GET"` (an int literal in 0..255); PROVED at base and candidate.
"""
# pycsl-expected: PASS
#@ no_exception \all
def f(n: int) -> int:
    if 71 in b'GET':
        return 1
    return 0
