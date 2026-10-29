from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

#@ no_exception \all
def f(a: int, b: int) -> int:
    c = a
    c <<= b
    return 1


if __name__ == "__main__":
    try:
        r = f(1, 10**20)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
