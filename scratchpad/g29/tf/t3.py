r"""G29 T3 — try/finally control-flow probe (claim != truth; CPython 3)."""
_ = 0  # anchor


#@ ensures \result != 3
def probe() -> int:
    x = 0
    for i in range(3):
        try:
            continue
        finally:
            x = x + 1
    return x


if __name__ == "__main__":
    print("CPython:", probe())
