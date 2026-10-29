from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

def h(x: int) -> int:
    for x0 in range(1):
        for x1 in range(1):
            for x2 in range(1):
                for x3 in range(1):
                    for x4 in range(1):
                        for x5 in range(1):
                            for x6 in range(1):
                                for x7 in range(1):
                                    for x8 in range(1):
                                        for x9 in range(1):
                                            for x10 in range(1):
                                                for x11 in range(1):
                                                    for x12 in range(1):
                                                        for x13 in range(1):
                                                            for x14 in range(1):
                                                                for x15 in range(1):
                                                                    for x16 in range(1):
                                                                        for x17 in range(1):
                                                                            for x18 in range(1):
                                                                                for x19 in range(1):
                                                                                    for x20 in range(1):
                                                                                        for x21 in range(1):
                                                                                            for x22 in range(1):
                                                                                                for x23 in range(1):
                                                                                                    for x24 in range(1):
                                                                                                        pass
    return 1


#@ no_exception \all
def f(n: int) -> int:
    return n + 1


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
