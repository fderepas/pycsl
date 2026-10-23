r"""two-level field receiver to a guarded method"""
_ = 0  # anchor


class Leaf:
    def __init__(self, x: int) -> None:
        self.x = x

    #@ requires self.x != 0
    #@ ensures \result == 1
    def get(self) -> int:
        return self.x // self.x


class Mid:
    def __init__(self) -> None:
        self.leaf = Leaf(0)


class Top:
    def __init__(self) -> None:
        self.mid = Mid()

    #@ ensures \result == 5
    def run(self) -> int:
        self.mid.leaf.get()
        return 5


if __name__ == "__main__":
    print("CPython:", Top().run())
