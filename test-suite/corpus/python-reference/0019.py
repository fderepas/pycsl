"""Test 0019 — Python Reference 2.4.1: Triple-quoted strings"""
_ = 0  # anchor
#@ ensures \result == 1
#@ assigns \nothing
def test_triple_quoted_strings() -> int:
    """Ref 2.4.1: a triple-quoted string is an ordinary `str`, and the two quoting styles
    denote the SAME value. The contract SAYS so; previously the whole body was
    `\"\"\"Ref 2.4.1: Triple-quoted strings.\"\"\"; return 0` (relaunch #46,
    `bin/check-vacuous-drivers.py`)."""
    a = """abc"""
    b = 'abc'
    if a == b:
        return 1
    return 0

if __name__ == "__main__":
    assert test_triple_quoted_strings() == 1
