"""Test 0023 — Python Reference 2.5.4.2: Escaped characters"""
_ = 0  # anchor
#@ ensures \result == 0
#@ assigns \nothing
def test_escaped_characters() -> int:
    """Ref 2.5.4.2: a backslash escape denotes ONE character — `\\n` is a newline, `\\t`
    a tab, `\\\\` a single backslash — so a two-character NOTATION has length one. That
    is a real obligation on the lowering of a string literal (WhyML rejects a raw newline
    inside `"..."`, so the emitter must escape it and keep the length right). Previously
    the body was `return 0`."""
    nl = "\n"
    tab = "\t"
    bs = "\\"
    if len(nl) == 1 and len(tab) == 1 and len(bs) == 1:
        return 0
    return 1

if __name__ == "__main__":
    assert test_escaped_characters() == 0
