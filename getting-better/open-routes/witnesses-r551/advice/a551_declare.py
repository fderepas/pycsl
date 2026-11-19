from typing import Any


class C:
    def __init__(self, s: Any) -> None:
        self.s = s


#@ no_exception \all
def f(k: int) -> int:
    v: Any = k
    c = C(v)
    return 1


if __name__ == "__main__":
    print(f(1))
