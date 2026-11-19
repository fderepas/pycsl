r"""G29 FR6 — a RECORD parameter's field set through `setattr` under `assigns \nothing`."""
_ = 0  # anchor


class P:
    def __init__(self) -> None:
        self.x = 5


#@ assigns \nothing
def f(p: P) -> None:
    setattr(p, "x", 9)


#@ requires p.x == 5
#@ ensures \result == 5
def probe(p: P) -> int:
    f(p)
    return p.x


if __name__ == "__main__":
    print("CPython:", probe(P()))
