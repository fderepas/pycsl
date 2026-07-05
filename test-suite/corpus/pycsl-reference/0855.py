"""Test 0855 — WL-05c (T7) regression lock (POSITIVE): a STANDALONE `del d[k]` on a dict
PARAMETER is caller-visible.

wrong-lowering-to-fix.md §WL-05c (consistent with WL-05b's `d[k]=v` param mutation).
A standalone function that item-mutates a dict param — here via `del d[k]` — is promoted
to a mutable `ref (map …)` with a `writes {d}` frame, so the deletion ESCAPES to the
caller: given `requires "a" in d`, after `del d["a"]` the postcondition `"a" not in d`
PROVES. PROVEN ⇒ PASS."""
_ = 0  # anchor
from typing import Dict


#@ requires "a" in d
#@ ensures "a" not in d
def del_dict_param(d: Dict[str, int]) -> None:
    del d["a"]
