---
name: pycsl-ub-catalog
description: Documents the catalog of Python undefined-behaviour (UB) categories that PyCSL detects, the detection mechanism for each, the verification stance (hard error / requires escape annotation / warning), and the corpus tests that exercise each detector. Use this skill when asking "what does PyCSL guarantee about Python UB", when adding or extending a UB detector, or when designing tests under `test-suite/corpus/pycsl-reference/` that exercise the UB perimeter.
---

# PyCSL Undefined-Behaviour Catalog

PyCSL's verification scope intentionally includes a small list of Python
constructs whose semantics are *genuinely* undefined or out-of-scope for
WhyML. Each category in this catalog has a static detection mechanism, a
verification stance, and (where applicable) an escape annotation. The
implementation lives across Module 1 (import classifier), Module 3
(weaver), Module 4 (semantic analyzer), and Module 5 (IR emitter).

The catalog is grouped by the NoException_and_UBDetection workplan
numbering (§7.1–§7.7). Entries are filled in as the corresponding PR
lands; expect partial coverage until all sub-features are merged.

---

## §7.1 Mutation during iteration

**Source pattern that triggers it.** Any `for x in C: ...` whose body
mutates the iterated collection `C`:

```python
for x in arr:
    arr.append(...)   # triggers (list.append on the iterated)
    arr.pop()         # triggers
    arr[i] = v        # triggers (subscript assignment)
    del arr[i]        # triggers
```

The full set of mutating methods is in
`IRScanner._MUTATING_METHODS`: `append`, `pop`, `clear`, `add`,
`remove`, `discard`, `update`, `extend`, `insert`, `setdefault`.

**Detection mechanism.** `IRScanner.find_iteration_mutations` is a
stateless walk of the IR statement list. For each `For` stmt whose
`iter` is a `Var(name=C)`, it recurses into the body collecting any
`ArraySet` against `C`, dotted-call `C.method(...)` where `method` is
in the mutating set, or `Delete`/`DelSubscript` against `C`. The
check runs from `pycsl.py:_run_pipeline` immediately after the IR is
validated, raising `PyCSLSemanticError` on the first violation.

**Verification stance.** *Hard error* by default. Mutating an iterated
list/dict corrupts CPython's iterator state and is genuine UB.

**Escape annotation.** `#@ allow_iteration_mutation` placed
immediately before the `for` statement (alongside `loop invariant` /
`loop variant`). Sets the per-loop `csl_allow_iteration_mutation`
flag, which Module 5 propagates as `allow_iteration_mutation: true`
on the IR for-loop node. The scanner respects the flag and skips the
mutation check for that single loop (the body's nested loops are
still checked).

**Corpus cross-reference:** `0404` (append), `0405` (pop), `0406`
(positive: mutating a different container), `0407`
(`allow_iteration_mutation` opt-in).

---

## §7.2 `__hash__` / `__eq__` consistency

**Source pattern that triggers it.** Any class that defines `__hash__`
and `__eq__` simultaneously. Hash/eq consistency (`a == b ⇒ hash(a)
== hash(b)`) is required by every container that uses the class as a
key. CPython does not enforce it; PyCSL surfaces the contract.

**Detection mechanism.** Module 5's `visit_ClassDef` (now at
`Module5_IREmitter.py:1216`) walks the class body and records
`has_hash` / `has_eq` / `is_unhashable` (only `__eq__` defined) on
the IR `type_decl` record. Module 6's `_emit_type_decls`
(`module6_whyml/preamble.py:548`) consults these flags and emits an
abstract `val function` pair plus a hash/eq relationship.

**Verification stance.** Default mode emits the relationship as a
WhyML *axiom* (the user is on the hook for the property; the axiom
documents the assumption). Strict mode
(`--strict-hash-eq-consistency`) emits it as a *goal* that Why3 must
discharge — typically via an external `#@ proof rocq` or
`#@ proof lean` citation.

Unhashable classes (`__eq__` without `__hash__`) emit a documentation
comment only; no goal/axiom is generated. Using such a class as a
dict/set key would raise `TypeError` at runtime, which UB-7.4 / future
`no_exception TypeError` work can flag separately.

**Escape annotation.** None directly — the strict-mode goal requires
an external `#@ proof` citation; the default-mode axiom is implicit
trust. To opt out of the check entirely, omit one of the methods or
do not derive the class from one that defines either.

**Corpus cross-reference:** `0411` (consistent, axiom mode), `0412`
(strict-mode unproven goal), `0413` (unhashable), `0414` (hash-only).

---

## §7.3 Concurrent races

**Source pattern that triggers it.** Any code under
`--memory-model concurrent` that:

- Reads or writes a shared variable outside its declared critical
  section (the `with mutex:` block named by `#@ shared X protected_by
  lock`).
- Declares a shared variable with `#@ shared X` (no `protected_by`) —
  unconditionally flagged because every access is a potential race.
- Acquires two locks in an order that conflicts with the declared
  `#@ lock_order` (potential deadlock).

**Detection mechanism.** `ConcurrencyChecker` already walks the AST
collecting these as `ConcurrencyWarning` records (see
`src/pycsl/ConcurrencyChecker.py:47`). UB-7.3 adds a
`strict_mode` flag: when set, the first warning is escalated to a
`PyCSLSemanticError`. The checker still runs and populates
`self.warnings` either way; strict mode just changes the response.

**Verification stance.** Default mode emits warnings to stderr. Under
`--strict-concurrent-checks` the first warning becomes a hard error.
Default remains *warning* for backward compatibility — existing
concurrent corpora (`pycsl-reference/0250`–`0263`) rely on the
warning-only contract.

**Escape annotation.** None at the access site — the fix is to add the
appropriate `#@ shared X protected_by L` declaration and wrap the
access in `with L: ... #@ critical L`. To opt out of the strict check
for a specific run, omit the `--strict-concurrent-checks` flag.

**Corpus cross-reference:** `0415` (unprotected access under strict),
`0417` (protected access under strict — passes).

---

## §7.4 C-extension boundary

**Source pattern that triggers it.** Any `import` or `from ... import`
of a module on the C-extension deny-list:

```python
import ctypes        # triggers
from cffi import FFI # triggers
import numpy.ctypeslib  # triggers
```

The default deny-list lives in `src/pycsl/import_classifier.py`
(`DEFAULT_DENY_LIST`): `ctypes`, `ctypes.util`, `cffi`,
`numpy.ctypeslib`, `cython`. Imports of any of these (or any
sub-module thereof) are classified as `UNVERIFIED`.

**Detection mechanism.** A new import-classification pass runs after
Module 4 semantic analysis and before Module 5 IR emission. It walks
the AST for `ast.Import` / `ast.ImportFrom`, classifies each module
against the deny-list, the trusted-stub set (under `src/pycsl_lib/`),
or the residual `UNRESOLVED` bucket. Only `UNVERIFIED` triggers a
hard error.

**Verification stance.** *Hard error* — `PyCSLSemanticError` at the
import line. Two opt-outs:

1. **Per-file `#@ \trusted` opt-in.** If at least one function in the
   file carries `#@ \trusted`, the file is treated as acknowledging the
   boundary; the import passes silently. This matches the existing
   trust mechanism PyCSL uses for stub files (`src/pycsl_lib/*.py`
   imports are all classified as `TRUSTED_STUB`).
2. **CLI flag.** `pycsl --allow-unverified-imports` disables the check
   entirely for one run. Useful for ad-hoc inspection but should not
   be enabled in CI.

**Escape annotation.** `#@ \trusted` on the function that calls into
the boundary. The annotation is the existing trust mechanism (it
emits `val` instead of `let` for the function, treating the body as
opaque). The new role at the C-extension boundary is just that *any*
function being `\trusted` in the file suppresses the import-level
error.

**Corpus cross-reference:** `0396` (deny-list rejection), `0397`
(`\trusted` opt-in), `0398` (`cffi`), `0400` (CLI override).

---

## §7.5 `__del__` / finalizer rejection

**Source pattern that triggers it.** Any `class` body containing a
`def __del__(self) -> None:` method.

**Detection mechanism.** `Module3_Weaver.visit_ClassDef` (line 159+)
scans each class body for a `FunctionDef` named `__del__`. If found
and the class lacks the `csl_allow_finalizer` flag (set by the
`#@ allow_finalizer` parser directive), the weaver raises
`PyCSLSemanticError` naming the offending class and line.

**Verification stance.** *Hard error* by default. The
non-determinism of CPython's finalizer protocol (timing depends on
the garbage collector, may be skipped entirely under interpreter
shutdown) makes any lifetime-dependent contract unsoundly modellable
in WhyML.

**Escape annotation.** `#@ allow_finalizer` immediately before the
`class` keyword. The annotation does *not* make the finalizer
verifiable — it documents the boundary so the rest of the class can
still be verified. Contracts that reference lifetime (e.g. "the
finalizer releases X") remain at risk.

**Corpus cross-reference:** `0401` (rejection), `0402`
(`allow_finalizer` opt-in), `0403` (baseline, no `__del__`).

---

## §7.6 non-trivial `__new__` rejection

**Source pattern that triggers it.** A `class` body whose `__new__`
does anything other than the default allocation — i.e. *not* a single
`return super().__new__(cls)` / `return object.__new__(cls)` (after an
optional docstring). Examples: caching / singletons (`return
cls._inst`), returning a different or conditionally-chosen instance,
or any branching/side-effecting body.

**Detection mechanism.** `Module3_Weaver.visit_ClassDef` scans for a
`FunctionDef` named `__new__` and calls `_is_trivial_new`; a
non-trivial `__new__` raises `PyCSLSemanticError` (UB-7.6) naming the
class and line. A trivial `__new__` is accepted and ignored
(construction proceeds via `__init__`).

**Verification stance.** *Hard error*, no escape annotation. PyCSL
models construction `C(...)` as a **fresh WhyML record literal**
(`base_op.md` Tier A — parametrized construction substitutes the call
args into the `__init__` field initialisers). Allocation interposition
(`__new__` returning a cached/other instance) breaks that model: the
result would no longer be a fresh `{...}`, and identity/caching
semantics cannot be soundly represented. Rejecting is the honest
boundary — we do not fake it.

**Corpus cross-reference:** `0497` (non-trivial `__new__` rejection),
`0496` (trivial `__new__` accepted + parametrized `__init__`), `0495`
(parametrized construction, no `__new__`).

---

## §7.7 unsound memoization (`@lru_cache` on a non-RT function)

**Source pattern that triggers it.** A function carrying a memoizing decorator
(`@lru_cache`, `@lru_cache(maxsize=…)`, `@cache`, `@cached_property`) that is
**not referentially transparent**.

**Detection mechanism.** `Module5._is_memoized` flags the decorator;
`_check_memoization_soundness` rejects (`PyCSLIRError`, UB-7.7) unless the
function is referentially transparent (RT): it must be **pure** (`#@ assigns
\nothing`, not `\trusted`, not `\diverges` — `_detect_purity`) AND read no
`#@ shared` mutable global (`_reads_any`). Module-level *constants* are fine.

**Verification stance.** *Hard error*, no escape annotation. PyCSL verifies the
function's **uncached** body and ignores the decorator. That is sound only when
caching is observationally transparent — i.e. the function is RT (same inputs →
same result, no effects). Memoizing an effectful or non-deterministic function
makes the cache return values inconsistent with the verified body, so the proof
would not describe the running program. (Why3 `let function` symbols are RT by
construction, and PyCSL already emits a pure non-method function as one — so for
an RT function no extra work is needed; this rule only gates the unsound case.)
Note: contracts must be placed **above** the decorator to attach.

**Corpus cross-reference:** `0515` (pure `@lru_cache` accepted + caller proof),
`0516` (memoizing a non-RT function rejected).

---

## Verification-perimeter philosophy

PyCSL's verification target is a subset of Python — value-only,
heap-explicit, exception-explicit. The UB catalog defines the boundary
of that subset. Each entry exists because the corresponding Python
construct cannot be soundly modelled in WhyML without external trust:

- `ctypes`/`cffi`/`cython` cross the value/memory boundary — a Python
  reference into an extension's memory has no WhyML representation.
- `__del__` introduces non-determinism in object lifetime; lifetime
  contracts can't be expressed against a garbage-collected runtime.
- Mutation during iteration corrupts CPython's iterator state in ways
  the WhyML array model doesn't capture.
- `__hash__` / `__eq__` inconsistency violates the set/dict contract
  that WhyML's `map` model assumes.
- Concurrent races without explicit mutex protocol are unsound under
  the monitor-invariant pattern PyCSL uses for `--memory-model
  concurrent`.

In every case the detector exists to *surface the boundary at
annotation time*, not to verify across it. Crossing the boundary
requires an explicit acknowledgement (`#@ \trusted`,
`#@ allow_finalizer`, `#@ allow_iteration_mutation`) that documents
the assumption rather than silently relying on it.

## Related skills and docs

- `config/skills/pycsl-software-architecture/SKILL.md` Section 1 —
  where each detector lives in the pipeline.
- `docs/pycsl-concrete-syntax-reference.md` — escape annotation grammar.
- `docs/pycsl-static-semantics-reference.md` — formal well-formedness
  conditions for each UB category.
- `test-suite/traceability-pycsl.md` — corpus-test cross-reference.
