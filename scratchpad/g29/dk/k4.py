r"""G29 K4 — collection semantics probe (claim != truth; CPython 7)."""
_ = 0  # anchor


#@ ensures \result != 7
def probe() -> int:
    d = {1: 2}
    return d.pop(5, 7)


if __name__ == "__main__":
    print("CPython:", probe())
