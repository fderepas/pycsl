"""Test 0172 — PyCSL Annotation Reference 9.7 (variation A)"""
_ = 0  # anchor
from os.path import join

#@ ensures \result == x + 1
def ignores_os(x: int) -> int:
    return x + 1

if __name__ == "__main__":
    assert ignores_os(5) == 6
