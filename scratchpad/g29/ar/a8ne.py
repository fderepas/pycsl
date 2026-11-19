r"""G29 A8 — arithmetic/sequence semantics probe (false claim; CPython 0)."""
_ = 0  # anchor


#@ ensures \result != 0
def probe() -> int:
    xs = [1] * -1
    return len(xs)


if __name__ == "__main__":
    print("CPython:", probe())
