from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

#@ no_exception \all
def f(s: str, t: str, u: str) -> int:
    y = s / t / u
    return 1


if __name__ == "__main__":
    try:
        r = f('a', 'b', 'c')
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
