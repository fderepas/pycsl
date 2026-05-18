"""Test 0093 — Python Reference 3.3.9: With Statement Context Managers"""
_ = 0  # anchor
#@ ensures \result == 0
def test_with_statement_context() -> int:
    """__enter__ and __exit__ for context managers."""
    class CM:
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass
    with CM() as c:
        pass
    return 0

if __name__ == "__main__":
    assert test_with_statement_context() == 0
