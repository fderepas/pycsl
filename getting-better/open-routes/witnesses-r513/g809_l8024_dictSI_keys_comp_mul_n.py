from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ no_exception \all
def f(d: Dict[str, int], n: int) -> int:
    v = [k * n for k in d]
    return 1


if __name__ == "__main__":
    try:
        r = f({"ab": 1}, 10**20)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
