"""Test 0796 — cleared-hash residual-close 1(b): the HONEST κ-unknown fallback boundary
(no false injectivity axiom on `str_hash_op`).

This is the LOCK on the residual: a dict keyed by a string expression whose value the model
CANNOT pin to a decidable/injective string — here a string METHOD result `s.upper()` — stays on
the opaque, collision-admitting `str_hash_op` (`str_hash_op (str_upper_op s)`), exactly the
documented κ-unknown fallback. `str_hash_op` is a bodyless `val`: Why3 treats it as an ARBITRARY
total function, so for distinct keys it may collide. Therefore a distinct-key NON-aliasing claim —
after `d[s.upper()] = 1; d[t.upper()] = 2`, that `d[s.upper()]` is still `1` even though `s != t`
— is UNPROVABLE, and MUST stay unprovable.

This driver is `# pycsl-expected: FAIL` on purpose: it is the evidence that we do NOT smuggle a
false injectivity claim onto `str_hash_op` (`proof_axiom_allowlist` unchanged; no hash-injectivity
axiom). The fallback is honest — the model declines to prove a distinct-key property it cannot
justify (and indeed `str.upper` is genuinely non-injective: `"a".upper() == "A".upper()`), rather
than asserting a collision-freedom it does not have. Contrast with 0795 (a concat key, whose native
`concat` IS left-cancellative, so its non-aliasing DOES prove)."""
# pycsl-expected: FAIL
_ = 0  # anchor
#@ requires s != t
#@ ensures \result == 1
#@ assigns \nothing
def unknown_kappa_hash_boundary(s: str, t: str) -> int:
    d = {}
    d[s.upper()] = 1
    d[t.upper()] = 2
    # UNPROVABLE: `str_hash_op` admits `str_hash_op(str_upper_op s) == str_hash_op(str_upper_op t)`
    # even when s != t, so writing the `t.upper()` entry may clobber the `s.upper()` entry.
    return d[s.upper()]
