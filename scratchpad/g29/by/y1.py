r"""bytes index is int"""
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    b = b"A"
    return b[0]


if __name__ == "__main__":
    print("CPython:", probe())
