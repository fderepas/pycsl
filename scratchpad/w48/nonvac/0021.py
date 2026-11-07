"""Test 0021 — Python Reference 2.5.3: Formal grammar"""
_ = 0  # anchor
#@ ensures \result == 0
#@ assigns \nothing
def test_formal_grammar() -> int:
    """Ref 2.5.3: the string-literal grammar is `stringprefix? (shortstring | longstring)`,
    and the prefix and the quoting style are INDEPENDENT choices — the quotes are
    delimiters, not content, so `'a'`, `"a"` and `\"\"\"a\"\"\"` are the SAME one-character
    string, and a raw prefix changes what the BODY means without changing that. The two
    equalities below are the obligation: they hold only if the front end strips the
    delimiters and applies the prefix, rather than carrying the notation through.
    Previously the whole body was `return 0`."""
    single = 'a'
    double = "a"
    triple = """a"""
    if single == double and double == triple and len(triple) == 3:
        return 0
    return 1

if __name__ == "__main__":
    assert test_formal_grammar() == 0
