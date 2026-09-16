r"""G29 H1 — route #149 x #147: an INHERITED constructor with an omitted positional default."""
_ = 0  # anchor


class Ay:
    def __init__(self, r: int = 5) -> None:
        self.r = r

    #@ requires True
    #@ ensures \result == self.r
    def get(self) -> int:
        return self.r


class Bee(Ay):
    pass


#@ ensures \result == 5
#@ assigns \nothing
def probe() -> int:
    b = Bee()
    return b.get()


if __name__ == "__main__":
    print("CPython:", probe())
