from typing import List, Dict, Any, Tuple, Optional

#@ ensures \result == 1
#@ assigns \nothing
#@ no_exception \all
def f(x: int) -> int:
    s = f"{x:>10}"
    return 1

if __name__ == "__main__":
    f(10**5000)
    print("no exception")
