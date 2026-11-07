r"""G29 A2 — arithmetic/sequence semantics probe (false claim; CPython 1)."""
_ = 0  # anchor


#@ ensures \result != 1
def probe() -> int:
    x = -7
    return x % 2


if __name__ == "__main__":
    print("CPython:", probe())
