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

The catalog is grouped by the UB-category numbering §7.1–§7.7.

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
dict/set key would raise `TypeError` at runtime, which the C-extension
boundary (UB-7.4) and `no_exception TypeError` modelling can flag
separately.

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
against the deny-list, the standard-library model set (under `src/pycsl_lib/`,
consumed as trusted stubs at the import boundary),
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

### §7.4a `struct.pack` / `struct.unpack` — faithful slots vs. residual boundary

`struct` is a C extension, but PyCSL models a subset of it faithfully rather
than treating every call as opaque (`module6_whyml/struct_format.py`,
`expressions.py:_handle_struct_call`). A **compile-time-constant** format string
is parsed into a slot sequence; two tiers result:

- **Faithful, guarded (in scope).** A WHITELISTED scalar-integer shape with an
  explicit standard byte-order prefix (`'<'`/`'>'`/`'='`/`'!'`) lowers to the
  `Pycsl.Struct.Std` family with a **per-field width/signedness tag**
  (`struct_{pack,unpack}_f<tag-join>`) carrying a **size law**
  (`len(pack(fmt,…)) == calcsize(fmt)`), a **per-field in-range guard**, and a
  **round-trip** `unpack(fmt, pack(fmt, …)) == (…)`. Shapes in scope:
  - single **unsigned** — `u16` (`'>H'`), `u32` (`'>I'`/`'>L'`);
  - single **signed** (two's complement) — `i16` (`'>h'`), `i32` (`'>i'`/`'>l'`),
    `i64` (`'>q'`); guard is the signed range `[-2^(8N-1), 2^(8N-1))`;
  - **multi-slot** — `u16u32` (`'>HI'`), `i32i32` (`'<ii'`). The per-field tag
    makes `'>HH'` (`u16u16`) and `'<ii'` (`i32i32`) DISTINCT symbols — resolving
    the earlier `slot_id` collision (both were `struct_pack_i2`);
  - **fixed-bytes** — `s4` (`'>4s'`): array identity `unpack(pack d) == d` under
    the length guard `len(d) == N`.
  See `axiom-registry.md`; anchors in `0777`–`0779.proofs/{rocq,lean}/StructResiduals.*`.

- **Residual boundary (out of scope → rejected or documented-opaque).** The
  following are *documented, honest residuals*, NOT faithfully modelled:
  - **Out-of-range value** for a standard-size slot. Real `struct.pack` RAISES
    `struct.error` (`'H' format requires 0 <= number <= 65535`). PyCSL models
    this as the pack `val`'s per-field `requires` — a **call-site VC**: an
    out-of-range pack is a proof FAILURE, not a silent truncation. The guard is
    *load-bearing* — dropping it makes the round-trip FALSE (the
    `guard_necessity_*` counterexamples: `unpack(pack 65536) = 0 ≠ 65536`;
    `unpack(pack 32768) = -32768 ≠ 32768`). Negative drivers: `0754`, `0780`
    (multi-slot field), `0781` (signed) — all `# pycsl-expected: FAIL`.
  - **Native size / alignment** (`'@'` prefix): see **§7.4b** — REJECTED.
  - **Float** slots (`f`/`d`) — the IEEE-754 mantissa/exponent bit-encoding does
    not lower to PyCSL's int/real model (no float-to-bits codec); these keep the
    size law only, and the byte layout is opaque. See §7.4c.
  - **`p`** (Pascal string), **`c`**, and **un-whitelisted multi-slot / wide**
    shapes (e.g. the os `'>IHHHHHII10Ixx'` = `i18`, `'>H30s'` = `i1a1`) keep the
    *legacy, unguarded* `UnixFs.Struct.*` shape-model axioms (which postulate the
    inverse over uninterpreted symbols; cautionary note in `axiom-registry.md`).
    The zero-trust way to model any of these is the body-faithful pure-Python byte
    codec of `0665` (`pack16`/`pack32`/`pack_inode`), which proves the guarded
    round-trip by SMT composition with NO axiom (and which already superseded the
    os re-key — see `cleared-pack.md` items S4/S5).

**Corpus cross-reference:** `0753` (faithful u16/u32), `0777` (multi-slot
`u16u32`), `0778` (signed `i16`/`i32`/`i64` + multi-slot signed `i32i32`), `0779`
(fixed-bytes `s4`); negatives `0754`/`0780`/`0781` (out-of-range guard-necessity),
`0782` (native `@` rejection); `0665` (zero-axiom body-faithful codec);
`0420`–`0425` (legacy abstract family, unchanged).

### §7.4b native `struct` size/alignment (`'@'` prefix) — REJECTED

A `struct` format with the native size/alignment prefix `'@'` is **rejected at
transpilation** with a clear diagnostic (`module6_whyml/expressions.py:
_handle_struct_call`). Native field sizes AND inter-field padding are
platform/ABI-dependent, so `calcsize` and the byte layout are undefined; a
standard-size size law or round-trip would be **unsound**. Rejection (rather than
silent opacity) is the sound choice — an opaque model could otherwise carry a
wrongly-sized `len(...)` claim. `calcsize()` also returns `None` for `'@'`
defensively (`struct_format.py`). Use an explicit standard-size prefix
(`'<'`/`'>'`/`'='`/`'!'`). Negative driver: `0782` (`# pycsl-expected: FAIL`).

### §7.4c `struct` float slots (`'f'`/`'d'`) — size law only, encoding opaque (YAGNI)

The round-trip for IEEE-754 `'f'`/`'d'` is a **documented YAGNI residual**. The
byte codec would have to extract the sign/exponent/mantissa bit-fields of a
float and reassemble them — a step that does **not lower** to PyCSL's value model
(floats are `real`, and `real → bits` is not an expressible total function in the
int/real theory; there is no `frexp`/bit-cast in scope). PyCSL therefore keeps the
**size law** (`calcsize('f') == 4`, `'d' == 8`) reachable via the opaque path but
makes **no round-trip claim** and treats the packed bytes as opaque. This is not a
provability-timeout — it is a modelling gap (no float-to-bits codec), so it is an
honest opacity note, not a faked axiom. Model a real float round-trip only if/when
a float-bit codec is added to the value model.

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
models construction `C(...)` as a **fresh WhyML record literal** —
parametrized construction substitutes the call args into the `__init__`
field initialisers. Allocation interposition
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

## §7.8 ragged / non-int-leaf in-place inner mutation of a nested list

**Source pattern that triggers it.** An in-place inner ELEMENT mutation
`a[i][j] = v` on a nested list `a: List[List[τ]]` (nested-list-mutable.md).

**Detection mechanism.** Module5 `_collect_inner_mutated_params` flags a nested
`List[List[…]]` param that the body inner-mutates (`a[i][j]=v`). An INT-leaf
(`List[List[int]]`) routes to the mutable built-in `matrix int` model
(`Matrix.set`/`Matrix.get`). Any other inner-mutated nested param stays on the
read-only, PURE-`seq`/`map` `array (seq τ)` model.

**Verification stance.** The mutable model is `matrix int`, which is **RECTANGULAR**
(a single uniform `columns`) and **int-leaf**. This is the perimeter:
- A NON-int-leaf inner mutation (`List[List[str]]` = `array (seq string)`) has no
  mutable 2-D built-in — the inner `seq` is immutable, so `a[i][j]=v` is a *hard
  type/verification failure* (REJECTED, never a silent unsound update). NEGATIVE
  driver `0804`.
- `a[i].append(...)` (SHAPE-CHANGE — a growable nested row) stays *opaque* (the
  `append_1` no-op makes no false post-state claim).
- The `matrix int` model **assumes rectangularity** (every row has `columns`
  elements). A genuinely RAGGED nested list mutated in place is outside the model's
  faithful domain — the rectangular assumption is a structural precondition (the
  same stance as the `\length2d` matrix path, 0018/0019). Passing a ragged list to
  a function verified under the matrix model is UB. Worst case is a type-error
  rejection (safe), never a false proof — `Matrix.set`/`Matrix.get` are faithful
  Why3 stdlib ops, so no unsound update is ever emitted.

**Corpus cross-reference:** `0802` (rectangular int read-back — supported),
`0803` (non-aliasing — supported), `0804` (non-int-leaf inner mutation — rejected),
`0797`/`0798` (read-only ragged nested lists — stay on `array (seq τ)`).

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
