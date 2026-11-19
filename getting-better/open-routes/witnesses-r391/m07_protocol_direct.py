from typing import Protocol


class P(Protocol):
    x: int


#@ no_exception \all
def f() -> None:
    P()


if __name__ == "__main__":
    try:
        f()
        print("no violation")
    except TypeError as e:
        print("VIOLATION TypeError", e)
