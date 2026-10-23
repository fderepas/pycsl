r"""G29 CO-Z7 — the EMPTY list literal as a value (claim != truth; CPython 0)."""
_ = 0  # anchor


#@ ensures \result != 0
def probe() -> int:
    xs: list = []
    return 1 if 0 in xs else 0


if __name__ == "__main__":
    print("CPython:", probe())
