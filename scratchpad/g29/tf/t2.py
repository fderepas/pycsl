r"""G29 T2 — try/finally control-flow probe (claim != truth; CPython 111)."""
_ = 0  # anchor


#@ ensures \result != 111
def probe() -> int:
    x = 0
    try:
        x = 1
        raise ValueError
    except ValueError:
        x = x + 10
    finally:
        x = x + 100
    return x


if __name__ == "__main__":
    print("CPython:", probe())
