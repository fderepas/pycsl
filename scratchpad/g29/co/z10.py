r"""G29 CO-Z10 — the EMPTY list literal as a value (claim != truth; CPython 0)."""
_ = 0  # anchor


#@ ensures \result != 0
def probe() -> int:
    return sum(x + 1 for x in [])


if __name__ == "__main__":
    print("CPython:", probe())
