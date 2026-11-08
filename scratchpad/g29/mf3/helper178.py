from typing import Dict


def get(d: Dict[str, int]) -> int:
    return d["b"]


class C:
    def __init__(self) -> None:
        self.d: Dict[str, int] = {"a": 1}

    def get(self) -> int:
        return self.d["b"]
