r"""G29 ST-S10 — string method probe (claim != truth; CPython 99)."""
_ = 0  # anchor


#@ ensures \result != 99
def probe() -> int:
    s = "abc"
    return ord(s[-1])


if __name__ == "__main__":
    print("CPython:", probe())
