from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

class Q:
    @staticmethod
    def m(k: int) -> int:
        return None


#@ no_exception \all
def f(k: int) -> int:
    return Q.m(k) + 1


if __name__ == "__main__":
    try:
        r = f(0)
        print('result', r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
