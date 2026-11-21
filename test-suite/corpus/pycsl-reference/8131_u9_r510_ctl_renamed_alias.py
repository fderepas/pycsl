r"""Test 8131 -- route #510 (control, expected PASS; the advice of PYCSL-R510-TYPE-STATEMENT-NAME-READ applied to 8101): the alias renamed `type KT = int` shadows no value, so `n // K` reads the module constant `K = 5`; CPython f(10) returns 2
"""
# pycsl-expected: PASS

K = 5


#@ no_exception \all
#@ ensures \result == n // 5
def f(n: int) -> int:
    return n // K


type KT = int


if __name__ == "__main__":
    print("result", f(10))
