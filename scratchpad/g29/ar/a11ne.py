r"""G29 A11 — arithmetic/sequence semantics probe (false claim; CPython -3)."""
_ = 0  # anchor


#@ ensures \result != -3
def probe() -> int:
    x = -7
    y = 2
    return int(x / y)


if __name__ == "__main__":
    print("CPython:", probe())
