# PyCSL Workplan — `no_exception` annotation + Undefined Behavior detection

> Plan for two related-but-distinct features extending PyCSL's verification scope: a `no_exception` contract annotation that turns implicit Python exceptions into proof obligations, and a set of UB detectors covering the five genuine-UB categories that survive in Python despite its memory-safe design.

---

## 0. Framing

Both features extend the same axis: **what counts as a verification failure**. Today PyCSL proves declared functional contracts (`requires` / `ensures` / `raises { ... }`). It does not constrain implicit exception escape (a `ZeroDivisionError` from `a / b` is currently invisible to the proof), and it does not flag the small list of Python operations whose semantics are genuinely undefined.

The two features are conceptually linked — both are about "bad behavior the contract should reject" — but technically very different:

- **`no_exception`** is a VC-injection feature. It hooks into the existing transpiler's expression/statement handlers and emits assertions corresponding to each implicit exception trigger. Architecturally it is a contract-vocabulary extension.
- **UB detection** is a heterogeneous bundle of five static analyses, most of which sit outside Module 6 (the transpiler) entirely. Some are class-level invariants, some are import-graph checks, some are dataflow analyses on the IR.

They share test infrastructure and skill-documentation surface, but the implementations are essentially independent. The plan treats them as parallel workstreams that meet only at the corpus and the skill updates.

### Relation to the Module 6 refactoring plan

If the Module 6 split (see `Module6_RefactoringPlan.md`) lands first, the `no_exception` work is significantly easier: the VC injection touches `module6_whyml/expressions.py` and `module6_whyml/statements.py` rather than the 4,678-line monolith. If it lands concurrently, expect merge conflicts in exactly those clusters. The recommended sequencing is: refactoring steps 1–7 first, then this work. Steps 8–10 of the refactor and this work can interleave safely.

---

## Part I — `no_exception`

### 1. Surface syntax

The contract directive is a new line inside a `#@`-prefixed contract block:

```python
#@ no_exception ZeroDivisionError
#@ no_exception ZeroDivisionError, IndexError   # multiple in one line
#@ no_exception \all                            # forbid any escaping exception
```

Multiple `no_exception` lines are allowed and union together. The `\all` form is equivalent to listing every exception PyCSL's model knows about (see §3) *plus* requiring the function's `raises { ... }` set to be empty for that proof step.

### 2. Semantics

For a function `f` annotated with `no_exception E_1, …, E_k`, the proof obligation becomes:

> Under the function's precondition, no execution of `f`'s body raises any `E_i` (directly or via a called function).

This is *additive* on top of the existing `requires` / `ensures` / `raises` obligations. `no_exception E` is in tension with `raises { E -> P }` — you cannot simultaneously say "may raise E with postcondition P" and "must not raise E". The parser must reject this combination.

When neither `raises { E }` nor `no_exception E` is present for some implicit-exception-triggering operation, current PyCSL behavior is preserved: the operation transpiles without an assertion, the proof goes through, and the runtime exception is the user's problem. This is the "ambient" tier and matches today's semantics for the unannotated `divide_256` example.

### 3. The exception trigger model

This is the bulk of the modeling work. Each implicit-exception-raising operation must be associated with a *trigger condition*: a side-condition (in the WhyML proof environment) that is sufficient to prevent the exception.

**Initial scope** (Phase 1 — the operations PyCSL already transpiles, with clean arithmetic triggers):

| Operation | IR shape | Exception | Trigger condition (assertion the VC must discharge) |
|---|---|---|---|
| `a / b` | `BinOp("/", a, b)` | `ZeroDivisionError` | `b <> 0` |
| `a // b` | `BinOp("//", a, b)` | `ZeroDivisionError` | `b <> 0` |
| `a % b` | `BinOp("%", a, b)` | `ZeroDivisionError` | `b <> 0` |
| `divmod(a, b)` | `Call("divmod", [a, b])` | `ZeroDivisionError` | `b <> 0` |
| `arr[i]` (1D) | `Subscript(arr, i)` | `IndexError` | `0 <= i < length arr` |
| `arr[i][j]` (2D) | nested `Subscript` | `IndexError` | `0 <= i < rows /\ 0 <= j < cols` |
| `arr[i] = v` | `ArraySet(arr, i, v)` | `IndexError` | `0 <= i < length arr` |
| `d[k]` (dict lookup) | `MapGet(d, k)` | `KeyError` | `has_key d k` |
| `d.pop(k)` without default | dotted call | `KeyError` | `has_key d k` |
| `1 << n`, `1 >> n` | `BinOp("<<"/">>", a, n)` | `ValueError` | `n >= 0` |
| `s.index(x)` on list/str | dotted call | `ValueError` | `mem x s` |
| `next(it)` | `Call("next", [it])` | `StopIteration` | depends on iterator model (Phase 2) |

**Phase 2 — operations needing more modeling**:

| Operation | Exception | Notes |
|---|---|---|
| `int(s)`, `float(s)` | `ValueError` | Requires string content modeling — skip until PyCSL has stronger string predicates. |
| `obj.attr` | `AttributeError` | Largely excluded by PyCSL's type system today; revisit when class modeling expands. |
| typed operations | `TypeError` | Same — generally pre-excluded by type checking; flag any residual cases as Phase 3. |
| recursive call | `RecursionError` | Already partially addressed by SCC analysis; integrate as a no-bound annotation rather than per-call VC. |

**Phase 3 — explicitly out of scope**:

- `MemoryError`, `KeyboardInterrupt`, `SystemExit` — system-level, not contract-level.
- `OverflowError` — does not apply to native Python ints; only meaningful at the C boundary, which is handled by UB-#4 instead.

This table is the central artefact of the feature. It needs to live somewhere stable — a new skill file `pycsl-exception-model.skill` is the natural home, since it will be consulted by both the parser (to validate exception names) and the transpiler (to look up trigger conditions).

### 4. Implementation phases

Each phase is one PR. The reference corpus and the test additions from §5 are the gate.

#### Phase 1.1 — Parser support

Module 4 (or whichever module handles contract syntax — confirm against `pycsl-software-architecture` Section 1) gains:

- Recognition of `no_exception` as a contract directive.
- Parsing of the comma-separated exception name list, and the `\all` form.
- Validation: each named exception must be in the model (Phase 1 table above); unknown names produce a clear error.
- Rejection: `no_exception E` together with `raises { E -> _ }` produces a clear error.

Output in the IR: a new per-function field `no_exception_set: List[str]` or `no_exception_all: bool`.

#### Phase 1.2 — Exception model module

Create `src/pycsl/exception_model.py` (or equivalent). Contents:

- The Phase 1 table from §3 encoded as a Python data structure mapping `(ir_op_kind, ir_op_subkind)` to trigger predicates.
- A function `triggers(op_ir, ctx) -> List[(exception_name, whyml_predicate_str)]` that returns the assertions an operation needs in a given context.
- A small predicate vocabulary in WhyML — `predicate no_div_zero (b: int) = b <> 0`, `predicate in_bounds (a: array int) (i: int) = 0 <= i < length a`, etc. — emitted as part of the preamble when the function uses `no_exception`.

This module is **the single source of truth** for "what operation raises what". Adding a new exception to the model is one entry in one table.

#### Phase 1.3 — VC injection in the transpiler

In `module6_whyml/expressions.py` (post-refactor) or `Module6_WhyMLTranspiler.py` (pre-refactor):

- `_handle_binop` for `/`, `//`, `%` consults the exception model; if the enclosing function has `no_exception ZeroDivisionError` (or `\all`), emit `assert { no_div_zero <b> };` before the operation.
- `_handle_subscript`, `_handle_array_set_stmt` likewise for `IndexError`.
- `_handle_map_get_expr` likewise for `KeyError`.
- `_handle_call_expr` checks the dotted-call cases (`.pop`, `.index`).

The assertion is a WhyML `assert` (logical, not runtime). It produces a VC; the WP backend either discharges it from the precondition or reports a failure. This is the Frama-C RTE/EVA model applied to Python.

A single helper on the facade — `self._maybe_emit_no_exception_assert(op_ir, indent) -> str` — keeps the call sites uniform and concentrates the conditional logic.

#### Phase 1.4 — Inter-procedural propagation

A function `f` calling `g` inherits `g`'s implicit exceptions. The model:

- If `g` has `no_exception E` proved, its call site is safe with respect to E.
- If `g` has `raises { E -> _ }`, its call site may raise E — which is fine unless `f` has `no_exception E`.
- If `g` has neither, the conservative answer is "may raise E" — but for backward compatibility, the *initial* implementation treats unannotated functions as if they raise nothing implicitly. This matches the "ambient" tier from §2 and avoids forcing the whole corpus to be re-annotated.

A later refinement (Phase 1.5, optional) can tighten this: a flag `--strict-no-exception-propagation` makes unannotated callees pessimistic. Document the tradeoff; do not enable by default.

#### Phase 1.5 — `\all` form

`no_exception \all` expands to the union of all Phase 1 exceptions in the model. Implementation: a single boolean on the function context; each handler in Phase 1.3 checks `func_ctx.no_exception_all or E in func_ctx.no_exception_set`.

The `\all` form also requires the function's `raises { ... }` set to be empty for the proof step. The parser enforces this when both are present and they conflict.

### 5. Test plan for Part I

The corpus needs three example classes per exception:

- **Proves under no annotation** — `divide_256(n)` returning `256 / n`. Baseline; current behavior unchanged.
- **Fails under `no_exception E`** — the same body with the new annotation but no strengthened precondition. Verifies the VC actually fires.
- **Proves under `no_exception E` with strengthened precondition** — `requires n != 0`. Verifies the precondition discharges the VC.

Multiply by the Phase 1 exception list. About 30 small test files. Most can be derived mechanically from a template.

A second corpus set covers inter-procedural cases: `f` calls `g`, where `g` is variously annotated. About 10 files.

### 6. Skill updates for Part I

- `pycsl-software-architecture.skill` Section 4 (contracts vocabulary) gains a `no_exception` entry with the syntax and semantics.
- `pycsl-software-architecture.skill` Section 6 ("Adding a new CSL keyword") workflow needs a worked example for `no_exception` — it's the most realistic walkthrough you can give of the full pipeline.
- New skill file `pycsl-exception-model.skill` documents the Phase 1 table from §3 and the rules for extending it. This skill is consulted by future agents adding new exception models.
- Both changes are CCB-tracked per the existing skill baseline.

---

## Part II — Undefined Behavior detection

The five UB categories from the design discussion are heterogeneous in mechanism and in cost. Treating them as one feature would be a category error — they share only the verification stance ("flag this as a proof-blocking issue"), not the implementation.

### 7. Sub-feature inventory

| # | UB category | Mechanism | Implementation cost | Priority |
|---|---|---|---|---|
| 7.1 | Mutation during iteration | Dataflow/frame-condition analysis on `for` loops | Medium | High |
| 7.2 | `__hash__` / `__eq__` inconsistency | Class-level VC | Medium (depends on class modeling depth) | Medium |
| 7.3 | Concurrent access without synchronization | Race detection in the concurrent memory model | Medium–High (depends on existing concurrent infrastructure) | Medium |
| 7.4 | C extension boundary | Import-graph check | Low | High |
| 7.5 | `__del__` / finalizer | Syntactic class-definition check | Low | Low |

Priority is set by value-per-effort: 7.4 and 7.1 are the highest-payoff items. 7.5 is the lowest because `__del__` is rare in verification-grade code anyway.

### 7.1 Mutation during iteration

The check, in plain language: in `for x in C: <body>`, no statement in `<body>` (or in any function called from it, transitively) may mutate `C`.

Implementation:

- Reuse the existing IR-walker pattern from `IRScanner` (post-refactor: `module6_whyml/ir_scanner.py`).
- New static method `find_iteration_mutations(stmts) -> List[(loop_target, mutating_stmt)]`.
- "Mutating" means: `ArraySet` on the loop target, `Call(".append" / ".pop" / ".clear" / ".add" / ".remove" / ".discard" / ".update" / ".extend", ...)` with the loop target as receiver, or `del target[...]`.
- Transitive case (function called in the body mutates the loop target) requires a `writes` clause on called functions — PyCSL already has the machinery for frame conditions, so this is a matter of consulting it.
- Report as a hard verification error, not a warning — this is genuine UB.

Optional escape hatch: a `#@ allow_iteration_mutation` annotation on the loop (rare, e.g. for `for k in list(d):` patterns where the user has materialized a snapshot).

### 7.2 `__hash__` / `__eq__` inconsistency

The check: for any class `T` with both `__hash__` and `__eq__` defined, prove `forall a b: T. a = b -> hash(a) = hash(b)`.

This is a class-level VC, not a function-level one. It lives wherever class modeling lives (likely Module 5 or wherever records/classes are processed).

Implementation:

- Detect classes with both methods defined.
- Generate a fresh WhyML goal: `goal hash_eq_consistent_T: forall a b: T. eq_T a b = true -> hash_T a = hash_T b`.
- If `__eq__` is defined but `__hash__` is not, the class is unhashable in Python — using it as a set/dict key is a `TypeError`. Detect statically and either warn or use this as input to the `no_exception TypeError` proof.

Initial scope can be limited to PyCSL's existing record/class subset. Expanding to general user-defined classes is a larger investment.

### 7.3 Concurrent access without synchronization

This depends heavily on what's already in the concurrent memory model. From the prior architecture review, `_shared_var_names` and a `concurrent` memory model exist. The minimum useful check:

- Every read or write of a shared variable must be inside a `with lock:` (or `CriticalSection`) block, where `lock` protects that variable.
- Lock-to-variable association is declared somewhere — either an annotation `#@ guarded_by lock_name` on each shared variable, or convention (`shared_x` protected by `lock_x`).

This is a standard concurrent-program verification problem. If PyCSL's existing concurrent model already enforces this, the work here is just "surface violations more visibly" — review existing diagnostics first before designing new ones. If it does not, this is the largest item in Part II.

### 7.4 C extension boundary

The check: any call to code outside PyCSL's verifiable subset is treated as untrusted.

Implementation:

- The import-resolution pass (Module 1 or 2) already knows which modules are imported. Add a check: imports from `ctypes`, `numpy.ctypeslib`, `cffi`, `cython`-compiled extensions, or anything matching a configurable deny-list are flagged.
- Calls into such modules require an `#@ trusted` annotation at the call site; without it, the function containing the call cannot be verified.
- The `@trusted` annotation already exists for some auto-trust paths in Module 6 (the prior architecture review mentioned `_auto_trusted_array_returns` etc.) — extend the vocabulary rather than inventing a new mechanism.

This is the cheapest item in Part II and gives the most "soundness perimeter" coverage for the effort.

### 7.5 `__del__` and finalizer

The check: any class with `__del__` defined is rejected (or requires `#@ allow_finalizer` annotation, which makes any contract referring to lifetime invalid).

Implementation: one syntactic check at class-parsing time. Trivial.

This is low priority because `__del__` is rare in numerical/algorithmic code — the kind of code PyCSL targets. But it's also a one-PR job whenever someone has half a day.

### 8. Implementation phases for Part II

Each sub-feature is one PR. They are independent of each other and can be parallelized across maintainers. Order by priority:

| Step | Sub-feature | PR scope |
|---|---|---|
| II.1 | 7.4 — C extension boundary | Import deny-list + `@trusted` extension + corpus examples |
| II.2 | 7.5 — `__del__` rejection | Class-parser check + corpus examples |
| II.3 | 7.1 — Mutation during iteration | New `IRScanner` method + frame-condition consultation + corpus |
| II.4 | 7.2 — Hash/eq consistency | Class-level VC generation + corpus |
| II.5 | 7.3 — Concurrent races | Audit of existing concurrent model first; design after the audit |

Steps II.1 and II.2 should land first regardless of which other features are in flight — they are cheap, high-soundness wins. Steps II.3 and II.4 require design work and corpus development. Step II.5 is the only one whose scope cannot be estimated without more investigation.

### 9. Test plan for Part II

Each sub-feature gets:

- Two negative examples (the UB pattern in its most direct form, and a subtler version).
- One positive example (a near-miss that should still verify — e.g., for 7.1, a loop that mutates a *different* container).
- One escape-hatch example (the annotation is present, verification proceeds).

About 20 files total across the five sub-features.

### 10. Skill updates for Part II

- `pycsl-software-architecture.skill` Section 4: add the new annotations (`@trusted`, `@allow_finalizer`, `@allow_iteration_mutation`, `@guarded_by`).
- `pycsl-software-architecture.skill` Section 1: if any new module is created (e.g., for 7.4's import check), add it.
- New skill file `pycsl-ub-catalog.skill` documenting the five UB categories, the check mechanism for each, and the verification stance. This becomes the reference document for "what does PyCSL guarantee about Python UB" — useful for both agents and users.

---

## 11. Cross-cutting concerns

### 11.1 Corpus organization

Both features add substantial corpus content. Recommend `tests/corpus/no_exception/` and `tests/corpus/ub/<category>/` subdirectories from the start — flat layouts become unmanageable.

### 11.2 Diagnostic quality

Both features produce *new failure modes* that didn't exist before. The user-facing diagnostic must say:

- **Which annotation** triggered the proof obligation (`no_exception ZeroDivisionError`).
- **Which operation** produced the unproved obligation (line, column, expression).
- **Which precondition would discharge it** (the trigger condition, e.g., `n != 0`). This is the highest-value diagnostic — it tells the user exactly what to add to `requires`.

The diagnostic infrastructure may need extension; budget for this explicitly rather than discovering it during the corpus pass.

### 11.3 Backward compatibility

The default behavior of an unannotated function must not change. Today PyCSL proves `divide_256(n)` returning `256 / n` with no preconditions; tomorrow it must still prove it. The features are purely opt-in via annotations. Any deviation from this is a breaking change for existing users and should be a separate, well-flagged release.

### 11.4 Interaction with the Module 6 refactor

- The `no_exception` VC injection touches expression and statement handlers. After the refactor these live in `module6_whyml/expressions.py` and `module6_whyml/statements.py`. Before the refactor they live at lines ~938–1820 and ~2073–3157 of the monolith.
- The UB detectors mostly live *outside* Module 6 (in the import resolver, in class processing, in `IRScanner`). The refactor is therefore less of a prerequisite for Part II than for Part I.

Recommended sequencing across all three workstreams (the refactor plus the two new features):

1. Module 6 refactor steps 1–4 (zero-risk extractions: `ir_scanner.py`, `scc.py`, `identifiers.py`, `auto_trust.py`, `abstract_ops.py`).
2. Part II steps II.1 and II.2 (cheap UB wins).
3. Module 6 refactor steps 5–7 (the larger mixin splits, including `expressions.py` and `statements.py`).
4. Part I Phases 1.1–1.5 (no_exception, now sitting in the cleanly-split expression and statement modules).
5. Part II steps II.3, II.4, II.5 (the heavier UB analyses).
6. Optional Module 6 refactor steps 8–10.

This ordering keeps each PR's diff scoped to one moving part — the corpus is the only continuous regression signal.

---

## 12. Risk and anti-patterns

**Over-modeling exceptions.** It is tempting, having built the Phase 1 trigger model, to keep going: add `AttributeError` for every attribute access, `TypeError` for every dynamic dispatch, `OverflowError` everywhere. Resist this. The Phase 1 set is chosen for its clean mathematical triggers; the Phase 2 set requires more semantic modeling and should follow real demand, not speculative completeness. *YAGNI*.

**Coupling Part I and Part II.** They share a verification stance but nothing else mechanically. A single PR that "implements UB detection" by piggybacking on the `no_exception` infrastructure would entangle two designs and make both harder to evolve. Keep them separate.

**Inventing one big "safety" annotation.** A tempting consolidation is `#@ safe` meaning "no exceptions and no UB". This is the wrong abstraction — users care about specific failure modes (a database client doesn't want `IndexError` but is fine with `IOError`). Keep annotations granular.

**Skipping the inter-procedural propagation design.** Phase 1.4 is the conceptually hardest part of Part I and is easy to defer or hand-wave. Pin down the rule before writing Phase 1.3, or Phase 1.3's call-site handling will be incoherent.

**Treating the exception model as code rather than a contract.** The Phase 1 table from §3 is part of PyCSL's verification semantics — "what does PyCSL guarantee?" depends on it. It belongs in a skill file under change control, not buried in a Python data structure that gets edited without review. This is what the proposed `pycsl-exception-model.skill` is for.

**Letting diagnostics lag.** The whole value of `no_exception ZeroDivisionError` is that the user gets a precise message about why it didn't prove. A feature that says only "VC failed" is technically correct and practically useless. Diagnostic quality (§11.2) is a feature requirement, not a stretch goal.

---

## 13. Out of scope

The following are real but deliberately deferred:

- **Soundness for full Python**: classes with metaclasses, dynamic attribute creation via `setattr`, `eval`/`exec`, monkey-patching at runtime. PyCSL's verification target is a subset; this work expands the subset slightly but does not aim for "any Python program".
- **Performance of the verifier**: VC count grows with `no_exception` usage. Profile after the Phase 1 corpus lands; do not over-design indexing or caching up front.
- **`OverflowError` modeling**: Python `int` is unbounded, so this exception does not arise in pure-Python code. It would arise at the C extension boundary, which UB-7.4 handles by refusing to verify across that boundary in the first place.
- **`KeyboardInterrupt` / `SystemExit` / `MemoryError`**: system-level, not contract-level. No reasonable specification can prove their absence.
- **A full effects system**: tempting to generalize "this function may raise E" into a tracked effect, à la Koka or OCaml 5. Worth doing eventually; far out of scope for this plan.

---

## 14. Summary

Two features, one workplan, three workstreams running in coordination.

`no_exception` is mechanically the bigger feature but conceptually the simpler: extend the contract vocabulary, build an exception-trigger model, inject WhyML assertions at the corresponding IR operations, and propagate the obligation through call sites. The Phase 1 table from §3 is the single source of truth and the central artefact.

UB detection is conceptually the bigger feature but mechanically a bundle of five small ones. The cheap-and-cheerful items (7.4, 7.5) should land first as low-effort soundness wins. The dataflow item (7.1) is medium effort and high value. The class-level item (7.2) and the concurrent item (7.3) follow once the class-modeling and concurrent-model coverage are audited.

The interaction with the Module 6 refactor is real but manageable: refactor steps 1–7 first, then Part I, with Part II's cheap items interleaved. The corpus is the gate at every step. The architecture skill is updated in lockstep with each PR.

The governing principle, same as the refactor plan: ship the cheap wins first, gate every step on the corpus, do not combine mechanical work with design work in a single PR.
