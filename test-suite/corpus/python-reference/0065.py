"""Test 0065 — Python Reference 3.2.12: I/O objects (also known as file objects)"""
_ = 0  # anchor
#@ ensures \result == 0
def test_io_objects() -> int:
    """I/O objects (file objects) support read/write."""
    import io
    buf = io.StringIO("hello")
    assert buf.read() == "hello"
    return 0

if __name__ == "__main__":
    assert test_io_objects() == 0
