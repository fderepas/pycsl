r"""and of negatives"""
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    return -6 & 5


if __name__ == "__main__":
    print("CPython:", probe())
