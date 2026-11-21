r"""G29 CO-Z9 — the EMPTY list literal as a value (claim != truth; CPython 1)."""
_ = 0  # anchor


#@ ensures \result != 1
def probe() -> int:
    return 1 if not [] else 0


if __name__ == "__main__":
    print("CPython:", probe())
