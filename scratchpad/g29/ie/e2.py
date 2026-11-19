r"""missing key inside the handler itself"""
from typing import Dict, List
_ = 0  # anchor


#@ ensures \result == 9
def probe() -> int:
    d: Dict[str, int] = {"a": 1}
    try:
        raise ValueError()
    except ValueError:
        v = d["b"]
        return 9
    except KeyError:
        return 9


if __name__ == "__main__":
    print("CPython:", probe())
