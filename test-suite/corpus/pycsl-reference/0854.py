"""Test 0854 — WL-05c (T7) regression lock (POSITIVE): a LOCAL dict `del d[k]` is
modelled FAITHFULLY.

wrong-lowering-to-fix.md §WL-05c. Module 5 used to flatten EVERY `del` to a bare
no-op (`Pass`), so `del d[k]` was silently dropped and a read-back unsoundly proved the
old value. `del d[k]` on a body-LOCAL dict now lowers to `map_update_none`
(= `Map.set m k None`): after `d["a"] = 7; del d["a"]` the key is genuinely CLEARED, so
`"a" not in d` holds and the function returns 0. PROVEN ⇒ PASS."""
_ = 0  # anchor
from typing import Dict


#@ ensures \result == 0
def local_del_clears_key() -> int:
    d: Dict[str, int] = {}
    d["a"] = 7
    del d["a"]
    if "a" in d:
        return 1
    return 0
