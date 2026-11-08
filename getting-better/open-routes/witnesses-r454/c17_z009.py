from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

class P:
    def __init__(self, x: int) -> None:
        self.x = x



#@ no_exception \all
def f(b: bool) -> int:
    return len((*b,))


if __name__ == "__main__":
    try:
        r = f(True)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
