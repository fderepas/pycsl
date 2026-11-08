r"""G29 LE-E5 — loop `else` clause probe (claim != truth; CPython 7)."""
_ = 0  # anchor


#@ ensures \result != 7
def probe() -> int:
    x = 0
    for i in range(0):
        x = 1
    else:
        x = 7
    return x


if __name__ == "__main__":
    print("CPython:", probe())
