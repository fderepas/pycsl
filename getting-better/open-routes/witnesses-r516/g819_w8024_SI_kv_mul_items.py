from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ no_exception \all
def f(d: Dict[str, int]) -> int:
    for k, v in d.items():
        w = k * v
    return 1


if __name__ == "__main__":
    try:
        r = f({"ab": 10**20})
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
