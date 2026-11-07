r"""G29 K3 — collection semantics probe (claim != truth; CPython 2)."""
_ = 0  # anchor


#@ ensures \result != 2
def probe() -> int:
    d = {1: 2}
    d.setdefault(1, 9)
    return d[1]


if __name__ == "__main__":
    print("CPython:", probe())
