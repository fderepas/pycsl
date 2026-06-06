# Broad cross-file inheritance — executable feature plan (ER supervisor form)

Executable form of `broad-cross-file-feature.md`, structured for
`bin/agent-feature-supervisor --feature-file broad-cross-file-feature-exec.md`.

Adds real class inheritance to PyCSL in four layers — (A) cross-module class
resolution, (B) field/method merging, (C) invariant inheritance, (D) behavioral-subtyping
proof obligations — reusing existing plumbing (`pycsl.py` import resolver, Why3 type
invariants, `_rewrite_ir_calls`). Full design rationale, edit-site citations, and
risk/fallback analysis live in `broad-cross-file-feature.md`.

> **Supervisor note (expected, not a defect).** The core-pipeline files this feature
> edits — `Module5_IREmitter.py`, `module6_whyml/preamble.py`, `module6_whyml/functions.py`,
> `Module4_SemanticAnalyzer.py` — are on the supervisor's **load-bearing deny-list**
> (`config/skills/agent-stdlib-annotate/references/load-bearing-files.md`). The supervisor
> is gate-only: it parses this plan, evaluates each phase's read-only `**Acceptance:**`
> claims, then **halts `human-needed` (exit 75)** rather than auto-editing those files. A
> human (or a delegated coding session) makes the edits; the Acceptance blocks below are
> the machine-checkable definition of done that the supervisor re-runs to confirm each
> phase actually shipped. `pycsl.py` itself is NOT load-bearing, so Layer-A work there does
> not trip the deny-list.

## Context

`visit_ClassDef`/`_collect_class_fields` ignore `node.bases`, so a subclass emits an empty
record and inherits nothing. The workaround (self-contained class re-declaring all fields +
copying every helper body) forks the proof and cannot express "the os layer is a refined
filesystem." This plan removes the blocker so e.g. `class MyOS(UnixInodeFileSystem)` works
with zero duplication and inherited invariants. Each phase is independently
`pycsl.py`-verifiable and adds a corpus test under `test-suite/corpus/pycsl-reference/`.

## Implementation surface

### Phase 0 — Class-level constants in the class IR

**Status:** DONE

Collect class-body integer constants (`O_CREAT = 64`, `BLOCK_SIZE = 512`) into the
`type_decls` record so subclasses can inherit them and contracts can reference them as
literals instead of opaque attribute reads. Edit `src/pycsl/Module5_IREmitter.py`
(`visit_ClassDef`, `_collect_class_fields`): walk class-body `Assign`/`AnnAssign` with
`Name` targets and constant int RHS into `type_decls[i]["constants"]`. Add corpus test
`test-suite/corpus/pycsl-reference/0440.py`: a class that uses its own class constant
inside a `#@` contract and verifies.

**Acceptance:**
- `test -f test-suite/corpus/pycsl-reference/0440.py` exits 0
- `.venv/bin/python3 src/pycsl/pycsl.py test-suite/corpus/pycsl-reference/0440.py` exits 0

### Phase 1 — Layer A: cross-module class resolution

**Status:** DONE

Extend the existing import resolver to carry imported **classes** (record + `<class>__*`
methods + invariants + constants), not just functions. Edit `src/pycsl/pycsl.py`: add
`_resolve_imported_classes` reusing `_process_dependency`, `_resolve_module_path`, and
`_rewrite_ir_calls`; surface the dependency's `type_decls` into an `imported_classes`
registry on the main IR. Add a base module
`test-suite/corpus/pycsl-reference/multi_file_lib/base_counter.py` and an importer
`test-suite/corpus/pycsl-reference/0441.py` that instantiates and calls a method of the
imported class.

**Acceptance:**
- `test -f test-suite/corpus/pycsl-reference/0441.py` exits 0
- `test -f test-suite/corpus/pycsl-reference/multi_file_lib/base_counter.py` exits 0
- `.venv/bin/python3 src/pycsl/pycsl.py test-suite/corpus/pycsl-reference/0441.py` exits 0

### Phase 2 — Layer B + C: same-file inheritance (fields, methods, invariants)

**Status:** DONE

Make `visit_ClassDef` read `node.bases` and, for a same-file base, merge fields
(`base ∪ own`), monomorphize inherited methods (clone IR, re-type `self` to the subclass,
re-mangle intra-`self` calls via `_rewrite_ir_calls`, emit as `let`), and conjoin
invariants (`base.class_invariants ++ own.class_invariants`). The invariant merge needs no
per-method code — `module6_whyml/preamble.py` `_emit_type_decls` already emits them as
Why3 type invariants that auto-thread into every method over the record. Edit
`src/pycsl/Module5_IREmitter.py` and `src/pycsl/module6_whyml/preamble.py`. Add corpus test
`test-suite/corpus/pycsl-reference/0442.py`: same-file `class Sub(Base)` where an inherited
method verifies over the subclass record and the subclass adds a method + an invariant.

**Acceptance:**
- `test -f test-suite/corpus/pycsl-reference/0442.py` exits 0
- `.venv/bin/python3 src/pycsl/pycsl.py test-suite/corpus/pycsl-reference/0442.py` exits 0
- `grep -c "class Sub" test-suite/corpus/pycsl-reference/0442.py` stdout >= `1`

### Phase 3 — Layers A + B + C: cross-file inheritance

**Status:** DONE

Combine Layer A resolution with Layer B/C merging so `class Sub(Base)` works when `Base` is
imported from another module. Edit `src/pycsl/Module5_IREmitter.py` (resolve bases against
the `imported_classes` registry) and `src/pycsl/Module4_SemanticAnalyzer.py` (validate base
resolvability; reject field rename across inheritance). Add base module
`test-suite/corpus/pycsl-reference/multi_file_lib/base_store.py` and subclass
`test-suite/corpus/pycsl-reference/0443.py` (the `MyOS(UnixInodeFileSystem)` shape: subclass
in one file, base imported), verifying with no duplicated fields/helpers. Confirm the
existing extreme-rigor example is unperturbed.

**Acceptance:**
- `test -f test-suite/corpus/pycsl-reference/0443.py` exits 0
- `.venv/bin/python3 src/pycsl/pycsl.py test-suite/corpus/pycsl-reference/0443.py` exits 0
- `.venv/bin/python3 src/pycsl/pycsl.py unix-filesystem/UnixInodeFileSystem.py 2>&1 | grep -c "Verification SUCCESS"` stdout >= `1`
- `grep -c "trusted reviewer:" unix-filesystem/UnixInodeFileSystem.py` stdout == `0`

### Phase 4 — Layer D: behavioral-subtyping proof obligations (flag-gated)

**Status:** DONE

For an override `Sub.m` of `Base.m`, emit Liskov obligations behind a new
`--check-behavioral-subtyping` flag: syntactic `assigns_sub ⊆ assigns_base` and
`raises_sub ⊆ raises_base` (hard error on violation), then SMT goals
`pre_base ⇒ pre_sub` and `post_sub ⇒ post_base`. Edit `src/pycsl/Module4_SemanticAnalyzer.py`
(syntactic containment) and add `_emit_override_obligations` in
`src/pycsl/module6_whyml/functions.py`. Add a positive corpus test
`test-suite/corpus/pycsl-reference/0444.py` (a refining override that verifies) and a
negative test `test-suite/corpus/pycsl-reference/0445.py` (a contravariant override that
must be rejected). Add `test-suite/agent-tests/test_inheritance_subtyping.py` exercising
both directions.

**Acceptance:**
- `test -f test-suite/corpus/pycsl-reference/0444.py` exits 0
- `test -f test-suite/corpus/pycsl-reference/0445.py` exits 0
- `.venv/bin/python3 src/pycsl/pycsl.py --check-behavioral-subtyping test-suite/corpus/pycsl-reference/0444.py` exits 0
- `.venv/bin/python3 src/pycsl/pycsl.py --check-behavioral-subtyping test-suite/corpus/pycsl-reference/0445.py` exits 1 *(contravariant override must be rejected)*
- `.venv/bin/python3 -m pytest test-suite/agent-tests/test_inheritance_subtyping.py -q` exits 0

## Notes

- Recommended cut line: ship Phases 0–3 (they deliver real `Sub(Base)` with no
  duplication + inherited invariants, retiring the self-contained-class workaround in
  `wp-and-files.md`); defer Phase 4 until a corpus case needs a refined override.
- Acceptance claims reference files this feature creates, so they fail until each phase is
  implemented — that is the intended ER semantics (the claim is the definition of done),
  and is independent of the load-bearing `human-needed` halt described above.
