r"""G29 T4 — try/finally control-flow probe (claim != truth; CPython 5)."""
_ = 0  # anchor


#@ ensures \result != 5
def probe() -> int:
    x = 0
    while True:
        try:
            break
        finally:
            x = 5
    return x


if __name__ == "__main__":
    print("CPython:", probe())
