"""WL-05c (T7) — the severity-1 fail-OPEN that this fix CLOSES (repro record).

BEFORE the fix: Module 5 flattened EVERY `del` to a bare `Pass`, so `del d[k]` was a
silent no-op. On a dict METHOD/param it let a caller/body prove the DELETED key was
STILL present with its OLD value — an UNSOUND false green. This driver is the exact
shape that used to prove: a method deletes `d["a"]` yet the body's `requires`/`ensures`
claim the key survives with value 7. In real Python `del d["a"]` removes the key, so
`d["a"] == 7` post-delete is FALSE.

AFTER the fix: `del d[k]` on a dict/set PARAMETER is a caller-visible mutation with no
`writes {d}` frame on the by-value `map` param, so it is REJECTED (verdict REJECTED),
the SAME boundary as `d[k]=v` on a param (WL-05). The unsound false green can no longer
be emitted. (A LOCAL del is instead lowered faithfully — see wl05c_local_del_FAITHFUL.)"""
_ = 0
from typing import Dict
class Box:
    def __init__(self) -> None:
        self._n = 0
    #@ requires d["a"] == 7
    #@ ensures d["a"] == 7
    def rm(self, d: Dict[str, int]) -> None:
        del d["a"]
