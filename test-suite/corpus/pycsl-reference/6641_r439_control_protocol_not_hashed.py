r"""Test 6641 -- route #439 (expected PASS): CONTROL: a file with a `Protocol` class and a `Callable` parameter that are NOT hashed, an `int` / `str` hashed under `no_exception \all`, and a typed field hashed (no computed-name store in the file), are not refused. PROVED at base and candidate.
"""
# pycsl-expected: PASS
from typing import Callable, Protocol

class Pr(Protocol):
    def __len__(self) -> int:
        ...


class R:
    def __init__(self, x: int) -> None:
        self.x: int = x


#@ no_exception \all
#@ ensures \result == n + 1
def f(c: Pr, cb: Callable[[], int], k: str, r: R, n: int) -> int:
    s = {k, "a"}
    u = {r.x}
    return n + 1


if __name__ == "__main__":
    try:
        r = f([1], lambda: 1, "k", R(2), 1)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
