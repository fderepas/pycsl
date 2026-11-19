r"""G29 K5 — collection semantics probe (claim != truth; CPython 1)."""
_ = 0  # anchor


#@ ensures \result != 1
def probe() -> int:
    d = {1: 2, 3: 4}
    d.pop(1)
    return len(d)


if __name__ == "__main__":
    print("CPython:", probe())
