r"""bool arithmetic"""
_ = 0  # anchor


#@ ensures \result == 1
def probe() -> int:
    t = True
    return t + t


if __name__ == "__main__":
    print("CPython:", probe())
