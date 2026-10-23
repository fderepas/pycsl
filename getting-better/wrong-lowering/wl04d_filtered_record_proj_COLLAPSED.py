"""WL-04d — FILTERED projection comprehension over a `List[<record>]` source — **FIXED**.

Before the fix: `[p.x for p in a if p.x > 0]` over a `List[Point]` source fell through
`_content_comp`'s record-source branch to the opaque `val list_comp (x:int):int`, so a
`-> List[int]` return (typed `array int`) was returned an INT → ill-typed WhyML
(TYPEERR — fail-closed, but unusable: neither the length bound nor any content fact
was expressible).

After the fix (wrong-lowering-to-fix.md §WL-04 FILTERED record residual): the filtered
record projection is realized as a per-instance `list_content_comp_<n>` val over
`array <record>` carrying the SOUND faithful law — the length BOUND
`len(result) <= len(a)` plus a membership+predicate+projection existential (each result
element is the projected field of SOME source record that passed the filter). From that
the FILTER CONSEQUENCE transfers to the projected result: `[p.x for p in a if p.x > 0]`
yields only positive elements. Verdict: PROVEN.

The result LENGTH is data-dependent (`0 <= len <= len(a)`), so NO exact length / per-index
content law is claimed — the false twin (wl04d_filtered_record_proj_falsetwin.py) stays
UNPROVEN.
"""
_ = 0
from dataclasses import dataclass
from typing import List


@dataclass
class Point:
    x: int
    y: int


#@ ensures \length(\result) <= \length(a)
#@ ensures \forall i; 0 <= i and i < \length(\result) ==> \result[i] > 0
#@ assigns \nothing
def positives(a: List[Point]) -> List[int]:
    """Every retained record passed `p.x > 0`, so every projected element is > 0
    (the filter consequence transfers through the projection)."""
    return [p.x for p in a if p.x > 0]
