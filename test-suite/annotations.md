# PyCSL Annotation Reference

This document normalizes the complete PyCSL contract annotation language
as implemented in the codebase (Module2_Parser EBNF grammar + Module5/6
transpilation). It is the authoritative source for writing test cases.

---

## 1. Annotation Syntax

All annotations are single-line Python comments starting with `#@`:

```python
#@ <directive> <expression>
```

Annotations must appear on the **leading lines** immediately before the
Python construct they annotate (function, class, loop, or statement).

---

## 2. Directives

### 2.1 Function/Method Contracts

| # | Directive | Syntax | Scope | Semantics |
|---|---|---|---|---|
| 1 | Precondition | `#@ requires <expr>` | Function/method | Must hold at entry |
| 2 | Postcondition | `#@ ensures <expr>` | Function/method | Must hold at exit |
| 3 | Frame condition | `#@ assigns <targets>` | Function/method | Only listed targets may be mutated |
| 4 | Function variant | `#@ \variant <expr>` | Function/method | Termination measure for recursive functions (must decrease, stay ≥ 0) |
| 5 | Structural variant | `#@ \variant (<expr>, <ordering>)` | Function/method | Termination via well-founded ordering |
| 6 | Diverges | `#@ \diverges` | Function/method | Function may not terminate (no termination proof required) |
| 7 | Trusted | `#@ \trusted` or `#@ \trusted reviewer: <REVIEWER_ID>` | Function/method | Body is not verified; contracts are assumed (axiom). The optional `reviewer:` clause names a human or process accountable for the trust assumption. See §2.1.7 below. |
| 8 | Bounded integers | `#@ assumes bounded_int(N)` | Function/method | Use `mach.int.IntN` types; auto-generates overflow VCs on `+`, `-`, `*` |
| 9 | Raises | `#@ raises ExcType when <cond>` | Function/method | Exceptional postcondition: exception raised only when `cond` holds |
| 10 | Thread entry | `#@ thread_entry` | Function/method | Marks function as a concurrent thread entry point; used with `--memory-model concurrent` |
| 11 | _(reserved — `proof` directive removed 2026-05-27)_ | | | |
| 12 | Axiom from proof | `#@ proof <rocq\|lean> <qualname>` | Module-level | Imports a Rocq or Lean theorem as a Why3 axiom in the preamble. When both `rocq` and `lean` directives name the same `pycsl_target`, the `proof2why3 cross-check` tool verifies their canonical forms agree before emission ("Rocq + Lean as Cross-Validated Spec Sources"). See §2.1.12 below. |
| 13 | No-exception | `#@ no_exception E1, E2, ...` or `#@ no_exception \all` | Function/method | Implicit Python exceptions become proof obligations. For each IR operation in the body that could raise a listed exception, Module 6 emits a WhyML `assert { trigger }`. The `\all` form expands to the full Phase 1 set in `exception_model.KNOWN_EXCEPTIONS` and requires `raises { }` to be empty. See §2.1.13. |
| 14 | Abstract | `#@ \abstract` | Function/method | Function is emitted as a **bodyless** WhyML `val` defined SOLELY by its contract (+ any `#@ proof` axioms). Unlike `\trusted` (a present-but-unchecked body), `\abstract` asserts there is no meaningful body — the contract IS the definition. Sound (uninterpreted `val`). Does **not** count as `\trusted`; the canonical 0-`\trusted` model for irreducibly-opaque ops (e.g. `ast.literal_eval`). See §2.1.14 below. |
| 15 | Guarded case | `#@ act <name>:` (with a 4-space-indented body of `#@ given` / `#@ requires` / `#@ ensures`) | Function/method | A named case guarded by its `given`. Desugars to ordinary `ensures \old(<given>) ==> <post>` / `requires <given> ==> <pre>` (no new IR node, 0 `\trusted`). See §2.1.15 below. |
| 16 | Case guard | `#@ given <expr>` | Inside an `act` | The case's pre-state guard (ACSL's `assumes`); only valid inside an `act` block. `\result` is not allowed here. |
| 17 | Complete cases | `#@ complete <name>, ...` | Function/method | Proof obligation that the named acts' guards cover every input — `ensures \old(g1) \|\| ... \|\| \old(gn)`. |
| 18 | Disjoint cases | `#@ disjoint <name>, ...` | Function/method | Proof obligation that at most one guard holds — per pair `ensures not(\old(gi) && \old(gj))`. |

Multiple `requires`/`ensures` lines are conjuncted (all must hold).

#### §2.1.7 Trusted (`\trusted [reviewer: <REVIEWER_ID>]`)

```python
#@ \trusted
def opaque_helper(x: int) -> int: ...

#@ \trusted reviewer: alice
def reviewed_helper(x: int) -> int: ...

#@ \trusted reviewer: pycsl-self-annotate
def auto_stubbed_helper(x: int) -> int: ...
```

Marks the function's **body as not verified** by PyCSL. Module 6
emits `val f (...) : R requires {...} ensures {...}` (signature +
contract only, no body); the contracts become axioms that callers
may freely assume.

**Optional `reviewer:` clause.** Grammar (§2.1.7 of the
concrete-syntax reference):

```
trusted_decl ::= "\trusted" ( "reviewer" ":" REVIEWER_ID )? ;
REVIEWER_ID  ::= /[A-Za-z0-9._@-]+/
```

The reviewer field is **accountability metadata**, not a
verification primitive. It documents *who* (or *what*) stands
behind the trust assumption since PyCSL itself does not verify the
body. The translational layer ignores it (§T.2.6 of the
translational reference): the WhyML output is identical whether
the clause is present or absent.

**Behaviour without `reviewer:`.** Parsing succeeds.
`Module3_Weaver._dispatch_function_contracts` emits a warning at
weave time:

> *"`\trusted` has no reviewer — add `reviewer: <name>` to document
> who is accountable for this trust assumption."*

The warning is informational; the file still compiles and proves.
Project convention treats an anonymous `\trusted` as a review
blocker — CI and PR review pipelines may promote the warning to an
error in stricter modes.

**Reviewer tag convention.** Two well-known categories:

- **Human identifier** — name, handle, or scoped identifier
  (`alice`, `charlie-mhe@example.org`). Use when a person reviewed
  the function and attests that the contract holds of the body.
- **Process identifier** — name of an automated tool or rule that
  emitted the directive. Use when a generator produces the
  `\trusted` and the trust delegates to that tool's documented
  rules. Known process tags:
  - `pycsl-self-annotate` — emitted by `bin/self-annotate-stub-gen.py`
    for mirror files under `src/self-annotate/src/`. See
    `src/self-annotate/coverage-report.md` and the
    `pycsl-stdlib-coverage` skill's growth criteria.
  - `auto-trust-<rule>` — reserved for future auto-trust rule
    families (e.g., `auto-trust-array-return` per
    `module6_whyml/auto_trust.py`'s `_should_auto_trust_*`
    predicates).

A directive whose reviewer tag matches no known pattern is still
syntactically valid; tooling reading the field should treat unknown
tags as opaque human-or-process identifiers.

**No new error codes.** The reviewer field has no semantic check at
Module 4 and no WhyML emission at Module 6. The static-semantics
reference §2.1.7 records the warning behaviour; the translational
reference §T.2.6 records the no-emission rule.

**Test-corpus cross-reference:** `0052`, `0160`, `0161` exercise
the bare `\trusted` form;
`test-suite/corpus/pycsl-reference/0397.py` exercises the
`reviewer:` clause via the UB-7.4 escape-annotation flow.

#### §2.1.12 Proof Citation (`proof`) — Rocq + Lean as Cross-Validated Spec Sources

```python
#@ proof rocq Pycsl.Reference.Gcd.gcd_divides_a
#@ proof lean Pycsl.Reference.Gcd.gcd_divides_a
```

Imports a Rocq or Lean theorem as a **Why3 axiom** in the generated WhyML
preamble. `#@ proof` has real semantic effect: Alt-Ergo/Z3 may use
the imported axiom to discharge obligations that SMT alone cannot handle.

**Cross-validation.** When both a `rocq` and a `lean` directive reference
the same `pycsl_target` name, the `proof2why3 cross-check` tool
extracts both theorem statements, converts them to a canonical IR form
(alpha-normalized, AC-flattened, `nat`/`Nat` → `int + ≥ 0`), and verifies
equality. This is the **"Rocq + Lean as Cross-Validated Spec Sources"**
pattern: two independent proof assistants must agree on the specification
before it enters the Why3 verification.

**Scope:** Module-level (placed before any function definition).

**Audit (`pycsl --audit-proof`).** The dotted `qualname` is enforced
as a namespace path: the cited theorem must be declared inside the
matching `Module`/`namespace` nesting in the proof file. Default proof
dirs are `<file>.proofs/{rocq,lean}/`; override with
`--rocq-proofs-path` / `--lean-proofs-path`. The audit can target only
one prover via `--audit-proof-rocq` / `--audit-proof-lean`. Exit 0 on
all PASS, 1 on any FAIL.

```bash
pycsl --audit-proof  myfile.py
pycsl --audit-proof-rocq myfile.py
pycsl --audit-proof-lean --lean-proofs-path /tmp/alt-lean myfile.py
```

**WhyML emission:** `Module6_WhyMLTranspiler` calls `proof2why3 emit` for
each `proof` directive, producing an `axiom pycsl_axiom_<target> : …`
block in the preamble.

**Cross-check statuses:**

| Status | Meaning |
|---|---|
| `reconciled` | Both Rocq and Lean present, canonical forms equal |
| `rocq-only` | Only Rocq statement found (warning emitted) |
| `lean-only` | Only Lean statement found (warning emitted) |
| `disagreement` | Both present but canonical forms differ (**pipeline halts**) |

**Worked example:** `test-suite/corpus/pycsl-reference/0342.py` (Euclidean
GCD) with proofs under `0342.proofs/{rocq,lean}/`.

#### §2.1.13 No-exception (`no_exception`)

```python
#@ no_exception ZeroDivisionError
#@ no_exception ZeroDivisionError, IndexError
#@ no_exception \all
```

A function-level directive turning **implicit** Python exceptions into
proof obligations. For each IR operation in the body whose shape could
raise a listed exception, Module 6 emits a WhyML `assert { trigger }`
immediately before the operation; the trigger predicate is looked up in
`src/pycsl/exception_model.py`.

**When to use.** Whenever the function must provably not escape via the
listed exception(s) — e.g. division helpers that must reject zero
divisors, array helpers that must respect bounds. The default behaviour
of an unannotated function is unchanged: implicit exceptions are not
proof-blocking.

**When NOT to use.** To bypass a `no_exception` proof failure with
`\trusted` — strengthen the precondition instead. The whole value of
`no_exception` is that a failed VC tells the user exactly which
precondition would discharge it.

**Conflicts.** `no_exception E` and `raises { E -> _ }` for the same `E`
on the same function are mutually contradictory and rejected by Module 4.
The `\all` form additionally requires `raises { }` to be empty.

**Known exceptions (Phase 1):** `ZeroDivisionError`, `IndexError`,
`KeyError`, `ValueError`, `StopIteration`. The authoritative set lives
in `exception_model.KNOWN_EXCEPTIONS`. Adding a new exception requires
extending both that set and the trigger table in the same module, plus
adding corpus tests under `test-suite/corpus/pycsl-reference/`.

**Test-corpus cross-reference:** parser tests are `0353`–`0357`; VC
injection tests are `0359`–`0395` (broken out by exception category in
the corpus numbering reservation under `traceability-pycsl.md`).

#### §2.1.14 Abstract (`\abstract`)

```python
#@ \abstract
#@ raises ValueError when True
#@ raises SyntaxError when True
def literal_eval(node_or_string: int) -> int: ...
```

Marks the function as **defined by its contract alone**. Module 6 emits
`val f (...) : R requires {...} ensures {...} raises {...}` — a signature
and spec with **no body** — exactly the WhyML shape of a `\trusted` stub.

Grammar (§2.1.14 of the concrete-syntax reference):

```
abstract_decl ::= "\abstract" ;
```

**`\abstract` vs `\trusted`.** Both emit a bodyless `val`, but the
provenance differs and the distinction is enforced by policy:

- `\trusted` — there *is* a Python body, and PyCSL is *trusting it
  unchecked*. Counts as trust; `bin/check-no-trusted-stubs.py` forbids it
  on `src/pycsl_lib/**` stubs.
- `\abstract` — there is *no meaningful body to check*; the contract (and
  any `#@ proof` axioms) IS the definition. Sound: an uninterpreted `val`
  constrains callers only through its spec. Does **not** count as
  `\trusted` and passes the stub lint.

Use `\abstract` for irreducibly-opaque operations — e.g. `ast.literal_eval`
(which IS Python's parser): its parsed value is uninterpreted, but its
bounded raises set (`ValueError`/`SyntaxError`, never code execution) is
the spec, so a `try/except` wrapper around it is provably total (corpus
`0449`). This is the 0-`\trusted` idiom: *"0 trusted ≠ 0 abstraction"* —
the opaque boundary is an explicit, auditable `val` spec rather than an
invisible unchecked body.

#### §2.1.15 Guarded cases (`act` / `given` / `complete` / `disjoint`)

A named, guarded contract case (ACSL "behavior"). Written as a Python-style
block: `#@ act <name>:` followed by a **4-space-indented** body of
`#@ given` / `#@ requires` / `#@ ensures` lines (strict — a misindented or
tab-indented body line is a hard error).

```python
#@ act neg:
#@     given x < 0
#@     ensures \result == 0 - x
#@ act pos:
#@     given x >= 0
#@     ensures \result == x
#@ complete neg, pos
#@ disjoint neg, pos
def myabs(x: int) -> int:
    if x < 0:
        return 0 - x
    return x
```

**Desugaring** (Module 3 — no new IR node, 0 `\trusted`): for an act with guard
`A` (the conjunction of its `#@ given` clauses), each `#@ ensures E` becomes
`ensures \old(A) ==> E` and each `#@ requires R` becomes `requires A ==> R`.
The guard is read in the **pre-state** (hence `\old`); `\result` is therefore
not allowed in a `given`. `#@ complete c1, ...` and `#@ disjoint c1, ...` become
**function-entry `#@ assert`** obligations — `assert g1 || ...` and per-pair
`assert not(gi && gj)`. At entry the state is the pre-state (no `\old` needed) and
the preconditions are hypotheses, so they discharge `Pre ⟹ ⋁gᵢ` / pairwise
disjointness **on all paths** (a gap/overlap fails the proof). A failed
case-postcondition is tagged `(* act <name> *)` in the emitted WhyML for traceability.

(The earlier draft lowered `complete`/`disjoint` to `ensures \old(…)`, which was
checked on normal return only — vacuous on `raise` paths. The function-entry assert
form removes that limitation.)

### 2.2 Loop Contracts

| # | Directive | Syntax | Scope | Semantics |
|---|---|---|---|---|
| 1 | Loop invariant | `#@ loop invariant <expr>` | `while`/`for` | Inductive property preserved each iteration |
| 2 | Loop variant | `#@ loop variant <expr>` | `while`/`for` | Termination measure (must decrease, stay ≥ 0) |
| 3 | Allow iteration mutation | `#@ allow_iteration_mutation` | `for` loop | Opts the loop out of UB-7.1 (mutation during iteration). See §2.2.3. |

#### §2.2.3 Allow iteration mutation (`allow_iteration_mutation`)

```python
#@ allow_iteration_mutation
for x in arr:
    arr.append(x + 1)
    return
```

Placed immediately before a `for` statement (alongside `loop
invariant` / `loop variant`). Disables the UB-7.1 check
(`IRScanner.find_iteration_mutations`) for that one loop, so the
body may mutate the iterated collection via `arr.append(...)`,
`arr.pop(...)`, `arr[i] = v`, `del arr[i]`, and the rest of the
mutating-method set (`clear`, `add`, `remove`, `discard`, `update`,
`extend`, `insert`, `setdefault`).

**Scope:** per-loop, not per-function. Nested loops inside a blessed
loop are still checked.

**When to use.** The canonical case is the snapshot pattern
(`for k in list(d): del d[k]`) — the iterator is over a freshly
materialized list, not the dict being mutated. Use the annotation
when you cannot or will not rewrite to the snapshot form. The
annotation documents the assumption; it does not make the mutation
safer.

**When NOT to use.** As a blanket suppression of the check. The hard
reject exists because iterator-state corruption is genuine UB in
CPython, not a verification quirk.

**Test-corpus cross-reference:** `0404` (append fails without the
annotation), `0405` (pop fails), `0406` (mutating a different
container — no annotation needed), `0407` (`allow_iteration_mutation`
opt-in proves).

### 2.3 Class Contracts

| # | Directive | Syntax | Scope | Semantics |
|---|---|---|---|---|
| 1 | Class invariant | `#@ class invariant <expr>` | `class` | Must hold at every method boundary |
| 2 | Allow finalizer | `#@ allow_finalizer` | `class` | Opts the class out of UB-7.5 (`__del__` rejection). See §2.3.2. |

Placed on leading lines **before** the `class` keyword.

#### §2.3.2 Allow finalizer (`allow_finalizer`)

```python
""  # pycsl
#@ class invariant self._n >= 0
#@ allow_finalizer
class WithFinalizer:
    def __init__(self) -> None:
        self._n: int = 0

    def __del__(self) -> None:
        self._n = 0
```

Placed immediately before the `class` keyword (in any order
relative to `class invariant` lines). Disables the UB-7.5 check in
`Module3_Weaver.visit_ClassDef`, which otherwise rejects any class
body containing a `def __del__` with `PyCSLSemanticError`.

**Scope:** per-class. The annotation does not propagate to other
classes in the same file.

**When to use.** When the class genuinely needs a finalizer (rare in
verification-grade code). The rest of the class can still be
verified — the annotation just documents that lifetime-dependent
contracts are not modelled in WhyML.

**When NOT to use.** As a workaround for not knowing whether a
finalizer is needed. CPython's GC may invoke `__del__` at any time
between unreachability and interpreter shutdown — and may skip it
entirely under shutdown. Any contract that references when the
finalizer runs is at risk regardless of this annotation.

**Test-corpus cross-reference:** `0401` (class with `__del__` is
rejected without the annotation), `0402` (`allow_finalizer` opt-in
accepts the class), `0403` (baseline: class without `__del__`
unaffected by the check).

### 2.4 Program Point Annotations

| # | Directive | Syntax | Scope | Semantics |
|---|---|---|---|---|
| 1 | Label | `#@ label <NAME>` | Statement | Marks a program point for `\at` references |
| 2 | Ghost assign | `#@ ghost <name> = <expr>` | Statement | Declare or assign a ghost variable (first occurrence declares) |
| 3 | Ghost augmented assign | `#@ ghost <name> += <expr>` | Statement | Augmented assignment to ghost variable (`+=`, `-=`, `*=`) |
| 4 | Critical section | `#@ critical <mutex>` | `with` statement | Declares the `with lock:` block as a critical section for `<mutex>`; triggers havoc+assume+assert in WhyML |
| 5 | Acquires | `#@ acquires <mutex>` | `with` statement | Explicit mutex acquire annotation (equivalent to `critical`; use when naming the acquire point explicitly) |
| 6 | Releases | `#@ releases <mutex>` | `with` statement | Explicit mutex release annotation (marks the release point; informational in current WhyML output) |
| 7 | Assert | `#@ assert <expr>` | Statement | Prove `<expr>` at this point **and assume it downstream** (prove-and-assume). A real proof obligation — **distinct from the Python `assert` statement**, which the prover ignores. Attaches to the following statement (like `#@ label`). `\result` is not allowed (it's bound only at return). |
| 8 | Check | `#@ check <expr>` | Statement | Prove `<expr>` at this point but **do not** assume it downstream (prove-and-discard). Otherwise as `#@ assert`. |

Ghost variables exist only in the verification model (erased at extraction).
They can be referenced in `loop invariant`, `requires`, `ensures`, and `\variant` expressions.
The `#@ ghost` directive must appear on a leading line before a Python statement.

---

### 2.5 Module-level meta-properties (HAPPY)

A **HAPPY** (High-level Assertion-Producing PYthon requirement) is one *module-level*
declaration of a cross-cutting region-integrity property over a shared instance field;
the compiler expands it into a per-site `#@ check` (§2.4) at every write of that field in
every method except an allowlisted set. One declaration replaces a disjoint-region
obligation otherwise hand-copied into every write site. (PyCSL's analogue of
MetAcsl/Frama-C HILARE high-level requirements; see `meta.md`.)

Written as a Python-style block (like `act`, §2.1.15): `#@ happy <name>:` followed by a
**4-space-indented** body:

```
#@ happy region_integrity:
#@     region 512 .. 2560
#@     writes self.disk outside region
#@     except _write_inode, _write_directory
```

| # | Directive | Syntax | Scope | Semantics |
|---|---|---|---|---|
| 1 | HAPPY | `#@ happy <name>:` block (`region LO .. HI` / `writes self.<field> outside region` / optional `except m1, m2, …`) | Module-level | Every write `self.<field>[i] = …` (point, slice, or augmented) in any method **not** in the `except` set must lie outside `[LO, HI)`. Expands to a per-site `#@ check ({i}) < LO or ({i}) >= HI` (slice `[a:b]`: `b <= LO or a >= HI`). |
| 2 | Preserves | `#@ \preserves` | Function/method | Opts a `\trusted`/`\abstract` (bodyless) method into the HAPPY trust boundary. The meta-pass synthesizes and attaches `ensures \forall i; (LO <= i and i < HI) ==> self.<field>[i] == \old(self.<field>[i])` (assumed at the boundary). A non-exempt `\trusted`/`\abstract` method **without** `#@ \preserves` is a hard error. |

**Expansion & soundness.** The obligation is injected at the *actual location written*, so it
needs no alias analysis (value-semantic arrays bar a local alias from mutating the shared
field) and no caller reasoning (an indirect write through a callee is caught at the callee's
own site — *universal coverage*, not the call graph, is load-bearing). A `\writing` HAPPY
emits `#@ check` (a single write's legality is not a reusable downstream fact). Each injected
check carries an `origin` comment naming the HAPPY and the offending site, so a failure points
to both. Per-method `requires`/`ensures` are unaffected.

**Validation.** Each `except` name must be a real method (a typo would silently widen coverage
— hard error); a HAPPY whose field is never written warns (inert). See `meta.md` for the
composition theorem (universal body coverage + the `\preserves` trust boundary ⟹ no execution
writes the region).

### 2.6 Module-level datatype declaration (`#@ datatype`)

Declares a **sum type** (algebraic data type) as a real Why3 `type`, placed at module level
(before the functions that use it). Constructors are either nullary or carry typed payloads:

```python
#@ datatype Color = Red | Green | Blue
#@ datatype Box = Some(int) | Pair(int, int) | Empty
```

| # | Directive | Syntax | Scope | Semantics |
|---|---|---|---|---|
| 1 | Datatype | `#@ datatype <Name> = <Ctor> [\| <Ctor> ...]` where each `<Ctor>` is a bare name (nullary) or `Name(T1, …)` (typed payload) | Module-level | Emits a Why3 `type <name> = Red \| Some int \| Pair int int \| …`. Payload types map `int`/`bool`→`int`, `str`→`string`, `float`→`real`. |

**Use sites.** Construct with the call form — `o = Some(7)` (a typed variant local) or a nullary
`o = Red`. Consume with a `match`/`case` whose arms are constructor patterns (§7.4) — the lowering
is a real Why3 `match` with **solver-checked exhaustiveness**, and `case Pair(a, b):` binds the
payloads. A param or local typed by the datatype is the variant type (`τ(D) = variant`, see the
static-semantics reference §1.4).

**Now supported (no-more-int Part 5–7).** Most of the former out-of-scope list is implemented:
- **Recursive datatypes** — single self-recursive (`Tree = Leaf | Node(Tree, Tree)`) and
  *mutually*-recursive groups (`Tree`↔`Forest`, emitted as one Why3 `type a = … with b = …` block),
  with `#@ \variant` termination for recursive functions over them.
- **Parametric datatypes** — `#@ datatype Option[T] = Nothing | Just(T)`, instantiated per use
  (`Just(7)` is `option int`, `Just(s)` is `option string` in the same program).
- **Guarded / nested / or-patterns** — `case Some(n) if n > 0`, `case Wrap(A(n))`,
  `case Red() | Green()` (incl. a payload bound identically across alternatives,
  `case Some(n) | Wrapped(n)`).
- **Captures referenced in contracts** — the constructor projectors `\is_ctor(x, Ctor)` and
  `\payload(x, Ctor[, i])` (§3 Expression Language) let a function-level `ensures` name a payload
  without a match.

**Still out of scope:** in-place mutation of a variant field (Why3 records are by-value — the
value-semantics boundary, `docs/pycsl-ownership-discipline.md`). `\payload` over a *type-parameter*
payload (e.g. `Option[T]`'s `Just`) needs use-site parametric instantiation — a documented follow-on.
See the `pycsl-annotate` SKILL §3f.

### 2.7 Mixin Composition (Tier 1)

Makes Python mixin composition **machine-checkable**: a `#@ mixin` class declares the methods it
`provides`, the sibling methods it `depends_method`/`requires_method` on, and the facade state it
`shared_state`/`touches_field`. A `#@ compose_from` class then composes several mixins, and Module 4
checks the composition is sound (every dependency has exactly one provider, no silent method
collision, every `self.<field>` write is declared) before flattening the providers into the
composer's record.

| # | Directive | Syntax | Scope | Semantics |
|---|---|---|---|---|
| 1 | Mixin | `#@ mixin` | `class` | Marks the class as a composable mixin (not instantiated directly). See §2.7.1. |
| 2 | Provides | `#@ provides <m>` | method | Declares the method `<m>` is a provider satisfying a sibling's dependency. |
| 3 | Shared state | `#@ shared_state <name>: <type>` | method | Declares `<name>` as **deliberately shared** facade state (multiple mixins may read/write it — not a conflict). D1. |
| 4 | Touches field | `#@ touches_field <name>: <type>` | method | Declares `<name>` as an **owned** field the method may touch (at most one owner; two owners → conflict, Tier 2). D1. |
| 5 | Depends method | `#@ depends_method <m>: <sig>` (+ indented `#@ ensures`) | method | A **concrete** dependency on a sibling/core method `<m>`; the provider's contract must refine the declared one. D2. |
| 6 | Requires method | `#@ requires_method <m>: <sig>` (+ indented `#@ ensures`) | method | An **abstract** operation the composing class must supply (verified once against an abstract `val`). D2. |
| 7 | Compose from | `#@ compose_from <M1>, <M2>, …` | `class` | Composes the named mixins: unique-provider + field-classification check, then flatten. |

Placed on leading lines before the `class`/`def` keyword, as with the other class/method directives.

#### §2.7.1 Worked example (the flagship)

```python
#@ mixin
class CoreEmit:
    #@ shared_state program_ir: int
    #@ provides emit
    #@ ensures \result >= 0
    #@ assigns \nothing
    def emit(self, x: int) -> int:
        return x if x >= 0 else 0

#@ mixin
class MapOps:
    #@ depends_method emit: (self, x: int) -> int
    #@   ensures \result >= 0
    #@ provides handle_get
    #@ ensures \result >= 0
    #@ assigns \nothing
    def handle_get(self, k: int) -> int:
        return self.emit(k)

#@ compose_from CoreEmit, MapOps
class Facade:
    #@ ensures \result >= 0
    #@ assigns \nothing
    def run(self, k: int) -> int:
        return self.handle_get(k)
```

Each `#@ mixin` is verified **once** in isolation against its `depends_method`/`requires_method`
interface (emitted as an abstract `val`); on `#@ compose_from`, Module 4 checks (a) every dependency
has **exactly one** provider, (b) no method has two providers (a silent collision), and (c) every
`self.<field>` a mixin method writes is declared `shared_state`/`touches_field` or initialised in
`__init__`. It then flattens the providers into the composer so `self.<m>(…)` resolves end-to-end.

**Determinism/purity (D3).** A dependency that must be referentially transparent is expressed with the
existing `#@ assigns \nothing` (which the RT inference in `module5/memoization_rt.py` already treats as
pure) — there is no separate `deterministic`/`pure` directive in Tier 1.

**Out of scope (boundaries, documented not faked).** The real facade dispatches handlers dynamically
via `getattr(self, _EXPR_DISPATCH[t])` / `_STMT_HANDLERS[s]`; Tier 1 verifies the mixin **algebra**
over *statically-named* providers and scopes that dynamic dispatch **out** (a separate coverage
obligation — see the static-semantics reference). Two-provider conflict resolution (a Tier-2 `resolve`
directive) and diamonds/general variance (Tier 3) are gated on a real driver.

**Test-corpus cross-reference:** `0549` (flagship composes + proves end-to-end), `0550` (missing
provider — rejected), `0551` (undeclared `self.<field>` write — rejected), `0552` (two providers of
the same method — rejected), `0553` (verify-once: a mixin method proves against an abstract
dependency).

---

## 3. Expression Language

### 3.1 Atoms

| # | Syntax | AST Node | Meaning |
|---|---|---|---|
| 1 | `42`, `-1`, `0` | `Number` | Integer literal |
| 2 | `x`, `n`, `total` | `Var` | Variable reference |
| 3 | `self.field` | `FieldAccess` | Class field access |
| 3b | `self.field[i]` | `FieldSubscript` | Element of an instance ARRAY field (e.g. for region-preservation: `self.disk[i] == \old(self.disk[i])`). Lowers to a subscript of the record field in the hoare model. |
| 4 | `arr[i]` | `SubscriptAccess` | Array element access |
| 5 | `\result` | `Result` | Return value (only in `ensures`) |
| 6 | `\old(<expr>)` | `Old` | Value of expression at function entry |
| 7 | `\at(<expr>, L)` | `At` | Value of expression at label `L` |
| 8 | `\length(arr)` | `ArrayLength` | Length of array `arr` |
| 9 | `\valid(arr, n)` | `Valid` | `arr[0..n)` is allocated |
| 10 | `\separated(a, na, b, nb)` | `Separated` | Regions `a[0..na)` and `b[0..nb)` don't overlap |
| 11 | `\length2d(a, m, n)` | `Length2D` | `a` has `m` rows each of length `n` |
| 12 | `\valid2d(a, i, j)` | `Valid2D` | `(i,j)` is a valid 2D index |
| 13 | `\nothing` | `Nothing` | Empty assigns target (pure function) |
| 14 | `"hello"` | `StringLiteral` | String literal (uses Why3 `string.String`) |
| 15 | `\is_sorted(arr, lo, hi)` | `IsSorted` | `arr[lo..hi)` is sorted ascending (pairwise adjacent) |
| 16 | `\sum(arr, lo, hi)` | `Sum` | Sum of `arr[lo..hi)` elements |
| 17 | `f(x, y)` | `CallExpr` | Pure function call in contract (see 4.1) |
| 18 | `True`, `False` | `CSLBool` | Boolean literal (`true` / `false` in WhyML). **Recommended** form for vacuous preconditions / postconditions (use `True` instead of the older `1 == 1` idiom). `False` is useful as a placeholder for intentionally-unprovable postconditions during incremental annotation. |
| 19 | `None` | `CSLNone` | None literal (maps to `0` in WhyML) |
| 20 | `arr[lo:hi]` | `CSLSlice` | Array slice (abstract `array_slice` function in WhyML) |
| 21 | `\permutation(a, b)` | `Permutation` | `a` is a permutation of `b`. Lowers to an **uninterpreted** `predicate permut` (not unfolded — permutation isn't first-order); constrained by a proof-assistant-imported axiom (`#@ proof`, §2.1.12). See `docs/framing-lemma-demonstration.md`. |
| 22 | `\is_ctor(x, Ctor)` | `CtorTest` | Datatype discriminator: true iff `x` was built with constructor `Ctor`. Lowers to `match x with Ctor _ … -> true \| _ -> false`. |
| 23 | `\payload(x, Ctor[, i])` | `CtorPayload` | Datatype projector: the i-th payload of `x` viewed as `Ctor` (`i` defaults to 0). Lowers to `match x with Ctor … z … -> z \| _ -> <typed default>`. Lets a contract name a `match` capture without a match (§2.6). |

### 3.2 Operators (by precedence, lowest first)

| # | Precedence | Operators | AST | Python equivalent |
|---|---|---|---|---|
| 1 | 1 (lowest) | `\forall var; body`, `\exists var; body` | `Forall`, `Exists` | Quantifiers (no direct equivalent) |
| 2 | 2 | `==>` (implies), `<==>` (iff) | `BinOp` | `not a or b`, `a == b` |
| 3 | 3 | `or` | `BinOp` | `or` |
| 4 | 4 | `and` | `BinOp` | `and` |
| 5 | 5 | `==`, `!=` | `BinOp` | `==`, `!=` |
| 6 | 6 | `<`, `>`, `<=`, `>=` | `BinOp` | same |
| 6b | 6.5 | `in`, `not in` | `CSLIn`, `CSLNotIn` | membership test (desugared to `∃` quantifier) |
| 7 | 7 | `+`, `-` | `BinOp` | same |
| 8 | 8 | `*`, `//`, `/`, `%` | `BinOp` | `//` and `/` → WhyML `div`; `%` → WhyML `mod` |
| 9 | 9 (highest) | `not`, unary `-`, unary `+` | `UnaryOp` | same |

**Note:** `/` in contracts maps to WhyML `div` (Euclidean integer division),
not Python's float division.

**Division-by-zero guards:** When `//` or `%` appear in **program code**
(not in contracts), PyCSL wraps them in helper functions `pycsl_div` /
`pycsl_mod` that carry a `requires { y <> 0 }` precondition. This
generates an automatic division-by-zero proof obligation at each call
site. In contracts (requires/ensures/invariants), bare `div` / `mod`
are used (logic context, no VC needed).

### 3.3 Quantifiers

```python
#@ requires \forall i; 0 <= i and i < n ==> arr[i] >= 0
#@ ensures \exists j; 0 <= j and j < n and arr[j] == target
#@ ensures \forall c: Color; rank(c) >= 0          # typed binder (quantification.md P1)
```

- An **untyped** bound variable (`\forall i; …`) is typed `int` in WhyML output (the
  legacy form, unchanged).
- A **typed** binder `\forall x: T; …` (quantification.md P1) ranges over a scalar
  (`int`/`bool`/`str`/`float`) or a declared `#@ datatype` / class, lowering to
  `forall x : t.`. An unresolved binder type is a hard Module-4 error — never a silent
  `int` default. A datatype binder may appear only in equality and pure observers
  (`\is_ctor`/`\payload` and `assigns \nothing` functions), not arithmetic.
- Body extends greedily to the end of the expression.
- Quantifiers can appear at top level or as RHS of `==>`, `and`, `or`.
- `\exist` (singular) is an accepted alias for `\exists`.
- Quantifiers may be nested.

### 3.4 Assigns Targets

| # | Syntax | Meaning |
|---|---|---|
| 1 | `\nothing` | No mutation allowed |
| 2 | `x` | Variable `x` may be mutated |
| 3 | `x, y` | Variables `x` and `y` may be mutated |
| 4 | `self.field` | Field may be mutated |
| 5 | `arr[lo..hi]` | Array region `arr[lo..hi)` may be mutated |

```python
#@ assigns \nothing
#@ assigns self._value
#@ assigns arr[0..n]
#@ assigns arr[0..n], brr[0..m]
```

---

## 4. NOT Supported in Contracts

The following Python constructs are **not valid** in `#@` expressions:

| # | Construct | Reason |
|---|---|---|
| 1 | `len(...)` | Use `\length(arr)` instead |
| 2 | ~~Function calls~~ | **Now supported** for pure functions (see Section 4.1) |
| 3 | List comprehensions | Not in grammar |
| 4 | `if`/`else` ternary | Not in grammar |

**Formerly unsupported, now supported:**
- `//` (floor division) and `%` (modulo) — added to grammar (see §3.2 row 8)
- `True` / `False` / `None` — added as atoms (see §3.1 rows 18–19)
- `in`, `not in` — added as membership operators (see §3.2 row 6b)

### 4.1 Pure Functions in Contracts

Functions annotated with `#@ assigns \nothing` (pure, side-effect-free) can
be called inside `#@ requires`, `#@ ensures`, and `#@ loop invariant`
expressions. The function must:

1. Have `#@ assigns \nothing` (no side effects)
2. Not be annotated with `#@ \diverges`
3. Have no mutable local variables (loop-free body: if/else + recursion + arithmetic)
4. Recursive functions must have a `#@ \variant` (termination proof)

Pure functions are emitted as WhyML `let function` (or `let rec function`),
making them usable in logical specifications.

```python
#@ ensures \result >= 0
#@ assigns \nothing
def abs_val(x: int) -> int:
    if x >= 0:
        return x
    return -x

#@ ensures \result == abs_val(a) + abs_val(b)
#@ assigns \nothing
def sum_abs(a: int, b: int) -> int:
    return abs_val(a) + abs_val(b)
```

Recursive pure functions:

```python
#@ requires n >= 0
#@ ensures \result >= 0
#@ assigns \nothing
#@ \variant n
def sum_to(n: int) -> int:
    if n == 0:
        return 0
    return n + sum_to(n - 1)

#@ requires n >= 0
#@ ensures \result == sum_to(n) * 2
#@ assigns \nothing
def double_sum(n: int) -> int:
    return sum_to(n) + sum_to(n)
```

---

## 5. Memory Models

PyCSL supports three memory models, selected via `--memory-model`:

| # | Model | Flag | Array semantics | Aliasing |
|---|---|---|---|---|
| 1 | Hoare (default) | `--memory-model hoare` | Value-typed (`array int`) | Not modeled (independent) |
| 2 | Typed | `--memory-model typed` | Heap-based (`map loc int`) | `\separated` needed |
| 3 | Store | `--memory-model store` | Single untyped heap | `\separated` needed |
| 4 | Concurrent | `--memory-model concurrent` | Value-typed shared vars + mutex invariants | Reduces to sequential WP via monitor-invariant pattern; shared vars declared with `#@ shared` |

### Hoare model
Arrays are independent value-typed entities. `arr[i] <- v` mutates only `arr`.
No aliasing is possible. `\separated` is trivially true.

### Typed model
Arrays are references (locations) into a global typed heap `int_mem : ref (map loc int)`.
`\valid(arr, n)` asserts the region is allocated.
`\separated(a, na, b, nb)` asserts disjoint regions.

### Store model
Single global untyped heap `store : ref (map loc int)`.
Same predicates as typed model but with a unified store.

### Concurrent model
Multithreaded programs using `threading.Lock` / `threading.RLock`. The
monitor-invariant pattern reduces concurrent verification to sequential WP proofs:

- Shared variables are emitted as module-level `val x : ref int` in WhyML.
- Critical section **entry**: havoc the shared variable, then `assume { mutex_inv }`.
- Critical section **exit**: `assert { mutex_inv }`.
- Thread entry functions containing `while True:` receive `diverges` in the WhyML spec.
- `lock_order` is required whenever any function acquires multiple mutexes simultaneously
  (nested `with` blocks holding two or more locks). It prevents deadlock by enforcing a
  total acquisition order.

Module-level declarations (`#@ shared`, `#@ mutex_invariant`, `#@ lock_order`) must be
placed before any function definition and attached to an anchor statement (`_ = 0  # anchor`).

---

## 6. Class Contract Patterns

### Level 2 — Mutable record types

```python
class Counter:
    def __init__(self):
        self._value = 0

    #@ requires amount >= 0
    #@ ensures self._value == \old(self._value) + amount
    #@ assigns self._value
    def increment(self, amount: int) -> int:
        self._value += amount
        return self._value
```

### Level 3 — Class invariants

```python
""  # pycsl
#@ class invariant self._value >= 0
class Counter:
    def __init__(self):
        self._value = 0

    #@ requires amount >= 0
    #@ ensures self._value == \old(self._value) + amount
    #@ assigns self._value
    def increment(self, amount: int) -> int:
        self._value += amount
        return self._value
```

The `""  # pycsl` marker on the line before `#@ class invariant` is
required by the ingestor for class-level annotations.

### Cross-field invariants

A class invariant may reference multiple fields. Mutating methods must
have `requires` clauses strong enough to *guard* the invariant — i.e.,
ensure that the invariant still holds after the method body executes.

```python
""  # pycsl
#@ class invariant self._lo <= self._hi
class Interval:
    def __init__(self):
        self._lo = 0
        self._hi = 0

    #@ requires lo <= self._hi
    #@ ensures self._lo == lo
    #@ assigns self._lo
    def set_lo(self, lo: int) -> None:
        self._lo = lo

    #@ requires hi >= self._lo
    #@ ensures self._hi == hi
    #@ assigns self._hi
    def set_hi(self, hi: int) -> None:
        self._hi = hi
```

The `requires lo <= self._hi` on `set_lo` *guards* the invariant: it
ensures `self._lo <= self._hi` is preserved after `self._lo = lo`.

### Multiple stacked invariants

A class may declare multiple `#@ class invariant` lines. Each is
checked independently at every method boundary.

```python
""  # pycsl
#@ class invariant self._size >= 0
#@ class invariant self._capacity > 0
#@ class invariant self._size <= self._capacity
class Buffer:
    def __init__(self):
        self._size = 0
        self._capacity = 10

    #@ requires self._size < self._capacity
    #@ ensures self._size == \old(self._size) + 1
    #@ assigns self._size
    def push(self) -> None:
        self._size = self._size + 1
```

### Invariant-guarding preconditions

For a method that mutates a field appearing in the class invariant,
the `requires` clause must be strong enough that the invariant is
maintainable. This is the key design principle (inspired by Creusot
from Inria): WhyML record invariants are checked at construction and
method exit; the *precondition* must guarantee the method can
preserve them.

```python
""  # pycsl
#@ class invariant self._balance >= 0
class BankAccount:
    def __init__(self):
        self._balance = 0

    #@ requires amount >= 0
    #@ ensures self._balance == \old(self._balance) + amount
    #@ assigns self._balance
    def deposit(self, amount: int) -> int:
        self._balance = self._balance + amount
        return self._balance

    #@ requires amount >= 0
    #@ requires amount <= self._balance
    #@ ensures self._balance == \old(self._balance) - amount
    #@ assigns self._balance
    def withdraw(self, amount: int) -> int:
        self._balance = self._balance - amount
        return self._balance
```

`requires amount <= self._balance` on `withdraw` is the **guard**
that makes the invariant `self._balance >= 0` provable after the
subtraction.

### Invariant witness

The `by { ... }` witness in WhyML is auto-generated from `__init__`
literal assignments (e.g., `self._value = 0` → `_value = 0`). If the
auto-generated witness does not satisfy the invariant, the transpiler
tries fallback values (0, 1, -1) and picks one that works.

---

## 7. `\old` and `\at` Expressions

### `\old(expr)`
References the value of `expr` at function entry.

```python
#@ ensures arr[0] == \old(arr[1])
#@ ensures self._value == \old(self._value) + amount
```

### `\at(expr, L)`
References the value of `expr` at program point labeled `L`.

```python
#@ label PRE
arr[0] = arr[0] + 1
# ... later in ensures:
#@ ensures arr[0] == \at(arr[0], PRE) + 1
```

---

## 8. Complete Grammar (EBNF)

Extracted from `Module2_Parser.py` — this is the canonical grammar:

```ebnf
?start: contract

?contract: precondition | postcondition | assigns
         | loop_invariant | loop_variant | class_invariant | label_decl
         | function_variant | function_variant_structural
         | diverges_decl | trusted_decl | abstract_decl | preserves_decl
         | assert_decl | check_decl | act_block | complete_decl | disjoint_decl
         | happy_decl

happy_decl:    "happy" CNAME ":" "region" expr ".." expr
               "writes" "self" "." CNAME "outside" "region"
               ("except" CNAME ("," CNAME)*)?
preserves_decl: "\preserves"
assert_decl:   "assert" expr
check_decl:    "check" expr

precondition:    "requires" expr
postcondition:   "ensures" expr
assigns:         "assigns" assigns_target
loop_invariant:  "loop" "invariant" expr
loop_variant:    "loop" "variant" expr
class_invariant: "class" "invariant" expr
label_decl:      "label" CNAME
function_variant:            "\variant" expr
function_variant_structural: "\variant" "(" expr "," CNAME ")"
diverges_decl:   "\diverges"
trusted_decl:    "\trusted"

?assigns_target: assigns_region_list | expr_list | "\nothing"

assigns_region_list: assigns_region ("," assigns_region)*
assigns_region:      CNAME "[" expr ".." expr "]"

?expr: implication
     | "\forall" CNAME ";" expr
     | "\exists" CNAME ";" expr
     | "\exist"  CNAME ";" expr

?implication: logical_or | implication IMPL_OP impl_rhs
?impl_rhs:   logical_or | "\forall"/"\exists"/"\exist" CNAME ";" expr

?logical_or:  logical_and | logical_or OR_OP or_rhs
?or_rhs:      logical_and | "\forall"/"\exists"/"\exist" CNAME ";" expr

?logical_and: equality | logical_and AND_OP and_rhs
?and_rhs:     equality | "\forall"/"\exists"/"\exist" CNAME ";" expr

?equality:    comparison | equality EQ_OP comparison
?comparison:  term | comparison COMP_OP term
?term:        factor | term ADD_OP factor
?factor:      unary | factor MUL_OP unary

?unary: UNARY_OP unary | atom

?atom: NUMBER | "self" "." CNAME "[" expr "]" | "self" "." CNAME | CNAME "[" expr "]" | CNAME
     | "\result" | "\old" "(" expr ")" | "\length" "(" CNAME ")"
     | "\valid" "(" CNAME "," expr ")"
     | "\separated" "(" CNAME "," expr "," CNAME "," expr ")"
     | "\at" "(" expr "," CNAME ")"
     | "\length2d" "(" CNAME "," expr "," expr ")"
     | "\valid2d" "(" CNAME "," expr "," expr ")"
     | "\is_sorted" "(" CNAME "," expr "," expr ")"
     | "\sum" "(" CNAME "," expr "," expr ")"
     | "(" expr ")"

IMPL_OP:  "==>" | "<==>"
OR_OP:    "or"
AND_OP:   "and"
EQ_OP:    "==" | "!="
COMP_OP:  ">" | "<" | ">=" | "<="
ADD_OP:   "+" | "-"
MUL_OP:   "*" | "/"
UNARY_OP: "not" | "-" | "+"
RANGE_OP: ".."

# Concurrent model annotations (--memory-model concurrent)
# These extend the ?contract rule:
shared_decl:          "shared" CNAME "protected_by" CNAME
                    | "shared" CNAME
mutex_invariant_decl: "mutex_invariant" CNAME ":" expr
lock_order_decl:      "lock_order" CNAME ("," CNAME)+
thread_entry_decl:    "thread_entry"
acquires_decl:        "acquires" CNAME
releases_decl:        "releases" CNAME
critical_decl:        "critical" CNAME
```

---

## 9. Pipeline Invocation

```bash
# Basic verification (default Hoare model, Alt-Ergo + Z3)
./pycsl test.py

# With specific memory model
./pycsl test.py --memory-model typed

# Keep generated WhyML for debugging
./pycsl test.py --keep-mlw

# Specific prover
./pycsl test.py -p "Alt-Ergo,2.6.2,"

# Verify only a specific function (and its transitive call-dependencies)
./pycsl test.py --fun foobar

# Verify multiple specific functions
./pycsl test.py --fun foobar --fun helper
```

### Exit codes

| # | Code | Meaning |
|---|---|---|
| 1 | `0` | All goals verified (Valid) |
| 2 | `1` | Verification failed, incomplete, or pipeline error |

### Multi-file imports

PyCSL automatically resolves `from ... import ...` statements. When the
imported module is a local `.py` file, its functions are extracted as trusted
stubs (contracts assumed, bodies not verified). The main file's functions
are then verified against those contracts.

```python
# dir2/file2.py
from dir1.file1 import double_int   # auto-resolved if dir1/file1.py exists

#@ ensures \result == 2 * x
def foobar(x: int) -> int:
    return double_int(x)             # proven using double_int's contract
```

```bash
./pycsl dir2/file2.py   # resolves dir1/file1.py, imports double_int as trusted
```

Supported import forms:
- `from mod import name`
- `from mod import a, b` (multiple names)
- `from mod import name as alias`
- `from mod import *` (wildcard — imports called functions, respects `__all__`)
- `import mod as alias` (calls via `alias.func(x)`)
- `import mod` (calls via `mod.func(x)` or `mod.sub.func(x)`)
- Relative imports (`from .mod import name`)

External modules (stdlib, third-party) that cannot be resolved to a local file
are silently skipped.

### Recursive import resolution (`--deep`)

By default, only the main file's direct imports are resolved. With `--deep`,
PyCSL recursively resolves imports in dependency files (transitive chain).
Circular imports are detected and skipped with a warning.

```bash
# Resolve transitive import chains: A→B→C
./pycsl --deep file.py
```

### Output parsing

With `split_vc`, each function produces multiple sub-goals. Output lines
contain per-goal results:

```
FunctionName VCkind : Valid (0.01s, 42 steps)
FunctionName VCkind : Unknown (timeout)
```

A function is fully verified only when **all** its sub-goals are `Valid`.

---

## 7. Supported Body Constructs

The following Python constructs in function bodies are transpiled to WhyML:

### 7.1 Assert Statement

```python
assert x > 0, "x must be positive"
```

Transpiles to:

```whyml
check { [@expl:x must be positive] (x > 0) }
```

The message string (if present) becomes a WhyML `@expl:` attribute.
If no message, `"assertion"` is used as default.

### 7.2 Tuple Unpacking

```python
a, b = divmod(x, y)
```

Transpiles to a `let` destructuring followed by ref assignments.

### 7.3 Walrus Operator (`:=`)

```python
y = (x := n + 1)
```

The named expression `(x := expr)` both assigns to `x` and evaluates to
the assigned value. In WhyML, this is emitted as a `begin ... end` block
with a side-effectful assignment.

### 7.4 Match Statement

```python
match status:
    case 200:
        result = "ok"
    case 404:
        result = "not found"
    case _:
        result = "unknown"
```

Lowered to an if/elif chain comparing the subject against each pattern value.
Wildcard (`_`) becomes the final `else` branch.

**Constructor patterns over a `#@ datatype` (§2.6).** When the subject is a sum-type value, the
`case` arms use constructor patterns and lower to a **real Why3 `match … with … end`** (not an
if-chain), so the solver checks **exhaustiveness**:

```python
#@ datatype Box = Some(int) | Pair(int, int) | Empty

#@ ensures \result >= 0
def tag(b: Box) -> int:
    match b:
        case Some(v):      # `v` binds the payload
            return 0
        case Pair(a, c):
            return 1
        case Empty():
            return 2
```

lowers to `match b with | Some v -> … | Pair a c -> … | Empty -> … end`. A missing or extra
constructor is a hard error. Capture names (`v`, `a`, `c`) bind the payloads. **Guards**
(`case Some(v) if v > 0` → `Some v -> if v>0 then … else <fall-through>`), **nested patterns**
(`case Wrap(A(n))` → `Wrap (A n) -> …`), and **or-patterns** (`case Red() | Green()`, and a payload
bound identically across alternatives `case Some(n) | Wrapped(n)`) are all supported (§2.6).

### 7.5 Lambda

```python
f = lambda x, y: x + y
```

Transpiles to an anonymous function:

```whyml
fun (x: int) (y: int) -> (x + y)
```

---

## 10. Concurrent Model Annotations

Used with `--memory-model concurrent`. Placed on **leading lines** before the
module body (module-level declarations) or before `with` statements (critical
section annotations).

### 10.1 Module-Level Declarations

| # | Directive | Syntax | Semantics |
|---|---|---|---|
| 1 | Protected shared variable | `#@ shared <var> protected_by <mutex>` | `<var>` is a shared global; every read/write must be inside a `#@ critical <mutex>` block (Module4 enforces this) |
| 2 | Unprotected shared variable | `#@ shared <var>` | `<var>` is shared but unprotected; ConcurrencyChecker warns, Module4 is lenient |
| 3 | Mutex invariant | `#@ mutex_invariant <mutex>: <expr>` | `<expr>` must hold whenever `<mutex>` is free; checked at critical section exit (`assert { mutex_inv }`) |
| 4 | Lock order | `#@ lock_order <m1>, <m2>, ...` | Total order on mutex acquisition; required when any function holds one mutex while acquiring another |

Module-level `#@ shared` and `#@ mutex_invariant` declarations must be placed
before any function definition. Use `_ = 0  # anchor` as the target Python
statement for leading-line module annotations.

### 10.2 Placement and Rules

- Unprotected writes/reads of a `#@ shared protected_by` variable outside a critical
  section raise `PyCSLSemanticError` (Module4).
- Nested acquisition of multiple mutexes requires `#@ lock_order` to prevent deadlock.
- `queue.Queue`, `threading.Lock`, `threading.RLock` are trusted thread-safe types and
  need no `#@ shared` annotation.
- A `#@ mutex_invariant` expression may only reference variables protected by that mutex.
- `#@ critical <mutex>` and `#@ acquires <mutex>` are equivalent in Module5/Module6:
  both generate a `CriticalSection` IR node that wraps the `with` body with
  havoc+assume/assert invariant pairs.
- `#@ releases <mutex>` is stored on the `with` node but does not currently generate
  extra WhyML. It is informational (documents the release point for manual protocols).

### 10.3 Minimal Example

```python
# pycsl-flags: --memory-model concurrent --no-proof
#@ shared counter protected_by lock_counter
#@ mutex_invariant lock_counter: counter >= 0
_ = 0  # anchor
import threading
lock_counter = threading.Lock()
counter = 0

#@ thread_entry
#@ \diverges
def worker() -> int:
    #@ critical lock_counter
    with lock_counter:
        counter += 1
    return 0
```

---

## 11. Ghost Variable Types

Ghost variables are erased at extraction and live only in the verification model.
Use typed declarations to control the WhyML type of a ghost variable:

```python
#@ ghost <name> : <type> = <expr>
```

Untyped ghost declarations (`#@ ghost <name> = <expr>`) default to `int`.

> **Terminology**: For definitions of *ghost code*, *ghost state*, *witness*, *ghost lowering*,
> and related concepts, see [`docs/glossary/`](../docs/glossary/README.md).

### 11.1 Typed Ghost Declarations

| # | Type keyword | WhyML type | Initial value | Update syntax |
|---|---|---|---|---|
| 1 | `int` (default) | `ref int` | any int expr | `ghost x = e`, `ghost x += e` |
| 2 | `string` | `ref string` | `"..."` or `s ^ "..."` | `ghost s = s ^ "chunk"` |
| 3 | `array` | `array int` (not a ref) | `\copy(arr)` or `\make(n, v)` | `ghost snap[i] = e` |
| 4 | `ghost_dict` | `ref (map int (option int))` | `\empty_map` | `ghost d = \map_set(d, k, v)` |
| 5 | `ghost_list` | `ref (list int)` | `\nil` | `ghost l = \cons(x, l)` |
| 6 | `ghost_set` | `ref (map int bool)` | `\set_empty` | `ghost s = \set_add(s, e)` |
| 7 | `tuple2` | `ref (int, int)` | `\mktuple(a, b)` | `ghost p = \mktuple(a, b)` |
| 8 | `tuple3` | `ref (int, int, int)` | `\mktuple(a, b, c)` | `ghost t = \mktuple(a, b, c)` |
| 9 | `tuple4` | `ref (int, int, int, int)` | `\mktuple(a, b, c, d)` | `ghost q = \mktuple(a, b, c, d)` |

### 11.2 Ghost Expression Atoms

**Tuples:**
| # | Syntax | Meaning |
|---|---|---|
| 1 | `\mktuple(e1, e2, ...)` | Construct a tuple (2–4 elements) |
| 2 | `\fst(t)` | First component of a tuple2 |
| 3 | `\snd(t)` | Second component of a tuple2 |
| 4 | `\proj(t, i)` | i-th component (i must be an integer literal) |

**Strings:**
| # | Syntax | Meaning |
|---|---|---|
| 1 | `s ^ t` | String concatenation (Why3 `concat s t` — not `String.(^)`) |
| 2 | `"literal"` | String literal |
| 3 | `\str_length(s)` | String length (`String.length !s`) |
| 4 | `\str_sub(s, lo, hi)` | Substring from `lo` to `hi` (`String.substring !s lo (hi-lo)`) |

> **Runtime `str` uses the same `string.String` model** (τ(str) = string; the old int-hash
> dual model is unified — see static-semantics §1.4 and translational §T.6.15). These operators
> apply to a runtime `str` parameter/local, not only to a `#@ ghost s : string`: in a body,
> `len(s)` / `s + t` / `s[a:b]` / `s[i]` / `s == t` / `needle in haystack` /
> `s.startswith`/`.endswith`/`.find` lower through abstract `val …_op` bridges to the same
> `String.length`/`concat`/`String.substring`/`=` symbols, and the `\str_*` spec operators above
> relate the result to content. Drivers: corpus `0471` (substring search) and `0472`–`0494`.
> **Out of scope:** code points (`ord`, char ordering), `upper`/`lower`/`strip`/`replace`/`split`
> (opaque), `.decode`/`.encode` (opaque bytes↔str boundary), f-strings, `str`-keyed dicts (hash).

**Ghost arrays** (hoare model only):
| # | Syntax | Meaning |
|---|---|---|
| 1 | `\copy(arr)` | Snapshot of an existing array |
| 2 | `\make(n, v)` | Fresh array of length `n` filled with `v` |
| 3 | `ghost snap[i] = e` | In-place element update (`ghost_array_set`) |

**Ghost dicts** (backed by `map int (option int)`):
| # | Syntax | Meaning |
|---|---|---|
| 1 | `\empty_map` | Empty map (all keys absent: `const (None: option int)`) |
| 2 | `\map_get(d, k)` | Get value for key k; returns 0 if absent (`match Map.get !d k with \| Some v -> v \| None -> 0 end`) |
| 3 | `\map_set(d, k, v)` | `Map.set !d k (Some v)` |
| 4 | `\map_eq(d1, d2)` | Extensional equality |
| 5 | `#@ ghost d += \mktuple(k, v)` | Shorthand for `Map.set !d k (Some v)` (augmented assign) |
| 6 | `\has_key(d, k)` | True iff key k is present (`Map.get !d k <> None`). Safe even when 0 is a valid stored value |
| 7 | `\map_remove(d, k)` | Remove key k (set to absent: `Map.set !d k None`) |

**Ghost lists** (backed by Why3 `list int`):
| # | Syntax | Meaning |
|---|---|---|
| 1 | `\nil` | Empty list |
| 2 | `\cons(x, l)` | Prepend element |
| 3 | `\hd(l)` | Head element |
| 4 | `\tl(l)` | Tail |
| 5 | `\list_length(l)` | Length |
| 6 | `\nth(l, i)` | i-th element |
| 7 | `\mem(x, l)` | Membership test |
| 8 | `\append(l1, l2)` | Concatenation |
| 9 | `#@ ghost l += x` | Prepend shorthand: `ghost l := Cons x !l` |

**Ghost sets** (backed by `map int bool`):
| # | Syntax | Meaning |
|---|---|---|
| 1 | `\set_empty` | Empty set |
| 2 | `\set_add(s, x)` | Add element |
| 3 | `\set_remove(s, x)` | Remove element |
| 4 | `\set_mem(x, s)` | Membership test |
| 5 | `\set_card(s, lo, hi)` | Cardinality over integer range `[lo, hi)` |
| 6 | `\set_union(s1, s2)` | Functional union (λ k → s1[k] ∨ s2[k]) |
| 7 | `\set_inter(s1, s2)` | Functional intersection |
| 8 | `\set_diff(s1, s2)` | Functional set difference |
| 9 | `\set_subset(s1, s2)` | s1 ⊆ s2 (predicate) |
| 10 | `\set_eq(s1, s2)` | s1 = s2 extensionally |
| 11 | `#@ ghost s += x` | Add shorthand: `Map.set !s x true` |

### 11.3 Required Why3 `use` Declarations

The PyCSL preamble scanner auto-detects which ghost types are in use and emits the
appropriate `use` declarations. No manual configuration is needed.

| Ghost type | Why3 library added |
|---|---|
| `string` | `use string.String` |
| `array` | `use array.Array` (hoare/concurrent only) |
| `ghost_dict` | `use map.Map`, `use map.Const`, `use option.Option` |
| `ghost_set` | `use map.Map`, `use map.Const` |
| `ghost_list` | `use list.List`, `use list.Length`, `use list.NthNoOpt`, `use list.Mem`, `use list.Append` |

### 11.4 Validation Rules (Negative Constraints)

Module4 enforces the following semantic constraints on ghost variable usage:

| # | Constraint | Error class |
|---|---|---|
| 1 | `\proj(t, expr)` — index must be an integer literal, not a variable | Module4 semantic error |
| 2 | `\proj(t, i)` — index `i` must be within the arity of the declared tuple type (no Module4 check; Why3 rejects at type checking) | Why3 type error |
| 3 | `#@ ghost s += expr` where `s` is a `string` ghost — augmented assignment not supported on strings; use `ghost s = s ^ expr` instead | Module4 semantic error |
| 4 | Augmented-assign ops (`+=`, `-=`, `*=`) on ghost string variables: always rejected regardless of the value expression | Module4 semantic error |

### 11.5 Ghost Position: Trailing-Block Ghosts

A `#@ ghost` annotation may appear as the **last line in a loop or if body** (no following
Python statement in that scope). The annotation lives in the `IndentedBlock.footer` of the
libcst CST. Module1 detects it there and records it as a `TrailingSimpleStatement` contract.
Module3 attaches it to the last statement in the block as `csl_trailing_ghost_assigns`.
Module5 emits the ghost IR **after** that last statement, so it appears at the end of the
loop body in the generated WhyML.

```python
#@ ghost count = 0
#@ loop invariant count == i
while i < n:
    i += 1
    #@ ghost count = i    ← trailing ghost: emitted as last statement in loop body
```

Generated WhyML (inside the while body):
```whyml
i := !i + 1;
ghost count := !i
```

**Constraint:** A trailing ghost that is a *first declaration* (variable not yet declared
before the block) generates `let ghost x = ref val in ()`, which is valid WhyML but gives
`x` an empty scope. Declare ghost variables before the loop to ensure they are in scope
for loop invariants.

### 11.6 Ghost Array `\copy_range`

`\copy_range(arr, lo, hi)` creates a new ghost array containing `arr[lo..hi-1]`.
Lowers to `(Array.sub arr lo (hi - lo))` in Why3.

```python
#@ ghost snap : array = \copy_range(arr, 0, n)
#@ loop invariant \forall j; 0 <= j and j < i ==> snap[j] == arr[j]
```

| Syntax | Why3 emission | Why3 `use` |
|---|---|---|
| `\copy_range(arr, lo, hi)` | `(Array.sub arr lo (hi - lo))` | `use array.Array` (auto) |

**Preconditions** (enforced by Why3's `Array.sub`):
- `0 <= lo`
- `0 <= hi - lo` (i.e., `lo <= hi`)
- `lo + (hi - lo) <= Array.length arr` (i.e., `hi <= Array.length arr`)

These appear as Why3 sub-goals when the ghost is declared. Provide a `requires` or
`loop invariant` that establishes the bounds before the declaration point.

### 11.7 Memory-Model Parity for Ghost Array Snapshots

Ghost arrays (`array` type) and the operators `\copy`, `\copy_range`, and `\make`
are available **only under `hoare` and `concurrent` memory models**.

Under `typed` and `store` models, array parameters are lowered to `loc` (integer
pointer) in the generated WhyML. `Array.copy` and `Array.sub` expect `array int`, not
`loc`, so any ghost array declaration emitted under these models would be type-incorrect
in Why3.

**Restriction summary:**

| Ghost operation | `hoare` | `concurrent` | `typed` | `store` |
|---|---|---|---|---|
| `\copy(arr)` | ✓ | ✓ | ✗ | ✗ |
| `\copy_range(arr, lo, hi)` | ✓ | ✓ | ✗ | ✗ |
| `\make(n, v)` | ✓ | ✓ | ✗ | ✗ |

For snapshot-style reasoning under `typed`/`store`, use `\old(arr[i])` or quantify
over `\old` values in postconditions instead of ghost arrays.

The `--memory-model hoare` flag is the default; it can also be specified explicitly
via `# pycsl-flags: --memory-model hoare` in the source file.

### 11.8 Ghost String `\str_sub` Proof Pattern

`\str_sub(s, lo, hi)` lowers to `String.substring !s lo (hi - lo)` in Why3 (function
`substring` from `string.String`).

**Key axiom** (from Why3 `string.String`):
```
axiom substring_length: forall s i x.
  x >= 0 && 0 <= i < length s ->
    if i + x > length s then length(substring s i x) = length s - i
    else length(substring s i x) = x
```

**Provable loop invariant pattern** — prefix length:
```python
#@ ghost s : string = ""
#@ loop invariant \str_length(s) == i
#@ loop invariant i > 0 ==> \str_length(\str_sub(s, 0, i)) == i
#@ loop variant n - i
while i < n:
    #@ ghost s = s ^ "x"
    i = i + 1
```

The invariant `i > 0 ==> \str_length(\str_sub(s, 0, i)) == i` is discharged by
Alt-Ergo directly from `substring_length` and the `\str_length(s) == i` invariant.

**Constraints:**
- `\str_sub` is valid in loop invariants and `ensures` when the string is in scope.
- `lo >= 0`, `hi >= lo`, `hi <= \str_length(s)` must be guaranteed (either by a
  prior `requires` clause or by combining with another loop invariant).
- Ghost string variables declared inside the function body are **not** in scope for
  `ensures` clauses. Use `\str_sub` directly inside loop invariants instead.

| # | 11.8.1 | `\str_sub` prefix length proof | Test 0329 |

### 11.9 Ghost Dict `\map_remove` and Option-Type Design

Ghost dicts use `map int (option int)` internally. A stored value of 0 is **present** (Some 0),
not absent. `\has_key(d, k)` returns true if and only if `Map.get !d k <> None`.

`\map_remove(d, k)` sets key k to `None` (absent). After remove, `\has_key(d, k)` is false and
`\map_get(d, k)` returns 0 (the default for absent keys).

**Provable loop invariant pattern** — add-then-remove key 0, store 0 at key 1:
```python
#@ ghost d : ghost_dict = \empty_map
#@ loop invariant i > 0 ==> \has_key(d, 1)
#@ loop invariant i > 0 ==> \map_get(d, 1) == 0
#@ loop variant n - i
while i < n:
    #@ ghost d = \map_set(d, 0, i + 1)
    #@ ghost d = \map_remove(d, 0)
    #@ ghost d = \map_set(d, 1, 0)
    i = i + 1
```

The invariant `i > 0 ==> \has_key(d, 1)` is provable because `\map_set(d, 1, 0)` stores
`Some 0`, and `Some 0 <> None`. This was impossible under the old sentinel-0 design where
storing 0 was indistinguishable from "absent".

**WhyML emission for `\map_remove`:**
`\map_remove(d, k)` → `(Map.set {d_ref} {k} None)`

| # | Syntax | Why3 emission |
|---|---|---|
| 11.9.1 | `\map_remove(d, k)` | `Map.set !d k None` |

| # | 11.9.1 | Ghost dict `\map_remove` + option-type proof | Test 0330 |

---

## 12. Body-Level Data Structures

Beyond `#@ ghost ...` ghost variables, Python function bodies may declare
ordinary mutable dicts, sets, lists, and use builtins like `sorted`,
`range(start, stop)`, `Optional[T]`. The transpiler models these so the
body type-checks under Why3 and SMT can discharge non-trivial properties.

### §12.1 Body `dict`

| Form | Why3 emission | Notes |
|------|---------------|-------|
| `d = {}` (Assign) | `let d = ref (const (None: option int)) in` | Empty body dict initialised to total-None map |
| `d = dict()` (Call) | same | Same as above |
| `d[k] = v` (ArraySet) | `d := map_update_some !d k v` | Wrapper `val` whose `ensures` clause equals `Map.set m k (Some v)` — program-level so the result can be assigned to a non-ghost ref |
| `d[k]` (Subscript) | `(match Map.get !d k with \| Some v_ -> v_ \| None -> 0 end)` | Absent keys read as `0` (matching the ghost-dict convention) |
| `k in d` (BinOp) | `(match Map.get !d k with \| Some _ -> true \| None -> false end)` | Why3 program code lacks decidable `=` on `option int`, so match is used |
| `k not in d` | same with arms swapped | |

**Forbidden** (still): `d.items()`, `d.keys()`, `d.values()`, `d.get(k, default)`,
`del d[k]` as statement (use `s.discard(k)` on sets), iteration over `for k in d:`.

**Tests**: 0345 (round-trip), 0346 (in / not in).

### §12.2 Body `set`

Sets share the dict's `map int (option int)` model. Present keys map to
`Some 0`, absent keys to `None`. The body distinguishes them via the
literal type at assignment time.

| Form | Why3 emission | Notes |
|------|---------------|-------|
| `s = set()` / `s = frozenset()` | `let s = ref (const (None: option int)) in` | Empty body set |
| `s = {a, b, c}` (SetLit) | `let s = ref (map_update_some (map_update_some (const None) a 0) ...) in` | Chained inserts |
| `s.add(x)` | `s := map_update_some !s x 0` | Same wrapper as `d[k] = 0` |
| `s.discard(x)` | `s := map_update_none !s x` | Wrapper for `Map.set m k None` |
| `s.remove(x)` | same as `.discard` | (no KeyError semantics) |
| `x in s`, `x not in s` | match-based, same as dict | |

**Forbidden**: `s.union()`, `s.intersection()`, `s.difference()`, `len(s)`.

**Tests**: 0347.

### §12.3 Multi-argument `range(start, stop)`

`for i in range(start, stop):` lowers to a while-loop with `_idx_i`
initialised at `start`, bounded by `< stop`. Both arguments are
expressions (no constraint to literals).

**Tests**: 0327, 0328 (parse-level), 0348 (full proof with loop
invariants + variant).

### §12.4 `Optional[T]` and `Union[T1, T2]` return annotations

Module5 extracts parametric return annotations recursively:

- `-> Optional[T]` ⇒ `return_annotation = "<T_head>"` (e.g. `Optional[int]` → `"int"`, `Optional[List[str]]` → `"list"`)
- `-> Union[T, None]` ⇒ same as Optional (picks first non-`None` component)
- `-> Union[T1, T2, …]` ⇒ heuristic: first non-`None` component

PyCSL models `None` as `0`, so Optional adds no type-level info Module6
could use; the unwrap collapses to the inner type.

**Tests**: 0349 (Optional[int]), 0350 (Union[int, None]).

### §12.5 `sorted` builtin

`sorted(arr)` emits an abstract `val sorted_1 (a: array int) : array int`.
The abstract val has no axioms about the result's contents — Why3
knows only that it returns an array. Contracts cannot meaningfully
assert order or element identity through `sorted_1`.

`any(arr)` and `all(arr)` emit similar abstract vals returning `bool`.

**Tests**: 0351.

### §12.6 `bytes` and `bytearray` type unification

Python `bytes` and `bytearray` parameter types lower to WhyML
`array int` (each element conceptually a byte value 0..255; the
bound is not enforced by the abstract emission). Byte-string
literals (`b'...'`) lower to `ArrayLit` of byte values in the IR,
composing naturally with the existing `[default] * size →
Array.make` BinOp handler — so `b'\x00' * N` becomes
`(Array.make N 0)`.

This is **not** a new contract directive — it's a Module 5 / Module 6
emission rule. No `#@` syntax is involved. The effect is structural:
calls to `struct.unpack(fmt, data)` where `data` has a bytes-shape
(emitted as `array int`) get type-correct abstract-val signatures
from `_emit_dotted_call`, instead of the previous all-int default
that caused `array int @rho` vs `int` type clashes.

Per `missing-bytes-struct-feature.md` Phase 1. Lifts the
transpiler limit that previously forced `\trusted reviewer:` on
the 4 struct-heavy internals of
`unix-filesystem/UnixInodeFileSystem.py`.

### §12.7 `collections` constructors (content-modeled)

A handful of `collections` constructors are recognized **by bare name** (import-independent) and
routed to an existing modeled structure, so a local built from them carries real verifiable
content (no `#@` syntax — a Module 5 / Module 6 emission rule):

| Constructor | Models as | Content carried |
|---|---|---|
| `defaultdict(int)`, `Counter()`, `OrderedDict()` | body `dict` (§12.1) — `map int (option int)` | key read/write; a missing key reads `0` (which *is* `defaultdict(int)`/`Counter` semantics) |
| `deque()` | growable array (`array int` + length) | right-end `append`, `dq[i]`, `len(dq)` |
| `namedtuple('P', ['x','y'])` | synthesized record (§2 class records) | `Point(a, b).x == a` (literal fields) |

**Out of scope (sound under-approximation / opaque):** `defaultdict(list/set)` and other non-`int`
factories; deque left-end / `pop` (`appendleft`/`popleft`/`pop` — only right-end is modeled);
`OrderedDict` ordering; `Counter.most_common` ranking; `ChainMap`/`UserDict`/`UserList` (opaque int
handles); a `deque`/`Counter` built from an iterable models as **empty** (never proves a false
content claim). See the `pycsl-stdlib-coverage` SKILL for the per-member tier table. Drivers:
0498–0505.

### §12.8 Sum-type construction (`#@ datatype`)

A `#@ datatype` value is constructed in the body with the call form and consumed with a `match`:

```python
#@ datatype Box = Some(int) | Pair(int, int) | Empty
o = Some(7)          # → a typed variant local `let o = ref (Some 7) in`
n = Empty            # nullary constructor
```

This is the body side of §2.6 (the declaration) and §7.4 (constructor-pattern match). Drivers:
0520 (nullary enum), 0521 (payload construction + capture match).
