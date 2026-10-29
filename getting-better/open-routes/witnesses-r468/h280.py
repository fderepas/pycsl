from typing import List


def g(x: List[int]) -> None:
    def k() -> None:
        x.append(1)
    k()
