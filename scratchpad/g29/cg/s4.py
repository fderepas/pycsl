r"""G29 CG-S4 — route #153 carrier: a parameter rebound by a `match` CAPTURE pattern."""
_ = 0  # anchor


class C:
    def __init__(self, k: int) -> None:
        match 7:
            case k:
                pass
        self.x = k


#@ ensures \result == 5
#@ assigns \nothing
def probe() -> int:
    c = C(5)
    return c.x


if __name__ == "__main__":
    print("CPython:", probe())
