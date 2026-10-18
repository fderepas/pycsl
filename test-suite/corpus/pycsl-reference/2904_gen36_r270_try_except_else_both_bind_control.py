r"""Test 2904 — route #270 CONTROL (expected PASS): the same `try: C.g(1)` shape as 2900, but the
handler ALSO binds `y`, so `y` is definitely assigned on the exception path and on the `else`
path. CPython `f(False), f(True)` = 0, 0.
"""
# pycsl-expected: PASS
class C:
    def __init__(self) -> None:
        self.n: int = 0

    @staticmethod
    #@ ensures \result == x
    #@ raises ValueError when x > 0
    #@ assigns \nothing
    def g(x: int) -> int:
        if x > 0:
            raise ValueError("p")
        return x

#@ ensures \result >= 0
#@ assigns \nothing
def f(c: bool) -> int:
    try:
        C.g(1)
    except ValueError:
        y = 0
    else:
        y = 1
    return y

if __name__ == "__main__":
    print(f(False), f(True))
