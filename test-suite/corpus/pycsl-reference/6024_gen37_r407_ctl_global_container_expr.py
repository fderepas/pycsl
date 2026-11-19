r"""Test 6024 -- gen #37 route #407 (expected PASS): CONTROL: primitive arithmetic, a read-only display element, a tuple concatenation, an IfExp of strings and a class-body product of ints hashed (CPython ok). PROVED at base and candidate.
ROUTE #506 (run #4): now expected FAIL -- REFUSED PYCSL-R506-TRIGGER-SITE-UNLOWERED by design. The subscript sits in a position the lowering never evaluates, so the IndexError / KeyError obligation the `no_exception \all` claim covers is absent from the VC; the program is CPython-honest only because of its guard / data, which the model never checks (`A[1]` of a module list inside the set display: twin `{A[5]}` PROVED at base, CPython IndexError).
"""
# pycsl-expected: FAIL
A = [1, 2]
T = (1, 2)
K = 2 * 3 + 1
L = A[0]
U = T + (3,)
V = "a" if K else "b"


class C:
    N = 4
    M = N * 2


#@ no_exception \all
#@ ensures \result == 1
def f() -> int:
    s = {K, L, V, C.M, A[1]}
    return 1


if __name__ == "__main__":
    print(f())
