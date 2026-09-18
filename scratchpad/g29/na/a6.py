r"""G29 NA6 — chained comparison 1 < x > 0 with x = 5 is True."""
_ = 0  # anchor


#@ ensures \result == False
def probe() -> bool:
    x = 5
    return 1 < x > 0


if __name__ == "__main__":
    print("CPython:", probe())
