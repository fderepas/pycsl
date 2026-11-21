r"""G29 P7 — `__init__` passes `self` to a MODULE FUNCTION that stores the field."""
_ = 0  # anchor


class P:
    def __init__(self) -> None:
        self.x = 1
        init_p(self)


#@ assigns p.x
def init_p(p: P) -> None:
    p.x = 7


#@ ensures \result == 1
#@ assigns \nothing
def probe() -> int:
    p = P()
    return p.x


if __name__ == "__main__":
    print("CPython:", probe())
