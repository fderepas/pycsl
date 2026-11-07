from typing import List


def g(x: List[int]) -> None:
    x.__iadd__([1])
