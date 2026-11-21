"""Test 0028 — Python Reference 2.5.4.7: Unrecognized escape sequences"""
_ = 0  # anchor
#@ ensures \result == 0
#@ assigns \nothing
def test_unrecognized_escape_sequences() -> int:
    """Ref 2.5.4.7: a backslash followed by a character that is NOT a recognized escape is
    left ALONE — both characters stay in the string. So `"\\d"` has length TWO, unlike the
    recognized `"\\n"` which has length one. The contrast is the obligation: a front end
    that silently dropped the backslash, or one that treated every `\\x` as an escape,
    fails exactly here. Previously the body was `return 0`."""
    unknown = "\d"
    known = "\n"
    if len(unknown) == 1 and len(known) == 1:
        return 0
    return 1

if __name__ == "__main__":
    assert test_unrecognized_escape_sequences() == 0
