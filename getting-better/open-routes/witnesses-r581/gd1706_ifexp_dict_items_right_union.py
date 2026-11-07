from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ no_exception \all
def f(m: Dict[str, str], c: bool) -> int:
    x = m.items() if c else {}
    return len(x | {"z"})


if __name__ == "__main__":
    try:
        print("result", repr(f({"a": "x"}, False))[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
