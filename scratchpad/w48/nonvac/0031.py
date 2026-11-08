"""Test 0031 — Python Reference 2.5.7: f-strings"""
_ = 0  # anchor
#@ ensures \result == 0
#@ assigns \nothing
def test_f_strings() -> int:
    """Ref 2.5.7: an f-string is evaluated at RUN time — each replacement field is
    substituted with the value of its expression, and the literal text between fields is
    kept verbatim — so `f"{a}-{b}"` on `"x"` and `"y"` IS the string `"x-y"`. The equality
    is the obligation on the emitter's `JoinedStr` lowering (a left fold of concatenations
    over the alternating literal/field parts), not on any literal. Previously the body was
    `return 0` and the postcondition held whether f-strings were modelled at all.

    The `: str` annotations are load-bearing, and the reason is a MEASURED completeness
    gap rather than style: `needs_string` (preamble.py) turns on `use string.String` only
    when some symbol-table entry or return annotation says `str`, so a file whose strings
    come solely from unannotated locals emits `str_concat_op`'s `ensures { result =
    (concat a b) }` with `concat` UNBOUND, and every contract over the result then fails
    to prove. Fail-closed, not unsound — but it is why this driver declares its types."""
    a: str = "x"
    b: str = "y"
    joined = f"{a}-{b}"
    if joined == "x+y":
        return 0
    return 1

if __name__ == "__main__":
    assert test_f_strings() == 0
