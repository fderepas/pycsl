r"""G29 ST-S7 — string method probe (claim != truth; CPython 1)."""
_ = 0  # anchor


#@ ensures \result != 1
def probe() -> int:
    s = "hello"
    return 1 if "ll" in s else 0


if __name__ == "__main__":
    print("CPython:", probe())
