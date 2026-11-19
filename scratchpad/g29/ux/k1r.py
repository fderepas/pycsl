r"""constructor raising: caller declares no raises; the constructor's field assignment after the raise"""
_ = 0  # anchor


class C:
    def __init__(self, v: int) -> None:
        if v < 0:
            raise ValueError()
        self.v = v


#@ ensures \result == -1
def probe() -> int:
    c = C(-1)
    return c.v


if __name__ == "__main__":
    print("CPython:", probe())
