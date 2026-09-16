r"""G29 UNI-U5 — non-ASCII / escape string length (claim != truth; CPython 233)."""
_ = 0  # anchor


#@ ensures \result != 233
def probe() -> int:
    return ord("é")


if __name__ == "__main__":
    print("CPython:", probe())
