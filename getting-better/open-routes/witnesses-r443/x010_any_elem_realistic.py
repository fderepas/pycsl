from typing import Any, Dict, List, Optional, Set, Tuple, Union

#@ no_exception \all
def f(row: List[Any]) -> int:
    return len(row[0].strip()) if len(row) > 0 else 0


if __name__ == "__main__":
    try:
        r = f([42])
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
