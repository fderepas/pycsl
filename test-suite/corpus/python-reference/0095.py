"""Test 0095 — Python Reference 3.3.11: Emulating buffer types"""
_ = 0  # anchor
#@ ensures \result == 0
def test_buffer_types() -> int:
    """__buffer__ and __release_buffer__ for buffer protocol."""
    b = bytearray(b"abc")
    mv = memoryview(b)
    assert mv[0] == 97
    mv.release()
    return 0

if __name__ == "__main__":
    assert test_buffer_types() == 0
