from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

from os.path import join



#@ no_exception \all
def f(x: str) -> int:
    if isinstance(x, (int, join)):
        return 1
    return 0


if __name__ == "__main__":
    try:
        r = f('a')
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
