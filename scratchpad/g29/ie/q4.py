r"""sorted with key lambda subscript"""
from typing import Dict, List
_ = 0  # anchor


#@ no_exception KeyError
#@ ensures \result == 0
def probe() -> int:
    d: Dict[str, int] = {"a": 1}
    ks = sorted(["a", "b"], key=lambda k: d[k])
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
