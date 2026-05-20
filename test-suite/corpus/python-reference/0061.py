"""Test 0061 — Python Reference 3.2.9.3: Module dictionaries"""
# pycsl-expected: FAIL
_ = 0  # anchor
#@ ensures \result == 1
def test_generator_functions() -> int:
    """Generator functions use yield and return iterators."""
    def gen():
        yield 1
        yield 2
    g = gen()
    return next(g)

if __name__ == "__main__":
    assert test_generator_functions() == 1
