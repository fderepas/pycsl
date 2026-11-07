# self-field-append-wall.md — faithful `self._field.append(x)` emission (the pyval cascade's leverage node)

**For review. State-of-the-art report on the wall now gating the value-model cascade: the emitter lowers a
self-field list append to a shadow-local that never writes back. The MODELING is already proven; the wall is the
EMISSION + its blast radius.**

## 1. Global picture
PyCSL lowers annotated Python to WhyML discharged by Why3/SMT. The self-annotation effort mirrors the live emitter
into `src/self-annotate/src/` and drives its `#@ \trusted` stub count DOWN under a fixed contract, gated by three
disjoint oracle planes (fidelity, whole-file Why3 proof, corpus byte-diff-0 OR an M1 sanctioned-reset). Count is
**1015**, ledger **3** (must stay 3). The prior run BROKE the heterogeneous `Dict[str,Any]` value-model wall (built
+ certified axiom-free the `pyval` and emit_ir Call-internals ADTs; first count cut `_collect_typevar_registry`).
The cascade to the OTHER ≥4 module-body collectors (`_collect_final_registry`, `_collect_type_params`,
`_collect_class_fields`, `_synthesize_typeddict/namedtuple_functional`, `_synthesize_tuple_records`) is now blocked
on ONE shared node: a faithful self-field list append.

## 2. The wall — first seen (Bug 3)
Every one of those collectors ends by appending a built (heterogeneous) dict to a self-field list:
`self._final_registry.append({...})` / `program_ir["type_decls"].append({...})` / `self._env_keys.append(key)`.
The emitter lowers `self._field.append(x)` to a **shadow-local that never writes back**. Evidence — the only
existing precedent, `src/pycsl_lib/proc/__init__.py::setenv` (emitted `.mlw:133,150,154`):
```
let self__env_keys = Array.make 1024 0 in   (* a FRESH local, typed array int (int-erased) *)
self__env_keys[len] <- key                  (* writes the LOCAL, never the field *)
```
`self._env_keys` (the real field) is never assigned. So the append's EFFECT is unmodelled: a method's post-state
`self._field` is identical to its pre-state in the model. Two faces: **(a)** the append-emission facade (no
write-back, even for the homogeneous `array int` case); **(b)** the IREmitter mirror `PyCSLToJSONEmitter.__init__`
is `pass`/`\trusted` (a deliberately fieldless mixin — `_final_registry` is not a modeled field at all).

## 3. The deeper truth — a modeling choice, NOT a fundamental limit
A self-field IS a mutable record field; `self._field.append(x)` IS `self._field <- snoc (old self._field) x`. For
the heterogeneous case the field is `seq pyval` (reusing the certified `pyval` ADT). This **MODELING is already
PROVEN axiom-free** (hand `.mlw`, `why3 prove -P z3` all Valid: `append_final'vc`, read-back `class = Some (PStr
cls)`, sequential compose, evil-twin non-vacuous; `use seq.Seq` + `Seq.snoc`, reuses Phase2f, no axiom). What is
missing is the **EMISSION** (lower the append to a real field write-back, not a shadow-local) and, for the mirror,
a **stateful field declaration** (the `proc`/`UnixInodeFileSystem` stateful-record + class-invariant shape).

## 4. SOTA lens — faithful self-field mutation
The precedent exists: `@mutable_state` records with a class invariant already model self-field WRITES elsewhere
(the mutex/inode subsystems). The NEW capability is (i) a self-field-**append** effect (`field <- snoc old field
x`) emitted faithfully with its frame, and (ii) a `seq pyval` field for the heterogeneous element. This is the
read-side analogue of the pyval map store, one step up (a list-append effect instead of a map-update).

## 5. Honestly-costed routes
- **R-emit (make-or-break): faithful self-field-append emission.** Replace the shadow-local with a real
  `self._field <- snoc (old self._field) <elem>` (elem = a `pyval`/`PMap` for the heterogeneous case, reusing
  Phase2f — NO new cert; `array`-backed for the homogeneous case). **HIGH BLAST RADIUS: the corpus USES
  `self.field.append`** (proc `setenv` etc.), so this is an **M1 SANCTIONED-RESET, not byte-inert** — the diff must
  be EXACTLY the fix AND every affected corpus program must RE-PROVE. The decisive risk: the current facade may make
  corpus proofs pass *vacuously* (the append effect is invisible); a faithful write-back makes the effect real and
  could turn a vacuously-green corpus proof RED (revealing a latent-vacuous contract). The make-or-break is whether
  the affected corpus programs stay green under the faithful emission (clean M1) or break.
- **R-mirror: the fieldless-mirror stateful retrofit.** The IREmitter mirror needs `_final_registry` as a modeled
  `seq pyval` field + a class invariant to convert the collectors — invasive for a fieldless 60-stub mirror
  (no precedent, byte-diff risk). Alternative: a behavior-preserving **return-value refactor** of the collector
  (build a local list, return it; callers read the return) — avoids the self-field sink but changes live+mirror +
  the callers (must be byte-diff-0 on the corpus).

## 6. Honest limits + certificate
The `pyval` cert (Phase2f) already covers the `seq pyval` element soundness; a `seq pyval` append needs only
`seq.Seq`/`snoc` (Why3-intrinsic, no new axiom — verified in the R3 spike). The risk is NOT the model (proven) but
(a) the M1 corpus re-prove (does the faithful emission keep proc/etc. green?), and (b) the mirror-retrofit-vs-
return-refactor blast radius. Ledger stays 3.

## 7. The make-or-break question for review
Does replacing the shadow-local `self._field.append` facade with a **faithful `self._field <- snoc (old
self._field) x` write-back** (i) typecheck + prove for a fixture appending a `pyval`/`PMap`, AND (ii) keep every
affected CORPUS program (proc `setenv`, and any other `self.field.append` user) GREEN under an M1 sanctioned-reset
(the diff is exactly the write-back fix; each affected program re-proves) — axiom-free (ledger 3)? Or does the
faithful effect turn a currently-(vacuously)-green corpus proof RED (revealing the facade was load-bearing), making
the blast radius unbounded? **An oracle run — apply the minimal write-back to the append emission, re-emit +
`why3 prove` proc `setenv` (and grep the corpus for other `self.*.append` users), and report GREEN/RED per
program — should CONFIRM (clean M1) or REFUTE (corpus breaks) before any collector conversion.**
