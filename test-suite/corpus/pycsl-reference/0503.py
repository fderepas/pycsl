"""Test 0503 — collections: OrderedDict reduces to a plain dict (no order).

`OrderedDict()` uses the same `map int (option int)` model as `dict` — key/value content proves
(set a key, read it back), but insertion ORDER is not represented (Why3 maps are unordered), so
nothing about ordering is asserted. This is the Tier-2 boundary: content yes, order no."""
# pycsl-flags: --memory-model hoare
_ = 0  # anchor
from collections import OrderedDict


#@ ensures \result == 42
def store() -> int:
    od = OrderedDict()
    od[1] = 42
    return od[1]
