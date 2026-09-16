r"""G29 AS1 — an in-body `#@ assert` of a FALSE fact: an obligation, never an assumption."""
_ = 0  # anchor


#@ ensures \result == 7
def probe() -> int:
    x = 1
    #@ assert x == 7
    return x


if __name__ == "__main__":
    print("CPython:", probe())
