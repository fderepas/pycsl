from typing import Any, Protocol


class P(Protocol):
    def m(self) -> int:
        ...


#@ no_exception \all
def f(x: Any) -> bool:
    return isinstance(x, P)


if __name__ == "__main__":
    try:
        f(1)
        print("no violation")
    except TypeError as e:
        print("VIOLATION TypeError", e)
