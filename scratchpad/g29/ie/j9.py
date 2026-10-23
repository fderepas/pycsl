r"""G29 IE-J9 — a missing-key read in a helper, caught by the caller."""
from typing import Dict
_ = 0  # anchor


def get(d: Dict[str, int]) -> int:
    return d["zz"]


#@ ensures \result == 0
def probe() -> int:
    try:
        v = get({"a": 1})
    except KeyError:
        return 9
    return v


if __name__ == "__main__":
    print("CPython:", probe())
