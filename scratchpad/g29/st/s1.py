r"""G29 ST-S1 — string method probe (claim != truth; CPython 4)."""
_ = 0  # anchor


#@ ensures \result != 4
def probe() -> int:
    s = "a,b,,c"
    return len(s.split(","))


if __name__ == "__main__":
    print("CPython:", probe())
