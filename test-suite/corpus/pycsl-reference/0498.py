"""Test 0498 — collections: defaultdict(int) reduces to the dict model.

`defaultdict(int)` IS the `map int (option int)` model: its missing-key default (None → 0)
is exactly `defaultdict(int)` semantics. Reading an unset key gives 0, so `d[3] = d[3] + 7`
sets `d[3]` to 7. The factory arg is dropped (recognised by name); non-int factories
(`defaultdict(list)`) are out of scope — the missing-key default is hard-wired to 0."""
# pycsl-flags: --memory-model hoare
_ = 0  # anchor
from collections import defaultdict


#@ ensures \result == 7
def use_default() -> int:
    d = defaultdict(int)
    d[3] = d[3] + 7
    return d[3]
