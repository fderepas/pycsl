from typing import Any, Dict, List, Optional, Set, Tuple, Union

#@ no_exception \all
def f(count: int) -> int:
    return len(count) if count > 0 else 0


if __name__ == "__main__":
    try:
        r = f(3)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
