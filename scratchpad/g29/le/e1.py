r"""G29 LE-E1 — loop `else` clause probe (claim != truth; CPython 0)."""
_ = 0  # anchor


#@ ensures \result != 0
def probe() -> int:
    x = 0
    for i in range(3):
        if i == 1:
            break
    else:
        x = 5
    return x


if __name__ == "__main__":
    print("CPython:", probe())
