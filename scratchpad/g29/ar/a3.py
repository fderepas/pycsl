r"""G29 A3 — arithmetic/sequence semantics probe (false claim; CPython -1)."""
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    x = 7
    y = -2
    return x % y


if __name__ == "__main__":
    print("CPython:", probe())
