"""Test 0135 — Python Reference 6.2.3.2: String literal concatenation"""
_ = 0  # anchor
#@ ensures \result == 0
#@ assigns \nothing
def test_string_literal_concatenation() -> int:
    """Ref 6.2.3.2: ADJACENT string literals are concatenated at COMPILE time, so
    `"ab" "cd"` is one four-character literal and is the same value as `"abcd"` — no
    run-time `+` is involved. The equality is the obligation. Previously the body was
    `return 0` and the postcondition held whether or not the juxtaposition was
    understood at all."""
    a = "ab" "cd"
    b = "abcd"
    if a == b and len(a) == 5:
        return 0
    return 1

if __name__ == "__main__":
    assert test_string_literal_concatenation() == 0
