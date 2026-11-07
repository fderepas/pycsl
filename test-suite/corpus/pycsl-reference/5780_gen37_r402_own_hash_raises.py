r"""Test 5780 -- gen #37 route #402 (expected FAIL): the static class `D` defines its own `__hash__` that raises ValueError when `self.x == 1`; `{d}` under `no_exception \all` (CPython ValueError; PROVED at base 526d534de). REFUSED (PYCSL-R349-UNHASHABLE-RECORD: an own `__hash__` that is not a verified method counts as unhashable).
"""
# pycsl-expected: FAIL
class D:
    def __init__(self) -> None:
        self.x: int = 1

    def __hash__(self) -> int:
        if self.x == 1:
            raise ValueError("h")
        return 0


#@ no_exception \all
def f(d: D) -> int:
    s = {d}
    return len(s)


if __name__ == "__main__":
    try:
        print("result", f(D()))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
