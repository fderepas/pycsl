r"""G29 NA4 — tuple lexicographic comparison: (1, 5) < (2, 0) is True."""
_ = 0  # anchor


#@ ensures \result == False
def probe() -> bool:
    return (1, 5) < (2, 0)


if __name__ == "__main__":
    print("CPython:", probe())
