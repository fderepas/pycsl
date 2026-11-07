r"""control: tuple display unpack under no_exception ValueError"""
_ = 0  # anchor


#@ no_exception ValueError
#@ ensures \result == 3
def probe() -> int:
    a, b = 1, 2
    return a + b


if __name__ == "__main__":
    print("CPython:", probe())
