from typing import List, Dict, Any, Tuple, Optional

#@ ensures \result == 1
#@ assigns \nothing
#@ no_exception \all
def f(x: int, s: str) -> int:
    t = f"{x:.2}"
    return 1

if __name__ == "__main__":
    f(5, "ab")
    print("no exception")
