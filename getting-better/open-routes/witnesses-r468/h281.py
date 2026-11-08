from typing import List


def g(x: List[int]) -> None:
    (lambda: x.append(1))()
