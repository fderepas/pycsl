"""Test 0160 — PyCSL Annotation Reference 2.1.7 (variation A): trusted correct"""
_ = 0  # anchor
#@ ensures \result == x * 3
#@ \trusted
def triple(x: int) -> int:
    """Trusted: body assumed correct, contract used as axiom."""
    return x + x + x

#@ ensures \result == x * 3
def call_triple(x: int) -> int:
    """Caller that relies on trusted triple's contract."""
    return triple(x)

if __name__ == "__main__":
    assert call_triple(4) == 12
