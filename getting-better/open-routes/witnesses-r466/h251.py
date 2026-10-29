from dataclasses import dataclass


@dataclass
class P:
    xs: list[int] = []


def g(x: int) -> int:
    return x
