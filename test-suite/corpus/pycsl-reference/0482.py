"""Test 0482 — strings: __mul__ (`s * n`, repetition).
Target: repetition multiplies the length. PROVES as of the G2 strings feature: a string×int
`*` lowers to `str_repeat_op` (a `val` whose `ensures` pins `String.length result = n *
String.length s`); the content is opaque, only the length law is modeled (faithful)."""
# pycsl-flags: --memory-model hoare
_ = 0  # anchor
#@ requires n >= 0 and \str_length(s) >= 0
#@ ensures \str_length(\result) == n * \str_length(s)
#@ assigns \nothing
def rep(s: str, n: int) -> str:
    return s * n
