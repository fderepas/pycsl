# OPEN ROUTE #324 — A STRING SLICE INSIDE A CONTRACT USES RAW Why3 `String.substring` (negative bounds give "")
**Status: OPEN (gen #37, 2026-10-23), Severity 1.** Red-team round 18 (stdlib/builtin model); driver-reproduced on main 3b07a838 (rc=0; CPython violates).
Witnesses `witnesses-r324/`: `ensures \result == len(s[1:-1])` proves 0 (CPython 1) (q03); `len(s[-2:3])` (q05). expressions.py ~18829 emits the
raw `substring` for a contract-side slice; route #190 fixed the body side (guarded `str_sub_op`), route #262 contract-side INDEXING; contract
SLICES were missed.
Repair: lower contract-side str (and list) slices with Python slice semantics (normalise negative/out-of-range bounds as the body path does) or
refuse non-literal/negative bounds in contracts.
