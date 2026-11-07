r"""G29 MD4 — int() of a string literal and len(str(n))."""
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    return int("12") + len(str(-40)) - 12


if __name__ == "__main__":
    print("CPython:", probe())
