r"""float literal 1e23 is not exactly 10**23"""
_ = 0  # anchor


#@ ensures \result == 100000000000000000000000
def probe() -> int:
    return int(1e23)


if __name__ == "__main__":
    print("CPython:", probe())
