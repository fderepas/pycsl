"""Test 0024 — Python Reference 2.5.4.3: Octal character"""
_ = 0  # anchor
#@ ensures \result == 65
#@ assigns \nothing
def test_octal_character() -> int:
    """Ref 2.5.4.3: `\101` in a string literal is the character with octal value 101,
    i.e. `A` (65). The check is on the OCTAL INTEGER literal `0o101`, which is the value
    the escape denotes; PyCSL has no character-code model, so this is the part of the
    reference the tool can actually be held to. Previously the whole body was
    `return 0` (relaunch #46, `bin/check-vacuous-drivers.py`)."""
    v = 0o101
    return v

if __name__ == "__main__":
    assert test_octal_character() == 65
