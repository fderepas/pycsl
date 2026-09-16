r"""G29 A10 — arithmetic/sequence semantics probe (false claim; CPython 2)."""
_ = 0  # anchor


#@ ensures \result == 3
def probe() -> int:
    return True + True


if __name__ == "__main__":
    print("CPython:", probe())
