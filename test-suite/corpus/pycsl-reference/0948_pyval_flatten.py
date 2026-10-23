"""pyval-walker-impl.md C3 (driver-backlog item 3, from_sexp residual): the `list
pyval` FLATTEN catamorphism. Where C1/C1b (0943/0944/0945) return `List[str]`, this
returns `List[Any]` = `list pyval` — a list of the sub-NODES themselves, not strings
extracted from them (the `from_sexp._flatten_tuples` shape). This is a DISTINCT value
model: the accumulator element type is `pyval`, appended WHOLE (`out.append(node)`)
and the children flattened by a self-call on each spine element.

It is emitted as the certified mutual

    let rec flatten (v: pyval) : list pyval        variant { pv_size v }
    with flatten__list (l: list pyval) : list pyval variant { size_list l }

plus an inline TOTAL `list pyval` append (`flatten__ftapp`, `variant { a }`). The
cross-decreasing structural measures (pyval `pv_size` / `size_list`) discharge
termination AUTOMATICALLY — NO new axiom (ledger stays 3).

The emitted `flatten` body reads the REAL pyval spine (`is_plist v`, the `PList xs`
destructure, the self-recursion on each `sub`) with NO int-hash, NO oracle. It is a
STRUCTURAL lowering: the leading `out.append(node)` self-node head emits `Cons v_node
(...)`; DROP it (the 0949 twin) and the emission loses the `Cons v_node` head — the
mutation test, so it is not a facade.

POSITIVE witness (regression lock): `flatten` fires `recognize_pyval_flatten` and the
file PROVES. If a future edit drops the flatten recognition or the mutual-group
termination, `flatten` reverts to a `val` stub (emission byte-diff) and/or the proof
breaks.

No evil-twin applies: the recognizer forces the fixed `ensures True` shape (no
postcondition to refute) and emits NO oracle to collapse to — the mutation test +
`bin/check-emitted-vacuity.py` (0 input-blind) are the non-vacuity lock."""
from typing import Any, List


#@ requires True
#@ ensures True
#@ assigns \nothing
def flatten(node: Any) -> List[Any]:
    # Collect this node and all its sub-nodes at any depth (the self-node HEAD
    # variant: `out.append(node)` before the spine fold → `Cons v_node (...)`).
    out: List[Any] = []
    if isinstance(node, tuple):
        out.append(node)
        for sub in node:
            out.extend(flatten(sub))
    return out
