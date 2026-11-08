from typing import Any, Dict, List, Optional, Set, Tuple, Union

#@ no_exception \all
def f(x: float) -> int:
    return x.bit_length()


if __name__ == "__main__":
    try:
        r = f(1.5)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
