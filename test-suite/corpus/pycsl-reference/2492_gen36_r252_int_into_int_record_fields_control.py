r"""Test 2492 — route #252 (expected PASS): CONTROL: `int` values into `int` record fields (constructor
and store) keep integer field arithmetic.
"""
# pycsl-expected: PASS


class Box:
    def __init__(self, v: int, w: int):
        self.v: int = v
        self.w: int = w


#@ ensures \result == 0
#@ assigns \nothing
def f(n: int) -> int:
    b = Box(n, n)
    b.v = n + 1
    return b.v - b.w - 1


if __name__ == "__main__":
    assert f(5) == 0
