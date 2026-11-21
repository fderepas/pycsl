r"""Test 7023 -- route #452 (expected PASS): CONTROL -- `find` / `count` / `rfind` of int LITERALS in 0..255 on a bytes local; PROVED at base and candidate.
"""
# pycsl-expected: PASS
#@ no_exception \all
def f(n: int) -> int:
    data = b'GET / HTTP'
    return data.find(71) + data.count(0) + data.rfind(255)
