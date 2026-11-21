"""Advice of PYCSL-R461-IMPORT-RAISES followed on 7137: the computation `X = 1 // 0` MOVED into a function of the module (`compute_x(d)`, its divisor now a parameter the contract constrains), where it is verified."""
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

#@ requires d != 0
#@ no_exception \all
def compute_x(d: int) -> int:
    return 1 // d



#@ no_exception \all
def f(d: Dict[str, int], xs: List[int], n: int) -> int:
    return n


if __name__ == "__main__":
    try:
        r = f({}, [], 1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
