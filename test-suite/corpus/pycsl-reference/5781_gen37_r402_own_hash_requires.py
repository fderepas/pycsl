r"""Test 5781 -- gen #37 route #402 (expected FAIL): the own `__hash__` carries `#@ no_exception \all` under `#@ requires self.x != 1`; a hashing site does not discharge the precondition (CPython ValueError; PROVED at base 526d534de). REFUSED (PYCSL-R349-UNHASHABLE-RECORD: a verified `__hash__` has no `requires`).
"""
# pycsl-expected: FAIL
class D:
    def __init__(self) -> None:
        self.x: int = 1

    #@ requires self.x != 1
    #@ no_exception \all
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
