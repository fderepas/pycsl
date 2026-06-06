# make-it-work — implementation plan that makes the 15 failing claims pass

Executable plan for `./bin/agent-feature-supervisor --feature-file make-it-work.md`.
It re-expresses `broad-cross-file-feature-exec.md` as an **implementation** plan
whose phases create the missing fixtures and implement the compiler changes so
the **15 acceptance claims** currently failing in
`metrics/feature-supervisor/broad-cross-file-feature-exec/halt-report.md` become
satisfiable. Each phase's `**Acceptance:**` block is exactly the halt-report's
claims for that phase, so a green run of this plan == those claims pass.

Authored per `config/skills/project-lifecycle/SKILL.md` (SKILL-CMMI-LIFE-001):
the submission shape follows §4 **T7.1** + `references/feature-plan-submission.md`;
the per-phase **Specifier → Verifier → Reconciliator** roles and the L2–L5
hierarchy follow §3 (RACI) + `references/task-details.md`. Design rationale,
edit-site citations, and the SMT fallback ladder live in
`broad-cross-file-feature.md`.

> **Reality (expected, per T7.1).** Phases edit load-bearing pipeline files
> (`Module4_SemanticAnalyzer.py`, `Module5_IREmitter.py`, `module6_whyml/preamble.py`,
> `module6_whyml/functions.py`). The supervisor is gate-only: it will halt
> `human-needed` on those, so implementation is by a human or a reviewed
> delegate. This plan is the work order; the acceptance claims are the
> definition of done the supervisor re-runs to confirm each phase shipped.
> Corpus fixtures must verify under the **`hoare`** memory model (else
> `\array_eq` degenerates to `true`).

## Lifecycle mapping (SKILL-CMMI-LIFE-001 §3/§4)

| Phase | Level | Specifier (authors change + fixture spec) | Verifier (test plan) | Reconciliator |
|---|---|---|---|---|
| 0 | L2 System (SY3-Pycsl) | Software Engineer — class-constant collection in Module5 | acceptance claims + `pycsl.py 0440.py` | agent-feature-supervisor / human on halt |
| 1 | L2 System (SY3-Pycsl) | Software Engineer — cross-module class resolver in `pycsl.py` | acceptance claims + multi-file `pycsl.py 0441.py` | agent-feature-supervisor / human on halt |
| 2 | L2–L3 | Software Engineer — base-merge + monomorphize in Module5/preamble | acceptance claims + `pycsl.py 0442.py` | agent-feature-supervisor / human on halt |
| 3 | L2–L3 | Software Engineer — cross-file base resolution (Module5/Module4) | acceptance claims + UnixInodeFileSystem regression | agent-feature-supervisor / human on halt |
| 4 | L2 + L5 Unit | Software Engineer — behavioral-subtyping obligations (Module4/functions.py) | positive + negative override tests + pytest | agent-feature-supervisor / human on halt |

## Implementation surface

### Phase 0 — Class-level constants in the class IR

**Status:** DONE

**Make possible:** the 2 Phase-0 claims (`0440.py` exists and verifies).
**Create** `test-suite/corpus/pycsl-reference/0440.py`: a `# pycsl-flags: --memory-model hoare`
class with a class-body int constant (e.g. `CAP = 64`) used inside a `#@`
contract (`#@ ensures \result < CAP`), and a method that verifies.
**Edit** `src/pycsl/Module5_IREmitter.py` (`visit_ClassDef`, `_collect_class_fields`):
collect class-body `Assign`/`AnnAssign` with `Name` targets + constant int RHS
into `type_decls[i]["constants"]` so the constant lowers to a literal, not an
opaque attribute read.

**Acceptance:**
- `test -f test-suite/corpus/pycsl-reference/0440.py` exits 0
- `.venv/bin/python3 src/pycsl/pycsl.py test-suite/corpus/pycsl-reference/0440.py` exits 0

### Phase 1 — Layer A: cross-module class resolution

**Status:** DONE

**Make possible:** the 3 Phase-1 claims.
**Create** `test-suite/corpus/pycsl-reference/multi_file_lib/base_counter.py`
(a small verifiable class) and `test-suite/corpus/pycsl-reference/0441.py`
(`# pycsl-flags: --memory-model hoare`) that imports it, instantiates it, and
calls a method.
**Edit** `src/pycsl/pycsl.py`: add `_resolve_imported_classes` reusing
`_process_dependency` / `_resolve_module_path` / `_rewrite_ir_calls`; surface the
dependency's `type_decls` + `<class>__*` methods into an `imported_classes`
registry on the main IR.

**Acceptance:**
- `test -f test-suite/corpus/pycsl-reference/0441.py` exits 0
- `test -f test-suite/corpus/pycsl-reference/multi_file_lib/base_counter.py` exits 0
- `.venv/bin/python3 src/pycsl/pycsl.py test-suite/corpus/pycsl-reference/0441.py` exits 0

### Phase 2 — Layer B + C: same-file inheritance (fields, methods, invariants)

**Status:** DONE

**Make possible:** the 3 Phase-2 claims.
**Create** `test-suite/corpus/pycsl-reference/0442.py`
(`# pycsl-flags: --memory-model hoare`): a same-file `class Base: ...` and
`class Sub(Base): ...` where an inherited method verifies over the subclass
record and `Sub` adds a method plus an invariant.
**Edit** `src/pycsl/Module5_IREmitter.py` (`visit_ClassDef` reads `node.bases`;
merge fields `base ∪ own`; monomorphize inherited methods — clone IR, re-type
`self` to `Sub`, re-mangle intra-`self` calls with `_rewrite_ir_calls`) and
`src/pycsl/module6_whyml/preamble.py` (consume merged `class_invariants` — Why3
type invariants auto-thread into every method, so the merge alone suffices).

**Acceptance:**
- `test -f test-suite/corpus/pycsl-reference/0442.py` exits 0
- `.venv/bin/python3 src/pycsl/pycsl.py test-suite/corpus/pycsl-reference/0442.py` exits 0
- `grep -c "class Sub" test-suite/corpus/pycsl-reference/0442.py` stdout >= `1`

### Phase 3 — Layers A + B + C: cross-file inheritance (+ regression)

**Status:** DONE

**Make possible:** the 2 failing Phase-3 claims (`0443.py`); the 2 regression
guards already pass and must stay green.
**Create** `test-suite/corpus/pycsl-reference/multi_file_lib/base_store.py` and
`test-suite/corpus/pycsl-reference/0443.py`
(`# pycsl-flags: --memory-model hoare`): subclass in one file, base imported (the
`MyOS(UnixInodeFileSystem)` shape), verifying with no duplicated fields/helpers.
**Edit** `src/pycsl/Module5_IREmitter.py` (resolve bases against the
`imported_classes` registry from Phase 1) and `src/pycsl/Module4_SemanticAnalyzer.py`
(validate base resolvability; reject field rename across inheritance).

**Acceptance:**
- `test -f test-suite/corpus/pycsl-reference/0443.py` exits 0
- `.venv/bin/python3 src/pycsl/pycsl.py test-suite/corpus/pycsl-reference/0443.py` exits 0
- `.venv/bin/python3 src/pycsl/pycsl.py unix-filesystem/UnixInodeFileSystem.py 2>&1 | grep -c "Verification SUCCESS"` stdout >= `1`
- `grep -c "trusted reviewer:" unix-filesystem/UnixInodeFileSystem.py` stdout == `0`

### Phase 4 — Layer D: behavioral-subtyping proof obligations (flag-gated)

**Status:** DONE

**Make possible:** the 5 Phase-4 claims. Heaviest/research-grade — see the
fallback ladder in `broad-cross-file-feature.md`.
**Create** `test-suite/corpus/pycsl-reference/0444.py` (a refining override that
verifies), `test-suite/corpus/pycsl-reference/0445.py` (a contravariant override
that must be REJECTED with exit 1 — not argparse exit 2), and
`test-suite/agent-tests/test_inheritance_subtyping.py` exercising both directions.
**Edit** `src/pycsl/Module4_SemanticAnalyzer.py` (syntactic `assigns_sub ⊆
assigns_base`, `raises_sub ⊆ raises_base`), `src/pycsl/module6_whyml/functions.py`
(`_emit_override_obligations`: `pre_base ⇒ pre_sub`, `post_sub ⇒ post_base`
goals), and `src/pycsl/pycsl.py` (add the `--check-behavioral-subtyping` flag;
exit 1 on a subtyping violation).

**Acceptance:**
- `test -f test-suite/corpus/pycsl-reference/0444.py` exits 0
- `test -f test-suite/corpus/pycsl-reference/0445.py` exits 0
- `.venv/bin/python3 src/pycsl/pycsl.py --check-behavioral-subtyping test-suite/corpus/pycsl-reference/0444.py` exits 0
- `.venv/bin/python3 src/pycsl/pycsl.py --check-behavioral-subtyping test-suite/corpus/pycsl-reference/0445.py` exits 1 *(contravariant override must be rejected)*
- `.venv/bin/python3 -m pytest test-suite/agent-tests/test_inheritance_subtyping.py -q` exits 0

## Notes

- Total acceptance bullets = 17 = the 15 failing claims + the 2 Phase-3
  regression guards (already green). A fully green run of this plan means all 15
  flip to pass while the 2 stay green.
- Sequencing matters: Phase 1's `imported_classes` registry is a prerequisite for
  Phase 3; Phase 2's merge/monomorphize precedes Phase 3's cross-file case.
  Implement and re-run phase-by-phase, watching claims flip.
- Recommended cut line (per `broad-cross-file-feature.md`): land Phases 0–3
  (real `Sub(Base)`, no duplication, inherited invariants) and defer Phase 4
  until a corpus case needs a refined override.
