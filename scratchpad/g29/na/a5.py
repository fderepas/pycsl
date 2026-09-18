r"""G29 NA5 — dict.pop removes the key; setdefault does not overwrite."""
from typing import Dict
_ = 0  # anchor


#@ ensures \result == 1
def probe() -> int:
    d: Dict[str, int] = {"a": 1, "b": 2}
    d.setdefault("a", 5)
    v = d.pop("b")
    return len(d) + v


if __name__ == "__main__":
    print("CPython:", probe())
