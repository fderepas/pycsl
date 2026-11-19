from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

class Q:
    @staticmethod
    def m() -> int:
        return None

    @staticmethod
    def p() -> int:
        return Q.m()


#@ no_exception \all
def f(k: int) -> int:
    return Q.p() + 1


if __name__ == "__main__":
    try:
        r = f(1)
        print('result', r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
