r"""join over generator of missing keys"""
from typing import Dict, List
_ = 0  # anchor


#@ no_exception KeyError
#@ ensures \result == 0
def probe() -> int:
    d: Dict[str, str] = {"a": "x"}
    s = "".join(d[k] for k in ["b"])
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
