"""WL-06d FALSE-TWIN (T10, P1-literal) — soundness oracle for the str-encode-literal
content law. Verdict: UNPROVEN (must NOT be PROVEN).

`"abc".encode()[0]` is `ord('a')==97`, so claiming it equals 98 is FALSE of real Python.
If this ever proves, the encode-literal fold has collapsed the code-point content
(severity-1 unsound). Pin to Z3 for a prompt refute."""
_ = 0


#@ ensures \result == 98
def enc_false_UNSOUND() -> int:
    b = "abc".encode()
    return b[0]
