# Body-gate refactor (Option A): faithful array-through-tuple typing for standalone os

**Goal.** Make `pycsl pure_lib/os/UnixInodeFileSystem.py` (the standalone model) verify the
`sys_*`/helper METHOD BODIES — a real, sound body gate (0 trusted) — so os method-body `#@ ensures`
(the existing gap-14/15/16 ones AND gap-17) are actually discharged, not assumed. Today the
standalone aborts on a CASCADE of emitter type errors; the `__init__.py` gate only verifies the
wrappers against ASSUMED method `val` contracts (see memory `os-gate-does-not-verify-method-bodies`).

**Branch.** `body-gate-array-tuple-typing` (keep `main` green). Intermediate states are RED (the
fixes are connected — `__init__` breaks until the whole set lands), so the **development gate is the
CORPUS** (byte-diff justified + `bin/run-reference-tests.sh` green); the standalone-os + `__init__`
green check is the FINAL acceptance, landed atomically.

## Gap inventory (cascade, in first-seen order)

1. **Method-call-STUB ensures: `\result[i]` → `subscript_get`** (current first error, mlw line ~99).
   `val self__read_inode_1 … ensures { (subscript_get result 0) = (inode_size self.disk x0) }` — the
   STUB-ensures builder in `src/pycsl/module6_whyml/functions.py` (`_build_method_*_ensures_map`,
   the classifier gap-17/18 touched) lowers `\result[i]` to the opaque `subscript_get` instead of
   `Array.get` (`result[i]`), even though the method returns `array int`. The method-BODY path
   (`expressions.py` L0, line ~1807) already handles this; the STUB path does not. (Triggered by the
   read-side `_read_inode` `\result[0]==inode_size` ensures; module-level `_unpack_inode` avoids it
   because it is not a method.) FIX: in the stub-ensures lowering, recognize `\result[i]` on an
   `array int`-returning method as `result[i]`.

2. **Per-slot tuple return types** (mlw line ~437). `find_return_type` (`ir_scanner.py` ~696) hardcodes
   `(int, int, …)` for EVERY tuple return; `_unpack_direntry`'s `(inode, name_bytes)` is `(int, bytes)`
   → the `let` body `(int, array int)` can't type-check against `(int, int)`. FIX (prototyped, works):
   `_refine_tuple_return_type` in `functions.py` infers each slot from the first tuple-return's elts
   (`array int`/`string`/`map`/`int`). NOTE the dead auto-trust no-op (`emit_as_val` computed before
   the four auto-trust blocks) — do NOT "fix" it (it over-trusts + breaks corpus byte-diff 0651);
   per-slot typing is the right fix, not auto-trust.

3. **Tuple-unpack-target typing + downstream array usage** (mlw line ~738/437-in-__init__). Once
   `_unpack_direntry : (int, array int)`, the caller's `name_bytes := _tu_name_bytes` fails — the
   local `name_bytes` is declared `ref 0` (int) but receives `array int`. Needs cross-function slot
   propagation: a var bound to the array slot of a tuple-returning call is `array int`. Then every
   downstream use of `name_bytes` (it's `bytes`: split/decode/compare) must be array-faithful. THIS is
   why current `__init__` green-ness depends on the WRONG `(int,int)` typing being internally
   consistent — fixing it is a connected refactor across `types.py`/`statements.py`/`expressions.py`.

4. **Array-ref local passed as arg without deref** (mlw line ~961). `let inode = ref (Array.make …)
   in … (self__write_inode_2 self !inode_num inode)` passes `inode` (a `ref (array int)`) where
   `array int` is expected — missing `!`. FIX: deref array-ref locals at call-argument sites
   (`statements.py`/`expressions.py` call-arg emission).

5. **(expected) more behind 4** — each fix reveals the next; complete the inventory during impl.

## Execution order (each step: corpus byte-diff justified + run-reference-tests green)

- S1: gap-1 (stub `\result[i]`→Array.get). Most isolated; likely corpus-byte-safe (no corpus method
  stub uses `\result[i]`). 
- S2: gap-2 (per-slot tuple types) — reland `_refine_tuple_return_type`.
- S3: gap-3 (unpack-target + downstream array typing) — the big connected piece.
- S4: gap-4 (ref-deref) + whatever S3 reveals.
## Cascade progress (standalone first-error line advances as gaps clear)

- gap-1 (stub `\result[i]`→Array.get) — DONE, committed `29b77e8`, corpus byte-IDENTICAL. (line 99 cleared)
- gap-2 (per-slot tuple return types, `_refine_tuple_return_type` in functions.py) — done on branch. (437 cleared)
- gap-3 (unpack-target typing): `_collect_struct_unpack_array_targets` generalized to any
  tuple-returning call + `_split_tuple_type` (types.py); `_build_method_return_type_map` now applies
  the tuple refinement (functions.py) so `_unpack_direntry : (int, array int)` reaches the map. (742 cleared)
- gap-4 (list-literal local mis-declared as `ref`): `_first_assign_kind` now classifies
  `ArrayLit`/`ListLit` as `"array"` (value-declared), consistent with `_array_locals` — so a list
  literal passed as a whole value emits its array, not the ref. (962 cleared)
- gap-5 (NEXT, line 1479): a `\forall k` binder in a body `#@ assert` (sys_unlink/rmdir uniqueness
  assert) is wrongly deref'd as `!k`. Pre-existing standalone-body bug, unmasked now that method
  bodies are reached. Register the quantifier binder in the body-assert lowering so `k` stays a logic
  var, not a ref. (likely more gaps behind it.)

NOTE: the cascade is DEEPER than 4 gaps. gaps 2–4 are WIP (corpus/`__init__` RED until the whole block
+ gap-5+ land). The branch preserves progress toward the atomic landing.

- S5 ACCEPTANCE: standalone os verifies (0 unproven, scan incl. "Out of memory"), `__init__` stays
  green (1217, 0 non-Valid), full corpus green, byte-diff diffs all justified. Then commit atomically,
  re-establish the os BODY baseline, and redo gap-17 write-side under the now-sound body gate.

## Gate discipline (non-negotiable)
- Scan EVERY non-Valid verdict (including `Out of memory`), not a keyword subset.
- `--fun` is VACUOUS for these methods — never use it to judge body soundness; use the standalone
  whole-file run.
- Corpus byte-diff differences are EXPECTED for the affected patterns; each must be inspected and
  justified (more-correct emission) AND the corpus proof (`run-reference-tests.sh`) must stay green.
