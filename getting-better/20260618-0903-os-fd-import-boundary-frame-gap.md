# GAP: fd-resolution-fidelity retirement blocked on import-boundary frame-ensures propagation

**STATUS: LOGGED GAP — tool-machinery change required (not a model limitation).**
Surfaced 2026-06-18 after the fd-reuse allocator landed.

## Context (what's now done)
The os model gained a faithful fd-reuse allocator `_alloc_fd` (verified, ZERO trust):
scans `fd_open[3..64)` for the first free slot, marks it open, returns it, or `-1`
(honest ENFILE) only when every slot is open. `sys_open`/`sys_dup`/`sys_creat` allocate
through it (the broken monotonic `next_fd` counter — which never reused closed slots and
falsely read "full" after 61 opens — is retired). Body gate 2047→2092, `__init__`
1159/0, full `formal_os_*` suite 18/18, all green.

## The remaining wall (the GAP)
The 2 `fd-resolution-fidelity` trusts (`sys_open` 1238, `sys_dup` 2192) STILL do not
retire. With `_alloc_fd`, the honest **free-slot-conditioned** direction
`(\exists k in [3,64). fd_open[k]==0) ==> \result >= 3` is **body-provable with zero
trust**. But the public API consumes the **unconditioned** no-ENFILE direction
(`open source ⇒ dup succeeds`), and the side-condition "a free slot exists" is **not
establishable across the import boundary**:
- the global `_filesystem` starts `fd_open = Array.make 64 0` (all free), but
- each syscall's import-boundary `val` **havocs the whole `fd_open` array** (only the
  returned slot's cell is pinned), so "table not full" does not survive a prior `open`.

The single-cell `fd_open` FRAME (`\forall k != \result. fd_open[k] == \old(...)`) would
close this — but the propagation machinery
(`_build_method_field_param_frame_ensures_map` / `_dotted_ensures_suffix`) **drops
quantified `\result`-referencing frame ensures** (kept frames must be quantifier-bearing,
self-field+param, and contain NO `\result`). Machine-confirmed: forcing the conditioned
ensures reds `__init__` 1159→1158 and `dup_of_valid_source_is_valid`; reverted.

## The fix (human-gated, substantial)
A propagation-machinery change: carry `\result`-referencing single-cell quantified frame
ensures across the import boundary, so a wrapper can prove `fd_open[k]` (k != the new fd)
is preserved by a prior syscall — letting "table not full" survive composition. This is
high-blast-radius (touches the method-call/import contract lowering for every syscall);
out of scope for a single allocator pilot.

## Net
Model upgraded (faithful fd reuse, honest ENFILE, `_alloc_fd` zero-trust). os bare
`\trusted` unchanged at 8 — the 2 `fd-resolution-fidelity` trusts are now blocked behind
this NAMED TOOL gap rather than a model limitation. Documented in-file at `sys_dup`.

## UPDATE 2026-06-18 — the FRAME-PROPAGATION half is SOLVED; the wall moved to GLOBAL-INIT state
The tool gap above is FIXED. A new `\result`-frame propagation map carries the single-cell
`\forall k != \result. fd_open[k] == \old(fd_open[k])` across the method-call/import boundary:
- `src/pycsl/module6_whyml/functions.py` `_build_method_result_frame_ensures_map` (twin of
  `_build_method_field_param_frame_ensures_map`, keeps EXACTLY the `\result`-bearing frames the
  old map drops), opt-in via `#@ propagate_frame`. Wired through `Module6_WhyMLTranspiler.py`,
  `expressions.py` `_resolve_dotted_signature` (new field_spec slot 5) + `_dotted_ensures_suffix`.
- `\result` lowers to the val's `result` keyword (= the call result), so binding is automatic —
  no explicit substitution. The frame now EMITS on `_filesystem_sys_open_2` / `_filesystem_sys_dup_1`.
- GATING: corpus byte-diff = 0 (603/603 byte-identical — inert on the corpus; only `propagate_frame`
  `\result`-frame methods emit it, which is os-only); reference suite green; `__init__` gate SUCCESS;
  full formal_os_* suite 17/17; strmod green. Added `#@ propagate_frame` docs to all 5 normative
  surfaces (fixed a PRE-EXISTING doc-coherency miss).

**PROOF the fix is correct & sufficient (the probe):** with the table's all-free start ASSUMED at
entry, `dup(open(p))` proves VALID with ZERO trust (sys_dup body de-trusted + free-slot-conditioned
no-ENFILE discharges from `_alloc_fd`'s completeness ensures; the propagated frame carries the
free-slot fact across the prior `open`). So the frame half is done.

**THE REMAINING WALL (the new, distinct GAP):** the internals-blind formal test
`dup_of_valid_source_is_valid` reasons about the module-global `_filesystem` HAVOC'd at function
entry — PyCSL does not surface the constructor's ALL-FREE initial state as an importer-function
precondition. Without that, the test cannot establish "a free slot exists" (the table could be full
at entry). Assuming all-free blanket is UNSOUND (false across a sequence of API calls sharing one
`_filesystem`). So the trust retirement (de-trusting sys_dup) STILL reds the dup formal test — NOT
because of frame propagation (solved) but because of GLOBAL-INITIAL-STATE modeling for an
internals-blind importer. Per doctrine (no formal_os red), the de-trust was REVERTED; the SOUND
frame infra + body-provable free-slot-conditioned contract are BANKED. os `\trusted` stays 8.
Next: surface the module-global constructor invariant at importer entry (a fresh-instance / per-test
init model), THEN the retirement lands with the frame already in place.
