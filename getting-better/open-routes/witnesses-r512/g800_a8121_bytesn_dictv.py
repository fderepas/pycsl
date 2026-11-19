from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ no_exception \all
def f(n: int, c: bool) -> int:
    v = {"k": bytes(n)}
    return 1


if __name__ == "__main__":
    try:
        r = f(10**20, False)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
