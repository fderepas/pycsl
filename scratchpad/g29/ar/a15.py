r"""G29 A15 — arithmetic/sequence semantics probe (false claim; CPython 2)."""
_ = 0  # anchor


#@ ensures \result == 3
def probe() -> int:
    x = 1 << 65
    return x >> 64


if __name__ == "__main__":
    print("CPython:", probe())
