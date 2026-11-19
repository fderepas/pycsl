from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

from h707 import S


#@ ensures \result == 1
def f(n: int) -> int:
    return 1 if S == 'é' else 0


if __name__ == "__main__":
    try:
        r = f(1)
        if not (r == 1):
            print('VIOLATION contract', r)
        else:
            print('result', r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
