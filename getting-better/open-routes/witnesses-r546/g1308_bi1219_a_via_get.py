from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

def g(d: Dict[str, int], k: int) -> Tuple[Any, int]:
    return (k, d.get("zz"))


#@ no_exception \all
def f(k: int) -> int:
    t = g({}, k)
    return t[1] + 1


if __name__ == "__main__":
    try:
        r = f(1)
        print('result', r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
