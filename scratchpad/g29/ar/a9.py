r"""G29 A9 — arithmetic/sequence semantics probe (false claim; CPython 3)."""
_ = 0  # anchor


#@ ensures \result == 4
def probe() -> int:
    return len(range(5, 0, -2))


if __name__ == "__main__":
    print("CPython:", probe())
