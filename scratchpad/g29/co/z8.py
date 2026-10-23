r"""G29 CO-Z8 — the EMPTY list literal as a value (claim != truth; CPython 0)."""
_ = 0  # anchor


#@ ensures \result != 0
def probe() -> int:
    return len([x for x in []])


if __name__ == "__main__":
    print("CPython:", probe())
