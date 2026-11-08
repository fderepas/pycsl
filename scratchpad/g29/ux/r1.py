r"""init raises via module helper"""
_ = 0  # anchor


def check(v: int) -> None:
    if v < 0:
        raise ValueError()


class C:
    def __init__(self, v: int) -> None:
        check(v)
        self.v = v


#@ ensures \result == 0
def probe() -> int:
    try:
        c = C(-1)
    except ValueError:
        return 9
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
