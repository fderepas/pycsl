r"""raises-when with handler in caller"""
_ = 0  # anchor


#@ raises ValueError when x < 0
def f(x: int) -> int:
    if x <= 0:
        raise ValueError()
    return x


#@ ensures \result == 0
def probe() -> int:
    try:
        f(0)
    except ValueError:
        return 9
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
