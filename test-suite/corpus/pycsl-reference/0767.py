"""Test 0767 — startswith is content-faithful, on simple AND derived receivers.

cleared-string.md S6. `str.startswith` lowers to `str_startswith_op` whose
`ensures` ties the 0/1 result to Why3's native `String.substring` prefix witness.
This test locks in TWO things:
  * `sw_simple` — a simple `str`-typed receiver with a prefix hypothesis (already
    content-faithful before this plan);
  * `sw_derived` — a DERIVED string receiver `(pre + rest).startswith(pre)`, newly
    content-faithful: the predicate handler now lowers ANY string-valued receiver
    (via `_str_method_recv_and_tail`), not only a simple name, so the constructive
    prefix provably holds. Previously the derived receiver fell through to an
    opaque uninterpreted predicate and this could not be proven.
"""
_ = 0  # anchor


#@ requires len(p) <= len(s)
#@ requires s[0:len(p)] == p
#@ ensures \result == 1
#@ assigns \nothing
def sw_simple(s: str, p: str) -> int:
    return s.startswith(p)


#@ ensures \result == 1
#@ assigns \nothing
def sw_derived(pre: str, rest: str) -> int:
    return (pre + rest).startswith(pre)
