r"""G29 ST-S11 — string method probe (claim != truth; CPython 3)."""
_ = 0  # anchor


#@ ensures \result != 3
def probe() -> int:
    s = "a b  c"
    return len(s.split())


if __name__ == "__main__":
    print("CPython:", probe())
