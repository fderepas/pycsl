r"""Test 4510 -- gen #37 route #337 (expected FAIL): `class P: pass`: `x < x` was int ordering, `no_exception \all` + `\result == False` PROVED; CPython TypeError. Erased; not provable.
"""
# pycsl-expected: FAIL
class W:
    def __sub__(self, o: object) -> int:
        return 1

class P:
    pass

#@ no_exception \all
#@ ensures \result == False
def f_lt_noexc(x: P) -> bool:
    return x < x

if __name__ == "__main__":
    assert f_lt_noexc(*(P(),)) == False, f_lt_noexc(*(P(),))
