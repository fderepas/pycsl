r"""Test 7864 -- route #496 (expected FAIL: PROVED at base, REFUSED PYCSL-R496-CALLEE-UNLISTED-CALL): g's `random.choice(xs)`; f catches IndexError; CPython f([]) returns 2 (red team 44 probe g516/o51605_random_choice_empty.py)
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ ensures \result == 1
def g(xs: List[int]) -> int:
    import random
    y = random.choice(xs)
    return 1


#@ ensures \result == 1
def f(xs: List[int]) -> int:
    try:
        return g(xs)
    except IndexError:
        return 2


if __name__ == "__main__":
    try:
        r = f([])
        if r != 1:
            print("VIOLATION contract", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
