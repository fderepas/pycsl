r"""Test 5782 -- gen #37 route #402 (expected FAIL): the raising `__hash__` is inherited from the file base `B` by `D(B)`, hashed as `d: D` (CPython ValueError; PROVED at base 526d534de). REFUSED (PYCSL-R349-UNHASHABLE-RECORD: the MRO-resolved `__hash__`).
"""
# pycsl-expected: FAIL
class B:
    def __init__(self) -> None:
        self.x: int = 1

    def __hash__(self) -> int:
        if self.x == 1:
            raise ValueError("h")
        return 0


class D(B):
    pass


#@ no_exception \all
def f(d: D) -> int:
    s = {d}
    return len(s)


if __name__ == "__main__":
    try:
        print("result", f(D()))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
