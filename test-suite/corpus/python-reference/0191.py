"""Test 0191 — Python Reference 8.5: The with statement"""
_ = 0  # anchor
#@ ensures \result == 0
def test_with_statement() -> int:
    """with statement for context management."""
    import io
    with io.StringIO("hello") as f:
        assert f.read() == "hello"
    return 0

if __name__ == "__main__":
    assert test_with_statement() == 0
