# Advice probe (route #457): witness 6864 with the claim dropped.
from json import loads


def f(x: int) -> int:
    if isinstance(x, loads):
        return 1
    return 0
