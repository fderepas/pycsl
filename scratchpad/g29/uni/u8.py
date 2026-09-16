r"""G29 UNI-U8 — non-ASCII / escape string length (claim != truth; CPython 3)."""
_ = 0  # anchor


#@ ensures \result != 3
def probe() -> int:
    s = "a\tb"
    return len(s)


if __name__ == "__main__":
    print("CPython:", probe())
