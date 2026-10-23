r"""G29 CO-Z4 — the EMPTY list literal as a value (claim != truth; CPython 0)."""
_ = 0  # anchor


#@ ensures \result != 0
def probe() -> int:
    n = 0
    for x in []:
        n = n + 1
    return n


if __name__ == "__main__":
    print("CPython:", probe())
