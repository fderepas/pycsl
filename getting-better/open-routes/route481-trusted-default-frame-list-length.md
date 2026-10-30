# OPEN ROUTE #481 — a `\trusted` function's inferred default frame keeps a list argument's LENGTH

**Status: REPAIRED (executor f2, driver run #3, 2026-10-30, off 8855b6b10), Severity 1.** Found by executor d1 (driver run #3, 2026-10-30) while repairing the cv6 emitter defects;
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

## REPAIR (executor f2, driver run #3, 2026-10-30; annotations §7.340)

One rule for every bodyless boundary: route #468's allow-list (inline at the end of `_run_pipeline`, mirror twin
`\trusted`) used to skip a def whose own `#@` block says `\trusted` ("a declared assumption"); it now judges it
like an imported or `\abstract` one. The user of `\trusted` trusts the CONTRACT; the length-keeping frame is the
tool's -- route #317's inferred `writes { xs }`, and a declared `#@ assigns xs` lowers to the same length-keeping
`writes { xs }` (Why3's `array` length is immutable), so the user-written frame is judged too (the same choice
#468 made for `\abstract` + `assigns x`). Refusal `PYCSL-R468-VAL-LIST-LENGTH` (message names route #481). Still
narrowed to vals the VERIFIED code of the file references (#468's rule), so an uncalled trusted stub is never judged.

BOUNDARY KINDS (probes `scratchpad/f2/p481/`, session scratchpad; verdict at base 8855b6b10 -> candidate):

| kind | probe | base | candidate |
|---|---|---|---|
| same-file `\trusted`, no `assigns`, `append` (the witness) | b01 | PROVED | REFUSED #468/#481 |
| same-file `\trusted`, no `assigns`, `pop` | b02 | PROVED | REFUSED |
| same-file `\trusted`, user `assigns xs`, `append` | b03 | PROVED | REFUSED |
| same-file `\trusted`, `assigns \nothing`, `append` | b08 | PROVED | REFUSED |
| same-file `\trusted`, no `ensures`, `append` | b07 | PROVED | REFUSED |
| same-file `\trusted`, closure `lambda: xs.append(1)` | b05 | PROVED | REFUSED |
| same-file `\trusted`, `xs.extend` | b06 | PROVED | REFUSED |
| same-file `\trusted`, `xs += [1]; return xs` | b17 | PROVED | REFUSED |
| same-file `\trusted`, `clear()` then index read | b12 | PROVED | REFUSED |
| `\trusted` METHOD, list parameter | b11 | PROVED | REFUSED |
| imported `\trusted` def (other module) | b10 | PROVED | REFUSED |
| `\abstract`, no `assigns` | b04 | REFUSED (#468) | REFUSED |
| verified callee with `#@ interface assigns x` | b15 | REFUSED (#49, Module 6) | REFUSED |
| verified recursive callee | b16 | REFUSED (#49) | REFUSED |
| `#@ no_inline` method on a global (rt38 l219) | -- | parse error (`assigns self.items` on no_inline) | unchanged |
| stdlib `heapq.heappush` / `bisect.insort` | b13 / b14 | REFUSED (#162) | REFUSED |
| CONTROL same-file `\trusted` store-only, no `assigns` | c01 | PROVED | PROVED |
| CONTROL same-file `\trusted` store-only, `assigns xs` | c03 | PROVED | PROVED |
| CONTROL `\abstract` store-only | c04 | PROVED | PROVED |
| CONTROL `\trusted` reads `len(xs)`, stores an element | c09 | PROVED | PROVED |
| CONTROL imported `\trusted` store-only | c10 | PROVED | PROVED |

Witnesses: `witnesses-r481/r481_trusted_append_len.py` PROVED at base, REFUSED; control
`r481_ctl_store_only.py` PROVED at both. Corpus `7560`-`7564` (PROVED at base, REFUSED), controls `7565`-`7567`
(PROVED at both).

RESIDUALS: a list FIELD written by a bodyless method (`self.xs.append`) is not covered (#468's residual); a
`\trusted` def nothing verified in the file references is not judged (it cannot make a caller's length wrong here).
