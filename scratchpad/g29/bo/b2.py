r"""invert"""
_ = 0  # anchor


#@ ensures \result == 4
def probe() -> int:
    x = 5
    return ~x + 10


if __name__ == "__main__":
    print("CPython:", probe())
