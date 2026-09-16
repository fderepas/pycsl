r"""G29 G3 — route #149 draft: a POSITIONAL `bool` default read as a truth value."""
_ = 0  # anchor


class Cy:
    def __init__(self, flag: bool = True) -> None:
        self.flag = flag


#@ ensures \result == 0
#@ assigns \nothing
def probe() -> int:
    c = Cy()
    if c.flag:
        return 1
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
