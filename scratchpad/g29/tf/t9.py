r"""G29 T9 — nested try/finally probe (claim != truth; CPython 7)."""
_ = 0  # anchor


#@ ensures \result != 7
def probe() -> int:
    x = 0
    try:
        try:
            raise ValueError
        finally:
            x = 7
    except ValueError:
        pass
    return x


if __name__ == "__main__":
    try:
        print("CPython:", probe())
    except Exception as e:
        print("CPython raises", type(e).__name__)
