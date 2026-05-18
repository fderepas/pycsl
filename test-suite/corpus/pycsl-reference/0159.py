"""Test 0159 — PyCSL Annotation Reference 2.1.6 (variation B)"""
_ = 0  # anchor
#@ ensures \result == x + 1
#@ \diverges
def diverges_inc(x: int) -> int:
    """Diverges: recursive increment."""
    return diverges_inc(x)

if __name__ == "__main__":
    print("PASS")
