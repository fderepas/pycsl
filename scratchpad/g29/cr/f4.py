r"""G29 F4 — #139 float carrier through a function taking the object."""
_ = 0  # anchor


class Cy:
    def __init__(self) -> None:
        self.r = 2.5


#@ requires True
#@ ensures \result == (1 if c.r > 2 else 0)
def big(c: Cy) -> int:
    if c.r > 2:
        return 1
    return 0


#@ ensures \result == 0
#@ assigns \nothing
def probe() -> int:
    return big(Cy())


if __name__ == "__main__":
    print("CPython:", probe())
