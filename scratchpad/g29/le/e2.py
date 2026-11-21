r"""G29 LE-E2 — loop `else` clause probe (claim != truth; CPython 103)."""
_ = 0  # anchor


#@ ensures \result != 103
def probe() -> int:
    x = 0
    for i in range(3):
        x = x + i
    else:
        x = x + 100
    return x


if __name__ == "__main__":
    print("CPython:", probe())
