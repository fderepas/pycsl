r"""G29 ST-S5 — string method probe (claim != truth; CPython 7)."""
_ = 0  # anchor


#@ ensures \result != 7
def probe() -> int:
    s = "hello"
    return len(s.replace("l", "LL"))


if __name__ == "__main__":
    print("CPython:", probe())
