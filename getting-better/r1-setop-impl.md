# r1-setop-impl.md — the string-keyed set-op lowering pass (item-7 R1, user-funded 18h)

Goal: make `Set[str]` lower to a STRING-keyed map (`map string (option int)`) everywhere — param,
field, local, set-ops — so `.add(str)`/`x in s`/`|`/`.copy()`/`.discard` typecheck and prove
faithfully. Fixes a real all-users faithfulness bug (currently `Set[str]` is int-keyed via
`str_hash_op`, an erasure), de-vacuifies `_emit_new_ghost_ref`, and unblocks item-2's F4.

## Banked seed (item-7 spike, PROVEN standalone — `def add_it(s: Set[str], x): s.add(x)` L3-tc ✓ + proves)
4 emitter edits: (a) `functions.py::_emit_param` set branch consults `_dict_key_types` (was hard-coded
`map int (option int)`); (b)+(c) `_build_method_param_types_map` + `_build_method_param_whyml_types_by_name`
pin `dict_key_types[arg]="string"` from a `Set[str]` annotation via `_m5_get_set_elem_type`; (d) Module5
`_build_function_symbol_table` pins it from the annotation.

## Measured cascade (item-7 boundary — each step revealed the next; this is the work)
1. **set-union `|`** (`expressions.py` L3660) `str_hash_op`-hashes the string element — needs a raw
   string-key branch, incl. the `<set>.copy()` LEFT-operand variant.
2. **`#@ requires_method` grammar** can't parse `Set[str]` (`Module2_Parser`) — falls back to `int`
   (worse). Extend the requires_method param-type grammar for `Set[str]`.
3. **membership `in` + `.add`/`.discard`** write sites all `str_hash_op`-hash — same raw-key fix.
4. **mirror inconsistent annotations** — 60 `local_refs: Set[str]` vs 15 `local_refs: int` vs 1 bare
   `set`. Reconcile to `Set[str]` where the live type is a str-name set.
5. **cross-file self-method bridges** default the callee set param to `map int` — infer string-key.
6. **de-vacuify `_emit_new_ghost_ref`**: `_seed_mutated_collection_params` (`functions.py` L4143)
   EXCLUDES methods from by-ref promotion, so `.add(target)` emits `()` → `target` erased. Lift the
   method exclusion (guardedly) so the ghost-ref add is caller-visible → removes it from KNOWN_ERASURES.

## Discipline — INCREMENTAL, byte-diff/M1-gated (this touches shared emission = corpus risk)
Each increment its own gate battery. Corpus byte-diff is the make-or-break: a `Set[str]` corpus program
that was int-keyed-and-WRONG will now emit differently — that is an **M1 SANCTIONED RESET** (§10.10) ONLY
if the diff is EXACTLY the string-key correction AND every affected program still PROVES. Any corpus
program that BREAKS (relied on the int-keyed lowering) is a STOP-and-report, not a force. Assert the
emitted population (786) on both sides (lesson k). Whole-file proofs uncapped (driver). Ledger 3.
Count MUST NOT rise; the payoff is de-vacuify (`_emit_new_ghost_ref` out of KNOWN_ERASURES) + the
faithfulness fix + any stubs a string-keyed-set census unblocks.

## Increment order (spike-gated; refutation-exit per increment)
- **I0 SPIKE (re-verify the seed):** reproduce `add_it` proving with the 4-edit seed. If it no longer
  proves, STOP — the seed regressed.
- **I1 — Set[str] type-plane (the seed, byte-inert):** param/field/local `Set[str]` → `map string
  (option int)`, gated on the `str` element type (Set[int] stays int-keyed). Byte-diff: any corpus
  Set[str] program changes are the M1 correction (verify re-proof); Set[int] unchanged.
- **I2 — set-op lowering string-key-aware:** union `|` (+`.copy()` left), membership `in`, `.add`,
  `.discard` — raw string key, retire `str_hash_op` for str-sets. Byte-diff/M1 per op.
- **I3 — requires_method grammar** for `Set[str]` (Module2_Parser). Byte-inert on corpus (no corpus
  program uses cross-mixin requires_method with a set param); fixes the mirror fallback.
- **I4 — mirror annotation reconcile** (`local_refs`/`declared_refs` → consistent `Set[str]`) +
  cross-file bridge string-key inference. Mirror-only where possible (byte-inert).
- **I5 — de-vacuify `_emit_new_ghost_ref`:** lift the method by-ref-promotion exclusion (guarded);
  confirm `.add(target)` is caller-visible, `target` referenced, remove from KNOWN_ERASURES.
- **I6 — census:** any other `\trusted` stubs now convertible via string-keyed sets? Convert (count DOWN).

Refutation exit at any increment that cascades unboundably or breaks a corpus program unfixably →
record the exact blocker + how far it got, revert THAT increment clean, keep the landed ones.
