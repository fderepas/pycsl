r"""Test 7440 -- cv6 D4 (expected FAIL, refused, route #264): `with open("x"):` where `open` is a SAME-FILE function returning a suppressing manager. The allow-list admits `open` only when the name is bound nowhere in the file, so the binding in the body stays not definite. CPython: UnboundLocalError.
"""
# pycsl-expected: FAIL
class Sup:
    def __enter__(self) -> int:
        return 0

    def __exit__(self, a, b, c) -> bool:
        return True


def open(p: str) -> Sup:
    return Sup()


def g() -> int:
    raise ValueError("x")


#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    with open("x"):
        y = g()
    return y


if __name__ == "__main__":
    try:
        print("result", f())
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
