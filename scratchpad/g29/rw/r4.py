r"""trusted callee raises-when understated"""
_ = 0  # anchor


#@ \trusted
#@ raises ValueError when x < 0
def f(x: int) -> int:
    if x <= 0:
        raise ValueError()
    return x


#@ no_exception ValueError
#@ ensures \result == 0
def probe() -> int:
    f(0)
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
