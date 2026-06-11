STATUS: DONE

<!-- IMPL VERIFICATION (11-1039, tool-agent — supersedes the prior over-claim):
The prior dispatch set DONE on a HAND-EDITED mlw (`why3 -a split_vc`), NOT the real
pipeline; the standard command still FAILED L3-tc (`unbound … '_filesystem'`).

REAL ROOT CAUSE of the os-case miss (NOT a multi-hop module_globals miss — the
propagation block fired and `_filesystem` WAS in the importer's module_globals):
the global's RECORD TYPE could not be located. `os/__init__.py` does
`_filesystem = UnixInodeFileSystem()` but only IMPORTS the `UnixInodeFileSystem`
record (`from .UnixInodeFileSystem import …`). With the standard `--deep`-off
pipeline, the os PACKAGE's OWN imports are not transitively resolved
(`_process_dependency(..., deep=False)`), so `UnixInodeFileSystem` is ABSENT from
the package IR's `type_decls` (it holds only `DirEntry`). The propagation block's
`rec_name in dep_types` guard (ir_resolve.py) therefore failed, the type was never
propagated, Module6 fell back to `get_disk _filesystem` (opaque, unbound).

FIX (src/pycsl/frontend/ir_resolve.py): new `_find_record_type_from_dep_imports`
helper — when a propagated global's record type is NOT in the dependency's own
`type_decls`, follow the dependency's OWN `imports` ONE hop to the module that
DEFINES the record (`os/__init__` → `UnixInodeFileSystem.py`), process it, and pull
its `type_decl`. Wired as a fallback in the spec-10 propagation block. Fail-loud if
not found (unbound type, never silently unsound).

VERIFIED via the EXACT standard command (NOT hand-edited mlw):
  .venv/bin/python3 src/pycsl/pycsl.py pure_lib_test/formal_os_namespace.py
  → L3-tc ✓. Emitted mlw has `type unixinodefilesystem = {…}`,
    `let _filesystem : unixinodefilesystem = {…}`, and `_filesystem.disk` record
    projection (NO get_disk).
  → mkdir_then_access_present'vc Postcondition: VALID (1236 then 1800 steps).
  → file_present_after_mkdir'vc Postcondition: VALID (1212 then 1772 steps).
  The 5 remaining Timeouts are EXACTLY the documented follow-on functions
  (rmdir/unlink/link/rename + their two-name absence/presence), whose dual ensures
  are NOT yet in the os model (spec §2.3, gap-9 beachhead boundary) — out of scope.

RE-GATE: full-corpus byte-diff IDENTICAL (bin/byte-diff-sweep.sh before/after, 595
files, diff exit 0); os module emission byte-identical (importer-side fix only) +
type-checks (proof status unchanged → green); conformance 38/38; doc-coherency green.

DONE is honest: the STANDARD pipeline proves mkdir→present + file_present_after_mkdir
through the public API; only the documented rmdir/unlink/link/rename follow-on remains.
-->

<!-- COORDINATION APPROVAL (editorial):
- OPTION B APPROVED (propagate the dependency's `module_globals` as a `let`-bound record + retain its
  record type, in ir_resolve.py mirroring the module_constants/inductive_decls blocks; no Module6 change).
  It is the ONLY type-checking form (Option A's pure logic accessor is rejected — the disk is a mutable
  `array int`), it is VALIDATED (the /tmp repro proves the consequence Valid, 13 steps), and soundness is
  faithful-by-construction: no new symbol — the importer's `_filesystem.disk` is the verbatim-copied
  record's field projection, reasoned about identically to the dependency; the consequence threads only
  through the wrapper ensures + gap-9's already-approved axiom binding. No new TCB.
- MANDATORY verify-at-impl (risk 2): the global's record TYPE must survive the importer's type-decl pruning
  — the two-file repro must emit `type store` (or equivalent) after the fix. Fail mode is fail-loud
  (unbound type), acceptable.
- MANDATORY (risk 3): extend the contract-referenced-name collection to include `Attribute.object`/`Var`
  names (not just `Call` names), so ONLY contract-referenced globals cross (keeps it tight + byte-additive).
- THE PROOF IT WORKED: `formal_os_namespace.py`'s mkdir→access-present must flip Unknown→VALID THROUGH THE
  PUBLIC API (the spec-9 mkdir/access ensures are already in the os model — gap-10's fix alone should flip
  the beachhead; rmdir/unlink/link/rename ensures are the follow-on stdlib turn).
Acceptance bar: the two-file repro proves; formal_os_namespace mkdir→present flips Unknown→VALID through the
API; full-corpus byte-diff IDENTICAL (bin/byte-diff-sweep.sh); os byte-identical/green; conformance 38/38;
doc green. On success set STATUS: DONE. -->

# Convergence spec — iteration 10 (cross-import propagation of a module-global record so its field projection types in an imported wrapper's logic `ensures`)

**Loop:** `config/skills/pycsl-stdlib-coverage` — Step 5 (tool fix unblocking a model consequence).
**Input:** `11-1039-convergence-gap-10.md` (symptom + minimal repro + root cause).
**Iteration:** N = 10.
**Phase:** SPEC ONLY. No `src/pycsl/` edit, no model re-application. Implementation follows after coordination sets STATUS: APPROVED.

This spec answers: **does giving the importer a logic-usable view of a dependency's module-global let the os-namespace consequence prove through the public API — and is the change byte-additive and sound?** Answer: **YES** — a `let`-bound record propagation (the only form Why3 accepts; a standalone pure accessor is rejected because the disk is a mutable array) makes `formal_os_namespace.py`'s mkdir→present flip Unknown→VALID, fires only for contracts referencing a propagated global (no corpus driver does), and is faithful by construction (the importer's `_filesystem.disk` is the *same* record-field projection the dependency uses).

---

## 1. The gap (one line)

An imported public wrapper's `#@ ensures` that references a dependency's module-global field — `dir_lookup(_filesystem.disk, 5, filepath) >= 0` — does not type-check in the importer: the importer never receives the dependency's `module_globals`, so `_filesystem` lowers to `val constant _filesystem : int` and `_filesystem.disk` to a PROGRAM val `(get_disk _filesystem)`, illegal in a logic `ensures`. (Full root cause + file:line in gap-10 §3.)

---

## 2. The fix (file:line)

### 2.1 The decisive measurement — only the `let`-bound record form type-checks

Three hand-fixed driver `.mlw` files were run through `why3 prove -P alt-ergo` (1.8.2):

| Candidate | Form | Result |
|-----------|------|--------|
| `/tmp/mgrepro/fixed.mlw` | `val function _filesystem_disk : array int` (standalone pure accessor — dispatch's option A) | **REJECTED** — `line 7: This value is mutable, it cannot be used as pure` |
| `/tmp/mgrepro/fixed2.mlw` | `val constant _filesystem : store` (`store` has `mutable disk`) | **REJECTED** — `line 8: This value is mutable, it cannot be used as pure` |
| `/tmp/mgrepro/fixed3.mlw` | `type store = { mutable disk: array int }` + `let _filesystem : store = { disk = (Array.make 8 0) }` + record-field projection (option B) | **VALID** — `_filesystem'vc` Valid (6 steps); `mkdir_then_access_present'vc` Valid (13 steps) |

The disk view is an inherently mutable `array int`; a *pure* accessor for it cannot be well-typed. Only the concrete `let`-bound record — exactly the in-module form (`preamble.py:1102-1123`) — works, and it proves the end-to-end consequence.

### 2.2 The change — propagate the dependency's `module_globals` into the importer

In `src/pycsl/frontend/ir_resolve.py`, `_resolve_direct_imports` (lines 284-353), ADD a propagation block mirroring the existing `module_constants` (lines 319-324) and `inductive_decls` (lines 337-348) blocks:

* Read `dep_globals = cache[abspath(resolved)].get("module_globals", [])`.
* Scope: copy only those whose name is referenced by an INJECTED stub's contract — reuse `_contract_referenced_names(dep_funcs)` (lines 246-267) the inductive block already uses, walking the `Var`/`Attribute` `object` names (extend that walker, or add a sibling, to collect `obj.name` of `Attribute` nodes), so only `_filesystem` crosses, not unrelated globals.
* Append de-duped (by `name`) into `ir_data.setdefault("module_globals", [])`.

Then ensure the global's record type SURVIVES type-decl pruning in the importer: the `UnixInodeFileSystem` record is imported transitively (`_resolve_imported_classes`, lines 416+) but is pruned when otherwise unreferenced; the propagated global re-references it, so either (a) propagate the global BEFORE pruning so the prune-walk sees the reference, or (b) explicitly retain any record type named by a propagated global's `class`. Verify against the actual prune site at implementation time (the importer mlw currently emits no `type unixinodefilesystem` — that must reverse).

No Module6 change is required: with `ir["module_globals"]` populated, `Module6_WhyMLTranspiler.py:71-72` fills `_module_global_classes`, `preamble.py:_emit_module_globals` (1102-1123) emits `let _filesystem : unixinodefilesystem = <literal>`, and the contract reference resolves through the EXISTING working in-module branches `expressions.py:1929-1934` (attribute → `_filesystem.disk`) and `1976-1977` (var → `_filesystem`) instead of the opaque fallbacks at `1941-1943` / `1989-1991`.

### 2.3 How the wrappers then carry the consequence

The wrapper ensures are ALREADY in `pure_lib/os/__init__.py` (added when gap-9 landed):
* `access` (lines 115-118): `(\result == 1) <==> (dir_lookup(_filesystem.disk, 5, filepath) >= 0)`.
* `mkdir`: `\result == 0 ==> dir_lookup(_filesystem.disk, 5, filepath) >= 0`.

With the propagation, both reference the importer's `let`-bound `_filesystem.disk` (the same symbol), so `mkdir_then_access_present`'s `mkdir(d); access(d)` threads the presence view from mkdir's ensures into access's iff and discharges `\result == 1` — the §2.1 `fixed3.mlw` proof at full scale. The follow-on MODEL turn is only extending the dual ensures to rmdir/unlink/link/rename (out of scope; gap-9 beachhead boundary).

---

## 3. The two-file repro (for the gate)

`/tmp/mgrepro/lib_mg.py` (dependency with a module-global object + a wrapper whose `#@ ensures` references the global's field) and `/tmp/mgrepro/drv_mg.py` (importer). Full source in gap-10 §2.

* BEFORE fix: `pycsl --no-proof drv_mg.py` → `L3-tc ✗`, `unbound function or predicate symbol 'get_disk'`.
* AFTER fix (expected): `pycsl --no-proof drv_mg.py` → `L3-tc ✓`, emitting `type store`, `let _store : store = { disk = 0 }`, `ensures { result = _store.disk }` in the importer — byte-identical to how `lib_mg.py` itself already emits the contract.

This minimal repro is the acceptance probe; it proves the fix without os/axiom machinery.

---

## 4. The gate (implementation must pass ALL before APPROVED→landed)

1. **Two-file repro flips:** `drv_mg.py` goes `L3-tc ✗ → ✓` (§3).
2. **API flip (the fixed point):** `pure_lib_test/formal_os_namespace.py` `mkdir_then_access_present` / `file_present_after_mkdir` flip **Unknown → VALID through the public API** (the dispatch's "proof the binding is real").
3. **os re-proves GREEN:** `pure_lib/os/__init__.py` + `UnixInodeFileSystem.py` re-prove at their current green (1807/0); the os module's OWN emission is unchanged (it already had `module_globals` — the fix is importer-side only).
4. **byte-additive:** `bin/byte-diff-sweep.sh` IDENTICAL. The propagation fires only when an IMPORTED stub's contract references a dependency module-global. NO corpus driver does: corpus module-global users (0576-0578 Account, 0595 Disk, 0602 Match, 0650 Lib, 0583 Reader) are all INTRA-module (a module that defines the global also uses it — that path is unchanged); none IMPORTS a wrapper whose contract names another module's global. Confirm with the sweep + `--no-typecheck`.
5. **conformance:** 38/38 `*.expected.mlw` unchanged; reference suite green.
6. **doc-coherency:** no new `#@` directive (`bin/doc-coherency.py --check` unaffected).

---

## 5. RISKS — led by byte-additivity + the soundness of the logic view

### 5.1 [BYTE-ADDITIVE — lead] The change is localizable and additive

The propagation block is gated on "a propagated global is referenced by an injected stub's contract." That condition is FALSE for every existing file:
* The os module ITSELF defines `_filesystem` and already has it in `module_globals` — the importer-side propagation never touches it (the global is local, not imported).
* Every corpus module-global user (§4) is intra-module; none imports a cross-module wrapper whose contract references the dependency's global.
* All non-os imports inject stubs whose contracts reference only params/results/registered logic symbols, never a dependency global.

So `_module_global_classes`/`type_decls`/`module_globals` of every existing importer are unchanged → emission byte-identical → `bin/byte-diff-sweep.sh` IDENTICAL. The TWO-FILE repro (`drv_mg.py`) and `formal_os_namespace.py` are the only files whose emission changes — both EXPECTED (the gap they close). This is a genuine byte-additive tool enabler, not a perturbation of existing module-global emission.

### 5.2 [SOUNDNESS — the logic view must not diverge] Faithful by construction

The risk in any "logic view of a program global" is that the logic symbol diverges from the program global's real state (proving a vacuous postcondition). Here it CANNOT, because the fix introduces NO new symbol: the importer's `_filesystem.disk` is the literal WhyML record-field accessor of a `let`-bound record whose type and literal are COPIED verbatim from the dependency's IR (the same `_emit_module_globals` lowering, `preamble.py:1102-1123`). The importer reasons about `_filesystem.disk` exactly as the dependency does. The wrapper stubs are trusted-`val` contracts (their relating bodies are dropped at the import boundary, as today); the consequence threads purely through the two wrappers' ensures sharing the one `_filesystem.disk` term — which is sound iff the wrapper ensures are sound, and THOSE are gap-9's already-approved cross-validated axiom binding, not introduced here.

### 5.3 [MODELLING — verify at impl] Record-type retention against pruning

The one non-mechanical step: the global's record type must survive the importer's type-decl pruning (the driver mlw currently emits no `type unixinodefilesystem`). The fix must either propagate the global before the prune-walk or explicitly retain a record named by a propagated global's `class`. If missed, emission fails with an unbound type rather than silently unsound — a fail-loud, easily-caught mode. Verify the two-file repro emits `type store` after the fix (§3).

### 5.4 [LOW] No inlining cascade

The spec-9 "cascades into method-inlining of the imported wrappers" warning does NOT materialize: the driver bodies have no `_filesystem.method()` receivers (they call public wrappers), and the wrappers are body-less `val` stubs. `apply_inline_globals` (`ir_inline.py:375`) and the Phase-3 no-alias check (`333-353`) are both no-ops on the driver. Measured in gap-10 §6.

### 5.5 [LOW] Scope of `_contract_referenced_names` extension

The existing `_contract_referenced_names` (ir_resolve.py:246-267) collects `Call` func names; the global is referenced as an `Attribute`/`Var`, so the scoping walk must be extended (or a sibling added) to collect `Var.name` / `Attribute.object` names. Minor, surfaced so the impl scopes the propagation tightly (only contract-referenced globals cross) and does not over-propagate every dependency global.

---

## Appendix — validation artifacts (throwaway, /tmp)

* `/tmp/mgrepro/lib_mg.py`, `/tmp/mgrepro/drv_mg.py` — the minimal two-file repro (lib `L3-tc ✓`; driver `L3-tc ✗` `get_disk` unbound).
* `/tmp/mgrepro/fixed.mlw`, `/tmp/mgrepro/fixed2.mlw` — the REJECTED pure-accessor candidates (`mutable … cannot be used as pure`).
* `/tmp/mgrepro/fixed3.mlw` — the VALID `let`-bound-record fix (why3 1.8.2: `mkdir_then_access_present'vc` Valid, 13 steps) — the end-to-end API-flip proof in miniature.

These are throwaway. The impl phase changes only `src/pycsl/frontend/ir_resolve.py` (the propagation block); no model edit is needed for the os flip (the wrapper ensures already exist).
