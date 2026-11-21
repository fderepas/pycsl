r"""G29 A1 — arithmetic/sequence semantics probe (false claim; CPython -4)."""
_ = 0  # anchor


#@ ensures \result != -4
def probe() -> int:
    x = -7
    return x // 2


if __name__ == "__main__":
    print("CPython:", probe())
