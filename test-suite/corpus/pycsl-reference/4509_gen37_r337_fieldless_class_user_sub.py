r"""Test 4509 -- gen #37 route #337 (expected FAIL): a FIELD-LESS class `W` was `type w = int`, its own `__sub__` (returns 1) ignored: `x - x == 0` PROVED; CPython 1. The parameter is erased: REFUSED (route #252, erased value into `-> int`).
"""
# pycsl-expected: FAIL
class W:
    def __sub__(self, o: object) -> int:
        return 1

class P:
    pass

#@ ensures \result == 0
def f_dunder_sub(x: W) -> int:
    return x - x

if __name__ == "__main__":
    assert f_dunder_sub(*(W(),)) == 0, f_dunder_sub(*(W(),))
