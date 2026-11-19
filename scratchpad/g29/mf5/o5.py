_ = 0  # anchor


def shift(x: int) -> int:
    return 1 << x


#@ no_exception ValueError
#@ ensures \result == 0
def probe() -> int:
    v = shift(-1)
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
