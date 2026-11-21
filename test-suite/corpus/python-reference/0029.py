"""Test 0029 — Python Reference 2.5.5: Bytes literals"""
_ = 0  # anchor
#@ ensures \result == 65
#@ assigns \nothing
def test_bytes_literals() -> int:
    """Ref 2.5.5: a bytes literal is a sequence of INTEGERS in `0..255`, so `b"ABC"[0]`
    is 65 and `len(b"ABC")` is 3, and the contract SAYS so. Previously the whole body was
    `\"\"\"Ref 2.5.5: Bytes literals.\"\"\"; return 0` (relaunch #46,
    `bin/check-vacuous-drivers.py`)."""
    data = b"ABC"
    if len(data) == 3 and data[1] == 66 and data[2] == 67:
        return data[0]
    return 0

if __name__ == "__main__":
    assert test_bytes_literals() == 65
