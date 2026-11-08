"""Test 0134 — Python Reference 6.2.3.1: Literals and object identity"""
_ = 0  # anchor
#@ ensures \result == 0
#@ assigns \nothing
def test_literals_and_object_identity() -> int:
    """Ref 6.2.3.1: the interpreter is FREE to reuse the object for an immutable literal,
    so whether two occurrences of the same literal are the SAME OBJECT is unspecified —
    CPython interns `"abc"` and answers True for `a is b`, and the language does not
    promise it. What IS specified is VALUE equality, and that is what this contract
    states. A driver asserting `a is b` would be pinning an implementation detail rather
    than the reference — and PyCSL narrows `is` to `==` for everything except the bool
    singleton (route #42, §T.5.12g), so it would also be asserting something the model
    cannot distinguish. Previously the body was `return 0`."""
    a = "abc"
    b = "abc"
    c = "abd"
    if a == b and len(a) == 3 and a == c:
        return 0
    return 1

if __name__ == "__main__":
    assert test_literals_and_object_identity() == 0
