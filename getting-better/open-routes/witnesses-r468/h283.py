from typing import List


def g(x: List[int]) -> None:
    import operator
    operator.iadd(x, [1])
