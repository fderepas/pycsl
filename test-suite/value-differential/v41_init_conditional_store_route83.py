"""v41 DISAGREE — ROUTE #83. A field stored INSIDE CONTROL FLOW in `__init__` was never even
considered (`for stmt in child.body:  # top-level only`), so it took the literal `0`.
CPython returns 7."""


class C:
    v: int

    #@ assigns self.v
    def __init__(self, n: int) -> None:
        self.v: int = 0
        if n > 0:
            self.v = n


#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    c = C(7)
    return c.v


if __name__ == "__main__":
    print(f())
