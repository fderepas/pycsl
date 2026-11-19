r"""G29 A13 — arithmetic/sequence semantics probe (false claim; CPython 3)."""
_ = 0  # anchor


#@ ensures \result == 4
def probe() -> int:
    s = "abcdef"
    return len(s[::-2])


if __name__ == "__main__":
    print("CPython:", probe())
