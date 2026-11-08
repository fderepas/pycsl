r"""G29 CG-S3 — `__init__` writes a field of a RECORD field it just built."""
_ = 0  # anchor


class In:
    def __init__(self) -> None:
        self.v = 1


class C:
    def __init__(self) -> None:
        self.inner = In()
        self.inner.v = 9


#@ ensures \result == 1
#@ assigns \nothing
def probe() -> int:
    c = C()
    return c.inner.v


if __name__ == "__main__":
    print("CPython:", probe())
