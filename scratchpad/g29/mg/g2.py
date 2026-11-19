r"""G29 MG2 — route #150 through a MODULE-GLOBAL instance: `G = C()` whose `__init__` calls a helper."""
_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.r = 1
        self._setup()

    #@ assigns self.r
    def _setup(self) -> None:
        self.r = 7


G = C()


#@ ensures \result == 1
def probe() -> int:
    return G.r


if __name__ == "__main__":
    print("CPython:", probe())
