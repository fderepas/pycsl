from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

K = 5


class C:
    #@ ensures \result == 5
    def m[K](self) -> int:
        return K


if __name__ == "__main__":
    try:
        r = C().m()
        if r != 5:
            print("VIOLATION contract", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
