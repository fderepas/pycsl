# RESOLVED (sys_dup): fd-resolution-fidelity retired via `#@ fresh_globals` global-init surfacing

**STATUS: sys_dup `fd-resolution-fidelity` RETIRED (2026-06-18) — `#@ fresh_globals` built, wired,
documented, and PROVEN sound + confined. os bare `\trusted` 8→7 (sys_dup); sys_open is the next PILOT.**
The original GAP (below, kept for the record) is closed for sys_dup by a sound, confined,
constructor-backed global-init surfacing directive — NOT a blanket-false `requires`.

## THE FIX THAT LANDED — `#@ fresh_globals`
The all-free entry state is surfaced SOUNDLY by a new opt-in, Module4-confined directive:
- **Constructor ensures (NEW):** `UnixInodeFileSystem.__init__` now carries
  `#@ ensures \forall k: int; (0<=k<64) ==> self.fd_open[k] == 0`. The transpiler emits a checked
  `let _filesystem_fresh_init () : unixinodefilesystem ensures {…} = <ctor literal>` that PROVES
  the post-state of the freshly constructed global (the `Array.make 64 0` witness) — the os
  `__init__` gate is GREEN with it.
- **`#@ fresh_globals` (NEW):** on a STANDALONE, internals-blind formal-test driver, emits at the
  driver's body entry an `assume` of each module-global singleton's constructor `#@ ensures`
  (`self` → the global). Wired grammar→validate→IR→WhyML; documented on all 5 normative surfaces
  (doc-coherency PASS); corpus exhibit `0713.py` (+ verified negative case).
- **Soundness/confinement:** Module4 (`core_ir_semantic._check_fresh_globals`) REJECTS the directive
  on a method (`self`-receiver) or any callee (`PYCSL-SEM-FRESH-GLOBALS`) — sound only for an
  independent entry point that runs on a freshly-imported global. The assumed fact is the
  constructor's PROVEN ensures (re-established by construction), never an arbitrary literal.
- **Retirement (sys_dup PILOT):** sys_dup body rewritten to the free-slot-CONDITIONED no-ENFILE
  (zero-trust via `_alloc_fd` completeness), `os.dup` wrapper conditioned to mirror, the
  `dup_of_valid_source_is_valid` formal test marked `#@ fresh_globals`. `\trusted reviewer:
  fd-resolution-fidelity` REMOVED from sys_dup. GATES: sys_dup body (full file) zero-trust SUCCESS;
  formal_os suite 17/17; os body gate 2135 Valid / 4 documented-residual unproven (unchanged class —
  `_unpack_direntry` ×2, `_now`, `sys_rename`; sys_dup NOT among them); os `__init__` GREEN; strmod
  GREEN; doc-coherency PASS.

---

# (ORIGINAL GAP — kept for the record)

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

## UPDATE 2026-06-18 (later) — the wall PRECISELY characterized at the WhyML level; SOUND mechanism scoped; still a GAP
A squeeze run drove the de-trust pilot end to end and pinned the wall to its exact WhyML cause.

**WHERE THE GOAL ACTUALLY REDS (two distinct sites, both real):**
1. **BODY of `sys_dup`** (`--fun unixinodefilesystem__sys_dup`, trust removed): the single unproven goal is
   `((oldfd<64) && (old fd_open[oldfd]=1)) -> result>=3` (the UNCONDITIONED no-ENFILE). This is
   **literally false as a body theorem** — a full table of OTHER open fds makes `_alloc_fd` return -1, so
   `result=-1`, not `>=3`. The body genuinely cannot prove it. The FREE-SLOT-CONDITIONED form
   `(... and \exists k. 3<=k<64 and \old(fd_open[k])==0) ==> result>=3` proves with ZERO trust (verified).
   So a sound de-trust REQUIRES rewriting the contract (body + `os.dup` wrapper) to the conditioned form.
2. **Formal test `dup_of_valid_source_is_valid`** (after the conditioned rewrite): reds because the test
   cannot establish the `\exists k. fd_open[k]==0` the conditioned `dup` val now demands.

**THE ROOT CAUSE (newly pinned):** the module-global `_filesystem` is HAVOC'd at EVERY importer-function
verification entry. PROOF: an `#@ assert \exists k. 3<=k<64 and _filesystem.fd_open[k]==0` placed at the
VERY FIRST line of a formal-test function (before any syscall) FAILS. The `let _filesystem = {...all-free
literal...}` is only the *initialization*; Why3 verifies each function with `_filesystem` in an ARBITRARY
state (standard treatment of a shared mutable global — other functions could have mutated it). The no-`writes`
murkiness on the import vals (Why3 warns "`_filesystem` is used under `old` but is not modified") is NOT the
blocker — see the diagnostic below.

**DIAGNOSTIC — the propagation half is DONE; only the entry state is missing:** with an explicit
`requires \forall k. (3<=k<64) ==> _filesystem.fd_open[k]==0` (all-free at entry) ADDED to the test, the
conditioned chain `dup(open(p))>=3` PROVES with ZERO trust, AND a `dup(dup(open(p)))` chain ALSO proves
(the `open`/`dup` single-cell frames correctly carry occupancy from the all-free base — only the touched
cells become 1). So `#@ propagate_frame` (the prior layer) + `_alloc_fd`'s completeness ensures are
SUFFICIENT. The ENTIRE residual is: surface the all-free entry state SOUNDLY.

**THE SOUNDNESS LINE (sharp):**
- That `requires \forall k. fd_open[k]==0` is the FORBIDDEN blanket-false precondition: it lets the function
  *assume* all-free, which is false in any composed context (after a sequence of opens). NOT a deliverable.
- The SOUND surfacing must *establish* all-free BY CONSTRUCTION at the function entry (mirroring "a fresh
  driver freshly imports os, so `_filesystem.__init__` ran and the table is all-free at entry"), never
  *assume* it. The honest mechanism is a tool change that, for an internals-blind formal-test importer
  function, RE-ESTABLISHES the module-global constructor post-state at the function body entry (e.g. a
  `#@ fresh_globals` directive emitting `_filesystem`'s constructor literal / its all-free ensures at body
  start, so all-free is a PROVEN fact at entry, not a precondition). Soundness rests on the fresh-import-
  driver argument AND on these functions being independent entry-points never inter-called with the shared
  pre-mutated global — the mechanism must be confined to that case (a formal-test importer driver), never a
  general always-on assumption. Subtlety to guard: if surfaced as a blanket assumed fact on every importer
  function and one such function were CALLED by another (passing the already-mutated global), the callee
  would falsely assume all-free — UNSOUND. Confining the re-establishment to standalone driver entry avoids
  this.
- Also requires a constructor `#@ ensures` capturing the all-free initial state
  (`\forall k. (0<=k<64) ==> self.fd_open[k]==0`), currently ABSENT on `UnixInodeFileSystem.__init__`, as
  the fact the surfacing re-establishes.

**VERDICT: STILL A LOGGED GAP (sound surfacing not yet built).** The de-trust was piloted (sys_dup body
de-trusted + conditioned), the conditioned body proved zero-trust, the `os.dup` wrapper proved, but the
formal test reds for want of the sound entry-state surfacing — and the only thing that closes it (a blanket
all-free `requires`) is the forbidden unsound move. Per doctrine (no formal_os red, no unsound surface),
EVERYTHING was REVERTED. os `\trusted` stays 8. The remaining work is a NEW tool mechanism
(`#@ fresh_globals`-style constructor-post-state re-establishment at importer-driver entry) + the
constructor all-free `#@ ensures` — high-blast-radius, human-gated. The frame infra + body-provable
conditioned contract remain BANKED and ready: the day the entry state is surfaced soundly, the retirement
lands with one rewrite.

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
