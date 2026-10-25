from typing import Protocol


class P(Protocol):
    def m(self) -> int:
        ...


class Q(P, Protocol):
    pass


#@ no_exception \all
def f() -> None:
    Q()


if __name__ == "__main__":
    try:
        f()
        print("no violation")
    except TypeError as e:
        print("VIOLATION TypeError", e)
