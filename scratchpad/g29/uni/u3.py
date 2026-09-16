r"""G29 UNI-U3 — non-ASCII / escape string length (claim != truth; CPython 2)."""
_ = 0  # anchor


#@ ensures \result != 2
def probe() -> int:
    s = "é"
    return len(s.encode())


if __name__ == "__main__":
    print("CPython:", probe())
