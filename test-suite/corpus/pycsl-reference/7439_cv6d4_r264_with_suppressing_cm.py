r"""Test 7439 -- cv6 D4 (expected FAIL, refused, route #264): a binding inside a `with` whose context manager SUPPRESSES the body's exception (`__exit__` returns True). The new non-suppressing allow-list (builtin `open`, `warnings.catch_warnings`) does not cover a user class, so `y` stays not definitely assigned. CPython: UnboundLocalError.
"""
# pycsl-expected: FAIL
class Sup:
    def __enter__(self) -> int:
        return 0

    def __exit__(self, a, b, c) -> bool:
        return True


def g() -> int:
    raise ValueError("x")


#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    with Sup():
        y = g()
    return y


if __name__ == "__main__":
    try:
        print("result", f())
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
