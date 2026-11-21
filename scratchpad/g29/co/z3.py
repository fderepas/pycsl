r"""G29 CO-Z3 — the EMPTY list literal as a value (claim != truth; CPython 0)."""
_ = 0  # anchor


#@ ensures \result != 0
def probe() -> int:
    return 1 if any(x == 0 for x in []) else 0


if __name__ == "__main__":
    print("CPython:", probe())
