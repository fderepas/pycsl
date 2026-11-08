r"""or with large"""
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    x = 1 << 64
    return (x | 1) - x


if __name__ == "__main__":
    print("CPython:", probe())
