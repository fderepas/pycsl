"""v40 DISAGREE — ROUTE #79's widest carrier: a PARAMETERLESS `__init__` was never scanned at
all (`if not pset: break` fired first), so every computed field took the literal `0`. No
census written as "the complement of the capture rule" could reach it. CPython returns 9."""
K: int = 8


class C:
    x: int

    #@ assigns self.x
    def __init__(self) -> None:
        self.x = K + 1


#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    c = C()
    return c.x


if __name__ == "__main__":
    print(f())
