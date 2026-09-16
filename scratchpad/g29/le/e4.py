r"""G29 LE-E4 — loop `else` clause probe (claim != truth; CPython 5)."""
_ = 0  # anchor


#@ ensures \result != 5
def probe() -> int:
    x = 0
    i = 0
    while i < 3:
        i = i + 1
    else:
        x = 5
    return x


if __name__ == "__main__":
    print("CPython:", probe())
