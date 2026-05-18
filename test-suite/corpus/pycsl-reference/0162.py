"""Test 0162 — PyCSL Annotation Reference 2.1.7 (variation A): trusted wrong body"""
_ = 0  # anchor
#@ ensures \result == x * 2
#@ \trusted
def trusted_wrong(x: int) -> int:
    """Body is wrong (returns x*3) but trusted: contract assumed."""
    return x * 3

#@ ensures \result == x * 2
def caller_of_wrong(x: int) -> int:
    """Caller proven using assumed contract."""
    return trusted_wrong(x)

if __name__ == "__main__":
    pass
