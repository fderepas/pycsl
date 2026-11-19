r"""module-global attribute receiver to a guarded method"""
_ = 0  # anchor


class Leaf:
    def __init__(self, x: int) -> None:
        self.x = x

    #@ requires self.x != 0
    #@ ensures \result == 1
    def get(self) -> int:
        return self.x // self.x


class Holder:
    def __init__(self) -> None:
        self.leaf = Leaf(0)


_h = Holder()


#@ ensures \result == 5
def probe() -> int:
    _h.leaf.get()
    return 5


if __name__ == "__main__":
    print("CPython:", probe())
