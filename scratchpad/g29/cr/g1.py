r"""G29 G1 — route #82's own deferral: "a non-constant [keyword-only] default stays omitted and is
route #79's class". An omitted keyword-only argument whose default is a MODULE CONSTANT."""
_ = 0  # anchor
K = 5


class Cy:
    def __init__(self, *, r: int = K) -> None:
        self.r = r


#@ ensures \result == 0
#@ assigns \nothing
def probe() -> int:
    c = Cy()
    if c.r > 2:
        return 1
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
