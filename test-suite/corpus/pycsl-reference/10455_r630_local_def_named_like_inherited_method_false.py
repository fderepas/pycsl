r"""Test 10455 -- run #9 u72, review rt80 R3a, route #630 (FAIL, PRE-EXISTING). A program function named
`base__m` (the mangled name of the inherited method qg72.Base.m) returns 2. The base-class resolver skipped
the library method because the name was taken, and X inherited the LOCAL function: `x.m() == 2` PROVED at
L20. CPython runs qg72.Base.m and prints "result 1". REFUSED: PYCSL-SEM-IMPORT-FUNCTION-NAME-CLASH.
"""
# pycsl-expected: FAIL
import qg72


#@ ensures \result == 2
#@ assigns \nothing
def base__m(k: int) -> int:
    return 2


class X(qg72.Base):
    pass


#@ ensures \result == 2
#@ assigns \nothing
def g(x: X) -> int:
    return x.m()


if __name__ == "__main__":
    print("result", g(X()))
