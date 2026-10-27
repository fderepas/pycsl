r"""Test 6024 -- gen #37 route #407 (expected PASS): CONTROL: primitive arithmetic, a read-only display element, a tuple concatenation, an IfExp of strings and a class-body product of ints hashed (CPython ok). PROVED at base and candidate.
"""
# pycsl-expected: PASS
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
