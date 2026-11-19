r"""G29 A6 — arithmetic/sequence semantics probe (false claim; CPython -6)."""
_ = 0  # anchor


#@ ensures \result == -5
def probe() -> int:
    x = 5
    return ~x


if __name__ == "__main__":
    print("CPython:", probe())
