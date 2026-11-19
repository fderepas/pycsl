from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

def k0() -> bool:
    return True


#@ no_exception \all
def f(d: Dict[str, int]) -> int:
    return -(d.get("k") if k0() else 0)


if __name__ == "__main__":
    try:
        r = f({})
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
