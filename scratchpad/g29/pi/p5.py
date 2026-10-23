r"""G29 P5 — `__init__` stores through a local ALIAS of self."""
_ = 0  # anchor


class P:
    def __init__(self) -> None:
        self.x = 1
        me = self
        me.x = 7


#@ ensures \result == 1
#@ assigns \nothing
def probe() -> int:
    p = P()
    return p.x


if __name__ == "__main__":
    print("CPython:", probe())
