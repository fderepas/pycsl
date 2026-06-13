# Allocator / loop-writer type-invariant propagation — dedicated plan (2026-06-13)

Goal: close the remaining body-gate residual on the **loop-bearing disk writers**
(`_alloc_block`, `_alloc_inode`, and by extension `_write_inode`, `_write_directory`,
`_format_disk`, and the disk-mutating syscalls), extending the validated leaf-pattern
win so `pycsl pure_lib/os/UnixInodeFileSystem.py` (the standalone body gate) moves from
1573/1670 (94.2%) toward complete — without regressing os `__init__` (green) or the
corpus.

This is a **multi-piece tool + model effort with uncertain payoff**; it deserves its own
session. Do NOT start it as a side-quest. The cheap/medium levers are all exhausted (see
"Dead ends" below) — only the full design here has a chance.

---

## 0. What already landed (do not redo) — on `main`

- `cdab9ba` feat(os) pt1: **triggered `block5_decode_frame`** in the registry
  (`src/pycsl/module6_whyml/preamble.py`, flattened multi-pattern
  `[slot_inode d1 5 k, slot_inode d0 5 k | slot_name ...]`; logic-identical so
  Block5DecodeFrame.{v,lean} still apply; os-only axiom → corpus byte-identical) +
  **`_poke(p,v)` leaf** (single-byte write outside block 5; bears the class-invariant
  maintenance once, in minimal context). **`_set_bitmap`: 6 timeouts → 0.**
- `485f35c` feat(os) pt2: dropped now-redundant slot-frame ensures on
  `_set_bitmap`/`_alloc_block`/`_alloc_inode`.
- Gated: **os `__init__` SUCCESS / 0 non-Valid** throughout; `_poke` proves 18/18.
- Diagnosis docs: `RESUME-STATE.md` sections "DIRECTORY-FRAME REWORK" + "OPTION (a) /
  ALLOCATOR ROOT-CAUSE".

The leaf pattern works because the leaf **proves** the invariant itself. The allocators
fail because they must **inherit** it from a callee — and that inheritance is the wall.

---

## 1. The two-layered wall (root cause, validated 2026-06-13)

In the standalone emit (`pycsl … --keep-mlw`), `_alloc_block` lowers its body to:
```
while ... do
  if (self__get_bitmap_2 4 !i) = 0 then begin
    let _ = (self__set_bitmap_3 self 4 !i 1) in ();   (* <-- a STUB, not the real method *)
    raise (Return !i) end ; ...
```
where the stub is declared contractless:
```
val self__set_bitmap_3 (self: unixinodefilesystem) (x0 x1 x2: int) : unit   (* no requires/ensures/writes *)
```

**Layer 1 — method-call contract gap.** Intra-class `self._set_bitmap(...)` /
`self._get_bitmap(...)` calls inside ANOTHER method of the same class lower to abstract
`val` stubs (`self__set_bitmap_3`, `self__get_bitmap_2`), NOT to the verified
`unixinodefilesystem___set_bitmap` (which IS proven 7/7 but is unused by callers). The
stub carries none of the method's contract, and crucially does not convey that the
post-state satisfies the **type (class) invariant**. See
`memory/pycsl_method_call_contract_gap.md` — it claims self-calls work, but the
TYPE-INVARIANT is not propagated through them in this case.

**Layer 2 — inline-`forall` type-invariant doesn't propagate even WITH a contract.**
Hand-experiment (`/tmp/bg10.mlw`): gave the stub `writes { self.disk }` +
`ensures Array.length self.disk = Array.length (old self.disk)`. `_alloc_block` gained
Valid goals but kept ~6 **Type-invariant** timeouts (1 OOM + 1 Timeout + ~4 Unknown).
Reason: the class invariant is an **inline `forall`** (uniqueness double-`forall` over
`slot_inode`/`slot_name`; byte-range `forall i. 512≤i<2560 → 0≤disk[i]≤255`). A
`forall`-hypothesis (post-call invariant) discharging a `forall`-goal (exit invariant)
needs per-skolem instantiation → the same E-match explosion the leaf rework removed.

So the allocators are blocked by the **interaction** of Layer 1 and Layer 2. Fixing
either alone is insufficient (validated — see Dead ends).

---

## 2. Design — "named predicate done right" + method-call resolution

The fix must make the callee's invariant guarantee usable by the caller as a **single
opaque atom**, so no `forall` instantiation happens at the call/return boundary.

### 2a. Named, abstract class-invariant predicates
Introduce two **abstract** predicates over the disk, declared in
`_AXIOM_FUNCTIONS["UnixFs.Dir."]` (the same machinery that declares
`slot_inode`/`slot_name`/`dir_lookup`):
- `predicate uniq (d: array int)` — directory uniqueness.
- `predicate inode_bytes_valid (d: array int)` — the `[512,2560)` byte-range.

Use them **in the class invariant** (`#@ class invariant uniq(self.disk)`,
`#@ class invariant inode_bytes_valid(self.disk)`), replacing the inline `forall`s.
Then a callee that maintains the type invariant exposes `uniq self.disk` /
`inode_bytes_valid self.disk` as **atoms**, and the caller's exit goal is the SAME atom →
literal match, O(1), no instantiation. (This is the part the 2026-06-13 hand-experiment
got WRONG: it kept a `[uniq d]` trigger on the intro axiom that force-fired re-derivation;
see Dead ends.)

Backing axioms (each must be **cross-validated** in Rocq+Lean like the existing
`UnixFs.Dir.*`, OR proven as why3 `lemma`s if SMT-dischargeable — prefer lemma to avoid
TCB growth):
- `uniq_intro`: `(forall i j. <uniqueness body over d>) → uniq d` — establish from the
  forall (constructor, directory mutators). **No trigger that forces firing on `uniq d`**
  (that re-derives in callers). If a trigger is needed, key it on the forall's witness
  terms, not on `uniq d`.
- `uniq_elim` (only if a consumer needs the unfolded form).
- `uniq_block5_frame`: `(forall b. 2560≤b<3072 → d0[b]=d1[b]) → uniq d0 → uniq d1` — the
  predicate-level frame; lets a writer that proved its block-5 byte-frame conclude
  `uniq` preservation as an atom. (Provable from `block5_decode_frame` + `uniq_intro`/
  `uniq_elim` — emit as a why3 `lemma`.)
- analogous `ibv_*` for `inode_bytes_valid` (the byte-range frame is simpler: an update
  outside `[512,2560)` preserves it; an update inside needs the written byte ∈ [0,255]).

DECISION POINT (resolve first, see §3.0): does PyCSL support **defining/declaring a
predicate** and **referencing it in a `#@ class invariant`**? Today only built-in
uninterpreted predicates exist (`\permutation`→`permut`). The `_AXIOM_FUNCTIONS` raw-text
mechanism can emit `predicate uniq (d: array int)`, but the model needs to *call*
`uniq(self.disk)` in a `#@ class invariant` and have it lower to `uniq disk`. Verify
`Module2_Parser` + the class-invariant lowering path accept a predicate application as a
proposition; if not, that's the first tool task.

### 2b. Fix the method-call contract gap for intra-class helper calls
`_alloc_block`/`_alloc_inode` (and the syscalls) must call the **real verified**
`set_bitmap`/`get_bitmap`/`write_inode`/… so why3 uses the callee's contract AND its
type-invariant guarantee on the result.

Two sub-problems:
1. **Resolution**: `self._set_bitmap(...)` should emit a call to
   `unixinodefilesystem___set_bitmap self ...`, not the `self__set_bitmap_3` stub.
   Investigate `expressions._handle_dotted_call` / the self-call path (the Gap-7
   void/mutating self-call fix in `memory/pycsl_method_call_contract_gap.md` should
   already cover `assigns`-only methods — find why it doesn't fire here; likely the
   helper isn't in the resolved method map, or the stub path wins).
2. **Ordering**: a real call needs the callee emitted BEFORE the caller (the
   `/tmp/bg9.mlw` experiment failed with `unbound function 'unixinodefilesystem___set_bitmap'`
   because alloc precedes set_bitmap in the emit). Use the existing `scc.py` ordering —
   but the dependency edge only exists once resolution (1) creates the real call. Confirm
   `scc.py` topologically orders by the real call graph; if helpers are leaves they
   should sort first. Mutually-recursive groups → `let rec … with`.

### 2c. Loop interaction
After 2a+2b, `_alloc_block`'s loop calls the real `set_bitmap` (maintains `uniq`/`ibv` as
atoms) then `return i`. The loop invariant need not carry the type invariant if why3
re-assumes it for the havoc'd field at the loop head AND the callee guarantee gives the
atom on the write path. If a residual remains, add `#@ loop invariant uniq(self.disk) and
inode_bytes_valid(self.disk)` explicitly (now cheap atoms).

---

## 2.5 Implementation map — PRECISE code sites (established 2026-06-13)

Investigation while starting the implementation pinned the exact sites. **Why the earlier
named-predicate experiment failed is now understood**: alloc called the CONTRACTLESS stub
`self__set_bitmap_3`, so it had no `uniq(post)` hypothesis to match — the predicate idea was
right but starved by the method-call gap. Both fixes (predicate + method-call) are required.

- **DONE (`755f89e`)**: `preamble.py` `_precompute_axiom_logic_funcs._names_of` +
  `_inductive_referenced_axiom_decls` + `_emit_uncited_axiom_func_decls` now recognize
  `predicate FOO (args)` (was `val function`/`function` only). So an abstract `predicate uniq
  (d: array int)` added to `_AXIOM_FUNCTIONS["UnixFs.Dir."]` will bind + be emitted before the
  record. Corpus-neutral until such a decl exists.
- **Method-call gap (Layer 1) — the two sites:**
  1. `scc.py::find_calls_in_ir` (line ~10) matches `obj["func"] in func_names_set`. A
     `self._set_bitmap(...)` call node's `func` is the DOTTED name `"self._set_bitmap"`, NOT the
     method func name `"unixinodefilesystem___set_bitmap"` in `func_names_set` → **no ordering
     edge**. Body calls DO create edges (line 93 `body_edges`, unlike contract refs) — so once
     the name resolves, ordering (callee-before-caller) works automatically. Need to resolve
     `self.<m>` → `<class>__<m>` here, which requires per-function class context threaded into
     `sort_functions_by_scc` (currently absent — it sees a flat function list).
  2. `expressions.py::_handle_dotted_call` (line ~818): the CONCRETE-call path already exists at
     lines 828-835 for `_composed_provider_methods` (`(<class>__<m> self args)`). Extend it to
     intra-class `self._helper()` where the helper is a same-file verified method — emit the
     concrete call so why3 uses the real method's contract AND its type-invariant guarantee on
     the result. `_composed_provider_methods` is populated from `ir["composed_provider_methods"]`
     (Module6 line 478); either add the verified helpers there or add a parallel set.
  RISK: this changes method-call lowering used CORPUS-WIDE (many files use `self.method()`),
  and ordering. MUST gate on the full corpus PROOF, expect iteration. Scope it so only
  same-file verified-method self-calls switch to concrete (others keep the abstract `val`).
- **Predicate atoms + triggers (Layer 2):** after the method-call gap is fixed so alloc HAS the
  `uniq(post)`/`inode_bytes_valid(post)` hypotheses, add the abstract predicates + intro/elim/
  frame axioms (see §2a). Trigger discipline (critical — validated failures in §7): `uniq_intro`
  must NOT force-fire on `[uniq d]` (it made every uniq goal re-derive the forall + regressed
  `_poke`); `_poke`/disjoint writers need a `uniq_block5_frame` atom-level axiom
  (`byte-frame → uniq d0 → uniq d1`); directory mutators need `uniq_elim` (`uniq d → forall`)
  to feed `insert_preserves_unique`. The intro/elim pair is a DEFINITION (sound by construction,
  no Rocq/Lean needed); the frame axiom is derivable → emit as a why3 `#@ lemma`.

## 2.6 IMPLEMENTATION RESULT 2026-06-13 — allocators FIXED, but Layer 1 regresses mutator-callers
Implemented Layer 1 (`a9c6bd3`) + Layer 2 (`01fb652`) + §3.4 loop invariants (`65bbda8`).
Per-function body-gate measurement (standalone, 30s, both provers):
- **FIXED (slot-PRESERVING writers):** `_alloc_block` 38/38, `_alloc_inode` 38/38,
  `format_disk` 87/87, `_set_bitmap`, `_poke` 18/18, constructor 18/18; `sys_rename` 6->0,
  `sys_rmdir` 4->2.
- **REGRESSED (slot-CHANGING mutator callers):** `sys_link` ~0->18 (8 OOM+10 T),
  `sys_unlink` 8->18, `sys_mkdir` 0->2.
- **ATTRIBUTION (worktree at a9c6bd3 = Layer 1 only, inline invariants):** `sys_link`
  8 OOM+10 T, `sys_unlink` 7 OOM+15 T, `sys_mkdir` 2 T — IDENTICAL to Layer 1+2. So the
  regression is **Layer 1's concrete calls**, not Layer 2. Calling a directory mutator
  (`_write_directory`) CONCRETELY surfaces its intrinsically-expensive inline-forall
  uniqueness maintenance in the caller. Layer 2 is neutral there.
- **Net body-gate: roughly a WASH.** NOT a committed-test regression — os `__init__` stays
  GREEN (sys_* are trusted vals there); the body gate was never a green target (94.2% WIP).
  This is residual REDISTRIBUTION.
- **THE CLEAN FIX (next focused step): SCOPE the concrete-call routing** in
  `expressions._handle_dotted_call` to fire ONLY for slot-PRESERVING callees (the leaf
  disk writers `_poke`/`_set_bitmap`/`_write_inode` that write outside block 5), keeping
  abstract stubs for the slot-CHANGING directory mutators (`_write_directory`/`_write_entry`/
  `_zero_entry`/...). That keeps the allocator/write/format win and DROPS the
  link/unlink/mkdir regression (restoring them to their clean pre-rework state). Detection
  options: (a) an explicit small denylist of the block-5 mutator method names (precise, the
  set is fixed & small); (b) a principled signal — a callee carrying a block-5 byte-frame
  ensures is slot-preserving. Gate: re-measure link/unlink/mkdir return to clean + allocators
  stay fixed + os __init__ green + corpus byte-diff (only 0654 expected). Then full body gate.

## 2.7 SCOPE-TO-WIN ATTEMPT 2026-06-13 — CROSS-GATE CONFLICT (reverted, not landed)
Tried scoping the concrete-call routing to slot-PRESERVING callees by marking the heavy
helpers `#@ no_inline` and making `_handle_dotted_call` skip `no_inline` callees (general
rule) + a `_no_inline_methods` set in Module6. STANDALONE result was excellent — concrete
ONLY `_set_bitmap`/`_poke`, everything else (`_write_inode`/`_alloc_block`/`_alloc_inode`/
`_write_directory`/`_write_entry`/`_zero_entry`) abstract: **link 18->1, unlink 18->4,
mkdir 2->1, allocators stay 38/38, format_disk 0 non-Valid.** A clean net-positive on the
body gate.
BUT it **REGRESSED os `__init__`** (the committed green deliverable): `truncate'vc`
Out-of-memory. Root cause: `no_inline` is OVERLOADED — it means BOTH (a) my new
"skip concrete sibling-call" AND (b) the ORIGINAL "don't inline the body into wrappers."
Marking `_write_inode` no_inline made os `__init__`'s `truncate` wrapper use `_write_inode`'s
CONTRACT instead of inlining its body, and the contract is insufficient for truncate's
block-frame assertion -> OOM. So `_write_inode` cannot be `no_inline`, yet `_write_inode`
concrete is exactly what regresses standalone link/unlink. Reverted (working tree back to
`65bbda8`, os `__init__` green).
**THE CLEAN FIX needs a flag DECOUPLED from `no_inline`** (one that ONLY skips the concrete
sibling-call, leaving `__init__` inlining untouched). Two options:
  (a) NEW opt-IN directive `#@ sibling_concrete` on `_set_bitmap`/`_poke` only (concrete-call
      becomes opt-in; default reverts to the pre-Layer-1 abstract stub = no link/unlink
      regression, no `__init__` effect). ~8 mechanical edits across the pipeline + doc/corpus
      (language-audit). The DEFAULT-OFF means it cannot regress `__init__` or the corpus.
  (b) STUB-ENSURES pivot (no concrete-call at all): revert Layer 1; add `#@ ensures
      uniq(self.disk)` + `inode_bytes_valid(self.disk)` to `_set_bitmap`/`_poke`; the
      allocators then get the atoms from the abstract STUB's propagated field-ensures (+ loop
      invariants). Cleanest IF the stub path propagates a predicate-call field-ensures
      (UNVERIFIED — test first). No concrete-call, so no `__init__`/corpus risk.
Recommend (a) — opt-in is the safest (default-off cannot regress anything).

## 2.8 OPTION (a) LANDED 2026-06-14 — clean win via `#@ sibling_concrete` opt-in directive
Implemented the decoupled opt-in flag (commits `c474f9e` tool+model, `a2c4d59` docs+corpus).
New directive `#@ sibling_concrete`: an intra-class `self.<m>()` call to a MARKED callee
lowers to a CONCRETE call (caller inherits the callee's contract + type/class-invariant
guarantee as an atom); all other self-calls keep the default abstract stub. Decoupled from
`no_inline` (sibling-call lowering only), so it does NOT touch `__init__` wrapper inlining —
resolving the §2.7 cross-gate conflict. Marked `_set_bitmap` + `_poke` only.
RESULT vs ORIGINAL baseline (standalone body gate, 30s): allocators ~10 -> 38/38 each (FIXED);
format_disk 4 -> 0; unlink 8 -> 4; link 0 -> 1; mkdir 0 -> 1; rename/rmdir unchanged. **Net
+26, no regression of substance.** GATED: os `__init__` GREEN (0 non-Valid); corpus byte-diff
= ONLY 0654 (reverts to its pre-broad-Layer-1 abstract stub, still proves) + new 0705 (proves);
doc-coherency PASSES (5 surfaces). Wired: Module2 grammar/node/transformer, Module3 weaver flag,
Module5 IR flag, Module6 set + opt-in routing, scc edge-scoping. The full body-gate headline
re-run is in `.audit-cache/bodygate/final.txt`.
DONE for the plan's core. Remaining residual (link/mkdir 1 Timeout each; the deep directory-
mutator maintenance) is minor and out of scope — the allocators (the target) are fully proven.

## 3. Implementation steps (ordered; gate after each)

0. **Feasibility spike (≤1 session, do FIRST):** confirm PyCSL can declare an abstract
   predicate and reference it in a `#@ class invariant`. Minimal model: a 1-field class
   with `#@ class invariant p(self.a)` + `predicate p` via `_AXIOM_FUNCTIONS` + an intro
   axiom. If it emits + typechecks, proceed. If not, the predicate-in-invariant lowering
   is task #1.
1. Add `uniq`/`inode_bytes_valid` predicates + intro/frame axioms (cross-validated or
   lemma) to the registry; rewrite the two class invariants to use them. Re-prove the
   **constructor** (must still establish them via intro + `empty_disk_slots_dead`) and
   **`_poke`/`set_bitmap`** (must still maintain them via intro). Target: constructor
   18/18, set_bitmap 0 non-Valid — i.e. no regression from the named form.
2. Fix the method-call resolution (2b.1) so `_alloc_block` calls the real `set_bitmap`/
   `get_bitmap`. Fix ordering (2b.2).
3. Re-gate the allocators with the fast loop (below). Expect them to drop to ~0; if loop
   residual, add the cheap atom loop invariants (2c).
4. Propagate to `_write_inode` (in-range blit — may need an `_poke`-like blit leaf or its
   existing near-clean state suffices: baseline 1 Unknown), `_write_directory`,
   `_format_disk`, then the disk-mutating syscalls (`sys_write`, `sys_unlink`,
   `sys_rename`, `sys_rmdir`, `sys_truncate`, …).
5. Full standalone body-gate run (multi-hour, background) → new Valid/1670 count.

---

## 4. Gating (NON-NEGOTIABLE — see RESUME-STATE "Gating discipline")

- **Fast per-function loop** (≈1 min/fn): emit once
  `pycsl pure_lib/os/UnixInodeFileSystem.py --keep-mlw --no-proof`, then
  `why3 prove -a split_vc -P "Alt-Ergo,2.6.2," -P "Z3,4.13.3," --timelimit 30 <mlw>
  -T PyCSL_Program -G "unixinodefilesystem___alloc_block'vc"`. Scan EVERY non-Valid incl.
  "Out of memory".
- **os `__init__` GREEN** after every step (`pycsl pure_lib/os/__init__.py`, 0 non-Valid).
- **Corpus**: any registry/emitter change → `bin/byte-diff-sweep.sh` both ways vs HEAD;
  behavior-changing → gate on the corpus PROOF (`bin/run-reference-tests.sh`), NOT just
  byte-diff. (New `UnixFs.Dir.*` axioms are os-only → corpus byte-safe, but a generic
  predicate-in-invariant lowering change is NOT os-only — sweep it.)
- **Any new axiom** must be cross-validated Rocq+Lean (or be a why3-checked `#@ lemma`,
  preferred — no TCB growth). Do not add trusted axioms.

## 5. Reference corpus (REQUIRED for the tool features — see memory) — ✅ DONE
- ✅ `0706` — a class with `#@ class invariant field_nonneg(self.x)` using a named
  REGISTRY predicate (the §3.0 feature), proving establishment + maintenance (`af109b5`).
- ✅ `0705` — an intra-class `self.bump()` call to a `#@ sibling_concrete` field-mutating
  helper inside a loop, the caller inheriting the class invariant as an atom (`a2c4d59`).

## 6. Risks / fallbacks
- **Predicate-in-invariant unsupported** → the §3.0 lowering becomes the gating tool task;
  if it balloons, fall back to keeping inline invariants and pursuing option (a) proper
  (explicit `\old`-arg frame-lemma application — a separate frontend feature, also large).
- **why3 still re-derives** even with atoms (e.g. it unfolds the predicate via the intro
  axiom's trigger) → ensure intro/frame axioms are NOT triggered on `uniq d`/`ibv d`;
  validate on `/tmp/bg5.mlw` before touching the model.
- **Method-call resolution regresses the corpus** → it's a broad change; the corpus PROOF
  gate is mandatory, expect iteration.
- **Uncertain payoff**: if after 2a+2b the allocators still time out (Layer-2 persists for
  a reason not yet understood), STOP and reconsider — do not grind. The leaf win is banked
  regardless.

## 7. Dead ends (do NOT retry — all validated negative 2026-06-13, /tmp artifacts noted)
- Reworking the line-436 byte-range invariant (trigger / removal): minor; removal clears
  only ~2/6 of set_bitmap's goals. (/tmp/bg_trig3.mlw, /tmp/bg_nodiskinv.mlw)
- Triggers on invariants/ensures/the block5 axiom in FULL context: plateau; +120s budget
  doesn't help (genuinely hard, not slow). (/tmp/bg_trig2.mlw, /tmp/t120_result.txt)
- Update-keyed frame lemma `[uniq (d[k<-v])]`: doesn't fire (mutable-field write isn't a
  syntactic `d[k<-v]` term). (/tmp/poke_test.mlw)
- Abstract `uniq` predicate WITH `[uniq d]` trigger on intro: backfires (forces
  re-derivation), regresses `_poke` 18→17, no alloc fix. (/tmp/bg6.mlw)
- Abstract `uniq` WITHOUT trigger: still no alloc fix. (/tmp/bg8.mlw)
- Contracted stub (`writes`+length, no real call): alloc still ~6 Type-invariant
  timeouts. (/tmp/bg10.mlw)
- Per-function axiom scoping (earlier): zero proof-perf benefit. (reverted `b1e1d12`)
