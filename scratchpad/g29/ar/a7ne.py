r"""G29 A7 — arithmetic/sequence semantics probe (false claim; CPython 0)."""
_ = 0  # anchor


#@ ensures \result != 0
def probe() -> int:
    s = "abc"
    return len(s * -1)


if __name__ == "__main__":
    print("CPython:", probe())
