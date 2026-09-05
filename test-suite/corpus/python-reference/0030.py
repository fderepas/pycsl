"""Test 0030 — Python Reference 2.5.6: Raw string literals"""
_ = 0  # anchor
#@ ensures \result == 2
#@ assigns \nothing
def test_raw_string_literals() -> int:
    """Ref 2.5.6: in a RAW string the backslash is an ordinary character, so `r"\\n"` has
    length 2 while `"\\n"` has length 1 — that difference IS the feature, and the contract
    SAYS it. Previously the whole body was `\"\"\"Ref 2.5.6: Raw string literals.\"\"\";
    return 0` (relaunch #46, `bin/check-vacuous-drivers.py`)."""
    raw = r"\n"
    cooked = "\n"
    if len(cooked) == 1:
        return len(raw)
    return 0

if __name__ == "__main__":
    assert test_raw_string_literals() == 2
