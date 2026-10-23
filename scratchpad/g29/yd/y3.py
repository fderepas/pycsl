r"""yield inside a loop"""
from typing import List, Iterator, Generator
_ = 0  # anchor


def gen(n: int) -> Iterator[int]:
    for i in range(n):
        yield i


#@ ensures \result == 0
def probe() -> int:
    s = 0
    for x in gen(3):
        s = s + x
    return s


if __name__ == "__main__":
    print("CPython:", probe())
