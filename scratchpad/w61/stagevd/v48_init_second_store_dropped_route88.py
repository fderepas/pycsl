"""v48 DISAGREE — ROUTE #88. A scalar field's LAST store in `__init__` lost to its FIRST:
`_collect_class_fields` guarded every store with `target.attr not in field_names_seen`, so
the class emitted literally `{ n = 1 }`. CPython returns 2."""


class C:
    n: int

    #@ assigns self.n
    def __init__(self) -> None:
        self.n = 1
        self.n = 2


#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    c = C()
    return c.n


if __name__ == "__main__":
    print(f())
