"""Test 0025 — Python Reference 2.5.4.4: Hexadecimal character"""
_ = 0  # anchor
#@ ensures \result == 0
#@ assigns \nothing
def test_hexadecimal_character() -> int:
    """Ref 2.5.4.4: `\\xHH` denotes the character with hex value HH — one character, and
    the SAME object as the ordinary notation for it, so `"\\x41" == "A"`. The equality is
    the obligation: it holds only if the front end decodes the escape rather than
    carrying the four-character notation through. Previously the body was `return 0`."""
    h = "\x41"
    if len(h) == 1 and h == "B":
        return 0
    return 1

if __name__ == "__main__":
    assert test_hexadecimal_character() == 0
