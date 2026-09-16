r"""G29 UNI-U2 — non-ASCII / escape string length (claim != truth; CPython 1)."""
_ = 0  # anchor


#@ ensures \result != 1
def probe() -> int:
    s = "aé"
    return len(s[1:])


if __name__ == "__main__":
    print("CPython:", probe())
