"""pyval-walker-impl.md C2 — the `[-2]` DISCRIMINATING TWIN of 0946.

Byte-for-byte identical to 0946 EXCEPT `short_name` returns `parts[-2]` instead of
`parts[-1]`. The neg-index lowering is NOT a facade that ignores k: the emitted
`short_name` body here reads `nths v_parts (lens v_parts - 2)` where 0946 reads
`nths v_parts (lens v_parts - 1)`. A neg-index recognizer that hard-coded the last
element (or dropped k) would make these two files emit the SAME .mlw — so the pair
IS the mechanical discrimination lock for the offset (the same distinction the
mirror mutation test on `_const_name`/`_ind_short_name` established: `[-1]` -> `- 1`,
`[-2]` -> `- 2`).

Both files PROVE (the walker forces `ensures True`; k only changes which total,
in-range read is emitted). This is the POSITIVE half of the pair; the regression
signal is the emitted-offset difference, not a proof failure."""
from typing import Any, List, Optional


#@ requires True
#@ ensures True
#@ assigns \nothing
def find_components(payload: Any) -> List[str]:
    if isinstance(payload, tuple):
        if payload and payload[0] == "Leaf":
            return leaf_components(payload)
        for sub in payload:
            r = find_components(sub)
            if r:
                return r
    return []


#@ requires True
#@ ensures True
#@ assigns \nothing
def leaf_components(kn: Any) -> List[str]:
    out: List[str] = []
    if not isinstance(kn, tuple):
        return out
    if kn and kn[0] == "Leaf":
        for seg in kn:
            if isinstance(seg, tuple) and seg[0] == "Id" and len(seg) >= 2:
                out.append(seg[1])
    return out


#@ requires True
#@ ensures True
#@ assigns \nothing
def short_name(node: Any) -> Optional[str]:
    if not isinstance(node, tuple) or len(node) < 2:
        return None
    parts = find_components(node[1])
    return parts[-2] if parts else None
