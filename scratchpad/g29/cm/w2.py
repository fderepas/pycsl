r"""G29 CM2 — `__enter__` mutates a field; the `with` body reads it."""
_ = 0  # anchor


class Ctx:
    def __init__(self) -> None:
        self.n = 0

    #@ assigns self.n
    def __enter__(self) -> "Ctx":
        self.n = 5
        return self

    def __exit__(self, a: object, b: object, c: object) -> bool:
        return False


#@ ensures \result == 0
def probe() -> int:
    c = Ctx()
    with c:
        r = c.n
    return r


if __name__ == "__main__":
    print("CPython:", probe())
