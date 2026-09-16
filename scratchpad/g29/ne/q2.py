r"""G29 NE-Q2 — `int(s)` on a string attribute of a record."""
_ = 0  # anchor


class P:
    def __init__(self) -> None:
        self.s = "abc"


#@ no_exception ValueError
def probe() -> int:
    p = P()
    return int(p.s)


if __name__ == "__main__":
    try:
        print("CPython:", probe())
    except Exception as e:
        print("CPython raises", type(e).__name__)
