r"""constructor raising under no_exception ValueError"""
_ = 0  # anchor


class C:
    def __init__(self, v: int) -> None:
        if v < 0:
            raise ValueError()
        self.v = v


#@ no_exception ValueError
#@ ensures \result == 0
def probe() -> int:
    c = C(-1)
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
