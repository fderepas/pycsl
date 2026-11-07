from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ no_exception \all
def g(d: Dict[str, str]) -> int:
    return 1 if d.get("k") in "ab" else 0


#@ no_exception \all
def f(d: Dict[str, str]) -> int:
    return g(d)


if __name__ == "__main__":
    try:
        r = f({})
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
