_ = 0  # anchor


def shift(x: int) -> int:
    return 1 << x


#@ ensures \result == 0
def probe() -> int:
    try:
        v = shift(-1)
    except ValueError:
        return 9
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
