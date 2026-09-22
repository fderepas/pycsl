"""v73 DISAGREE — a BARE `return` is `None`, not the integer 0 (ROUTE #198)."""


def g(x: int) -> int:
    if x > 0:
        return
    return 5


#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    y = g(1)
    if y == 0:
        return 0
    return 7


if __name__ == "__main__":
    print(f())
