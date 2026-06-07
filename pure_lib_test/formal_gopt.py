"""Formal tests for pure_lib/gopt (getopt) — body-level verification.

PyCSL tool gap: tuple return types aren't propagated through cross-module
import stubs. The formal contracts (parsed + remaining == n) are verified
body-level in pure_lib/gopt/__init__.py (23 VCs, all proven).

This placeholder documents the gap. Formal test VCs for gopt are
generated at body level, not at caller level."""


#@ requires n >= 0
#@ ensures \result >= 0 and \result <= n
def test_getopt_bound_placeholder(n: int) -> int:
    """Placeholder: actual tuple verification is body-level."""
    if n > 0:
        return n
    return 0
