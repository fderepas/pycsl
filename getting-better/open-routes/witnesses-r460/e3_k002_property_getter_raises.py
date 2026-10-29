from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

class C:
    def __init__(self, d: Dict[str, int]) -> None:
        self.d = d

    @property
    def v(self) -> int:
        return self.d['k']



#@ no_exception \all
def f(d: Dict[str, int]) -> int:
    c = C(d)
    return c.v


if __name__ == "__main__":
    try:
        r = f({})
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
