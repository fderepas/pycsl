from typing import Dict
_ = 0  # anchor


#@ no_exception KeyError
#@ ensures \result == 0
def probe() -> int:
    d: Dict[str, int] = {"a": 1}

    def inner() -> int:
        return d["b"]

    v = inner()
    return v * 0


if __name__ == "__main__":
    print("CPython:", probe())
