r"""Test 10523 -- run #9 u76, review rt84 F2, route #634. Control: the helper zu76b.f declares
`#@ assigns r.b` and writes exactly r.b; the caller claims the OTHER field r.a is unchanged (`cd <tree root> &&
python <this file>` prints "CPython g(R(1,0)) = 1"). The importer val carries `writes { r.b }`: PROVED.
"""
# pycsl-expected: PASS
from zu76b import R, f


#@ requires r.a == 1
#@ ensures \result == 1
def g(r: R) -> int:
    f(r)
    return r.a


if __name__ == "__main__":
    print("CPython g(R(1,0)) =", g(R(1, 0)))
