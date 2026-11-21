r"""Test 5307 -- gen #37 route #387 (expected FAIL): annotated `K: int = 5` under `if False:` in a class body, `C.K == 5`; FAIL at base, REFUSED after (route #387).
"""
# pycsl-expected: FAIL
class C:
    def __init__(self) -> None:
        self.n: int = 0

    if False:
        K: int = 5


#@ ensures \result == 5
def f() -> int:
    return C.K


if __name__ == "__main__":
    try:
        r = f()
        print("VIOLATION f =", r) if r != 5 else print("no violation")
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
