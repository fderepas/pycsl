from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

@property
def size(p: str) -> int:
    return len(p)



#@ no_exception \all
def f(path: str) -> int:
    return size(path)


if __name__ == "__main__":
    try:
        r = f('ab')
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
