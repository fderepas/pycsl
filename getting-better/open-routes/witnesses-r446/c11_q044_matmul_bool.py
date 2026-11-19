from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

#@ no_exception \all
def f(a: bool) -> int:
    return a @ a


if __name__ == "__main__":
    try:
        r = f(True)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
