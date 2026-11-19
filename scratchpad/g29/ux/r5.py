r"""init implicit missing key"""
_ = 0  # anchor


from typing import Dict


class C:
    def __init__(self, d: Dict[str, int]) -> None:
        self.v = d["b"]


#@ ensures \result == 0
def probe() -> int:
    try:
        c = C({"a": 1})
    except KeyError:
        return 9
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
