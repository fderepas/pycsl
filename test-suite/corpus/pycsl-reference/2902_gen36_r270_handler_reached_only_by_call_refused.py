r"""Test 2902 — route #270 (expected FAIL, refused): the handler is reached only through the
call `C.g(1)` (no local read in the `try` body), so #264's graph left the handler UNREACHABLE
and never checked its read of `y`. CPython `f(False)`: `UnboundLocalError` inside the handler.
`\result >= 0` PROVED at c9d7f157.
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
        return y
    return 0

if __name__ == "__main__":
    try:
        print(f(False))
    except UnboundLocalError as exc:
        print("UnboundLocalError:", exc)
