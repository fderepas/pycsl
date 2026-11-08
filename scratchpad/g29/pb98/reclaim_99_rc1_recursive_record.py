from typing import List
_ = 0  # anchor


class Node:
    def __init__(self) -> None:
        self.v: int = 1
        self.kids: List[int] = []


#@ ensures \result == 99
def probe() -> int:
    n = Node()
    return n.v
