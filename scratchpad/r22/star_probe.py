from typing import List


class P:
    def __init__(self):
        self.n = 0

    def sink(self, p, *nodes):
        self.n = self.n + len(nodes) + p

    def caller_star_only(self, xs: List[int]):
        self.sink(1, *xs)

    def caller_mixed(self, a: int, xs: List[int]):
        self.sink(1, a, *xs)
