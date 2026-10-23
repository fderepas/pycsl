"""pyval-walker-impl.md C3: the DISCRIMINATING TWIN of 0948 — byte-identical except
it DROPS the self-node head `out.append(node)`, so it collects only the strict
sub-nodes (the children's flattenings), NOT the node itself. This exercises the
`head` knob of `recognize_pyval_flatten`/`emit_pyval_flatten_group`: 0948 emits
`else Cons v_node (flatten__list ...)` (self-node included), while THIS emits
`else (flatten_nohead__list ...)` (no `Cons v_node` head).

It is the mechanical NON-FACADE regression lock for the flatten carrier: a template
that hard-coded the `Cons v_node` head (ignoring the body) would emit 0948 and 0949
IDENTICALLY — but they differ, proving the emitter tracks the presence/absence of the
`out.append(node)` statement, not a fixed template.

Both twins fire `recognize_pyval_flatten` and PROVE (the mutual `pv_size`/`size_list`
termination holds with or without the head). No new axiom; ledger 3."""
from typing import Any, List


#@ requires True
#@ ensures True
#@ assigns \nothing
def flatten_nohead(node: Any) -> List[Any]:
    # Collect only the strict sub-nodes (NO self-node head): the emission loses the
    # `Cons v_node` that 0948 carries.
    out: List[Any] = []
    if isinstance(node, tuple):
        for sub in node:
            out.extend(flatten_nohead(sub))
    return out
