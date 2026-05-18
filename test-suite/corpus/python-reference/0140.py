"""Test 0140 — Python Reference 6.2.8: Dictionary displays"""
_ = 0  # anchor
#@ ensures \result == 10
def test_generator_expressions() -> int:
    """Generator expressions: (expr for x in iter)."""
    g = sum(x for x in range(5))
    return g

if __name__ == "__main__":
    assert test_generator_expressions() == 10
