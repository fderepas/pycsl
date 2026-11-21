r"""float literal 0.1 times 3 into int after scaling"""
_ = 0  # anchor


#@ ensures \result == 3
def probe() -> int:
    return int(0.1 * 3 * 10)


if __name__ == "__main__":
    print("CPython:", probe())
