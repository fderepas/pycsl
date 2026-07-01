# b1-plan.md — Resolve imported dataclass types in single-file self-annotation (the "B1" blocker)

> **Purpose.** Fix the `b14.md` **B1** blocker — the DOMINANT wall across the whole
> body-faithful-emitter track (`ir-schema-spec.md` Phase C, `semantic-ceiling-plan.md`,
> `a2-a3-plan.md §10.2`). When PyCSL verifies a single self-annotate mirror file that
> does `from ir_schema import AssignStmt`, the type is **opaque** ("external module,
> no local source found — skipping"), so `stmt: AssignStmt` degrades to `Any` and
> `stmt.target` is an untyped getattr — the Phase-A/B typed-schema payoff (and the
> now-complete `phase-b-expr` typing) **does not transfer to single-file isolation**.
> B1 is what gates A3 / Slice-0 and any body-faithful `_handle_*` contract.
>
> **Scope.** This is a *front-end / import-resolution* feature, not a proof or a
> modeling change. It does **not** touch Ceiling B (metacircular adequacy) or the
> A2 string-op feature — those remain. B1 unblocks the *type-resolution*
> precondition so a converted emitter method can be **framed and its typed fields
> read**; the emitter's string reasoning (A2) and the coherence residual (D2) are
> separate.
>
> **Convention.** Named repo-root plan file. Byte-identical gate (`bin/byte-diff-sweep.sh`)
> — this changes *resolution*, never emission. Minimal reproduction first.

---

## 0. Root cause (measured — both in `src/pycsl/frontend/ir_resolve.py`)

The self-annotate suite runs `pycsl <file>` on the mirror
`src/self-annotate/src/module6_whyml/statements.py`, which imports its IR types
from `ir_schema` (living at `src/pycsl/ir_schema.py`, **outside** the mirror tree).
Two independent gaps make the import opaque:

- **B1-a — module not located.** `_resolve_module_path(module, level, main_file)`
  "Searches: main file's directory first, then CWD." For an absolute import
  `from ir_schema import …` from a mirror file, it looks in
  `src/self-annotate/src/module6_whyml/` and CWD — never in `src/pycsl/`. → returns
  `None` → the `_resolve_direct_imports` "external module, no local source found —
  skipping" branch fires (`ir_resolve.py:388`).
- **B1-b — dataclasses not injected even if located.** `_process_dependency` "Run
  Modules 1→5 on filepath, return **list of func_ir dicts**" — it injects imported
  **functions** (and constants, and *some* record types via
  `_find_record_type_from_dep_imports`), but does **not** extract the dependency's
  `@dataclass` definitions as record `type_decls` for the importer. So even a
  located `ir_schema` would not make `AssignStmt` a usable typed record.

**Existing machinery to reuse:** Module 5 already turns a *locally-defined*
`@dataclass` into a WhyML record (`Module5_IREmitter._collect_class_fields` +
`_is_dataclass_decorated`, `ir-schema-spec.md §11`). B1 is: make an *imported*
dataclass go through the same path.

---

## 1. Objective & success criterion

**Objective.** When PyCSL verifies a file that imports a `@dataclass` from a
resolvable module, register that dataclass as a **typed record type** in the
importer's IR, so a parameter `stmt: AssignStmt` supports typed field access
(`stmt.target : str`, `stmt.value : ExprIR`) — exactly as if the class were
defined locally.

**Done =**
- A standalone 2-file probe (module with `@dataclass class Foo: x: str`; importer
  with `def f(o: Foo) -> str: #@ ensures \result == o.x ; return o.x`) that
  **FAILS today** (B1 reproduction) now **verifies SUCCESS**.
- The self-annotate mirror `statements.py` resolves `from ir_schema import …` (no
  "external module … skipping" for `ir_schema`), and at least one `_handle_*`
  method's `stmt` parameter is a typed record (probed by a body-faithful contract
  on a typed field).
- **byte-diff 0** across the 627-file corpus (resolution change, not emission).
- The self-annotate suite stays green.

---

## 2. The two sub-fixes

### B1-a — locate the module (search path)
Extend module resolution so an importer can find a dependency that lives elsewhere
in the repo. Options (pick one; **recommend the explicit search path**):

| Option | Change | Trade-off |
|---|---|---|
| **A (search path) — recommended** | `_resolve_module_path` also searches a configurable import root (CLI `--import-path DIR`, repeatable; the self-annotate runner passes `--import-path src/pycsl`). | Explicit, no mirror duplication; a small CLI + resolver change. |
| B (mirror the module) | Copy/symlink `ir_schema.py` into `src/self-annotate/src/ir_schema.py`. | Zero resolver change, but a large generated mirror file to keep in sync (fights the mirror-check gate). |
| C (package verify) | Verify the mirror as a package with `--deep` from a root where `ir_schema` resolves. | Reuses `--deep`, but changes the suite's invocation model and pulls in more deps. |

Option A is the smallest, most explicit change and does not add a maintained
mirror copy.

### B1-b — inject the imported dataclass as a record type
When `_process_dependency` runs Modules 1→5 on the located source, also collect the
`@dataclass` `type_decls` it produced (Module 5 already emits these for the dep's
own classes) and **inject the ones the importer names** into the importer's IR
`type_decls`, de-duped by name (local definitions win), scoped like the existing
`_find_record_type_from_dep_imports` record propagation. Then Module 6 sees
`AssignStmt` as a record and a `stmt: AssignStmt` parameter gets typed-field
lowering — the same path a locally-defined dataclass already takes.

---

## 3. Work items

| WI | Item | Gate |
|---|---|---|
| **B1.0** | **Minimal reproduction**: 2-file probe (`m_types.py` dataclass + importer using `o.x` in a contract) — confirm it FAILS today (opaque field). | probe FAILS (baseline) |
| **B1.1** | B1-a: `--import-path` CLI arg (repeatable) threaded to `_resolve_module_path`; search those roots after main-dir/CWD. | probe's module now *resolves* (no "external … skipping") |
| **B1.2** | B1-b: `_process_dependency` returns the dep's `type_decls`; `_resolve_direct_imports` injects the imported dataclass records into the importer (dedup, local-wins). | probe VERIFIES SUCCESS |
| **B1.3** | Wire the self-annotate runner: pass `--import-path src/pycsl` for the mirror files; confirm `ir_schema` resolves (no skip message). | mirror resolves ir_schema |
| **B1.4** | Un-`\trust` ONE leaf `_handle_*` in the mirror that reads a typed field (e.g. a `stmt.target`/`stmt.value` access) with a body-faithful contract; confirm it verifies. | one method body-faithful; suite green |
| **B1.5** | Non-vacuity + corpus: a false contract on the typed field FAILS; a `pycsl-reference` case exercising an imported-dataclass field stays Valid. | non-vacuity holds |
| **B1.6** | Docs: mark `b14.md` B1 / `ir-schema-spec.md §10` CLOSED; note the residual (A2 string ops, Ceiling B) for a fully body-faithful emitter. | docs reconciled |

---

## 4. Gate criteria

1. **Byte-identical** across the 627-file sweep — B1 changes import *resolution*
   and *type registration*, never the emitted WhyML for existing corpus files
   (they don't import cross-tree dataclasses). Any diff is a regression.
2. **The B1.0 probe flips** FAIL → SUCCESS after B1.1+B1.2.
3. **Self-annotate suite green** (`bin/run-self-annotation-suite.sh`), with the
   `ir_schema` import now resolved (grep the run for the absence of the
   "external module … skipping" line for `ir_schema`).
4. **≥1 real `_handle_*` un-`\trusted`** and body-faithful (B1.4) — the concrete
   proof B1 is closed, not just resolvable.
5. **Non-vacuity** (B1.5): a wrong typed-field contract FAILS.

---

## 5. Non-goals (honest)

- **Not** the A2 string-op feature — an un-`\trusted` handler that transforms
  string *content* (`replace`/`split`/…) still won't verify (`a2-a3-plan.md §10.1`);
  B1 only makes its typed *fields* readable and its frame stateable (with A3).
- **Not** Ceiling B — the body-faithful `ensures` still bottoms out at the audited
  evaluator axioms (D2); B1 removes the *type-opacity* wall, not the metacircular one.
- **Not** general Python import semantics — B1 resolves `@dataclass` *record types*
  (and keeps the existing function/constant/record-global handling); arbitrary
  class hierarchies / methods on imported classes are out of scope.
- **Not** the full 12-method emitter conversion — B1.4 converts **one** leaf to
  prove the mechanism; scaling is the follow-on (bounded by A2/A3 per method).

---

## 6. Smallest first experiment (B1.0 + B1.1 + B1.2, one arm)

```
m_types.py:      @dataclass
                 class Foo:
                     x: str
use_foo.py:      from m_types import Foo
                 #@ ensures \result == o.x
                 def get_x(o: Foo) -> str:
                     return o.x
```
1. `pycsl use_foo.py` today → **FAIL** (`Foo` external/opaque, `o.x` untyped). Confirm.
2. B1.1 (`--import-path .`) → `Foo` resolves (no skip line).
3. B1.2 (inject the dataclass record) → `o.x` is `Foo.x : str` → **SUCCESS**.

If steps 2–3 close on this two-file case, B1 is validated end-to-end and B1.3–B1.4
apply it to the real mirror. If `_process_dependency`'s Module-1→5 run on the dep
surfaces a deeper opacity (e.g. the dataclass field is itself an imported type
needing recursive resolution), that is the precise next scope — resolve it with
`--deep`-style recursion, still bounded.

---

## 7. Why this is the high-leverage unlock

B1 is the single blocker named across **every** doc on the body-faithful track:
`b14.md` ("DOMINANT"), `ir-schema-spec.md §10` (the reason Phase C stalled),
`semantic-ceiling-plan.md §12.2`, `a2-a3-plan.md §10.2` (gates A3/Slice-0). Closing
it converts "the typed-IR payoff doesn't reach single-file self-annotation" into
"it does" — after which the body-faithful route is gated only by the *modeling*
work (A2 string ops, A3 assigns-framing), not by type-opacity. It is a **bounded
front-end fix** (two functions in `ir_resolve.py` + a CLI flag + reuse of Module 5's
dataclass extraction), fully byte-diff-gated, and **not itself ceiling-blocked** —
unlike the modeling it unblocks.

---

## 8. EXECUTION RESULT (2026-07-01) — §6 experiment validated; B1-a implemented, B1-b already worked

Ran the §6 smallest experiment first. **Key discovery: B1-b was NOT broken.** A
same-directory probe (`Foo` dataclass + importer using `o.x` in a contract)
**already verified SUCCESS** — the resolver *does* inject an imported `@dataclass`
as a typed record once the module is located (the `ir-schema-spec.md §11`
dataclass→record machinery already covers imports). So the real blocker is **B1-a
alone**: cross-directory module *location*.

**Reproduced B1-a** (true cross-dir): `m_types.py` on `PYTHONPATH` but not in the
importer's dir / CWD / `src` / `Lib` → `Foo` opaque → `o.x` untyped → **FAILED**.

**Implemented B1-a** (Option A): a repeatable CLI `--import-path DIR`, threaded
`pycsl.py → resolve(import_paths=…) → _EXTRA_IMPORT_PATHS`, searched by
`_resolve_module_path` *after* the built-in roots (opt-in; default unchanged).

**Gates (all green):**
- §6 probe **flips FAIL → SUCCESS** with `--import-path <lib>` (module resolves →
  `o.x : str` typed → contract proven).
- **Non-vacuity:** a deliberately false `ensures \result == "…"` on the same typed
  field **FAILS**.
- **Byte-diff 0** across the 627-file corpus (default resolution unchanged).

**Status of the work items:** B1.0 ✅ (reproduced), B1.1 ✅ (`--import-path`),
B1.2 ✅ (already worked — no code needed). **Remaining (supervised, per plan):**
- **B1.3** — wire the self-annotate runner to pass `--import-path src/pycsl` and
  confirm the real mirror resolves `ir_schema` (no "external … skipping").
- **B1.4** — un-`\trust` one leaf `_handle_*` reading a typed `stmt` field and
  confirm it verifies body-faithful (the concrete close of B1).
- **B1.5/B1.6** — corpus/non-vacuity on the real mirror; reconcile `b14.md` B1 /
  `ir-schema-spec.md §10`.

**Net:** the type-opacity mechanism is fixed and proven on the minimal case with
full gates. The remaining B1.3–B1.4 apply it to the real mirror — the next step,
where the deeper opacity (recursive dataclass fields that are themselves imported
types, e.g. `stmt.value : ExprIR`) may surface and, per §6, is resolved with
`--deep`-style recursion (still bounded, not ceiling-blocked).

---

## 9. B1.3 RESULT (2026-07-01) — the real mirror resolves ir_schema into typed records

Wired the self-annotate runner and confirmed B1.3 end-to-end on the **real** mirror.

**Achieved:**
- `pycsl src/self-annotate/src/module6_whyml/statements.py --import-path src/pycsl`
  now resolves the mirror's `from ir_schema import …`: **26 imported classes**
  registered as records (e.g. `AssignStmt` = record + 17 helpers), **0 `ir_schema`
  imports skipped** (was: all skipped, opaque). Still `Verification SUCCESS`.
- **The §8 recursive-field worry did NOT materialize.** `ExprIR`-typed fields
  (e.g. `stmt.value`) resolved cleanly — those classes live in `ir_schema` too and
  come in as records in the same pass. No `--deep` recursion was needed.
- Runner wiring (`bin/run-self-annotation-suite.sh`): a mirror-scoped
  `--import-path $PROJECT_ROOT/src/pycsl` (applied only to `src/self-annotate/*`,
  since real `src/pycsl/` files resolve their own dir and the redundant path
  perturbs them). Regression-free for every mirror file (verdicts unchanged;
  `statements.py`/`expressions.py` still SUCCESS, now with typed IR records).

**Honest caveat — a PRE-EXISTING, UNRELATED suite failure:** `src/pycsl/errors.py`
fails on `main` independent of B1 — a deterministic WhyML **type error** (`line 36:
expression has type int, expected string`; a str/int mismatch, likely no-more-int
fallout). Confirmed failing pre-#101, post-#101, and on a fully pristine tree, in
0.8s. It is **not** caused or fixed by B1.3 (the runner change is scoped away from
it). So the suite's overall exit is red *for a reason orthogonal to B1* — flagged
here for separate triage, not conflated with this work. (An earlier "suite exit 0"
reading was a measurement bug: `$?` after a `| tail` pipe captured tail's code.)

**Work-item status:** B1.0 ✅ · B1.1 ✅ · B1.2 ✅ (already worked) · **B1.3 ✅**
(mirror resolves ir_schema into typed records; runner wired). **Next — B1.4:**
un-`\trust` one leaf `_handle_*` that reads a typed `stmt` field and prove it
body-faithful (the concrete close). Separately: fix the pre-existing errors.py
int/string type error to get the suite back to green.

---

## 10. B1.4 RESULT (2026-07-01) — B1 type-resolution is closed; a downstream lowering bug is the next wall

Un-`\trusted` the cleanest leaf — `_handle_ghost_array_set_stmt` (reads typed
`stmt.target/index/value`, pure-concat body, **no state mutation**) — and let
PyCSL CHECK its body (`--import-path src/pycsl`). It **FAILED**, and the failure
precisely localizes the next blocker.

**B1 itself is confirmed CLOSED.** The imported records resolve and the `val`
signatures are correctly typed — the emitted WhyML has
`val …__handle_ghost_array_set_stmt (… stmt: ghostarraysetstmt …)` and
`type ghostarraysetstmt = { mutable ghostarraysetstmt_target: string; … }`. The
Phase-A/B typed-schema payoff **does** reach single-file self-annotation now.

**The new wall — imported-`@dataclass` field-access lowering.** The checked body
emitted `arr := (whyml_ident stmt.target)` → Why3 **"unbound function or predicate
symbol 'target'"**. Root cause (localized):
- Fields that occur in *several* records (`target`, `value`, `op` — the ~26 Stmt
  records collide) are **ambiguous**, so the record *declaration* prefixes them
  via `_field_label` → `ghostarraysetstmt_target` (`expressions.py:2888`).
- But the field *access* `stmt.target` did **not** prefix — because `rec_lower`
  (the record type of `stmt`) is resolved only through the **`is_typeddict`-gated**
  path (`expressions.py:2395`): a Var's record type is taken only when
  `_record_types[sym]["is_typeddict"]`. An imported `@dataclass` is a record but
  **not** a TypedDict, so `rec_lower` stays `None`, `_field_label` returns the bare
  `target`, and it mismatches the prefixed declaration → unbound.
- Secondary gap: `stmt.index.to_dict()` lowered to a receiver-less nullary
  `stmt_index_to_dict_0 ()` (the sub-field `.to_dict()` call dropped its receiver).

**So B1.4 is BLOCKED on a Module-6 lowering fix, not on type resolution:** teach
the attribute-access lowering to resolve `rec_lower` for an imported-`@dataclass`
-typed parameter (register the param's record type in `_current_symbol_table` +
relax the `is_typeddict` gate to any record, so ambiguous fields prefix
consistently on the access side), and fix the sub-field `.to_dict()` receiver
loss. This is byte-diff-sensitive (it touches record field-access shared with the
627-corpus's local records), so it needs its own careful, fully-gated pass — **not
an unsupervised edit.** The mirror was reverted to its committed `\trusted` state
(no code left changed).

**Work-item status:** B1.0–B1.3 ✅. **B1.4 ◻ BLOCKED** on the imported-record
field-access lowering (precisely localized above) — the next concrete fix.
This is the honest edge: B1 *resolves* the types; *using* a typed imported-record
field in a checked body needs one more Module-6 lowering fix.

---

## 11. B1.4 FIELD-ACCESS FIX (2026-07-01) — the lowering bug is fixed; next layer is emitter-body int-typing

Fixed the §10 field-access lowering bug. In `_handle_attribute_expr`'s
`_record_locals` branch (`expressions.py`), an ambiguous field now qualifies via
`_field_label` using the record's `whyml_name` (resolved from the symbol table;
the `_record_types` key is CamelCase, so match on the raw name, not `.lower()`).
Non-ambiguous fields keep the exact bare form.

**Verified:** the un-`\trusted` `_handle_ghost_array_set_stmt` body now emits
`whyml_ident stmt.ghostarraysetstmt_target` (correctly qualified) — the "unbound
symbol 'target'" error is **gone**. **Byte-diff 0** across the 627-file corpus (no
corpus driver has an ambiguous-field access through this path, so the change is
inert there; only the imported-Stmt-record case is affected).

**The next layer (revealed, NOT this fix):** the same handler now fails one line
later with *"expression has type string, but expected int"* — because the
emitter's own string-valued locals are modeled as int: `let arr = ref 0 in; arr :=
whyml_ident(...)` (a `string`). This is the **no-more-int modeling gap applied to
the emitter body** — the local-type inference defaults call-result locals to `int`
instead of reading the callee's `-> str`. Plus the secondary `.to_dict()`
receiver-loss (`stmt.index.to_dict()` → nullary `stmt_index_to_dict_0 ()`). Both
are broader modeling fixes (string-typed locals + method-receiver lowering), not
the field-access bug — the honest next blockers, tracked separately.

**Net:** one concrete, byte-clean lowering bug removed from the body-faithful path
(imported-record ambiguous-field access now correct). B1.4 still not fully closed
(a handler body-faithful) — it now bottoms out at the emitter-body int-typing gap,
which is the same modeling ceiling A2 documents, not a type-opacity issue.
The mirror was reverted to its committed `\trusted` state.
