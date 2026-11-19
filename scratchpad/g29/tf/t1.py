r"""G29 T1 — try/finally control-flow probe (claim != truth; CPython 2)."""
_ = 0  # anchor


#@ ensures \result != 2
def probe() -> int:
    try:
        return 1
    finally:
        return 2


if __name__ == "__main__":
    print("CPython:", probe())
