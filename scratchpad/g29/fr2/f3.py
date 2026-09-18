r"""G29 FR2-3 — module function with `assigns \nothing` mutates a record argument's field."""
_ = 0  # anchor


class P:
    def __init__(self) -> None:
        self.x = 0


#@ assigns \nothing
def poke(p: P) -> None:
    p.x = 5


#@ ensures \result == 0
def probe() -> int:
    p = P()
    b = p.x
    poke(p)
    return p.x - b


if __name__ == "__main__":
    print("CPython:", probe())
