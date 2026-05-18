"""Test 0175 — Python Reference 7.7: The yield statement"""
_ = 0  # anchor
#@ ensures \result == 1
def test_yield_statement() -> int:
    """yield produces a value from a generator."""
    def gen():
        yield 1
    return next(gen())

if __name__ == "__main__":
    assert test_yield_statement() == 1
