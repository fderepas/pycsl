class D:
    def __init__(self, n: int) -> None:
        self.n = n

    def hexdigest(self) -> str:
        return str(self.n)


class K:
    def __init__(self) -> None:
        self.c = 0

    def sha256(self, b: bytes) -> D:
        self.c = self.c + 1
        return D(self.c)
