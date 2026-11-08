r"""G29 ST-S12 — string method probe (claim != truth; CPython 4)."""
_ = 0  # anchor


#@ ensures \result != 4
def probe() -> int:
    s = "hello"
    return s.index("o")


if __name__ == "__main__":
    print("CPython:", probe())
