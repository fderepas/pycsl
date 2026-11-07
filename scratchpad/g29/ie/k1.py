r"""G29 IE-K1 — an `ensures True` method whose handler path breaks the class invariant."""
_ = 0  # anchor


#@ class invariant self.x >= 0
class C:
    def __init__(self) -> None:
        self.x = 0

    #@ assigns self.x
    def m(self, s: str) -> None:
        try:
            v = int(s)
            self.x = 1
        except ValueError:
            self.x = -1


#@ ensures \result >= 0
def probe() -> int:
    c = C()
    c.m("1.5")
    return c.x


if __name__ == "__main__":
    print("CPython:", probe())
