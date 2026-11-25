r"""Test 10520 -- run #9 u76, review rt84 F2, route #634. The helper zu76a.f declares `#@ assigns
\nothing` but writes the field r.b of its record parameter inside a loop; the caller assumes r.b unchanged.
`cd <tree root> && python <this file>` prints "CPython g(R(1,0)) = 5", the claim below is false. L21 (and u74)
PROVED it (zu76a proved alone, the importer saw `val f (r: r) : int` with no `writes`). REFUSED:
PYCSL-FUNCTION-FRAME (the imported body writes a parameter its declared frame does not name).
"""
# pycsl-expected: FAIL
from zu76a import R, f


#@ requires r.b == 0
#@ ensures \result == 0
def g(r: R) -> int:
    f(r)
    return r.b


if __name__ == "__main__":
    print("CPython g(R(1,0)) =", g(R(1, 0)))
