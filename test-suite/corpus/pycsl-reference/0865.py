"""Test 0865 — WL-06d regression lock (POSITIVE): FAITHFUL str-LITERAL `.encode()` byte CONTENT.

wrong-lowering-to-fix.md §WL-06d (P1-literal). A pure-ASCII string LITERAL
`"abc".encode()` constant-folds to the `array int` byte literal of its code points
([97,98,99]) — EXACTLY like a `bytes` literal (WL-06b) — via
`expressions._encode_string_literal`. So the exact byte-content read PROVES, the
byte-RANGE invariant `0 <= b[i] < 256` is derivable (no axiom), and (0866) a FALSE
content claim stays UNPROVEN. The `.encode("ascii")`/`.encode("utf-8")` spellings agree
byte==ord for ASCII, so they fold identically. A non-literal receiver, a non-ASCII byte,
or an unmodelled encoding keeps the sound opaque `encode_N` val (declined, not mis-lowered).
"""
_ = 0  # anchor


#@ ensures \result == 97
def enc_a() -> int:
    b = "abc".encode()
    return b[0]


#@ ensures \result == 99
def enc_c() -> int:
    b = "abc".encode("utf-8")
    return b[2]


#@ ensures \result == 66
def enc_ascii_arg() -> int:
    b = "ABC".encode("ascii")
    return b[1]


#@ ensures 0 <= \result and \result < 256
def enc_range() -> int:
    b = "hello".encode()
    return b[0]


if __name__ == "__main__":
    assert enc_a() == ord("a")
    assert enc_c() == ord("c")
    assert enc_ascii_arg() == ord("B")
    assert 0 <= enc_range() < 256
