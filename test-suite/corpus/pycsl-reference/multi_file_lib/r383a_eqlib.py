class D:
    def __init__(self, x: int) -> None:
        self.x = x

    def __eq__(self, other: object) -> bool:
        return isinstance(other, D) and other.x == self.x
