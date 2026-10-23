r"""G29 ST-S2 — string method probe (claim != truth; CPython 2)."""
_ = 0  # anchor


#@ ensures \result != 2
def probe() -> int:
    s = "  ab  "
    return len(s.strip())


if __name__ == "__main__":
    print("CPython:", probe())
