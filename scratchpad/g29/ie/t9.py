r"""G29 IE-T9 — int overflow in float conversion via a division caught by ArithmeticError."""
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    try:
        f = 10 ** 400 / 3
    except ArithmeticError:
        return 9
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
