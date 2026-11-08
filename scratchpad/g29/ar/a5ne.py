r"""G29 A5 — arithmetic/sequence semantics probe (false claim; CPython -1)."""
_ = 0  # anchor


#@ ensures \result != -1
def probe() -> int:
    x = -1
    return x >> 1


if __name__ == "__main__":
    print("CPython:", probe())
