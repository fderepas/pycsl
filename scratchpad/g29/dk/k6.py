r"""G29 K6 — collection semantics probe (claim != truth; CPython 2)."""
_ = 0  # anchor


#@ ensures \result != 2
def probe() -> int:
    s = {1, 1, 2}
    return len(s)


if __name__ == "__main__":
    print("CPython:", probe())
