"""WL-03 baseline (NOT a finding) — a LOCAL tuple is faithful; t[1]==20 proves.
Shows the collapse is param/field-specific, contradicting the unqualified tau row."""
_ = 0
#@ ensures \result == 20
def f() -> int:
    t = (10, 20)
    return t[1]
