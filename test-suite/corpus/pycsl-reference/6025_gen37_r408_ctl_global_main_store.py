r"""Test 6025 -- gen #37 route #408 (expected PASS): CONTROL: a module list never stored to, its element hashed (CPython ok). PROVED at base and candidate.
ROUTE #506 (run #4): now expected FAIL -- REFUSED PYCSL-R506-TRIGGER-SITE-UNLOWERED by design. The subscript sits in a position the lowering never evaluates, so the IndexError / KeyError obligation the `no_exception \all` claim covers is absent from the VC; the program is CPython-honest only because of its guard / data, which the model never checks (`XS[0]` of a module list inside the set display: twin `{A[5]}` PROVED at base, CPython IndexError).
"""
# pycsl-expected: FAIL
XS = [1, 2]


#@ no_exception \all
#@ ensures \result == 1
def f() -> int:
    s = {XS[0]}
    return 1


if __name__ == "__main__":
    print(f(), len(XS))
