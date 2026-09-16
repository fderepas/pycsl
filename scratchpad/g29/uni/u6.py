r"""G29 UNI-U6 — non-ASCII / escape string length (claim != truth; CPython 2)."""
_ = 0  # anchor


#@ ensures \result != 2
def probe() -> int:
    s = "aéb"
    return s.find("b")


if __name__ == "__main__":
    print("CPython:", probe())
