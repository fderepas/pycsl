# Broad compiler feature: cross-module class inheritance with verified behavioral subtyping

## Context

Today PyCSL cannot model class inheritance. `Module5_IREmitter.visit_ClassDef`
(`:1065`) and `_collect_class_fields` (`:1013`) never read `node.bases`; a class
record's fields/methods/invariants come only from *that* class's own body. So
`class MyOS(UnixInodeFileSystem)` emits an **empty** record (no `disk`/`fd_*`, no
inherited syscalls), and every `self.field` becomes an opaque abstract op. The only
workaround is a **self-contained class that re-declares all fields and copies every
helper body** — which forks the proof (the `0 \trusted` guarantee earned on the base
must be re-earned and kept in sync on the clone) and cannot express "the os layer *is* a
refined filesystem."

This plan adds the real feature in four layers, each reusing machinery that already
exists. The strategic payoff is for the **standard-library annotation program** (real
Python/Go/C++ library code is inheritance-heavy): it removes a structural blocker,
eliminates clone-drift, and is the only sound way to give a subtype a *stronger* contract
than its base while staying substitutable.

## What already exists (reuse, do not rebuild)

- **Cross-module FUNCTION resolution** — `pycsl.py` `_extract_imports` (`:45`),
  `_resolve_module_path` (`:78`, searches main-file dir → CWD → `Lib/`),
  `_process_dependency` (`:127`, runs Modules 1→5 on the dep, BFS transitive callees,
  circular-import guard, `--deep`), `_resolve_direct_imports` (`:195`). It injects
  imported **functions** as `trusted: True` stubs. **It ignores `ir_data["type_decls"]`
  (classes).** ← the gap layer A fills.
- **`_rewrite_ir_calls`** (`:66`) — renames `Call.func` throughout an IR tree. Reused to
  re-mangle inherited self-method calls from `<Base>__m` to `<Sub>__m`.
- **Class record emission** — `Module5.visit_ClassDef` emits a `type_decls` record
  `{kind:record, name, fields, class_invariants, field_defaults, has_hash, has_eq}`;
  methods are separate function-IRs named `<class>.lower()__<method>` carrying
  `kind:method`, `self_type:<class>`.
- **Class invariants ⇒ Why3 type invariants** — `preamble.py _emit_type_decls`
  (`:525`, invariant block `:567-601`) emits `type t = {…} invariant { I } by { wit }`.
  Why3 **auto-assumes** `I` on every `(self:t)` parameter and **auto-checks** it on every
  mutation/return. This means invariant inheritance needs *only* a merge of the invariant
  IR lists — no per-method threading code.
- **Contract emission** — `functions.py _emit_contracts` (`:152`) →
  `requires {}`/`ensures {}`/`writes {}`/`raises {}`; `self` typed `(self:<self_type>)`
  at `:107`; record fields tracked in `_record_types` (`preamble.py:536`).

## Layer A — Cross-module symbol resolution (classes, constants)

**Goal:** when a module imports a name used as a base class (or instantiated), pull that
class's full IR — record (fields + invariants + defaults) + its `<class>__*` method IRs +
class-level constants — into the main compilation, keyed in a new registry.

**Edits:**
- `pycsl.py`: add `_resolve_imported_classes(...)` alongside `_resolve_direct_imports`.
  `_process_dependency` already returns the dep's full `ir_data` (cached) — extend it (or
  a sibling) to also surface `ir_data["type_decls"]` and the `<name>__*` methods for an
  imported class `name`, not just free functions. Build
  `ir_data["imported_classes"] = { Name: {record, methods, constants, source_module} }`.
- **Class constants** (`O_CREAT=64`, `BLOCK_SIZE=512`) are class-body assigns not in the
  IR today (they lower opaque; the base file uses literals). Add collection in
  `Module5.visit_ClassDef`: walk class-body `Assign`/`AnnAssign` with `Name` targets and
  constant int RHS into `type_decls[i]["constants"]`. Needed so subclasses inherit flags.
- `import_classifier.py`: a local project import (`from UnixInodeFileSystem import
  UnixInodeFileSystem`) is already allowed (not on the deny list) — confirm, no change.

**Decision — trusted vs re-verified imports:** imported base classes are resolved to full
IR (record + method bodies), NOT just trusted contracts, because layers B/C must
*monomorphize and re-verify* inherited bodies against the subclass record. Keep the
existing `trusted` stub path for plain function imports unchanged.

**Phase gate:** a multi-file corpus test where the importer merely *uses* an imported
class (`x = Base(); x.m()`), proving the record + method IR cross the module boundary.
Template: `test-suite/corpus/pycsl-reference/multi_file_lib/` + `0056.py` invocation.

## Layer B — Method / field merging

**Goal:** `class Sub(Base)` ⇒ subclass record = `base.fields ∪ own.fields`; subclass
method table = inherited base methods (re-typed to `Sub`) + own/overriding methods.

**Edits (all in `Module5_IREmitter`):**
- `visit_ClassDef` (`:1065`): read `node.bases`. Resolve each base via the same-file class
  table or layer-A `imported_classes`. Compute merged `fields` (base ∪ own; own wins on
  name clash) and pass to the `type_decls` record.
- `_collect_class_fields` (`:1013`): prepend resolved base fields before walking own
  `__init__` (dedupe by name).
- **Monomorphize inherited methods:** for each base method `<Base>__m` not overridden in
  `Sub`, clone its function-IR, set `self_type=Sub`, rename to `<Sub>__m`, and run
  `_rewrite_ir_calls` to rewrite intra-`self` calls `<Base>__k → <Sub>__k`. Emit as a
  normal `let` over the `Sub` record. **Why monomorphize:** Why3 records are nominal — a
  `sub` value is not a `base` value, so we cannot pass `Sub` where `Base` is expected.
  Cloning+re-typing reuses the entire existing method-emission path (each method is just a
  function over the `Sub` record, whose superset of fields makes every `self.field`
  resolve). It is the IR-level analog of Why3 `clone`.
- **Constants:** merge `base.constants ∪ own.constants` into the subclass record.

**Re-verify vs trust inherited bodies:** default **re-verify** (emit inherited clones as
`let`) so a subclass that strengthens invariants (Layer C) must prove inherited methods
still preserve them. Offer `--trust-inherited` (emit inherited as `val` with base
contract) as a fast path *only* when the subclass adds no invariant and no override.

**Risks:** (1) a base method that returns/takes the base type by name needs the same
monomorphization on those signatures; for the int/array field model this is rare — flag
and fall back to re-typing. (2) name-mangling collisions — guard by checking
`<Sub>__m` not already present (own method wins). **Phase gate:** same-file `class
Sub(Base)` corpus test: inherited method verifies over the subclass record, own method
added.

## Layer C — Invariant inheritance

**Goal:** subclass carries `base.class_invariants ∧ own.class_invariants`; every inherited
and new subclass method assumes+preserves the conjunction.

**Edit (one place):** in `visit_ClassDef`, set the merged record's `class_invariants =
base.class_invariants (IR) ++ own.class_invariants (IR)` (dedupe). Because
`preamble.py _emit_type_decls` (`:567-601`) emits these as a Why3 **type invariant** that
Why3 auto-threads into every `(self:Sub)` method, **no per-method code is needed** — the
merge alone propagates the invariants to inherited *and* new methods. The `by { witness }`
inhabitant must satisfy the merged invariant; the existing witness search
(`_check_witness_vals`, `:587-600`) + `field_defaults` from the merged `__init__` cover
it; extend the witness combos if a merged invariant needs a specific seed.

**Risk:** a base invariant referencing a base field the subclass renamed — disallow field
rename across inheritance (own field with a base name = same field). **Phase gate:**
subclass adds an invariant; an inherited mutator must re-prove the base invariant (it
does, via Why3 type-invariant checking) — corpus test asserts SUCCESS, and a deliberately
invariant-breaking inherited path fails (negative test).

## Layer D — Behavioral-subtyping (override) proof obligations

**Goal:** for every override `Sub.m` of `Base.m`, prove Liskov substitutability so a
`Sub` is safe wherever a `Base` is expected:
- `pre_base ⇒ pre_sub` (precondition weakened),
- `post_sub ⇒ post_base` (postcondition strengthened),
- `assigns_sub ⊆ assigns_base`, `raises_sub ⊆ raises_base` (no new effects/exceptions).

**Edits (new emission in `module6_whyml`, gated behind `--check-behavioral-subtyping`):**
- Add `_emit_override_obligations(sub_method, base_method)` parallel to
  `_emit_function` (`functions.py:215`). The base method's contracts come from the
  layer-A `imported_classes`/same-file table; both contract sets are already lowered to
  WhyML by `_emit_contracts`'s `_expr_to_whyml`.
- **Cheap first (syntactic, no SMT):** `assigns_sub ⊆ assigns_base` and `raises_sub ⊆
  raises_base` as set-containment checks at IR level — emit a hard error on violation.
- **Then (SMT):** per override, emit a Why3 `goal Sub_m_refines_Base_m : forall <self:Sub>
  <args>. (pre_base -> pre_sub) /\ (forall \result <post-state>. post_sub -> post_base)`,
  over the shared arg/state model (the `Sub` record, since fields are a superset).
- **Alternative considered:** Why3's native `clone … with` module refinement. Rejected as
  the primary because the codebase emits plain `goal`/`lemma`/`axiom` (cf. `preamble.py
  _AXIOM_REGISTRY`) and has no module-cloning usage; explicit goals fit the existing
  emission and audit tooling (`--audit-proof`, `cmmi-audit.sh [STRUCT]`).

**This is the heaviest layer** (capturing two contracts symbolically + quantifying over a
shared state). Stage it last and behind a flag; ship A+B+C first (they already unblock
`MyOS extends UnixInodeFileSystem` with zero duplication). **Phase gate:** a refining
override verifies; a contravariant (illegally weakened postcondition) override fails the
goal — negative corpus test.

## Phases (each independently `pycsl.py`-verifiable; each adds a corpus test)

0. **Class constants in IR** — collect class-level int constants into the `type_decls`
   record (prereq for inheriting flags). Corpus: a class using its own constant in a
   contract. Gate: SUCCESS.
1. **Layer A** — cross-module class extraction into `imported_classes`. Corpus: importer
   uses an imported class instance. Gate: record+methods cross the boundary; SUCCESS.
2. **Layer B+C, same-file** — `class Sub(Base)` in one file: field+method+invariant merge,
   inherited methods monomorphized & re-verified. Corpus: same-file subclass. Gate:
   inherited + own methods verify; merged invariant auto-threaded; SUCCESS, 0 `\trusted`.
3. **Layers A+B+C, cross-file** — `class Sub(Base)` with `Base` imported. Corpus: the
   `MyOS(UnixInodeFileSystem)` shape (multi_file_lib-style). Gate: SUCCESS, no field/helper
   duplication, 0 `\trusted`.
4. **Layer D** — override obligations behind `--check-behavioral-subtyping`: syntactic
   assigns/raises containment first, then pre/post goals. Corpus: a refining override
   (passes) + a contravariant override (fails). Gate: positive SUCCESS, negative correctly
   rejected.

## Critical files
- `src/pycsl/pycsl.py` — `_resolve_imported_classes` (Layer A); reuse `_process_dependency`
  (`:127`), `_resolve_module_path` (`:78`), `_rewrite_ir_calls` (`:66`).
- `src/pycsl/Module5_IREmitter.py` — `visit_ClassDef` (`:1065`) read `node.bases` + merge;
  `_collect_class_fields` (`:1013`) prepend base fields; class-constant collection;
  inherited-method monomorphization.
- `src/pycsl/module6_whyml/preamble.py` — `_emit_type_decls` (`:525`) consumes merged
  invariants/fields/constants (largely unchanged — the merge happens upstream).
- `src/pycsl/module6_whyml/functions.py` — `_emit_contracts` (`:152`), `_emit_function`
  (`:215`); NEW `_emit_override_obligations` (Layer D).
- `src/pycsl/Module4_SemanticAnalyzer.py` — validate base resolvability; field-rename
  rejection; override signature compatibility (Layer D syntactic checks).
- `test-suite/corpus/pycsl-reference/` — new tests per phase (+ a `multi_file_lib/` base
  module for the cross-file cases).

## Verification
- Per phase: `.venv/bin/python3 src/pycsl/pycsl.py <file>` → "Verification SUCCESS",
  exit 0; negative tests exit non-zero with the expected diagnostic.
- Regression: full `bin/run-reference-tests.sh --pycsl` green (the merge/monomorphize path
  must not perturb non-inheriting classes — they have empty `node.bases`); `cmmi-audit.sh`
  `[STRUCT]` unchanged for existing files; `unix-filesystem/UnixInodeFileSystem.py` still
  SUCCESS + 0 `\trusted` + `--audit-proof` 18/18.
- End-to-end payoff demo: re-express `MyOS(UnixInodeFileSystem)` with **no** duplicated
  fields/helpers and confirm the verified `open` (from the companion `wp-and-files.md`
  plan) verifies via inherited state + invariants — i.e. this feature retires the
  self-contained-class workaround.

## Cost / sequencing honesty
A+B+C are mechanical-but-broad and deliver the user-visible win (real
`Sub(Base)` with no duplication, inherited invariants). **D is genuinely research-grade**
(behavioral-subtyping obligation generation + the SMT/Rocq interplay) and carries the bulk
of the risk and test burden; it is flag-gated and last so the first three layers can land
and be used immediately. Recommended cut line if scope must shrink: ship **0–3**, defer
**4** until a corpus case actually needs an overriding subtype with a refined contract.
