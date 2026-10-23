r"""G29 SC1 — a global-instance method call inside a contract."""
_ = 0  # anchor


class C:
    def __init__(self, x: int) -> None:
        self.x = x

    def val(self) -> int:
        return self.x + 1


_g = C(0)


#@ ensures \result == _g.val()
def probe() -> int:
    return _g.x


if __name__ == "__main__":
    print("CPython:", probe(), _g.val())
