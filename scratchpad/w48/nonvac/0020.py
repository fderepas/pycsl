"""Test 0020 — Python Reference 2.5.2: String prefixes"""
_ = 0  # anchor
#@ ensures \result == 0
#@ assigns \nothing
def test_string_prefixes() -> int:
    """Ref 2.5.2: the `r` prefix makes a RAW string literal, in which a backslash is an
    ordinary character rather than the start of an escape. So `r"\\n"` is TWO characters
    where `"\\n"` is one, and the contract can say so through `\\length`. Previously the
    body was `return 0` and the postcondition held whatever the prefix meant."""
    plain = "\n"
    raw = r"\n"
    if len(plain) == 1 and len(raw) == 3:
        return 0
    return 1

if __name__ == "__main__":
    assert test_string_prefixes() == 0
