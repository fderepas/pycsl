r"""G29 T8 — nested try/finally probe (claim != truth; CPython 7)."""
_ = 0  # anchor


#@ ensures \result != 7
def probe() -> int:
    x = 0
    try:
        try:
            x = 1
        finally:
            x = 7
    except ValueError:
        x = 100
    return x


if __name__ == "__main__":
    try:
        print("CPython:", probe())
    except Exception as e:
        print("CPython raises", type(e).__name__)
