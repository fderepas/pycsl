r"""G29 GL-H4 — argument expression with a global call evaluated twice? actual is non-trivial."""
_ = 0  # anchor


class C:
    def __init__(self, x: int) -> None:
        self.x = x

    #@ assigns self.x
    def bump(self) -> int:
        self.x = self.x + 1
        return self.x

    def twice(self, d: int) -> int:
        return d + d


_g = C(0)


#@ ensures \result == 3
def probe() -> int:
    a = _g.x
    r = _g.twice(_g.bump())
    return r - 2 * a + _g.x - a
if __name__ == "__main__":
    print("CPython:", probe())
