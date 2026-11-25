r"""Test 10525 -- run #9 u76, review rt84 F2, route #634. Control: the helper zu76n.f declares `#@ assigns
\nothing` and only reads its record parameter; the caller claims r.b unchanged (`cd <tree root> && python <this
file>` prints "CPython g(R(1,0)) = 0"): PROVED.
"""
# pycsl-expected: PASS
from zu76n import R, f


#@ requires r.b == 0
#@ ensures \result == 0
def g(r: R) -> int:
    f(r)
    return r.b


if __name__ == "__main__":
    print("CPython g(R(1,0)) =", g(R(1, 0)))
