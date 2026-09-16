r"""G29 F16 — route #148 control: an INTEGRAL float literal `2.0` is still carried (value 2)."""
_ = 0  # anchor


class Cy:
    def __init__(self) -> None:
        self.r = 2.0


#@ ensures \result == 1
#@ assigns \nothing
def probe() -> int:
    c = Cy()
    if c.r > 1:
        return 1
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
