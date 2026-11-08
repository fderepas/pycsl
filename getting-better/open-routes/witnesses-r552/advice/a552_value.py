from typing import Dict, List


def h(x: int) -> int:
    return x + 1


#@ no_exception \all
def f(k: int, xs: List[int], d: Dict[str, int]) -> int:
    return h(k)


if __name__ == "__main__":
    print(f(1, [1], {"a": 1}))
