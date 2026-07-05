"""WL-06d POSITIVE (T10, P1-literal) — FAITHFUL str-LITERAL `.encode()` byte CONTENT.
Verdict: PROVEN.

A pure-ASCII string LITERAL `"abc".encode()` constant-folds to the `array int` byte
literal of its code points ([97,98,99]) — like a `bytes` literal (WL-06b) — via
`expressions._encode_string_literal`. The exact byte-content read PROVES and the
byte-RANGE invariant `0<=b[i]<256` is derivable (no axiom). `.encode("ascii")` /
`.encode("utf-8")` agree byte==ord for ASCII."""
_ = 0


#@ ensures \result == 97
def enc_a() -> int:
    b = "abc".encode()
    return b[0]


#@ ensures \result == 66
def enc_ascii_arg() -> int:
    b = "ABC".encode("ascii")
    return b[1]


#@ ensures 0 <= \result and \result < 256
def enc_range() -> int:
    b = "hello".encode()
    return b[0]
