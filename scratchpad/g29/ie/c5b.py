r"""G29 IE-C5b — nested dict built by stores, missing inner key read caught."""
from typing import Dict
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    inner: Dict[str, int] = {"x": 1}
    d: Dict[str, Dict[str, int]] = {}
    d["a"] = inner
    try:
        v = d["a"]["y"]
    except KeyError:
        return 9
    return v


if __name__ == "__main__":
    print("CPython:", probe())
