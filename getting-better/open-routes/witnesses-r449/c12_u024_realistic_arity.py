from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

def parse(path: str, mode: int) -> int:
    return len(path) + mode



#@ no_exception \all
def f(path: str, mode: int) -> int:
    return parse(path, mode, True)


if __name__ == "__main__":
    try:
        r = f('x', 1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
