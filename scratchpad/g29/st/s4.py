r"""G29 ST-S4 — string method probe (claim != truth; CPython 3)."""
_ = 0  # anchor


#@ ensures \result != 3
def probe() -> int:
    s = "hello"
    return s.rfind("l")


if __name__ == "__main__":
    print("CPython:", probe())
