"""Test 0841 — WL-04d regression lock (POSITIVE, FILTERED record projection): a
FILTERED projection comprehension `[p.x for p in a if <cond(p)>]` over a flat
`List[<record>]` source now realizes a per-instance `list_content_comp_<n>` val
carrying the SOUND faithful law — a length BOUND plus a membership+predicate+
projection existential — not the prior hard TYPEERR (an opaque `list_comp` int
returned where `array int` was expected).

Before the fix, a filtered projection over a `List[Point]` source fell through
`_content_comp`'s record branch to `val list_comp (x:int):int` (an opaque INT), so
a `-> List[int]` return (typed `array int`) was returned an int → ill-typed WhyML
(TYPEERR, fail-closed but unusable). The result LENGTH is data-dependent
(`0 <= len(result) <= len(a)`), so NO exact length / per-index content law is
claimed. What PyCSL now proves:

  * the length BOUND `len(result) <= len(a)` (the filter only removes elements);
  * a membership+predicate+projection existential — each result element is the
    projected field of SOME source record that passed the filter; and
  * from that, the FILTER CONSEQUENCE transfers to the projected result:
    `[p.x for p in a if p.x > 0]` yields only positive elements (each equals a
    retained `(a[j]).x` for which `(a[j]).x > 0` held).

The element and predicate are lowered NATIVELY over the record binder
(`(src[j]).x`), the SAME projection `\result[i]` / `a[j].x` lowers to — sound, no
new axiom (definitional `ensures`; Array read law is Why3 stdlib). SMT spike:
test-suite/corpus/conformance/spikes/wl04d_filtered_record_proj_spike.mlw (Valid on
Alt-Ergo AND Z3).

Ground truth: filtering a list of Points by `p.x > 0` and projecting `.x` yields a
list of positive ints, no longer than the source. Twin: 0842 (# pycsl-expected:
FAIL) falsely claims the filter is length-preserving, which must NOT prove.
"""
_ = 0  # anchor
from dataclasses import dataclass
from typing import List


@dataclass
class Point:
    x: int
    y: int


#@ ensures \length(\result) <= \length(a)
#@ ensures \forall i; 0 <= i and i < \length(\result) ==> \result[i] > 0
#@ ensures \forall i; 0 <= i and i < \length(\result) ==> (\exists j; 0 <= j and j < \length(a) and a[j].x > 0 and \result[i] == a[j].x)
#@ assigns \nothing
def positives(a: List[Point]) -> List[int]:
    """Every retained record passed `p.x > 0`, so every projected element is > 0
    and is the `.x` of some retained source record (the honest existential)."""
    return [p.x for p in a if p.x > 0]


#@ ensures \length(\result) <= \length(a)
#@ assigns \nothing
def nontrivial_pred(a: List[Point]) -> List[int]:
    """A predicate over TWO field projections still lifts; the length bound holds."""
    return [p.y for p in a if p.x > 0 and p.y >= p.x]
