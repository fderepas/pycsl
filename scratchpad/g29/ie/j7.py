r"""control: present key read inside try/except KeyError proves"""
from typing import Dict
_ = 0  # anchor


#@ ensures \result == 1
def probe() -> int:
    d: Dict[str, int] = {"a": 1}
    try:
        v = d["a"]
    except KeyError:
        return 9
    return v


if __name__ == "__main__":
    print("CPython:", probe())
