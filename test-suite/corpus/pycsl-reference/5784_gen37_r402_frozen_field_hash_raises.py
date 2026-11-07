r"""Test 5784 -- gen #37 route #402 (expected FAIL): a frozen `@dataclass R` with a field of class `K` whose `__hash__` raises; `{r}` hashes the field (CPython ValueError; PROVED at base 526d534de). REFUSED (PYCSL-R349-UNHASHABLE-RECORD: the field fixpoint).
"""
# pycsl-expected: FAIL
from dataclasses import dataclass


class K:
    def __init__(self) -> None:
        self.x: int = 1

    def __hash__(self) -> int:
        if self.x == 1:
            raise ValueError("h")
        return 0


@dataclass(frozen=True)
class R:
    k: K


#@ no_exception \all
def f(r: R) -> int:
    s = {r}
    return len(s)


if __name__ == "__main__":
    try:
        print("result", f(R(K())))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
