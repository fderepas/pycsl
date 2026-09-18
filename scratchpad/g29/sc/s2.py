r"""G29 SC2 — a record-method call inside a contract on a parameter."""
_ = 0  # anchor


class C:
    def __init__(self, x: int) -> None:
        self.x = x

    def val(self) -> int:
        return self.x + 1


#@ ensures \result == c.val()
def probe(c: C) -> int:
    return c.x


if __name__ == "__main__":
    print("CPython:", probe(C(0)), C(0).val())
