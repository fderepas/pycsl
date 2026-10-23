r"""G29 UNI-U4 — non-ASCII / escape string length (claim != truth; CPython 2)."""
_ = 0  # anchor


#@ ensures \result != 2
def probe() -> int:
    s = "日本"
    return len(s)


if __name__ == "__main__":
    print("CPython:", probe())
