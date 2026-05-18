"""Test 0141 — Python Reference 6.2.9: Generator expressions"""
_ = 0  # anchor
#@ ensures \result == 3
def test_yield_expressions() -> int:
    """yield produces a value from a generator."""
    def gen():
        yield 1
        yield 2
    return sum(gen())

if __name__ == "__main__":
    assert test_yield_expressions() == 3
