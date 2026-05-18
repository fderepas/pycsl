"""Test 0166 — PyCSL Annotation Reference 9.4 (variation A)"""
_ = 0  # anchor
# pycsl-flags: --fun verified_fn
#@ ensures \result == x + x
def verified_fn(x: int) -> int:
    return x + x

#@ ensures \result == 999
def wrong_fn(x: int) -> int:
    return 0

if __name__ == "__main__":
    assert verified_fn(3) == 6
