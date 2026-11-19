r"""Test 5090 -- gen #37 route #373 (expected PASS): CONTROL: a nested def `-> int` in a method and a nested def in a plain function keep `t - t == 0` (an unconstrained int over-approximates an int result; CPython 0).
"""
# pycsl-expected: PASS
class W:
    #@ ensures \result == 0
    def m(self) -> int:
        def g() -> int:
            return 3
        t = g()
        return t - t

#@ ensures \result == 0
def h(n: int) -> int:
    def k(z: int) -> int:
        return z
    v = k(n)
    return v - v

if __name__ == "__main__":
    assert W().m() == 0
    assert h(4) == 0
