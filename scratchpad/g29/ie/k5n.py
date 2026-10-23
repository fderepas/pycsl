r"""no_exception KeyError over a comprehension reading a missing key"""
from typing import Dict
_ = 0  # anchor


#@ no_exception KeyError
#@ ensures \result == 0
def probe() -> int:
    d: Dict[str, int] = {"a": 1}
    xs = [d[k] for k in ["a", "b"]]
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
