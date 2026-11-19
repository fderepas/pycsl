r"""G29 T11 — nested try/finally probe (claim != truth; CPython 99)."""
_ = 0  # anchor


#@ ensures \result != 99
def probe() -> int:
    x = 0
    for i in range(2):
        try:
            if i == 1:
                raise ValueError
        finally:
            x = x + 1
    return x


if __name__ == "__main__":
    try:
        print("CPython:", probe())
    except Exception as e:
        print("CPython raises", type(e).__name__)
