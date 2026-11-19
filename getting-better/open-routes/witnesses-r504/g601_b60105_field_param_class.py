from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

class K:
    def __init__(self, n: int) -> None:
        self.a = n
        self.b = n


#@ requires k.a == k.b
#@ ensures \result == True
def f(k: K) -> bool:
    return k.a is k.b


if __name__ == "__main__":
    try:
        k = K(1000)
        k.b = int("1000")
        r = f(k)
        if r != True:
            print("VIOLATION contract", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
