"""v49 AGREE — ROUTE #88's completeness gain. The field's default is now taken from its LAST
top-level store, so the TRUE claim PROVES where it was refused before. The AGREE direction is
what stops this gate being satisfiable by refusing everything, and it independently confirms
#88 was closed by a FAITHFUL CAPTURE rather than a refusal. CPython returns 2."""


class C:
    n: int

    #@ assigns self.n
    def __init__(self) -> None:
        self.n = 1
        self.n = 2


#@ ensures \result == 2
#@ assigns \nothing
def f() -> int:
    c = C()
    return c.n


if __name__ == "__main__":
    print(f())
