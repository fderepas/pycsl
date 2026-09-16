r"""G29 ST-S3 — string method probe (claim != truth; CPython 2)."""
_ = 0  # anchor


#@ ensures \result != 2
def probe() -> int:
    s = "hello"
    return s.find("l")


if __name__ == "__main__":
    print("CPython:", probe())
