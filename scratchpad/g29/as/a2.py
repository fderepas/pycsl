r"""G29 AS2 — a `#@ check` of a false fact then the same claim."""
_ = 0  # anchor


#@ ensures \result == 7
def probe() -> int:
    x = 1
    #@ check x == 7
    return x


if __name__ == "__main__":
    print("CPython:", probe())
