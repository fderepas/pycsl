r"""no_exception KeyError nested dict inner"""
from typing import List, Dict
_ = 0  # anchor


#@ no_exception KeyError
#@ ensures \result == 0
def probe() -> int:
    d: Dict[str, Dict[str, int]] = {"a": {"x": 1}}
    v = d["a"]["y"]
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
