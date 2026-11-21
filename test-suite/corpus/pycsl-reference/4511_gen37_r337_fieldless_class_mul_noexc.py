r"""Test 4511 -- gen #37 route #337 (expected FAIL): `class P: pass`: `x * 0 + 1 == 1` PROVED under `no_exception \all`; CPython TypeError. Erased: REFUSED (route #252).
"""
# pycsl-expected: FAIL
class W:
    def __sub__(self, o: object) -> int:
        return 1

class P:
    pass

#@ no_exception \all
#@ ensures \result == 1
def f_mul_noexc(x: P) -> int:
    return x * 0 + 1

if __name__ == "__main__":
    assert f_mul_noexc(*(P(),)) == 1, f_mul_noexc(*(P(),))
