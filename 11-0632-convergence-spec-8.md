STATUS: DONE

<!-- COORDINATION APPROVAL (editorial):
- Part 1 (propagate the dependency's `inductive_decls` into the importer's ir_data in ir_resolve.py,
  de-dup by name + scoped to referenced names, mirroring module_constants): APPROVED — this is the real
  fix; Part 1 must always WIN over Part 2 (carry the real decl, never the type-only reconstruction).
- Part 2 (emit an unknown CONTRACT-position symbol as a logic predicate/function typed from the symbol
  table, not a program `val`): APPROVED as the safety net, but NARROW — fire ONLY in formula/contract
  position (hang off the existing contract-context flag), NEVER for body-position unannotated calls
  (risk 3). It needs its OWN targeted test (an imported contract referencing an *undeclared* predicate).
- MANDATORY (risk 1): the byte-diff proves only NON-perturbation (no corpus file is inductive AND
  import-crossing), so it CANNOT regress-test the new path. Add a CORPUS REFERENCE TEST under
  test-suite/corpus/pycsl-reference/ — a two-file inductive-import driver (a module exporting a function
  whose `ensures` references an `#@ inductive` predicate, + a driver importing it) — that type-checks AND
  proves. Without it a future refactor could silently break predicate-crossing with a green byte-diff.
Acceptance bar: the new corpus inductive-import driver type-checks + PROVES; the /tmp repro proves; Part 2
targeted test proves; full-corpus byte-diff (bin/byte-diff-sweep.sh) IDENTICAL; conformance 38/38; os
byte-identical; doc green. On success set STATUS: DONE. -->

# Convergence spec — iteration 8 (carry a contract-referenced LOGIC symbol across the `from pure_lib.os import …` boundary)

**Loop:** `config/skills/pycsl-stdlib-coverage`.
**Input gap:** `11-0632-convergence-gap-8.md` (N = 8). **Stamp:** `11-0632`, iteration `N = 8`.
**Phase:** SPEC. No `src/pycsl/` edits in this phase; implementation follows after STATUS: APPROVED.

---

## Gap recap (confirmed empirically)

The gap-7 fix is a SHARED "name present" logic view that mutators establish (`mkdir(d) ⇒ present(d)`)
and observers reflect (`access(d) == 1 <==> present(d)`), expressed as a module-level `#@ inductive`
predicate. It is **correct inside the defining module** but **dropped across the
`from pure_lib.os import mkdir, access` boundary** that the formal test crosses. The importer then
substitutes a PROGRAM `val present_1 (x0:int):int`, which is (1) illegal in `ensures`/logic position and
(2) mistyped `int` vs the `string` argument — so the importing test fails the L3 type-check before any
prover runs.

**Reproduced** (two files under `/tmp/indprobe/`, the exact gap-doc shape):

- Standalone `osmod.mlw` — CORRECT (logic symbol):
  ```
  inductive present string =
    | Present_intro : (forall n : string. ((present n) -> (present n)))
  ...
  ensures  { ((result = 1) <-> (present filepath)) }
  ```
- Importer `test_os.mlw` — BROKEN:
  ```
  val present_1 (x0: int) : int                         (* program val, int arg, _1 suffix *)
  ...
  ensures  { ((result = 1) <-> (present_1 filepath)) }  (* present_1 in logic position *)
  ```
- `pycsl /tmp/indprobe/test_os.py --no-proof` → `L3-tc ✗` ("This term has type unit…"; the `present_1`
  unbound-symbol error follows). Confirms the test cannot type-check once the os public contracts carry
  the predicate.

### The two pinned sites

**LOSS SITE — `src/pycsl/frontend/ir_resolve.py`** (the importer drops the logic decl).
The Module6 transpiler builds `self._inductive_preds` and emits the `inductive …` block solely from
`self.ir.get("inductive_decls", [])` (`src/pycsl/Module6_WhyMLTranspiler.py:389-393` and again
`:417-420`; emitter `src/pycsl/module6_whyml/preamble.py:766` `_emit_inductive_decls`). The IR field
`inductive_decls` is produced by `src/pycsl/frontend/Module5_IREmitter.py:206`. But `resolve_imports`
(`ir_resolve.py:647`) and its direct-import helper (`_resolve_direct_imports`, `ir_resolve.py:207`,
specifically the injection at `:236` and the constants-propagation at `:242-252`) propagate ONLY
`ir_data["functions"]` and `ir_data["module_constants"]` from the dependency. The dependency's
`inductive_decls` is **never copied** into the importing `ir_data`. Consequence: in the importer's
transpile, `self.ir.get("inductive_decls", [])` is empty → `self._inductive_preds` does NOT contain
`present` → the contract's `present(filepath)` is not recognised as a predicate application.

**WRONG-EMISSION SITE — `src/pycsl/module6_whyml/expressions.py:1079-1098`** (the program-`val`
fallback). With `present` absent from `_inductive_preds`, the bare-`Call` lowering
(`expressions.py:1036`) skips the inductive arm at `:1053` (`if func_name in self._inductive_preds`) and
falls through to the generic unannotated-callee fallback at `:1079-1098`:
```
arity_fn = f"{safe_fn}_{n}"                              # :1087 → present_1
self._add_abstract_op(
    f"val {arity_fn} {' '.join(f'(x{i}: int)' for i in range(n))} : int")   # :1091-1092 → program val, int args
```
This is exactly the two compounded faults: a program `val` (illegal in `ensures`) with `int` args
(mistyped against `string`) and the `_1` arity suffix. (The dotted-call sibling at `:799-894`
— `param_types.append("int")` `:831`, `val {arity_name} … : {ret_type}` `:893` — has the same shape and
the same fix for dotted predicate references, but the reproducer takes the bare-Call arm.)

This is **not** model-fixable (the defining module is already correct; the fault is purely in how the
importer lowers a contract symbol it did not receive a logic decl for) and **not** an SMT/Rocq+Lean wall
(the file never reaches the prover; it fails L3 type-check first).

---

## Part 1 — propagate the logic decl across the import boundary

**File:** `src/pycsl/frontend/ir_resolve.py`.

When the importer injects an imported function stub whose contract references a module-level logic
predicate, it must also inject the dependency's `#@ inductive` (and any module-level logic
`predicate`/`function`) declarations into the importing `ir_data`, so the SAME emission path that proves
the module standalone fires in the importer.

**How os emits its OWN logic decls today (the path to reuse):** Module5 records each `#@ inductive` in
`ir_data["inductive_decls"]` (`Module5_IREmitter.py:206`); Module6 reads `self.ir.get("inductive_decls",
[])` to (a) register predicate names in `self._inductive_preds`
(`Module6_WhyMLTranspiler.py:389-393`, `:417-420`) and (b) emit the `inductive …` block via
`preamble.py:_emit_inductive_decls` (`:766`). **Reuse this verbatim** — the only thing missing in the
importer is that `ir_data["inductive_decls"]` is empty because nobody copied the dep's.

**Change (mirrors the `module_constants` propagation at `ir_resolve.py:242-252`):** in
`_resolve_direct_imports` (and, for symmetry, the wildcard/module helpers), after `_inject_functions`,
read the resolved dependency's `inductive_decls` from the cache and merge them into the importer's IR by
name (skip names the importer already declares, to avoid duplicate Why3 decls):

```python
dep_ind = (cache.get(os.path.abspath(resolved), {}) or {}).get("inductive_decls", [])
if dep_ind:
    tgt = ir_data.setdefault("inductive_decls", [])
    have = {d["name"] for d in tgt}
    for d in dep_ind:
        if d["name"] not in have:
            tgt.append(copy.deepcopy(d))      # copy.deepcopy already imported at ir_resolve.py:24
            have.add(d["name"])
```

After Part 1, the importer's `self._inductive_preds` contains `present`, so `expressions.py:1053`
fires and lowers `present(filepath)` to `(present filepath)`; `_emit_inductive_decls` emits the real
`inductive present string = …` into the test's preamble. The `present_1`-fallback is never reached.

**Scope note (do not over-propagate):** propagate ONLY decls whose predicate name is actually referenced
by an injected stub's contract (or, simplest and equally byte-additive, only when the importing module
actually injects function stubs from that dependency). os's standalone preamble has many logic decls; the
importer needs only those the injected public contracts mention. Restricting to referenced names keeps
the importer's preamble minimal and avoids dragging unrelated internal predicates across the public
boundary.

---

## Part 2 — type an unknown contract symbol as a logic predicate (defensive fallback)

**File:** `src/pycsl/module6_whyml/expressions.py:1079-1098` (and the dotted sibling `:799-894`).

Part 1 fixes the reproducer. Part 2 hardens the case where the decl is genuinely absent (e.g. an
imported contract references a predicate the dependency forgot to declare, or a future shape Part 1 does
not yet cover): a contract symbol the emitter does not recognise must be emitted as a logic
`predicate`/`function`, NOT a program `val`, and its arg types must come from the enclosing stub's
symbol table.

**Recognise "logic position".** The bare-`Call` lowering must distinguish a call appearing inside a
contract formula (`ensures`/`requires`/inductive rule) from a call in program-body position. The
contract lowering already flows through `_coerce_to_bool` / the contract emitter, which knows it is in a
formula (it special-cases `_inductive_preds`, `Exists`/`Forall`/`Compare` at `expressions.py:64-66`). The
fallback at `:1079-1098` should, when invoked from contract context, emit a logic decl instead of a
program `val`:
```
# logic, not program; arg types from the symbol table, not int
predicate {name} {argtypes}
# or, for a non-bool result:
function {name} {argtypes} : {ret}
```

**Recover arg types from the enclosing stub's symbol table.** `_current_symbol_table` and
`_formal_params` are already attributes on the emitter (used at `expressions.py:271,341,380,609,862`).
The symbol table maps a param name to its Python type (`"str"`, `"float"`, `"list"`, …); map it to the
WhyML type the rest of the emitter uses (`"str"`→`string`, `"float"`→`real`, list/tuple/bytes→`array
int`, default `int`). So `present(filepath)` with `filepath: str` in the stub's symbol table types as
`predicate present string`, not `val present_1 (int):int`. (For an imported stub, the stub IR carries its
own `symbol_table`; the recovered type must use the IMPORTED stub's declared param types, not the
caller's.)

**De-dup.** Use the existing abstract-op de-dup machinery (`_add_abstract_op` / `_axiom_emitted_decls`)
so the same predicate referenced by both `mkdir` and `access` emits exactly once.

Part 2 is the safety net; Part 1 is the real fix. Both must land together so that whether the decl
crosses (Part 1) or is reconstructed (Part 2), the symbol is a correctly-typed LOGIC symbol.

---

## Scope check — is this the right fix, or is there a simpler one?

**Assessed: the tool fix is necessary; there is no sound model workaround.**

- The os namespace test imports only the public functions (`mkdir`/`access`/…), as a caller must, and
  goes through the module-level `_filesystem` global, which the pure-`val` boundary drops. The two `val`s
  therefore share no state; the ONLY thing that can tie "a name a mutator wrote" to "what an observer
  reads" is a shared LOGIC symbol both contracts reference — exactly the gap-7 `present` view.
- Expressing the consequence "via a public observer the test already calls" does not avoid the shared
  symbol: the consequence IS the agreement between two different syscalls (`mkdir` and `access`), so it
  inherently needs a common predicate in both contracts. There is no single observer whose own return
  code expresses it without becoming vacuous.
- The instance-method route (a `formal_os_io.py`-shaped driver that constructs `UnixInodeFileSystem()`
  locally and calls `sys_*` methods carrying `self` + `writes self.disk`) is a real alternative for a
  DIFFERENT test, but it changes what is being verified (local construction, not the public module API).
  The loop rule for the namespace test is that it drives the public API; so the predicate-crossing tool
  fix is required for THAT test.

---

## Two-file repro for the gate

`/tmp/indprobe/osmod.py` + `/tmp/indprobe/test_os.py` (the exact gap-doc shape, already created and
confirmed to reproduce the bug). Acceptance after the fix:

1. `pycsl /tmp/indprobe/test_os.py --keep-mlw --no-typecheck --no-proof` → `test_os.mlw` contains
   `inductive present string = …` and `(present filepath)` (NOT `val present_1 … : int`,
   NOT `(present_1 filepath)`).
2. `pycsl /tmp/indprobe/test_os.py --no-proof` → `L3 ✓` (type-checks; the `present` symbol is bound and
   `string`-typed). (Note: the reproducer's imported stubs also surface an unrelated `: unit` return-type
   quirk from the `...` ellipsis body; the gate is specifically that `present` becomes a correctly-typed
   logic symbol — give the stubs concrete `int` bodies or explicit return annotations if needed to
   isolate the predicate check.)
3. With full provers, `mkdir_then_access_present` proves Valid (the consequence reduces to the shared
   `present` law the two contracts now share).

**Corpus reference test (required by the reference-corpus rule):** add a two-file inductive-import driver
under `test-suite/corpus/pycsl-reference/` (a module exporting a function whose `ensures` references an
`#@ inductive` predicate, imported by a driver) so this path gains permanent byte-diff coverage — see
RISKS for why the current corpus does NOT cover it.

---

## Gate (byte-ADDITIVE)

1. **Full-corpus byte-diff IDENTICAL** via `bin/byte-diff-sweep.sh` (the sweep emits every
   `test-suite/corpus/pycsl-reference/0*.py` with `--no-proof --no-typecheck --keep-mlw` and diffs).
   The change only fires when an imported contract references an `#@ inductive`/logic symbol, and NO
   current corpus file is both an importer AND inductive (confirmed below) → emission is unchanged for
   every existing file.
2. **Conformance 38/38.**
3. **os re-proves byte-identical** (1804/1804 Valid VCs; os standalone emission is unchanged because Part
   1 only adds an importer-side propagation and Part 2 only fires on an unknown contract symbol, which os
   standalone never hits).
4. **doc-coherency green.**
5. **Two-file repro** type-checks + proves (above).

---

## RISKS (lead: byte-additivity + importer-perturbation)

1. **Is this byte-additive and localizable? — YES, with one coverage caveat.**
   - Part 1 adds an importer-side copy of `inductive_decls` that fires only when the dependency HAS
     inductive decls AND the importer injects its stubs. Part 2's logic-vs-program branch fires only when
     a contract references an UNKNOWN symbol in formula position. Neither condition is met by any current
     corpus file.
   - **Confirmed empirically:** `grep -rln "#@ inductive" test-suite/corpus/` returns inductive files
     (0562, 0572, 0574, 0575, 0581, 0582, …) and there ARE import-crossing drivers in the swept
     `pycsl-reference/0*.py` set (0504 `from collections import Counter`, 0516 `from functools import
     lru_cache`, etc.), but the intersection — a driver that is BOTH inductive AND import-crossing — is
     **empty**. So the new branches never fire on the existing corpus → byte-diff is identical.
   - **Coverage caveat (the real risk to flag):** *because* the intersection is empty, the byte-diff
     sweep does NOT exercise the new path — it only proves the change does not perturb existing importers
     (which it covers well: many `0*.py` importers run `resolve_imports`). The new behavior's only
     positive coverage is the /tmp two-file repro. **Mitigation:** the corpus reference test above must be
     added so the path is permanently swept; otherwise a future refactor could silently break
     predicate-crossing with a green byte-diff.

2. **Does propagating logic decls across imports risk perturbing existing multi-file drivers? — Low,
   if scoped.** The propagation is keyed on `inductive_decls` being present in the dependency; today's
   imported deps (`collections`, `functools`, stdlib stubs, local record/class imports) carry none, so
   `ir_data["inductive_decls"]` stays empty for them and `_inductive_preds`/`_emit_inductive_decls` are
   unchanged. The one way to perturb a working importer would be to propagate a dep's INTERNAL predicate
   that the importer does not reference and that collides with an importer-local name — avoided by the
   name-de-dup (`if d["name"] not in have`) and the "only referenced names" scoping in Part 1.

3. **Part 2 logic-vs-program context detection.** The fallback at `expressions.py:1079-1098` is shared
   between body-position calls (where a program `val` is correct) and contract-position calls (where a
   logic predicate is required). The change must fire ONLY in contract/formula context — a too-broad
   trigger would flip body-position unannotated calls from program `val` to logic `predicate` and break
   them. The contract emitter already tracks formula context (it special-cases `_inductive_preds` and the
   quantifier/compare nodes at `:64-66`); Part 2 must hang off that same context flag, not off the bare
   `_handle_*_call` entry. This is the subtlest part of the change and warrants its own targeted test
   (an imported contract referencing an *undeclared* predicate, to exercise Part 2 without Part 1).

4. **Faithfulness.** Reconstructing an undeclared predicate (Part 2) infers only its argument TYPES, not
   its meaning — it stays an abstract logic symbol with no axioms (sound: it constrains nothing it
   shouldn't). Part 1 is the faithful path (carries the dep's actual `inductive`/rules). Part 2 must
   never be preferred when Part 1 can supply the real decl; order the lowering so a propagated decl
   always wins.

---

## Report summary

- **Loss site:** `src/pycsl/frontend/ir_resolve.py` — `resolve_imports`/`_resolve_direct_imports`
  (`:207`, inject `:236`, constants-propagation model `:242-252`) never copy the dependency's
  `inductive_decls` (produced at `Module5_IREmitter.py:206`, consumed at
  `Module6_WhyMLTranspiler.py:389-393`/`:417-420` and `preamble.py:766`).
- **Wrong-emission site:** `src/pycsl/module6_whyml/expressions.py:1079-1098` — generic unannotated-callee
  fallback emits `val {name}_{n} (x0:int):int` (program val, int arg, `_1` suffix); dotted sibling
  `:799-894` has the same shape.
- **Two-part fix:** Part 1 — propagate `inductive_decls` across the import (reuse the `module_constants`
  pattern). Part 2 — when a contract references an unknown symbol in formula position, emit a logic
  `predicate`/`function` typed from the enclosing stub's symbol table (`_current_symbol_table` /
  `_formal_params`), not a program `val`.
- **Byte-additive / localizable:** yes — confirmed no corpus file is both inductive and import-crossing,
  so the corpus byte-diff is identical; both new branches are guard-gated on conditions the corpus never
  meets.
- **Lead risk:** the byte-diff sweep proves only NON-perturbation, NOT correctness of the new path (zero
  inductive+import corpus coverage) — a corpus reference test MUST be added; and Part 2's
  logic-vs-program context detection is the subtle spot.
