r"""Test 7441 -- cv6 D4 (expected FAIL, refused, route #264): `with warnings.catch_warnings():` where `warnings` is a PARAMETER holding a suppressing manager. The allow-list admits `m.catch_warnings(...)` only when `m` is bound in the file solely by `import warnings [as m]`. CPython: UnboundLocalError.
"""
# pycsl-expected: FAIL
class Sup:
    def __enter__(self) -> int:
        return 0

    def __exit__(self, a, b, c) -> bool:
        return True

    def catch_warnings(self) -> "Sup":
        return self


def g() -> int:
    raise ValueError("x")


#@ ensures \result == 1
#@ assigns \nothing
def f(warnings: Sup) -> int:
    with warnings.catch_warnings():
        y = g()
    return y


if __name__ == "__main__":
    try:
        print("result", f(Sup()))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
