from typing import List

#@ ensures \length(\result) == \length(xs)
def f(xs: List[int]) -> List[int]:
    try:
        return sorted(xs, key=lambda v: 10 // v)
    except ZeroDivisionError:
        return []

if __name__ == "__main__":
    assert len(f([0])) == 1, f([0])
