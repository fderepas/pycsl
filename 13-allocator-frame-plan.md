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

## 5. Reference corpus (REQUIRED for the tool features — see memory)
Add focused `test-suite/corpus/pycsl-reference/0XXX.py` cases:
- a class with `#@ class invariant p(self.field)` using a named predicate (the §3.0
  feature), proving establishment + maintenance;
- an intra-class `self._helper()` call where the caller inherits the callee's class
  invariant as an atom (the method-call-resolution + ordering fix), e.g. a loop that
  calls a field-mutating helper and proves the invariant at exit cheaply.

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
