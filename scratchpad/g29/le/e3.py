r"""G29 LE-E3 — loop `else` clause probe (claim != truth; CPython 0)."""
_ = 0  # anchor


#@ ensures \result != 0
def probe() -> int:
    x = 0
    i = 0
    while i < 3:
        i = i + 1
        if i == 2:
            break
    else:
        x = 5
    return x


if __name__ == "__main__":
    print("CPython:", probe())
