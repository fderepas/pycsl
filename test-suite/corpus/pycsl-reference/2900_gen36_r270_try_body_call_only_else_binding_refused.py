r"""Test 2900 — route #270 (expected FAIL, refused): the `try` body is only a call that reads no
local (`C.g(1)`, declared `raises ValueError when x > 0`), so #264's must-assign graph had NO
exception edge into the handler and the `else`-path binding of `y` looked definite. CPython
`f(False)`: `C.g(1)` raises, the handler passes, `else` is skipped, `return y` raises
`UnboundLocalError`. `\result >= 0` PROVED at c9d7f157.
"""
# pycsl-expected: FAIL
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
    if c:
        y = 2
    try:
        C.g(1)
    except ValueError:
        pass
    else:
        y = 1
    return y

if __name__ == "__main__":
    try:
        print(f(False))
    except UnboundLocalError as exc:
        print("UnboundLocalError:", exc)
