r"""G29 T6 — try/finally control-flow probe (claim != truth; CPython 8)."""
_ = 0  # anchor


#@ ensures \result != 8
def probe() -> int:
    x = 0
    try:
        try:
            raise ValueError
        finally:
            x = 7
    except ValueError:
        x = x + 1
    return x


if __name__ == "__main__":
    print("CPython:", probe())
