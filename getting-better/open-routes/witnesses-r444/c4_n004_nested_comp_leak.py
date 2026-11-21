from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

#@ no_exception \all
def f(xs: List[List[int]]) -> int:
    g = [y for x in xs for y in x]
    return y


if __name__ == "__main__":
    try:
        r = f([[1]])
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
