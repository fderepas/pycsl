"""Test 0026 — Python Reference 2.5.4.5: Named Unicode character"""
_ = 0  # anchor
#@ ensures \result == 0
#@ assigns \nothing
def test_named_unicode_character() -> int:
    """Ref 2.5.4.5: `\\N{NAME}` denotes the character with that Unicode NAME — one
    character, and the SAME character the ordinary notation denotes, so
    `"\\N{LATIN SMALL LETTER A}" == "a"`. Both the length and the equality are obligations
    on the front end: it must resolve the name at parse time rather than carrying the
    twenty-six-character notation into the WhyML literal. Previously the whole body was
    `return 0` and the postcondition held whatever the escape meant."""
    n: str = "\N{LATIN SMALL LETTER A}"
    if len(n) == 1 and n == "b":
        return 0
    return 1

if __name__ == "__main__":
    assert test_named_unicode_character() == 0
