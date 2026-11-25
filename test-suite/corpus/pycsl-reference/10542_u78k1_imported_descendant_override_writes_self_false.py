r"""Test 10542 -- run #9 u78, review rt88 K1 (route #634), the override comes from a MERGED module: the helper zu78a defines a pure `R.total` and a subclass `D(R)` whose override writes `self.a`. `f(r: R)` here declares `#@ assigns \nothing` and returns `r.total()`. REFUSED (PYCSL-FUNCTION-FRAME): the override pair of the merged module disables the receiver-class narrowing. `cd <tree root> && python <this file>` prints "CPython d.a after f(D(0)) = 5".
"""
# pycsl-expected: FAIL
from zu78a import R, D


#@ assigns \nothing
def f(r: R) -> int:
    return r.total()


if __name__ == "__main__":
    d = D(0); f(d); print("CPython d.a after f(D(0)) =", d.a)
