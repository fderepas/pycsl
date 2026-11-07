from typing import List


class W:
    def put(self, y: List[int]) -> None:
        y.append(1)


def g(x: List[int]) -> None:
    W().put(x)
