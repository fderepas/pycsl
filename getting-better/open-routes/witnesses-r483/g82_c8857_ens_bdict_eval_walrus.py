from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

from h8807 import K


#@ ensures \result == n
def f(n: int) -> int:
    return n * K


if __name__ == "__main__":
    try:
        r = f(1)
        if r != 1:
            print('VIOLATION contract', r)
        else:
            print('result', r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
