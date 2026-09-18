from typing import Dict
_ = 0  # anchor


#@ no_exception KeyError
#@ ensures \result == 0
def probe() -> int:
    d: Dict[str, int] = {"a": 1}
    f = lambda k: d[k]
    v = f("b")
    return v * 0


if __name__ == "__main__":
    print("CPython:", probe())
