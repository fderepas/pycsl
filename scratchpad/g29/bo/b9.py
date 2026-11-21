r"""abs of min int like"""
_ = 0  # anchor


#@ ensures \result < 0
def probe() -> int:
    x = -(2 ** 63)
    return abs(x)


if __name__ == "__main__":
    print("CPython:", probe())
