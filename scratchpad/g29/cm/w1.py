r"""G29 CM1 — a context manager whose `__exit__` SUPPRESSES the exception."""
_ = 0  # anchor


class Quiet:
    def __init__(self) -> None:
        self.n = 0

    def __enter__(self) -> "Quiet":
        return self

    def __exit__(self, a: object, b: object, c: object) -> bool:
        return True


#@ ensures \result != 1
def probe() -> int:
    q = Quiet()
    with q:
        raise ValueError
    return 1


if __name__ == "__main__":
    print("CPython:", probe())
