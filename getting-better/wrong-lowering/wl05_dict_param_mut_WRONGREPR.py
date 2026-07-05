"""WL-05b FIXED (was WL-05 WRONG-REPR) — now PROVEN: an item-assignment to a PARAMETER
dict is modelled as a caller-visible mutable `ref (map …)` with a `writes {d}` frame, so
`d[k]=v` write-read-back proves faithfully. Historical bug (kept for the repro record):
item-assignment to a PARAMETER dict USED TO emit WhyML that treats the
by-value param as a mutable `ref` inconsistently:
    d := map_update_some !d "a" 5;          (* d :=/!d on a non-ref value *)
    (match Map.get d "a" ...)               (* and reads `d`, not `!d` *)
-> ill-typed (`string -> option int but expected ref 'mu`).

Detector D5 consequence (write->read-back) + D2: TYPEERR. A LOCAL dict write-read-back
IS faithful (wl05_dict_local_FAITHFUL.py), so this is param-specific. Only RECORD and
LIST param mutation are documented out-of-scope; dict/set param mutation is not, and
it emits broken WhyML rather than a clean rejection."""
_ = 0
from typing import Dict
#@ ensures \result == 5
def f(d: Dict[str, int]) -> int:
    d["a"] = 5
    return d["a"]
