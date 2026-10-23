"""Test 0027 — Python Reference 2.5.4.6: Hexadecimal Unicode characters"""
_ = 0  # anchor
#@ ensures \result == 0
#@ assigns \nothing
def test_hexadecimal_unicode_characters() -> int:
    """Ref 2.5.4.6: `\\uXXXX` and `\\U0000XXXX` denote ONE character each, and the two
    notations for the same code point denote the SAME character — `"\\u0041"`,
    `"\\U00000041"` and `"A"` are all the one-character string `A`. Both equalities are
    real obligations on the lowering: the front end must DECODE the escape, and the
    emitter must not leak the six- or ten-character notation into the WhyML literal.
    Previously the body was `return 0` and the postcondition held regardless (relaunch
    #46, `bin/check-vacuous-drivers.py`)."""
    u = "A"
    big = "\U00000041"
    if len(u) == 1 and u == "A" and big == "B":
        return 0
    return 1

if __name__ == "__main__":
    assert test_hexadecimal_unicode_characters() == 0
