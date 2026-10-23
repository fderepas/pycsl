"""WL-06d FALSE-TWIN (T10, P3) — soundness oracle for the constructor CONTENT law.
Verdict: UNPROVEN (must NOT be PROVEN).

`bytes([65])[0]` is 65, so claiming it equals 66 is FALSE. The content ensures must not
be inverted/over-claimed. Pin to Z3 for a prompt refute."""
_ = 0


#@ ensures \result == 66
def ctor_content_false_UNSOUND() -> int:
    b = bytes([65])
    return b[0]
