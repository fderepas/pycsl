"""Test 0006 — Python Reference 2.1.4: Encoding declarations"""
_ = 0  # anchor
# -*- coding: utf-8 -*-
#@ ensures \result == x + 1
def test_encoding_declaration(x: int) -> int:
    """Encoding declarations appear on line 1 or 2."""
    return x + 1

if __name__ == "__main__":
    assert test_encoding_declaration(0) == 1
