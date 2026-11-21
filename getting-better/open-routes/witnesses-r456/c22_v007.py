from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

#@ no_exception \all
def f(s: Set[int], d: Dict[int, List[int]]) -> int:
    return len(s.difference(d.keys(), d.values()))


if __name__ == "__main__":
    try:
        r = f({1}, {1: [1]})
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
