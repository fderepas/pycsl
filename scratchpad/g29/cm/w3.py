r"""G29 CM3 — `__exit__` mutates a field after the body."""
_ = 0  # anchor


class Ctx:
    def __init__(self) -> None:
        self.n = 0

    def __enter__(self) -> "Ctx":
        return self

    #@ assigns self.n
    def __exit__(self, a: object, b: object, c: object) -> bool:
        self.n = 9
        return False


#@ ensures \result == 0
def probe() -> int:
    c = Ctx()
    with c:
        pass
    return c.n


if __name__ == "__main__":
    print("CPython:", probe())
