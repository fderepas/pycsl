r"""xor negative"""
_ = 0  # anchor


#@ ensures \result == 3
def probe() -> int:
    x = -4
    return x ^ 1


if __name__ == "__main__":
    print("CPython:", probe())
