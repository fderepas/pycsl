# OPEN ROUTE #481 — a `\trusted` function's inferred default frame keeps a list argument's LENGTH

**Status: OPEN, Severity 1.** Found by executor d1 (driver run #3, 2026-10-30) while repairing the cv6 emitter defects;
reproduced by the driver on main d6abee90b (`scratchpad/rp481/repro.sh`, session scratchpad).

Witness `witnesses-r481/r481_trusted_append_len.py`: a same-file `#@ \trusted` function `k(xs: List[int])` with NO
`#@ assigns` clause whose body does `xs.append(1)`; its caller `f` claims `#@ ensures \result == \old(len(xs))` and
returns `len(xs)` after `k(xs)`. pycsl: rc=0, Verification SUCCESS. CPython: `f([])` returns 1 (contract broken).
Control `witnesses-r481/r481_ctl_store_only.py` (the trusted body only stores `xs[0] = 1`): proves, and CPython agrees.

WHY IT PROVES: the trusted stub is emitted with the inferred default frame `writes { xs }` (route #317), and a Why3
`array`'s length is immutable under `writes`, so `Array.length xs` is preserved across the call -- the frame claims
something the (unverified, trusted) body does not do. The user trusted the CONTRACT (`ensures True`), not a
length-preserving frame; the length preservation is the TOOL's inference. Same defect class as route #49 (local
callees, repaired by the resizable lowering) and route #468 (imported un-contracted callees, repaired at the import
boundary): the same-file `\trusted` boundary still uses the fixed-length array.

PROPOSED SYSTEMATIC REPAIR: one rule for every bodyless / trusted boundary: a default (inferred, not user-written)
`writes { x }` on a list parameter must also havoc its length (the #468 repair's model or the #49 resizable model),
or, allow-list polarity, the caller may read the length / index the argument after such a call only when the
callee's frame is user-written (`#@ assigns`) or its body is verified. Check every other inferred-frame site
(`\abstract`, interface, `no_inline`, stubs from `pycsl_lib`) for the same shape.
