"""Test 0173 — PyCSL Annotation Reference 9.7 (variation B)"""
_ = 0  # anchor
from sys import argv

#@ ensures \result == x * x
def ignores_sys(x: int) -> int:
    return x * x

if __name__ == "__main__":
    assert ignores_sys(3) == 9
