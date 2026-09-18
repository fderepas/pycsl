r"""pow negative exponent int"""
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> float:
    x = 2
    return x ** -1


if __name__ == "__main__":
    print("CPython:", probe())
