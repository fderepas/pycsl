r"""Test 6982 -- route #450 (expected PASS): CONTROL: `super().h(k)` in an override, resolved to the base `B.h(self, k)` (it binds), the caller under `#@ no_exception \all`; and `super().__str__()` of an `Exception` subclass (resolved through the real `BaseException.__str__`). Admitted; PROVED at base and candidate (CPython ok).
"""
# pycsl-expected: PASS
class B:
    #@ ensures \result >= k
    def h(self, k: int) -> int:
        return k


class Q(B):
    #@ ensures \result == k + 1
    def h(self, k: int) -> int:
        super().h(k)
        return k + 1


class E(Exception):
    def __str__(self) -> str:
        return super().__str__()


#@ no_exception \all
#@ ensures \result == n + 1
def f(p: Q, n: int) -> int:
    return p.h(n)


if __name__ == "__main__":
    print(f(Q(), 2), str(E("x")))
