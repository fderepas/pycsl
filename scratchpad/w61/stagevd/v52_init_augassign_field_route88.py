"""v52 DISAGREE — ROUTE #88's AugAssign carrier, which was ALSO A SURVIVOR OF ROUTE #83's
REPAIR in its nested spelling: #83's walk tests `ast.Assign`/`ast.AnnAssign` only, so an
augmented store matched neither guard. The field is now `(any int)` — unconstrained, which is
the honest answer since an augmented store is not reducible to a record literal. CPython
returns 5."""


class C:
    n: int

    #@ assigns self.n
    def __init__(self) -> None:
        self.n = 0
        self.n += 5


#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    c = C()
    return c.n


if __name__ == "__main__":
    print(f())
