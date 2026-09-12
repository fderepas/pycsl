"""v50 DISAGREE — ROUTE #88 IN THE OTHER DIRECTION. `_collect_init_construction` APPENDED to
`init_body`, so an earlier PARAM-dependent store survived a later literal one that superseded
it. Paired with v48 this says the model had no notion of store ORDER at all, rather than a
preference for literals. CPython returns 3."""


class C:
    n: int

    #@ assigns self.n
    def __init__(self, k: int) -> None:
        self.n = k
        self.n = 3


#@ ensures \result == 7
#@ assigns \nothing
def f() -> int:
    c = C(7)
    return c.n


if __name__ == "__main__":
    print(f())
