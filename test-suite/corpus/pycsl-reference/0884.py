"""Test 0884 — GenericFold A-unit frame-fidelity: a `\nothing` assigns on a mutating walk FAILS. # pycsl-expected: FAIL

The exact in-tuple walk of 0882, but the contract falsely claims `assigns \nothing`
while the body mutates the by-ref `Set[str]` accumulator (`acc.add(...)`).

The GenericFold recognizer is fail-closed on the declared frame: it only fires when
the accumulator appears in `#@ assigns`. A `\nothing` assigns therefore does NOT get
the certified catamorphic lowering, and the mutating set-parameter walk cannot verify
by any other path — so this test must remain UNPROVEN.

If 0884 ever PASSES, the frame-fidelity check regressed — a walk that demonstrably
mutates its caller-visible set accumulator has been accepted under a `assigns \nothing`
claim (the exact contract-vs-implementation hole the recognizer's assigns check closes).
"""
# pycsl-expected: FAIL
from typing import Any, Set


#@ requires True
#@ ensures True
#@ assigns \nothing
def collect_assign_targets_bad(node: Any, acc: Set[str]) -> None:
    if isinstance(node, dict):
        if node.get("stmt") in ("Assign", "AugAssign") and isinstance(node.get("target"), str):
            acc.add(node["target"])
        for v in node.values():
            collect_assign_targets_bad(v, acc)
    elif isinstance(node, list):
        for x in node:
            collect_assign_targets_bad(x, acc)
