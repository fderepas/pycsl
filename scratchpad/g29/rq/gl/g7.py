r"""G29 GL7 — a statement-position call on a module-global instance whose tail `return` calls a mutator: the mutation is dropped with the discarded return value."""
_ = 0  # anchor


class C:
    def __init__(self, x: int) -> None:
        self.x = x

    #@ assigns self.x
    def bumpret(self) -> int:
        self.x = self.x + 1
        return self.x

    #@ assigns self.x
    def run(self) -> int:
        return self.bumpret()


_g = C(0)


#@ ensures \result == 0
def probe() -> int:
    a = _g.x
    _g.run()
    return _g.x - a


if __name__ == "__main__":
    print("CPython:", probe())
