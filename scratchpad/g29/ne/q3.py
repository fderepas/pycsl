r"""G29 NE-Q3 — `int(s[0:2])` on a string slice."""
_ = 0  # anchor


#@ no_exception ValueError
def probe() -> int:
    s = "abcd"
    return int(s[0:2])


if __name__ == "__main__":
    try:
        print("CPython:", probe())
    except Exception as e:
        print("CPython raises", type(e).__name__)
