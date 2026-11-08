from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

class C:
    def __init__(self, n: int) -> None:
        self.__x = n


class D(C):
    def get(self) -> int:
        return self.__x


#@ no_exception \all
def f(n: int) -> int:
    return D(n).get()


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
