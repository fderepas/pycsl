r"""G29 F1 — carrier-rerun on gen #27's #139 `field_defaults` arm: `int(rhs.value)` on a FLOAT
literal records 2 for `self.r = 2.5`. Read it through a comparison that types as bool/int."""
_ = 0  # anchor


class Cy:
    def __init__(self) -> None:
        self.r = 2.5

    #@ requires True
    #@ ensures True
    def big(self) -> int:
        if self.r > 2:
            return 1
        return 0


#@ ensures \result == 0
#@ assigns \nothing
def probe() -> int:
    c = Cy()
    return c.big()


if __name__ == "__main__":
    print("CPython:", probe())
