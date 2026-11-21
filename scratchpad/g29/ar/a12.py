r"""G29 A12 — arithmetic/sequence semantics probe (false claim; CPython -8)."""
_ = 0  # anchor


#@ ensures \result == -7
def probe() -> int:
    return pow(-2, 3)


if __name__ == "__main__":
    print("CPython:", probe())
