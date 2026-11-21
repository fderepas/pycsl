from typing import Dict, List, Optional


#@ no_exception \all
def g(x: int) -> int:
    return x + 1


#@ no_exception \all
def gl(x: int) -> int:
    return len([1, 2][x:])


class DC:
    #@ no_exception \all
    def __init__(self, x: int) -> None:
        self.x = x + 1
