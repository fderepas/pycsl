r"""G29 T5 — try/finally control-flow probe (claim != truth; CPython 11)."""
_ = 0  # anchor


#@ ensures \result != 11
def probe() -> int:
    x = 0
    try:
        x = 1
    except ValueError:
        x = 2
    else:
        x = x + 10
    return x


if __name__ == "__main__":
    print("CPython:", probe())
