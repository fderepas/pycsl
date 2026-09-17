from typing import Dict, List

LIMIT = 3


def get(d: Dict[str, int]) -> int:
    return d["b"]


def idx(xs: List[int]) -> int:
    return xs[5]


def div(x: int) -> int:
    return 10 // x


class K:
    def __init__(self) -> None:
        self.d: Dict[str, int] = {"a": 1}

    def read(self) -> int:
        return self.d["zz"]
