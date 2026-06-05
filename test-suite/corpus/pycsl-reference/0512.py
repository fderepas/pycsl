"""Test 0512 — string + dict: a string-equality guard drives a dict value.

Content `==` on `str` (via `str_eq_op`) selects which value lands in `d[0]`: equal strings store
1, unequal store 0. The postcondition relates the result to the string comparison through the
dict slot."""
# pycsl-flags: --memory-model hoare
_ = 0  # anchor


#@ requires \str_length(s) >= 0
#@ ensures (s == t) ==> \result == 1
#@ ensures (s != t) ==> \result == 0
def eq_flag(s: str, t: str) -> int:
    d = {}
    if s == t:
        d[0] = 1
    else:
        d[0] = 0
    return d[0]
