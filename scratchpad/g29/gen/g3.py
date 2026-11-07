r"""G29 GEN3 — `list()` of a user generator."""
from typing import Iterator, List
_ = 0  # anchor


def gen() -> Iterator[int]:
    yield 7


#@ ensures \result != 1
def probe() -> int:
    xs: List[int] = list(gen())
    return len(xs)


if __name__ == "__main__":
    print("CPython:", probe())
