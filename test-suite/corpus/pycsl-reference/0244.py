"""Test 0244 — PyCSL Annotation Reference 8.1 (class invariant from __init__)"""
""  # pycsl
#@ class invariant self.magic_number == 42
class MagicNumber:
    def __init__(self):
        self.magic_number = 42

#@ requires 1 == 1
#@ ensures \result == 42
#@ assigns \nothing
def f() -> int:
    a = MagicNumber()
    return a.magic_number

if __name__ == "__main__":
    assert f() == 42
