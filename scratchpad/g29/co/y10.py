r"""G29 CO-Y10 — a STRING index past its end under no_exception IndexError."""
_ = 0  # anchor


#@ no_exception IndexError
def probe() -> str:
    s = "abc"
    return s[5]


if __name__ == "__main__":
    try:
        print("CPython:", probe())
    except Exception as e:
        print("CPython raises", type(e).__name__)
