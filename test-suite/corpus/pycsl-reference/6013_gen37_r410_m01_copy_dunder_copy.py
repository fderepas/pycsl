r"""Test 6013 -- gen #37 route #410 (expected FAIL): red team 32 witness `m01_copy_dunder_copy` -- `copy.copy` / `copy.replace` of a class that overrides the copy protocol (PROVED at base 4431ef86f; CPython violates, see the driver). REFUSED (PYCSL-R349-UNHASHABLE-RECORD: a class whose closure binds `__copy__` / `__replace__` / ... has an UNKNOWN copy class).
"""
# pycsl-expected: FAIL
import copy


class D:
    def __init__(self) -> None:
        self.x: int = 1

    def __copy__(self) -> list:
        return [1]


#@ no_exception \all
def f(d: D) -> int:
    s = {copy.copy(d)}
    return len(s)


if __name__ == "__main__":
    try:
        r = f(D())
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
