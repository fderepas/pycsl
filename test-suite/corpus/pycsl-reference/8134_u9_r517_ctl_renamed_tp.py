r"""Test 8134 -- route #517 (control, expected PASS; the advice of PYCSL-R517-TYPE-PARAM-NAME-READ applied to 8125): the class type parameter renamed `class C[T]:` shadows no value, so the method's `n // K` reads the module constant; CPython C().m(10) returns 2
"""
# pycsl-expected: PASS

K = 5


class C[T]:
    #@ no_exception \all
    #@ ensures \result == n // 5
    def m(self, n: int) -> int:
        return n // K


if __name__ == "__main__":
    print("result", C().m(10))
