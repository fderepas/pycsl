"""Test 0158 — PyCSL Annotation Reference 2.1.6 (variation A)"""
_ = 0  # anchor
#@ ensures \result >= 0
#@ \diverges
def diverges_loop(x: int) -> int:
    """Diverges: potentially infinite loop."""
    return diverges_loop(x)

if __name__ == "__main__":
    print("PASS")
