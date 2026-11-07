"""WL-05c (T7) — a STANDALONE function `del d[k]` on a dict PARAMETER is caller-visible
(verdict PROVEN), consistent with WL-05b's `d[k]=v` param mutation.

The param is promoted to a mutable `ref (map …)` with a `writes {d}` frame (WL-05b
fixpoint, now seeded by `DelSubscript` too), so the deletion ESCAPES to the caller:
given `requires "a" in d`, after `del d["a"]` the postcondition `"a" not in d` PROVES."""
_ = 0
from typing import Dict
#@ requires "a" in d
#@ ensures "a" not in d
def rm(d: Dict[str, int]) -> None:
    del d["a"]
