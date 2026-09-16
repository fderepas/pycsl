r"""G29 GEN2 — a generator with a return value stops early."""
from typing import Iterator
_ = 0  # anchor


def gen(n: int) -> Iterator[int]:
    i = 0
    while i < n:
        if i == 2:
            return
        yield i
        i = i + 1


#@ ensures \result != 1
def probe() -> int:
    t = 0
    for x in gen(5):
        t = t + x
    return t


if __name__ == "__main__":
    print("CPython:", probe())
