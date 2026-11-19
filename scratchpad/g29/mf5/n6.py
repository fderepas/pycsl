_ = 0  # anchor


def div(x: int) -> int:
    return 10 // x


#@ no_exception ZeroDivisionError
#@ ensures \result == 0
def probe() -> int:
    v = div(0)
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
