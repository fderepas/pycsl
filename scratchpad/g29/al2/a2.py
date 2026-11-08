r"""G29 AL2-A2 — a record passed twice (aliased record arguments)."""
_ = 0  # anchor


class P:
    def __init__(self) -> None:
        self.x = 5


#@ ensures p.x == \old(p.x) + 1
#@ ensures q.x == \old(q.x)
#@ assigns p.x
def f(p: P, q: P) -> None:
    p.x = p.x + 1


#@ ensures \result == 5
def probe() -> int:
    o = P()
    f(o, o)
    return o.x


if __name__ == "__main__":
    print("CPython:", probe())
