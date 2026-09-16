r"""G29 UNI-U1 — non-ASCII / escape string length (claim != truth; CPython 1)."""
_ = 0  # anchor


#@ ensures \result != 1
def probe() -> int:
    s = "é"
    return len(s)


if __name__ == "__main__":
    print("CPython:", probe())
