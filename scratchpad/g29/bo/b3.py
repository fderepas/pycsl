r"""right shift negative"""
_ = 0  # anchor


#@ ensures \result == -2
def probe() -> int:
    x = -7
    return x >> 2


if __name__ == "__main__":
    print("CPython:", probe())
