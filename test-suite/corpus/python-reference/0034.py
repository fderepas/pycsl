"""Test 0034 — Python Reference 2.6.1: Integer literals"""
_ = 0  # anchor
#@ ensures \result == 31
#@ assigns \nothing
def test_integer_literals() -> int:
    """Ref 2.6.1: a decimal, a hexadecimal, an octal, a binary and an underscored
    integer literal all denote the SAME value, and the contract SAYS SO — this driver
    used to be `\"\"\"Ref 2.6.1: Integer literals.\"\"\"; return 0`, which proved nothing
    about integer literals at all (relaunch #46, `bin/check-vacuous-drivers.py`)."""
    dec = 31
    hexa = 0x1F
    octal = 0o37
    binary = 0b11111
    under = 3_1
    if dec == hexa and octal == binary and under == dec:
        return dec
    return 0

if __name__ == "__main__":
    assert test_integer_literals() == 31
