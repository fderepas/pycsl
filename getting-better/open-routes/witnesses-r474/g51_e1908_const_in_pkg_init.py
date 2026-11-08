from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

from p1908 import K


#@ no_exception \all
def f(n: int) -> int:
    return n // K


if __name__ == "__main__":
    try:
        print('result', f(1))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
