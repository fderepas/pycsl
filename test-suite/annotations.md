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
| 16 | Lemma | `#@ lemma` | Function/method (`-> None`) | The function is a PROVED logical fact. Lowers to `let [rec] lemma name (params) : unit requires {H} ensures {C} [variant {m}] = <proof body>`: Why3 verifies the body, then `forall params. H -> C` is usable by later goals. A recursive lemma's self-calls are the induction hypotheses; `#@ \variant` is optional (Why3 infers a structural variant and rejects ill-founded recursion). Must be `-> None` / `assigns \nothing`; may not rest on a `\trusted` fact. Introduces NO axiom that isn't itself checked. See §2.1.16 below. |
| 17 | Uses | `#@ uses <lemma>` | Function/method | Cites a `#@ lemma` whose general fact this function's proof relies on but does not *name* (e.g. a `\forall`-over-a-recursive-datatype goal discharged by the lemma). Forces the lemma to be emitted before this function so its fact is in scope. Ordering-only — emits no WhyML. See §2.1.17 below. |
| 16 | Case guard | `#@ given <expr>` | Inside an `act` | The case's pre-state guard (ACSL's `assumes`); only valid inside an `act` block. `\result` is not allowed here. |
| 17 | Complete cases | `#@ complete <name>, ...` | Function/method | Proof obligation that the named acts' guards cover every input — `ensures \old(g1) \|\| ... \|\| \old(gn)`. |
| 18 | Disjoint cases | `#@ disjoint <name>, ...` | Function/method | Proof obligation that at most one guard holds — per pair `ensures not(\old(gi) && \old(gj))`. |
| 19 | No inline | `#@ no_inline` | Method on a module-global instance | **Modular-verification boundary (no-inline.md).** The method's body is verified once against its contract (emitted as a `let`); callers reuse its **contract** (a contract-call to an abstract `val` carrying the result-only `ensures`) instead of splicing the inlined body. Avoids re-proving a large body in every caller's context (the os `sys_write` inlining blow-up). Sound iff the body stays a verified `let` — a false `ensures` makes the *callee* fail. |
| 26 | Sibling concrete | `#@ sibling_concrete` | Method | **Opt-in concrete sibling-call (allocator-frame §2.7).** An intra-class `self.<m>()` call to a method marked `#@ sibling_concrete` is lowered to a CONCRETE call `(<class>__<m> self args)` — so the caller gets the callee's full contract AND its type/class-invariant guarantee on the post-state — instead of the default abstract `val` stub (which conveys neither). Use ONLY on cheap-to-maintain leaf writers whose guarantee the caller can absorb as an atom (e.g. the os bitmap leaves `_set_bitmap`/`_poke`, letting the allocators inherit the disk class invariant). Decoupled from `no_inline`: affects sibling-call lowering only, NOT wrapper inlining. Default off → every existing self-call keeps its abstract-stub lowering (byte-identical). Sound: a concrete call to a verified `let` is the method's real semantics. |
| 27 | Propagate frame | `#@ propagate_frame` | Method | **Opt-in quantified-frame propagation across the call/import boundary (os-roadmap M4).** A method's `#@ assigns self.f` only frames `self.f` as a WHOLE on the abstract boundary `val` — so a caller sees the whole field havoced (only the result-pinned cell survives). With `#@ propagate_frame`, THIS method's QUANTIFIED single-cell self-field FRAME `ensures` (`\forall k. guard -> self.f[k] == \old(self.f[k])`) is carried onto its boundary `val`, letting a caller prove every *other* cell is preserved by the call. Two frame shapes are propagated: param-referencing frames (e.g. the os `_zero_entry` slot frame, trigger pinned on the post-state decode application) and `\result`-referencing single-cell frames (`\forall k != \result. self.f[k] == \old(self.f[k])`, where `\result` lowers to the val's `result` keyword = the call's return value — e.g. the os `sys_open`/`sys_dup` `fd_open` allocator frame, letting "the table is not full" survive a prior open). Opt-in ON PURPOSE: a broad frame trigger can E-match-poison term-rich sibling callers, so mark ONLY methods whose callers need *and* can absorb the frame. Default off → byte-identical emission. Sound: the propagated `\forall` is the SAME frame the callee's body verifies, never a fabricated or broadened one. |
| 28 | Fresh globals | `#@ fresh_globals` | Top-level driver (NOT a method, NOT a callee) | **Opt-in, CONFINED constructor-post-state surfacing for a standalone formal-test driver (fresh-globals.md).** Why3 verifies every importer function with each shared mutable module-global in an ARBITRARY (havoc'd) state — so an internals-blind driver cannot establish the global's freshly-imported initial state (e.g. the os `_filesystem` fd table being ALL-FREE at entry). `#@ fresh_globals` re-establishes, at the driver's body entry, each module-global singleton's CONSTRUCTOR post-state — the class `__init__`'s `#@ ensures` with `self` rewritten to the global — as an ASSUMED fact (`assume { \forall k. (0<=k<64) -> g.fd_open[k] == 0 }`). The assumed fact is NOT an arbitrary literal: it is the constructor's `#@ ensures`, which the transpiler ALSO emits as a checked function (`let g_fresh_init () : C ensures { … } = <constructor literal>`) PROVING the post-state holds of the freshly constructed global — so the assume is proof-backed. **SOUNDNESS (Module4-enforced):** sound ONLY for an independent entry point that runs on a freshly-imported global and is NEVER entered with a pre-mutated one. Module4 REJECTS `#@ fresh_globals` on a method (`self`-receiver) and on any function CALLED by another (a callee inherits its caller's possibly-mutated global) — error `PYCSL-SEM-FRESH-GLOBALS`. It RETIRES a reviewer trust (the os `fd-resolution-fidelity` unconditioned no-ENFILE `\result>=3` — FALSE at table-full) by replacing the false unconditioned body theorem with a free-slot-conditioned one whose side-condition this sound, confined, constructor-backed entry fact establishes. |
| 29 | Verify module | `#@ verify_module <name>` | Method | **Opt-in axiom isolation via separate Why3 modules (module-emission.md).** A method tagged `#@ verify_module <name>` is emitted into its OWN top-level Why3 `module` (shared infra — record type, val-functions, predicates, witness/class-invariant axioms — re-declared per module, the concrete record type shared via a common base `module` `use`d everywhere), so that ONLY the `#@ proof` axioms cited by the functions in that group are in scope for its goals. Methods sharing the same `<name>` co-reside in one module. A cross-module `self.<m>(...)` call (a sibling in a different `verify_module` group, or the flat default module) is lowered to the **proven** contract of the callee via Why3 module **`clone`-refinement** (the interface `module` declares the callee's contract; the owning provider `module` proves the real `let` *implements* it — Why3's synthetic `<fn>'refn'vc`, validated non-vacuous), i.e. a PROVEN cross-module interface, **never** an assumed-`val` boundary, a new `\trusted`, or a new axiom (the net TCB is unchanged — every function proved once, against a proven contract). Resolves the os read+write `field_to_str`/`dir_blit_marker` axiom co-residence that OOMs `_zero_entry` at ~9.5 M steps and blocks the `_dir_lookup` read-side de-trust. Default (untagged) → the single flat `module PyCSL_Program` is emitted unchanged → corpus byte-identical. (Why3 `scope` does NOT isolate axioms — a scope is a namespace; only separate `module`s do.) See §2.1.29 below. |

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

#### §2.1.16 Lemma (`lemma`)

A `#@ lemma` marks a `-> None` function as a **proved logical fact**. It lowers to a
Why3 `let [rec] lemma`: the body is verified against the contract, then the contract
becomes a usable fact `forall params. requires -> ensures` for later goals.

```python
#@ lemma                                   # non-recursive — SMT discharges the body
#@ requires a >= 0 and b >= 0
#@ ensures a + b >= 0
#@ assigns \nothing
def sum_nonneg(a: int, b: int) -> None:
    pass

#@ lemma                                   # recursive — induction; \variant mandatory
#@ ensures to_int(n) >= 0
#@ \variant n
#@ assigns \nothing
def to_int_nonneg(n: Nat) -> None:
    match n:
        case Z():     pass
        case S(m):    to_int_nonneg(m)      # self-call = the induction hypothesis
```

- **Assume-vs-prove.** `#@ \trusted` is *assumed* (a `val`, full trust); `#@ proof
  rocq|lean` is *proved elsewhere* (an `axiom`, audited); `#@ lemma` is **proved here**
  — Why3 checks the body and the conclusion is usable only after it verifies. A lemma
  introduces no axiom that isn't itself checked.
- **Well-formedness (Module 4 rejects, hard error).** A lemma must be `-> None` and
  `assigns \nothing` (ghost discipline — erased at extraction, computes nothing), must
  state ≥1 `#@ ensures`, and is not `#@ \diverges`. A plain lemma may **not** call a
  `\trusted` function (it would smuggle an *unverified* fact into a checked lemma — Why3
  cannot catch this). **Termination is Why3's job, not a PyCSL check:** `#@ \variant`
  on a recursive lemma is *optional* — Why3 infers a structural variant and rejects
  ill-founded recursion via its termination VC (so a non-terminating "lemma" cannot
  export `False`). Supply `#@ \variant` only for a non-structural measure.
- **Use.** Once verified, a lemma's conclusion is available globally (and an explicit
  `lemma_name(args)` call in another function's body forces the instantiation at that
  point). Prefer `#@ lemma` over `#@ proof` when Why3 + induction can discharge it,
  keeping the proof in-repo and machine-checked.

**Test-corpus cross-reference:** `0558` (non-recursive, SMT), `0559` (recursive,
induction over `#@ datatype`, explicit `#@ \variant`), `0570` (recursive, NO
`#@ \variant` — Why3 infers it), `0560` (non-terminating lemma → Why3 termination VC
rejects it), `0561` (false `ensures` — body fails), `0571` (calls a `\trusted` fn —
trust-leakage rejected).

#### §2.1.17 Uses (`uses`)

`#@ uses <lemma>` cites a `#@ lemma` whose **general fact** a function's proof relies on
without *naming* it — the canonical case being a universal over a recursive `#@ datatype`:

```python
#@ ensures \forall x: Nat; to_int(x) >= 0   # not SMT-dischargeable; needs induction
#@ uses to_int_nonneg                        # the recursive lemma that proves it
#@ assigns \nothing
def all_nonneg() -> int:
    return 0
```

A `#@ lemma`'s conclusion is exported as `forall params. H -> C` to every goal emitted
**after** it. The wrapper's goal is discharged by that fact — but since the wrapper never
mentions `to_int_nonneg` by name, no reference exists to force the lemma to be emitted
first. `#@ uses` supplies exactly that ordering edge (it is consumed by the SCC sort,
`scc.py`), so the lemma precedes the function and its fact is in scope.

- **Ordering-only — emits no WhyML.** Unlike an explicit lemma *call* in the body
  (`to_int_nonneg(Z())`, which also forces the order but instantiates a throwaway
  argument), `#@ uses` is a pure, non-instantiating citation.
- The cited name must be a function/lemma in scope. Multiple `#@ uses` lines are allowed.

**Test-corpus cross-reference:** `0565` (a `\forall x: Nat; to_int(x) >= 0` wrapper
discharged via `#@ uses` of the recursive lemma). Background: `scc.md` / `scc2.md`.

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
| 3 | HAPPY (protects) | `#@ happy <name>: protects <path>, … [except m1, …]` (07-1143 R1/R2) | Module-level | Subsystem ownership: no method outside `except` may DIRECTLY write any protected (possibly dotted/nested, e.g. `world.fs.disk`) path. Expands to a per-site `#@ check False` at each non-exempt direct write. Aliasing a protected base into a non-exempt local (`x = world.fs`) is a hard error (it would evade the check). A non-exempt `\trusted`/`\abstract` method whose `assigns` names a protected path needs `#@ \preserves`, else hard error. |
| 4 | HAPPY (parametric) | `#@ happy <name>(<p>): protects <path>[LO : HI] [except …]` (07-1143 R3) | Module-level | Per-object confinement: `LO`/`HI` may use the bound `<p>`. A method binds it with `#@ footprint <name>(arg)`; each write `<path>[i]=v` gets `#@ check (LO[p:=arg] <= i and i < HI[p:=arg])` (CONTAINMENT — composed with an indexed `assigns` frame this gives per-object preservation). A non-exempt method with no `footprint` writing the path is forbidden (`check False`). |
| 5 | Footprint | `#@ footprint <name>(<arg>)` | Function/method | Binds the parameter of the parametric HAPPY `<name>` to the method's own argument `<arg>`, so the per-site region check (row 4) is specialised to the object this method operates on. |
| 6 | HAPPY (reads / H-I1) | `#@ happy <name>:` block (`region LO .. HI` / `reads self.<field> outside region` / optional `except m1, …`) | Module-level | **Read confinement** (the read mirror of row 1). Every READ `self.<field>[i]` (point or slice) in any method **not** in `except` must lie outside `[LO, HI)`. Expands to a per-READ-site `#@ check ({i}) < LO or ({i}) >= HI`. Aliasing the protected field into a non-exempt local (`x = self.<field>`) is a hard error (a read through the alias would evade the check); a non-exempt `\trusted`/`\abstract` method (no checkable body) must be in `except`. The C sibling (macsl) expresses this as `\context(\reading)`. Drivers `0715` (positive) / `0716`–`0718` (negatives). |
| 7 | HAPPY (targets/postcond) | `#@ happy <name>:` block (`targets <method>` / `postcond <expr>`) | Module-level | The general **named-postcondition** form (macsl's `\targets(<m>), \context(\postcond)`). Attaches `<expr>` to `<method>` as an `ensures`, verified in the method's own body. Powers **H-R** (`nonrepud_complete`/`_append_only`) and **H-E** (`priv_monotonic`). A missing `targets` method is a hard error. Drivers `0719` (positive) / `0720` (negative). |
| 8 | HAPPY (targets/precond / H-S) | `#@ happy <name>:` block (`targets <method>` / `precond <expr>`) | Module-level | **Check-before-use capability** (macsl's `\targets(<m>), \context(\precond)`). The target ASSUMES `<expr>` (a precondition on its body); every **call site** must PROVE it — the meta-pass injects `#@ check <expr>` before each `self.<method>(…)` (PyCSL has no WP-style automatic call rule for the abstract self-call stub, so the obligation is injected, equivalent to macsl's WP call-site precondition). A caller that skipped the grant fails IN THE CALLER. Powers **H-S** (`authn`). Drivers `0721` (positive) / `0722` (negative). *Currently injected at `self.<method>(…)` self-call sites; receiver-var call sites are a follow-up.* |
| 9 | HAPPY (targets/total / H-D) | `#@ happy <name>:` block (`targets <method>` / `total`) | Module-level | **Totality / availability** (macsl's `\context(	otal)`). Names PyCSL's default-on termination guarantee (Why3 emits a termination VC; each loop needs a `#@ loop variant`) and forbids the only opt-out: `#@ \diverges` on the target is a hard error. An unbounded (variant-less) loop fails its termination VC — the non-termination/DoS the policy excludes. Powers **H-D** (`availability`). Drivers `0726` (positive) / `0727`–`0728` (negatives). |
| 10 | HAPPY (noninterference / H-I2) | `#@ happy <name>:` block (`targets <method>` / `noninterference secret <p1>, …`) | Module-level | **Noninterference** (macsl's `\context(
oninterference)`). The meta-pass SYNTHESIZES a self-composition twin `<method>__selfcomp` that calls `<method>` twice — public params shared, the listed `secret` params split `_a`/`_b` — and asserts the two results are equal. Discharged modularly from `<method>`'s result-`ensures`: a result that depends on a secret makes `ra == rb` unprovable (a leak). Not a new relational WP mechanism — a synthesized 1-safety driver, exactly macsl's `emit_selfcomp`. Powers **H-I2**. Drivers `0729` (positive) / `0730` (negative). |

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

### 2.8 Module-level inductive predicate (`#@ inductive`)

A `#@ inductive` declares a **least-fixpoint relation** by Horn-clause rules (a property that
is *not* a terminating boolean function — well-formedness, reachability, typing). It is
**logic-only** (usable in `requires`/`ensures`/loop invariants/lemmas, never executable). Why3
derives introduction, inversion, and induction principles.

```python
#@ inductive even(n: int):
#@     even_zero: even(0)
#@     even_step: \forall m: int; even(m) ==> even(m + 2)
```

| # | Directive | Syntax | Scope | Semantics |
|---|---|---|---|---|
| 1 | Inductive | `#@ inductive <p>(<params>):` then rules `<name>: <horn-clause>` 4-space-indented under it | Module-level | Declares predicate `<p>` by its Horn-clause rules. Each rule body is an ordinary PyCSL contract expression — `\forall m: int; even(m) ==> even(m + 2)` reuses the typed-quantifier + implication + predicate-application grammar; the conclusion must apply the predicate being defined. The indentation groups the rules (there is **no** `rule` keyword — retired). Lowers to a Why3 `inductive p t1 … = | Rule : clause …` (no closing `end` for a single predicate). |

- **Usage.** `even(k)` is a predicate application usable in any contract (`#@ ensures even(4)`).
  Introduction discharges `even(4)` (even(0)→even(2)→even(4)); inversion proves `not even(<odd>)`.
  A **universally-quantified consequence** — a fact true of EVERY value of the predicate,
  `\forall n; even(n) ==> P(n)` — is proved by **induction on the derivation**: state it as a
  `#@ lemma` whose `ensures` is the consequence; PyCSL drives Why3's `induction_pr` transformation
  (after `split_vc` introduces the `even n` premise) for any module declaring an inductive predicate.
  The SMT backend alone cannot do this (it would invent the induction and time out). Inductive
  predicates + `#@ lemma` are a pair (driver `0581`).
- **Mutually-inductive groups.** A `with <q>(<params>):` continuation block (same indentation as the
  `inductive` header, its rules indented under it) joins `q` into the same least-fixpoint group, so
  rules of `p` and `q` may reference each other. The whole group lowers to one Why3
  `inductive p … = | … with q … = | …` (still no closing `end`):
  ```python
  #@ inductive even(n: int):
  #@     even_zero: even(0)
  #@     even_succ: \forall m: int; odd(m) ==> even(m + 1)
  #@ with odd(n: int):
  #@     odd_succ: \forall m: int; even(m) ==> odd(m + 1)
  ```
- **Soundness — strict positivity.** The defined predicate may occur in rule premises only
  *positively* (never under negation or in a nested implication's antecedent), guaranteeing a
  least fixpoint exists. **Why3 enforces this** ("non strictly positive occurrence …") across the
  whole group; a non-positive rule fails. (A cleaner Module-4 pre-check is a documented refinement.)
- **Reflection.** Connect the logic-only predicate to an EXECUTABLE decision function via an agreement
  lemma: a recursive `let function` `p_dec` returning 0/1, and a `#@ lemma` proving
  `p_dec(n) == 1 <==> p(n)` by induction (composing the consequence `p(n) ==> …`, the inversion
  `p(n) ==> … or …`, and the decision function's own recursion). Lets you reason with `p` in specs and
  compute with `p_dec` (driver `0582`).
- **Boundaries.** The relational form (a non-structural, multi-arg predicate like reachability) works
  on this same machinery (driver `0572`). Coinductive predicates are out of scope.

**Test-corpus cross-reference:** `0562` (`even`, introduction proves `even(4)`), `0563`
(non-strictly-positive rule — rejected), `0572` (relational/reachability), `0574` (mutual `even`/`odd`
group), `0575` (non-positive occurrence in a `with`-member — rejected group-wide), `0581`
(universally-quantified consequence via `#@ lemma` + `induction_pr`), `0582` (reflection: decision
function + agreement lemma).

### 2.9 Bounded contract expansion (`#@ for`)

A `#@ for <var> in range(<lo>, <hi>):` block opens a 4-space-indented body of `requires`/`ensures`
clauses and is **bounded macro-expansion**: it desugars (Module3) to the **ground** clauses a human
would otherwise type, one per index, with `<var>` substituted by an integer literal.

```
#@ for k in range(0, 4):
#@     requires 0 <= data[k] and data[k] <= 255
```

desugars to four ground clauses `requires 0 <= data[0] and data[0] <= 255`, … `data[3]`.

| # | Directive | Syntax | Scope | Semantics |
|---|---|---|---|---|
| 1 | For | `#@ for <var> in range(<lo>, <hi>):` then `requires`/`ensures` clauses 4-space-indented under it (one-arg `range(<hi>)` ≡ `range(0, <hi>)`) | Function | Expands to ground clauses: for each integer `m` in the Python range `[lo, hi)` (lower-inclusive, **upper-exclusive**), each body clause with `<var>` replaced by the literal `m`, in iteration-then-body order. **Not** a `\forall` — the output is quantifier-free, so it carries no E-matching cost. **Meaning-preserving**: the generated WhyML is byte-identical to the hand-written clauses (a spelling, not a meaning). |

- **Static bounds (v1).** `<lo>`/`<hi>` must be integer literals; a non-constant bound is a hard,
  fail-loud error (never a silent fallback to `\forall` or to skipping expansion). Named-constant bounds
  (`range(0, NUM_BLOCKS)`) are a staged follow-on.
- **`for` vs `\forall`.** Use `#@ for` for **fixed-size** repetitive clauses (codec bytes, struct
  fields) — readability with ground-clause cost; use `\forall` for **symbolic/unbounded** properties.
- **Errors.** Non-constant bound, empty body, and a body clause not mentioning `<var>` are fail-loud.
- Reference driver: `test-suite/corpus/pycsl-reference/0666.py`.

### 2.10 Contract opacity (`#@ interface` / `#@ reveal`)

Track B (`b-spec.md`): a function may carry **two** contracts — a rich **definition** contract (the
plain `#@ requires`/`ensures`/`assigns`, verified against the body) and a narrow **interface** contract
(what callers/importers see by default). `#@ interface` declares the latter; `#@ reveal` lets a specific
caller opt back into the definition. This is opacity as a feature (the Dafny `{:opaque}`/`reveal`
analogue): the definition's extra facts are hidden behind the interface, so a heavy function (e.g. the
codec's 18 per-field `ensures`) is verified once but only burdens the call sites that reveal it — not
every importer.

```
#@ ensures \result[0]*256 + \result[1] == v   # the rich DEFINITION (verified against the body)
#@ interface ensures \length(\result) == 2     # the narrow INTERFACE callers see by default
def _pack_uint16_be(v: int) -> list: ...

#@ reveal _pack_uint16_be                       # THIS caller opts into the definition's facts
```

| # | Directive | Syntax | Scope | Semantics |
|---|---|---|---|---|
| 1 | Interface | `#@ interface ensures <expr>` / `#@ interface requires <expr>` / `#@ interface assigns <target>` | Function/method | The narrow contract callers/importers see; the rich `#@ requires`/`ensures`/`assigns` is the *definition*. The interface must be a sound **weakening** of the definition — the **narrowing VC** (Module 6, owning unit) emits Why3 goals proving `definition ⟹ interface` for `ensures` and `interface ⟹ definition` for `requires`; an interface claiming *more* than the definition proves is **rejected** (unprovable goal). Absent ⇒ interface = definition (fully transparent; existing code byte-identical). |
| 2 | Reveal | `#@ reveal <fn>` | Statement (at a call site) | This caller opts into `<fn>`'s rich definition contract at this site (its facts are otherwise hidden behind the interface). Within the owning unit it is a no-op (the definition is the visible `let`); across modules it cites the exported definition-fact. |

- **Soundness.** Opacity adds no trust: the narrowing VC proves the exported interface is implied by the
  verified definition, so a caller relying on the interface relies on a fact the definition established.
- **Why it exists.** It dissolves import-stub bloat — the rich contract proves where it is visible, the
  light interface keeps importers cheap, and `#@ reveal` pays the rich cost only where needed.

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
| 24 | `\in_globals(name)` | `InGlobals` | **Introspection (07-1839):** `name` is a statically-declared module binding (function / class / module global / constant). Three-valued, **true-only lower bound**: decided-true (→ `true`) for a declared name; **unknown** otherwise (the world is open — `import`/`exec` inject names), so it lowers to an uninterpreted bool, **never** decided-false. Compile-time knowledge; no runtime `globals()` dict. |
| 25 | `\in_scope(name)` | `InScope` | **Introspection (07-1839 P3):** `name` is a local/parameter bound at this point, via **definite-assignment**. Three-valued: decided-true (→ `true`) if assigned on all paths (a parameter, or a top-level assignment before any branch/return); decided-false (→ `false`) if `name` is neither a parameter nor assigned anywhere; **unknown** (conditionally assigned) → uninterpreted bool. A dynamic `exec`/`eval` havocs the binding set (the decided-false direction is then withheld). |

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
#@ requires \forall x: int in s; x >= 0            # bounded over a set (P3)
#@ ensures \forall o: Account; o.balance >= 0      # over class instances (P4)
#@ ensures \forall i in range(lo, hi); i >= lo     # integer interval (07-1311 Q1)
#@ ensures \forall x in a; x >= 0                  # list elements (07-1311 Q1)
#@ ensures \forall k in d.keys(); k >= 0           # dict keys (07-1311 Q2)
#@ ensures \forall v in d.values(); v >= 0         # dict values (07-1311 Q3)
```

- An **untyped** bound variable (`\forall i; …`) is typed `int` in WhyML output (the
  legacy form, unchanged).
- A **typed** binder `\forall x: T; …` (quantification.md P1) ranges over a scalar
  (`int`/`bool`/`str`/`float`) or a declared `#@ datatype` / class, lowering to
  `forall x : t.`. An unresolved binder type is a hard Module-4 error — never a silent
  `int` default. A datatype binder may appear only in equality and pure observers
  (`\is_ctor`/`\payload` and `assigns \nothing` functions), not arithmetic.
- A **bounded** binder `\forall x [: T] in S; …` (P3) ranges over the members of a set
  `S`; it desugars to `\forall x [: T]; (x in S) ==> …` (`\exists … in S` → `… and …`).
  Set membership lowers to key membership (`Map.get S x`), which instantiates by
  e-matching given an `x in S` hypothesis. (Bounding over a *list* uses positional
  membership and may need a trigger to instantiate.)
- **Collection domains (07-1311).** `\forall i in range([lo,] hi); …` desugars to the direct
  integer bound `lo <= i and i < hi` (no `Array.length`) — the SMT-friendly index form.
  `\forall x in a; …` over a list ranges over its elements (positional membership). For a dict
  `d`: `\forall k in d;` and `\forall k in d.keys();` range over present keys
  (`Map.get d k <> None`); `\forall v in d.values();` ranges over stored values
  (`exists k. Map.get d k = Some v`) — quantification over map values. The two-binder
  `\forall k, v in d.items(); …` binds key and value of every present entry (`forall k. match
  Map.get d k with Some v -> … | None -> true end`). Element/value *membership* forms are
  trigger-limited for non-trivial properties; prefer the `range`/index form when the property is
  index-expressible.
- **Collection-typed binders (07-1311 Q4).** A binder may range over a whole collection:
  `\forall a : list; …` (`array int`, so `\length(a)` / `a[i]` work) and `\forall m : dict; …`
  (`map int (option int)`, so `m[k]` is a `Map.get`). The theory is imported even with no
  array/map locals in the function.
- A **class binder** `\forall o: C; …` (P4, value mode) ranges over instances of class
  `C`; `o.field` is the record field, and `C`'s `#@ class invariant` holds for every
  `o` automatically (it is emitted as a Why3 type invariant) — so the quantifier ranges
  only over invariant-satisfying instances without an explicit guard.
- A **multi-binder** `\forall x, y, …; P` is sugar for nested single binders
  `\forall x; \forall y; … P` (all `int`); `\exists` likewise. (Per-binder types —
  `\forall x: T, y: U;` — are not yet supported; nest explicitly.)
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

**Formal model (Phase 8, LINK 1).** The mechanized semantics models a lambda by
the *defunctionalized* pair `SLambda x param body` (construction — binds a
`VClosure` capturing the defining state) + `SCall` (application), proved sound in
both provers with 0 new axioms (`formal-semantics-completion.md` §2 Phase 8). The
WhyML-`fun` lowering shown here is a **sound lowering of that same construct**;
the tool's `fun` is n-ary while the formal model is single-parameter + currying.
Reference cases: `pycsl-reference/0242` (single-param), `0243` (multi-param),
`0745` (lexical capture) — all Valid. Passing a lambda *as a function argument*
is not supported (a documented Phase-8 non-goal).

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
> (opaque), `.decode`/`.encode` (opaque bytes↔str boundary), f-strings. **A `str`-keyed dict/set is
> now faithful** — `dict[str, ν] ~ map string (option ν)` with the native, injective Why3 string key
> (`String.(=)`, no `str_hash_op`), so distinct keys are provably non-aliasing (cleared-hash.md,
> drivers `0755`–`0758`; κ inferred for `Dict[str,_]` params/locals, string-key literals, and
> string-key usage). A string **set** local is likewise native (`set() ~ map string (option int)`,
> present ≡ `Some 0`): `s.add(x)` and `x in s` agree on the raw string element (`0759`). **Residual:**
> a record *field* dict/set and any non-inferable-key dict keep the `map int` + opaque `str_hash_op`
> fallback (documented, not collision-sound); `hash(s)` as a bare `str→int` stays opaque (`0485`).

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

### §12.4 `Union` / `Optional` / `X | Y` annotations (typing-engagement ty1)

PEP 484 `Union[X, Y]`, PEP 604 `X | Y`, and `Optional[X]` (= `Union[X, None]`)
are **desugared at the front-end normalization seam** into a per-annotation-site
synthesized `type_decl` of kind `variant`:

```python
def f(x: Union[int, str]) -> int: ...   # synthesizes:
# type _union_f_0 = Arm_0_0 int | Arm_1_0 string
```

The variant name is `_union_<func>_<idx>` (per-site, deterministic). `None` arms
become a nullary `Arm_<idx>_None` constructor. `Any` arms are dropped (GT1 —
the static plane refuses gradual consistency; reported in `--soundness-report`).
Arms are de-duplicated (C1a) and ordered by source with `None` last (C1b).

**Static plane (Interpreted):** the variant type reuses the existing `#@ datatype`
machinery — `_variant_types` in functions.py resolves the param/return type, and
preamble.py emits the Why3 `type _union_N = Arm_0 of int | …`. Per-arm VCs (C2
injection, C3 projection) are emitted by `_emit_union_arm_vc`. `if x is None:`
on a Union-typed variable lowers to a constructor-pattern `match` (C5). `isinstance`
narrowing (C6) uses the existing tag machinery. Match exhaustiveness (C9) is
Why3's native check. C8 (no narrowing without a guard) and C11 (dead-arm
reporting) are `core_ir_semantic` well-formedness checks.

**Runtime plane (Shimmed):** `src/pycsl_lib/typ/__init__.py` provides a `Union`
shim with `#@ ensures \result == val` — identity, no validation (R1–R8, D4
no-blend). The static clauses are NOT discharged by the shim.

**Return-value auto-injection:** a function returning `Optional[int]` whose body
returns an `int` auto-injects into the matching arm constructor (`Arm_0_0 (expr)`).

**Tests**: 0349 (Optional[int] param), 0350 (Union[int, None] param).

### §12.5 `sorted` builtin

`sorted(arr)` emits an abstract `val sorted_1 (a: array int) : array int`
carrying three **definitional `ensures`** (cleared-array.md S5) — discharged
where `sorted` is used, NOT a global axiom:

* `Array.length result = Array.length a`;
* adjacent sortedness `forall i. 0 <= i < len-1 -> result[i] <= result[i+1]`
  (the exact formula `\is_sorted(result, 0, \length(result))` lowers to);
* `permut result a` (the SAME uninterpreted `permut` predicate that
  `\permutation(result, a)` lowers to).

So a driver CAN prove that `sorted`'s result is sorted and a permutation of the
input (test 0760). The conjunction is satisfiable ⇒ no vacuity; adding `ensures`
to an abstract val is monotone ⇒ cannot regress a prior opaque proof.

`any(arr)` and `all(arr)` emit similar abstract vals returning `bool` (no
result axioms).

**Tests**: 0351, 0760.

### §12.5a Content-faithful list comprehensions

A list comprehension `[elt for t in src (if cond)]` is content-faithful when
the element is a pure `int` expression over the loop target only — identity
`[x for x in a]` gives `result[i] == a[i]`, and `+ - *` arithmetic
`[x + 1 for x in a]` gives `result[i] == a[i] + 1`, both with
`\length(result) == \length(a)`. A filter `[x for x in a if …]` keeps only the
sound bound `\length(result) <= \length(a)`. Unliftable element shapes
(calls, projections with captured locals, string/seq elements, multi-generator)
and set/dict comprehensions stay opaque — never a false content claim
(cleared-array.md S1–S4).

**Tests**: 0761 (identity), 0762 (arithmetic), 0763 (filter bound),
0764 (NEGATIVE — false content claim rejected).

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

### §12.9 `Literal[v1, ..., vn]` annotations (typing-engagement ty1)

PEP 586 `Literal[v1, ..., vn]` is **desugared at the front-end normalization seam**
into a per-annotation-site synthesized **ground `requires` clause** (parameters) or
**ground `ensures` clause** (return):

```python
def f(x: Literal[1, 2]) -> int: ...   # synthesizes:
# requires { x = 1 \/ x = 2 }
```

The parameter's WhyML type stays the literal's base type (`int` for
`Literal[1, 2]` / `Literal[True]` / `Literal[None]`; `string` for `Literal["a","b"]`),
so `def f(x: Literal[1, 2]) -> int` lowers to
`let f (x: int) requires { x = 1 \/ x = 2 } = ...`. This reuses the EXISTING
`requires` / `ensures` IR list and the existing `BinOp`(`or`)/`==`/`Number`/
`String`/`Bool`/`None` IR expression nodes — **no new IR node, no IR_VERSION
bump, no new VC kind.** The `Literal[v]` degenerate single-value case (L5b)
synthesizes a bare `requires { x = v }` (no `\/` wrapper).

**Supported literal kinds (L4):** `int`, `str`, `bool` (→ 1/0), `None` (→ 0).
**Rejected (L4a):** `bytes` literals (`Literal[b"x"]`) — a static error with a
clear message, raised at normalization time. **Rejected (L5c):** nested
`Literal[Literal[...]]` and any non-literal form (`Literal[Color.RED]` — L4b
Enum, out of scope). **Rejected (sound stricter-than-S1):** mixed-kind literals
(`Literal[1, "a"]`) — PyCSL's parameter type-tag system is monomorphic (a
parameter has one WhyML type; Why3 has no `int \/ string` sum without a
constructor). The two-plane spec §1.6 permits sound expressibility to be
stricter than S1; this is that strictness.

Arms are de-duplicated (L5a) and source order is preserved (L5 — order is
irrelevant for the static judgment, since the disjunction is commutative).

**Static plane (Interpreted):** the synthesized `requires`/`ensures` IS the VC
— Why3 discharges it as a standard precondition/postcondition goal. L2
(narrowing by equality — `if x == 1:`) is emergent from the standard
path-condition VC on the existing `if x == v` lowering (no new node — the
disjunction is in the precondition, the path condition is the runtime `==`
test, and Why3's precondition-preservation-on-branch refines the disjunction on
each branch). L3 (match/if-chain exhaustiveness) is emergent from the existing
postcondition VCs. **No new `core_ir_semantic` check** beyond the L4a/L5c
normalization-time rejections.

**Runtime plane (Shimmed):** `src/pycsl_lib/typ/__init__.py` provides a
`Literal(*args, val)` shim with `#@ ensures \result == val` — identity, no
validation (LR1–LR8, LD3 no-blend). The static L1 value-set obligation is NOT
discharged by the shim (it is a precondition VC, invisible to the runtime).

**No GT gap** is tagged for `Literal` — the literal value set is finite,
enumerated, and decidable (the two-plane spec §4 confirms full soundness).

**Tests**: 0731 (witness — `Literal[1, 2]` param), 0732 (L2 narrowing),
0733 (negative — `Literal[b"x"]` rejected, L4a).

### §12.10 `Final[T]` annotations (typing-engagement ty1)

PEP 591 `Final[T]` (and bare `Final`) is **lowered at the front-end
normalization seam** to the degenerate single-attribute, single-writer form of
HAPPY's no-write confinement. The annotation's *type* is the inner type `T`
(F3 — no narrowing): `_normalize_final_annotation` recognizes `Final[T]`
(Subscript value=Name "Final") and bare `Final` (Name "Final"), returns `τ(T)`
(or `"Any"` for bare `Final`), and records the name in a per-module
**final registry** plumbed as `program_ir["final_registry"]` (omitted when
empty → byte-identical for Final-free modules). The write-policy itself is a
**static-semantics check** in `core_ir_semantic._check_final` (a syntactic
write-site walk over the IR body, NOT a VC):

```python
x: Final[int] = 5           # F1: module-level — write-once at declaration.
def f() -> int: return x    # a read; the declaration write is at module scope.

class C:
    attr: Final[int]        # F2: instance attribute — __init__-only writes.
    def __init__(self):
        self.attr = 0        # the single permitted write (modelled via the
                             # record's field_defaults / init_body path, NOT
                             # as a function-body statement).
```

**Static plane (Interpreted):** `_check_final` reuses HAPPY's no-write
confinement *pattern* (a write-site walk) in its degenerate single-attribute,
single-writer form. F1 (module-level Final — write-once): any `Assign`/
`AugAssign` to a registered module-level Final name in a function body →
`PyCSLSemanticError` (the declaration write is at module scope, not a function
body, so it is naturally not flagged). F2 (instance-attribute Final —
`__init__`-only): any `FieldAssign`/`FieldAugAssign` to `self.<attr>` (a
registered class_attr Final) in a function body → `PyCSLSemanticError`
(`__init__` is a dunder, skipped from `ir["functions"]`, so any function-body
write is by definition outside `__init__`). F3 (no narrowing) is satisfied by
construction — the type tag is `T`, not a refined type; no narrowing VC is
emitted. F2b (subclass `__init__` writes) is a documented strictness gap
(`27-0000-typing-spec-3` §6): a subclass `D(C)`'s `__init__` write to
`self.attr` is NOT flagged (dunders are skipped), a soundness-preserving
under-approximation.

**Runtime plane (Shimmed):** `src/pycsl_lib/typ/__init__.py` provides a
`Final(x0, x1, val)` shim with `#@ ensures \result == val` — identity, no
validation (FR1–FR6, FD2 no-blend). It is explicitly NOT a write-guard
descriptor — introducing one would blend the planes (FR6). The static
write-policy is NOT discharged by the shim (it is a semantic check,
invisible to the runtime).

**No new IR node, no IR_VERSION bump, no new VC kind.** The final registry is
an additive module-level metadata key (`program_ir["final_registry"]`); Module
6 ignores it, so emission is byte-identical for every Final-free driver.

**No GT gap** is tagged for `Final` — the write-restriction is a syntactic
write-site check (decidable by construction; the two-plane spec §4 confirms
full soundness).

**Tests**: 0734 (F1 witness — module-level Final), 0735 (F1 negative —
reassignment rejected), 0736 (F2 witness — instance-attr Final), 0737 (F2
negative — write outside `__init__` rejected).

### §12.11 `-> NoReturn` annotations (typing-engagement ty1)

PEP 484 `-> NoReturn` is **lowered at the front-end normalization seam** to a
`false` postcondition: the function never returns normally (it raises or
diverges). `_build_function_ir` recognizes `NoReturn` (Name "NoReturn") and
`typing.NoReturn` (Attribute `typing.NoReturn`) in the return annotation and
sets the IR flag `is_noreturn: true` (a new optional `FunctionIR` field, IR
v1.3 — emitted ONLY when true, so every non-NoReturn driver stays
byte-identical). Module 6 emits `ensures { false }` (NR1) — the same goal
shape the non-vacuity gate INJECTS, which is the crux of NR4.

```python
def f() -> NoReturn:        # NR1: lowers to `ensures { false }`
    raise Exception()       # NR2a: body raises (no normal exit) — justified

def g() -> NoReturn:
    while True: pass        # NR2a: body diverges — justified

def caller() -> int:
    f()
    return 1                # NR3: dead code — unreachable (f never returns)
```

**Static plane (Interpreted):**
- **NR1** (`ensures { false }`): Module 6 (`functions.py:_emit_contracts`)
  emits the `false` postcondition when `is_noreturn` is true. The VC discharges
  by the ABSENCE of a normal-exit path (the body raises or diverges), not by an
  inconsistent context.
- **NR2a** (body supports divergence): `core_ir_semantic._check_noreturn`
  rejects a NoReturn function whose body contains a `return` statement (a
  normal-exit path) OR whose body has no `raise` and no diverging construct
  (`While`/`For`/`CriticalSection`/`Call`) — it provably falls off the end. A
  conservative sound under-approximation (stricter than S1 is permitted).
- **NR3** (unreachable successor): `core_ir_semantic._check_noreturn_successors`
  flags any statement following a call to a NoReturn function as dead code
  (the callee's `false` postcondition makes the continuation contradictory).
- **NR4** (vacuity-gate exemption): the non-vacuity gate
  (`pycsl.py:_run_vacuity_gate`) EXEMPTS declared-NoReturn functions from the
  vacuity probe. The exemption is KEYED ON THE `-> NoReturn` ANNOTATION (the IR
  `is_noreturn` flag), NOT on the inferred `false` postcondition — the latter
  would exempt every genuinely-vacuous function, defeating the gate. A
  genuinely-vacuous function (inconsistent context, no NoReturn) is still
  probed and flagged.

**Runtime plane (Shimmed):** `src/pycsl_lib/typ/__init__.py` provides a
`NoReturn` alias object (a module-level constant) — introspectable, NO
enforcement (NR-R1–NR-R5, NR-D2 no-blend). The runtime does NOT enforce
divergence (NR-R3 — the central negative sentence: annotations are not
enforced). The static `false` postcondition is NOT discharged by the shim.

**IR_VERSION bump (1.2 → 1.3, additive).** The `is_noreturn` field is a new
optional `FunctionIR` field; it is ABSENT on non-NoReturn functions (the
emitter emits it only when true), so a `"1.0"`/`"1.1"`/`"1.2"` IR without it
remains byte-identical and ingestable. `"1.3"` is added to
`ACCEPTED_IR_VERSIONS`; older versions are kept.

**No GT gap** is tagged for `NoReturn` — the `false` postcondition is a genuine
proof obligation (the function must be shown to diverge or raise), not an
unsoundness. The NR4 vacuity-gate exemption is a gate-precision concern, not a
soundness gap.

**Non-vacuity gate ON BY DEFAULT (fail-closed; non-lin-int-div-fixed.md).** After
a file verifies, each body-bearing function is re-probed with an injected
`ensures false` (`split_vc`, per normal-exit path); a function VACUOUS on ALL
exits FAILs the run — closing the silent false-green from an inconsistent
context (e.g. the SMT nonlinear-integer-division vacuity). `-> NoReturn` and
`#@ \diverges` are EXEMPT (their sound green is expected-vacuous on the
unreachable normal exit). Opt out with `--no-check-vacuity`; `--no-proof` also
skips it. See `docs/pycsl-static-semantics-reference.md` §NR4.

**Tests**: 0738 (NR1/NR2a witness — `-> NoReturn` raises), 0739 (NR2a negative
— `-> NoReturn` with `return` rejected), 0740 (NR3 negative — dead successor
rejected), 0741 (NR4 — NoReturn passes `--check-vacuity`), 0752 (non-vacuity
gate self-test — an inconsistent-context function FAILs under the default gate,
PASSes with `--no-check-vacuity`).

### §12.12 `TypedDict` annotations (typing-engagement ty2)

PEP 589 `class Point(TypedDict): x: int; y: int` (and the functional form
`Point = TypedDict("Point", {"x": int, "y": int})`, plus PEP 655
`Required[T]`/`NotRequired[T]` per-key totality and `total=False` class-level
totality) is **lowered at the front-end normalization seam** to a record
`type_decl` with one field per declared key. Per the two-plane spec
(`typing-engagement/ty2/typeddict-twoplane-spec.md`) and the core-agent hard
rule (`typing-global-impl.md` §5, TY2): a TypedDict class synthesizes a WhyML
record `type td = { x: int; y: int }`, field access `p["x"]` becomes
record-field access `p.x`, and construction `{"x": 1, "y": 2}` becomes a
record literal.

**Normalization** (`Module5_IREmitter._emit_typeddict_record`): the
`visit_ClassDef` seam recognizes `class X(TypedDict)` (a base name `TypedDict`)
and dispatches to `_emit_typeddict_record`, which walks the class body's
`AnnAssign`s (the `x: int` field declarations) and emits a record `type_decl`
with one field per declared key (field types resolved via the existing
Union/Optional/Final/Literal-aware resolver `_field_type_from_annotation_inst`).
Per-key totality (PEP 655) and class-level totality (`total=False`) apply:
a not-required key's type is `Optional[T]` (reusing the TY1 Union variant
synthesis). The record carries NO `__init__`, NO class invariants, NO bases —
it is a pure data record. An optional `is_typeddict: True` field on the
record `type_decl` gates Module 6's subscript/literal lowering paths
(backward-compatible: defaults `False`, so NO IR_VERSION bump). For any class
that is NOT `class X(TypedDict)`, `visit_ClassDef` proceeds unchanged
(byte-identical emission for every non-TypedDict driver).

**Field access lowering** (`module6_whyml/expressions._typeddict_field_access`,
invoked from `_handle_subscript`): a string-literal subscript `p["x"]` on a
TypedDict-record-typed receiver lowers to a record-field read `p.x` (via the
existing `_field_label`). Why3 type-checks the field's declared type natively
(T5/T6). A non-literal index or an unknown key falls through to the opaque
`subscript_get` path (Why3 rejects — static error). Non-TypedDict receivers
fall through unchanged (byte-identical).

**Construction lowering**
(`module6_whyml/expressions._typeddict_record_literal`, invoked from the
`DictLit` branch of `_expr_to_whyml`): a dict literal `{"x": 1, "y": 2}` in a
TypedDict construction context (the enclosing function's return type is a
TypedDict record) lowers to a record literal `{ x = 1; y = 2 }` in declaration
order. Why3 type-checks each field's value against the declared type and
rejects missing/extra fields natively (T8/T9). Non-TypedDict dict literals fall
through to the existing empty-map stub (byte-identical).

**Static-semantics check** (`core_ir_semantic._check_typeddict_access`):
walks the body IR for `Subscript` nodes whose receiver is a TypedDict-record-
typed variable and flags a warning when the index is non-literal (T5 requires
literal keys). Why3 rejects the access at type-check; this surfaces the issue
earlier. Only fires on functions with a TypedDict-typed variable (zero impact
on every existing driver).

**Runtime shim** (`src/pycsl_lib/typ/__init__.py.TypedDict`): a thin shim
exposing the introspectable `TypedDict` class object with `#@ ensures \result
== val` — identity, no validation (R1–R8, D4 no-blend). A TypedDict instance IS
a plain dict at runtime (S4); the shim does NOT construct instances, only the
class object. The static record-shape obligation is NOT discharged by the shim
(it is Why3 record-type-checking, invisible to the runtime). The class form
`class Point(TypedDict)` is lowered at the front-end seam — it never reaches the
shim; the functional form `Point = TypedDict(...)` reaches the shim as an
opaque identity call.

**GT7** (analogous, NOT a new code) — D3 documents the
`isinstance`-against-TypedDict asymmetry: the static T2 record-shape
obligation must NOT be discharged by any runtime `isinstance`/presence check
(R4 raises `TypeError`; even `"x" in p` is the dict-plane behaviour, not the
static record-shape judgment). Tagged in the report as a
`no_blend_typeddict_isinstance` note.

**GT-T2-future** (out of scope) — cross-TypedDict structural subtyping (a
TypedDict with a superset of keys assignable to one with a subset) is flagged
for a future TY2 enhancement. This delivery limits T2 to same-named
assignability.

**Tests**: see the typing-engagement `ty2/conformance/` S5 subset + S4 shim
drivers (authored by the conformance-agent, never the core-agent).

### §12.13 `NamedTuple` annotations (typing-engagement ty2)

PEP 526 `class Point(NamedTuple): x: int; y: int` (and the functional form
`Point = NamedTuple("Point", [("x", int), ("y", int)])`, per PEP 484) is
**lowered at the front-end normalization seam** to a record `type_decl` with
one field per declared key, in declaration order (positional index is
significant). Per the two-plane spec
(`typing-engagement/ty2/namedtuple-twoplane-spec.md`) and the core-agent hard
rule (`typing-global-impl.md` §5, TY2): a NamedTuple class synthesizes a WhyML
record `type nt = { x: int; y: int }` (reusing the TypedDict record seam),
named field access `p.x` becomes record-field access, positional access
`p[0]` becomes record-field access by index, and construction `Point(1, 2)`
becomes a record literal.

**Normalization** (`Module5_IREmitter._emit_namedtuple_record`): the
`visit_ClassDef` seam recognizes `class X(NamedTuple)` (a base name
`NamedTuple`) and dispatches to `_emit_namedtuple_record`, which walks the
class body's `AnnAssign`s (the `x: int` field declarations, in declaration
order) and emits a record `type_decl` with one field per declared key (field
types resolved via the existing Union/Optional/Final/Literal-aware resolver
`_field_type_from_annotation_inst`). A field with a default (`x: int = 0`,
N1b) populates `field_defaults`; a field without a default is a required
positional argument (N7 — wrong arity is a static error). The record carries
`init_params` (field names in order) and `init_body` (each field set from its
same-named param) so positional construction `Point(1, 2)` reuses the EXISTING
Tier-A parametrized record construction (`_call_record_constructor`). The
record carries NO `__init__`, NO class invariants, NO bases — it is a pure
data record. An optional `is_namedtuple: True` field on the record
`type_decl` gates Module 6's positional-subscript lowering path
(backward-compatible: defaults `False`, so NO IR_VERSION bump). For any class
that is NOT `class X(NamedTuple)`, `visit_ClassDef` proceeds unchanged
(byte-identical emission for every non-NamedTuple driver). The pre-existing
`_synthesize_namedtuple_records` (functional `collections.namedtuple` form,
all-int fields) is NOT modified — it handles a different factory.

**Named field access lowering** (the EXISTING
`module6_whyml/expressions._handle_attribute_expr` path): a NamedTuple-
record-typed param is added to `_record_locals` by `_param_type_str`, so
`p.x` emits `p.x` (a record-field read). Why3 type-checks the field's declared
type natively (N4). An unknown attribute (`p.z`) is a Why3 type error (the
field doesn't exist). Non-NamedTuple receivers fall through unchanged
(byte-identical).

**Positional access lowering**
(`module6_whyml/expressions._namedtuple_positional_access`, invoked from
`_handle_subscript`): an integer-literal subscript `p[0]` on a NamedTuple-
record-typed receiver lowers to a record-field read of the field at that
declaration index (`p[0]` → `p.x`, `p[1]` → `p.y`). Why3 type-checks the
field's declared type natively (N5). An out-of-range index (`p[2]` on a
2-field Point) falls through to the opaque `subscript_get` path (Why3
rejects — static error). A non-literal index falls through unchanged (Why3
rejects — static error). Non-NamedTuple receivers fall through unchanged
(byte-identical).

**Construction lowering** (the EXISTING
`module6_whyml/expressions._call_record_constructor` path): a positional call
`Point(1, 2)` with `init_params` matching arity emits a record literal
`{ x = 1; y = 2 }` in declaration order. Why3 type-checks each field's value
against the declared type natively (N6).

**Static-semantics check** (`core_ir_semantic._check_namedtuple_access`):
walks the body IR for `Subscript` nodes whose receiver is a NamedTuple-record-
typed variable and flags a warning when the index is non-literal (N5 requires
literal indices). Why3 rejects the access at type-check; this surfaces the
issue earlier. Also walks for `Call` nodes to a NamedTuple constructor and
raises a hard `PYCSL-SEM-NAMEDTUPLE-ARITY` error when the call arity is wrong
(N7 — a NamedTuple's fields are required positional arguments unless they
have a default). Only fires on functions with a NamedTuple-typed variable or
a NamedTuple constructor call (zero impact on every existing driver).

**Runtime shim** (`src/pycsl_lib/typ/__init__.py.NamedTuple`): a thin shim
exposing the introspectable `typing.NamedTuple` class object with
`#@ ensures \result == val` — identity, no validation (R1–R9, D4 no-blend). A
NamedTuple instance IS a plain tuple at runtime (S4); the shim does NOT
construct instances, only the class object. The static record-shape obligation
is NOT discharged by the shim (it is Why3 record-type-checking, invisible to
the runtime). The class form `class Point(NamedTuple)` is lowered at the
front-end seam — it never reaches the shim; the functional form
`Point = NamedTuple(...)` reaches the shim as an opaque identity call.

**GT7** (analogous, NOT a new code) — D3 documents the
`isinstance`-against-NamedTuple asymmetry: the static N2 record-shape
obligation must NOT be discharged by any runtime `isinstance`/tuple-shape
check (R4 is a tuple-ness check, not a type-enforcement check). Tagged in the
report as a `no_blend_namedtuple_isinstance` note.

**Tests**: see the typing-engagement `ty2/conformance_nt/` S5 subset + S4 shim
drivers (authored by the conformance-agent, never the core-agent).

### §12.15 `Protocol` / `@runtime_checkable` / `#@ conforms_to` annotations (typing-engagement ty2)

**Surface** (PEP 544 / S2, resolved by S1): `class P(Protocol): ...` declares a protocol
class whose body is one or more method-signature members `def m(self, ...) -> R: ...`
(each the refinement target). `@runtime_checkable` decorates a protocol to opt it into
runtime `isinstance`/`issubclass` support (a RUNTIME-plane marker — it has NO static
effect). `#@ conforms_to P1, P2, …` (a class-level directive, parallel to `#@ compose_from`)
declares that a class conforms to the named protocols, synthesizing per-method contract-
refinement VCs.

**Static plane** (Interpreted): `class P(Protocol)` synthesizes a contract interface
(P1): a marker record (`is_protocol: True`, no fields) + each member emitted as an
`abstract: True` function (a bodyless `val` with its contract — the refinement target,
P1a). The `#@ ensures/requires/assigns` on a member is the refinement TARGET. Conformance
`C conforms to P` (declared via `#@ conforms_to P`) populates the EXISTING `overrides` IR
list with `(C__m, P__m)` pairs; `--check-behavioral-subtyping` emits the per-method
refinement goal `((pre_P -> pre_C) /\\ (post_C -> post_P))` (P2/P4 — per-method
behavioural refinement, NOT attribute presence). A class missing a member raises a static
error (P3); a non-refining contract makes the goal unprovable (P3). PEP 544 conformance is
structural/implicit; PyCSL's TY2 scope requires the explicit `#@ conforms_to` directive
(divergence-by-strictness — an implicit structural search is outside the per-module
verification model). NO `\trusted`; NO IR_VERSION bump (reuses the EXISTING `abstract`
function flag + the EXISTING `overrides` IR list + the EXISTING refinement-goal emitter).

**Runtime plane** (Shimmed): `@runtime_checkable` makes `isinstance(x, P)` check attribute
PRESENCE ONLY (S3/S4 — a `hasattr` loop over member names; NOT signature, NOT contract,
NOT attribute type). The `src/pycsl_lib/typ/__init__.py.runtime_checkable` shim is a thin
identity (`ensures \result == val`) that performs NO validation (R1–R7) — it does NOT
model the `hasattr` loop (a runtime attribute-presence check is outside the TY2 verified
surface).

**NO-BLEND** (D1, THE canonical GT7 trap): the static conformance obligation (P2/P4) is a
per-method contract-refinement VC — a WhyML formula over the two method contracts,
discharged by Why3/SMT. It must NOT be discharged by the runtime `@runtime_checkable`
`isinstance` presence check (R3 is attribute presence, a value check, NOT the contract-
refinement type judgment). The refinement goal is a spec formula; the runtime `hasattr` is
a value check — different WhyML terms. The keystone witness: a class with method PRESENCE
(passes runtime isinstance) but a NON-refining contract FAILS static conformance — the
runtime presence cannot rescue the static refinement VC. Tagged in the report as a
`no_blend_protocol_presence` note.

**Tests**: see the typing-engagement `ty2/conformance_proto/` S5 subset + S4 shim
drivers (authored by the conformance-agent, never the core-agent).

### §12.14 `@overload` annotations (typing-engagement ty2)

**Surface** (PEP 484 / S2, resolved by S1): an `@overload` family is a sequence of
N ≥ 1 `@overload`-decorated stubs `@overload def f(p_i: T_i) -> R_i: ...` (each with a
literal `...` / `pass` body) followed by exactly one non-`@overload` implementation
`def f(p) -> R: <body>`. A stub's `#@ ensures Q_i` must PRECEDE the `@overload` decorator
(the standard CSL contract-placement convention — a `#@` between `@overload` and `def`
lands on the decorator line, not the `def` line).

**Static plane** (Interpreted): an `@overload` family is a **guarded contract family**
(O1–O6). Each stub synthesizes a **guard** `G_i = isinstance(p_i, T_i)` — the same type-
predicate vocabulary the body-level `isinstance` lowering uses (`_handle_isinstance` →
`(subtag <typeof p_i> <T_i tag>)`, a WhyML bool). For each stub carrying `#@ ensures Q_i`,
a **guarded postcondition** `ensures { G_i ==> Q_i }` is synthesized and attached to the
single implementation (`contracts.ensures`), where `==>` is the implication operator
(parsed by `Module2_Parser` IMPL_OP, lowered to WhyML `->` by `identifiers.py`). The
implementation's body proves each `G_i ==> Q_i` under the guard assumption (O6 — the
guarded contract family proved against the single implementation). At a call site `f(v)`,
the argument's static type selects the active overload by type-based assignability (O4) —
native Why3 type-checking when the implementation's parameter is typed. For the guard to
be a **decided** type judgment (not a symbolic `typeof_op` placeholder), the
implementation's parameter must carry a type annotation (a TY2 scope restriction —
divergence-by-strictness; an unannotated implementation yields a symbolic guard, sound but
imprecise). The stubs themselves are NOT emitted as functions (their `...` body is
discarded — R1). NO `\trusted`; NO IR_VERSION bump (reuses the existing `contracts.ensures`
list + the existing `==>` / `isinstance` IR shapes).

**Runtime plane** (Shimmed): `@overload` stubs are discarded at runtime (S3/S4 — the
decorator returns `_overload_dummy` which raises if called; the implementation is a plain
function). `get_overloads` returns the registered stubs (introspection only). The
`src/pycsl_lib/typ/__init__.py.overload` shim is a thin identity (`ensures \result == val`)
that performs NO validation (R1–R7) — it does NOT model the implementation's isinstance
branches (those are body code, lowered through the existing statement path).

**NO-BLEND** (D1, the load-bearing trap): the static overload-selection obligation (O4/O5)
is a **type-based VC** — the argument's static type against the stub's parameter type,
discharged by Why3/SMT over the guard formula `subtag (typeof p_i) T_i`. It must NOT be
discharged by the implementation's runtime `isinstance` dispatch (R4 is value dispatch, a
runtime check on the value, NOT the type judgment). The guard is a WhyML *spec formula*
(over the parameter's type tag, decided from Γ's τ); the runtime `isinstance` is *body
code* (a value check). They are different WhyML terms — the runtime isinstance cannot
satisfy the static selection VC. Tagged in the report as a `no_blend_overload_isinstance`
note.

**Tests**: see the typing-engagement `ty2/conformance_ovl/` S5 subset + S4 shim
drivers (authored by the conformance-agent, never the core-agent).

### §12.16 `TypeVar` / `Generic` / PEP 695 type-parameter annotations (typing-engagement ty3)

**Surface** (PEP 484 + PEP 695 / S2, resolved by S1): `class C[T]: ...`, `def
f[T](): ...`, `T = TypeVar("T", bound=B)` + `class C(Generic[T])`. A generic
class/function parameterized by a type variable `T`.

**Static plane** (Interpreted): whole-module monomorphization. The
`frontend/monomorphize.py` step-5 IR-resolution pass COLLECTs concrete
instantiation sites (`C[int]()`, `x: C[int]`), and EMITs ONE name-mangled
specialized WhyML `let`/`val` per `(generic, concrete-type)` pair with `T`
substituted (`Stack` → `Stack_int`, `stack__push` → `stack_int__push`). The
TypeVar bound (`T: B`) is an instantiation-time obligation (the concrete type
must satisfy the bound — invariant checking, GT2). `ParamSpec`/`TypeVarTuple`
are schema-only loud-fails (GT3). Polymorphic recursion (`f[T]()` inside
`f[T]`) is a loud-fail (GT4). `Any` as a type argument is refused (GT1).
Variance is deferred (GT2 — invariant checking). An un-instantiated generic
emits NO specialized copy and is recorded Ignored/GT8.

**Runtime plane** (Shimmed): `TypeVar("T", bound=B)` constructs an
introspectable object (`__bound__`); `Generic[T]`/`C[int]` constructs a
`GenericAlias`; the bound is NOT checked at runtime (S3's negative sentence).
The shim is identity, no enforcement.

**Divergence / no-blend (D1)**: the static per-instantiation theorem
(`Stack_int.pop` returns `int`, provable because the int specialization was
emitted) vs the runtime generic-alias object (`Stack[int]` is a GenericAlias,
NO specialized proof). An un-instantiated generic must NOT claim a per-instance
theorem it never emitted — the coherent-and-wrong trap, typing edition.

**Tests**: see the typing-engagement `ty3/conformance/` S5 subset + S4 shim
drivers (authored by the conformance-agent, never the core-agent). Single-
instantiation path proves 10/10 VCs (the feasibility-probe shape); the
multi-instantiation Module 6 field-mangling gap is recorded in
`typing-engagement/ty3/33-1700-typing-gap-9.md`.

### §12.17 `Callable` (PEP 484) annotations (typing-engagement ty3)

**Surface** (PEP 484 / S2, resolved by S1): `f: Callable[[A1, ..., An], R]` —
a function-type annotation on a parameter.

**Static plane** (Interpreted): a `Callable[[A1, ..., An], R]`-typed parameter
lowers to a curried WhyML **function-type parameter** `<w1> -> ... -> <wr>` (C1).
Module 5 (`_m5_get_type_name_legacy` + `_encode_callable_annotation`) encodes
the arg-list + return type into the existing `symbol_table` value as
`"callable:<a1>,...-><r>"` (a new tag VALUE, NOT a new IR field → no
IR_VERSION bump). Module 6 (`_param_type_str` + `_callable_whyml_arrow`) emits
the arrow type. The call site `f(a1, ..., an)` already lowers to WhyML
application; Why3's typecheck discharges the arg-type match (C2) and the result
type (C3). A bare Callable gives NO value postcondition (C4 — `f` is opaque; a
value `ensures` on the enclosing function is correctly unprovable, NOT a
`\trusted` shortcut). Scope limit (C5): only `int`/`bool`/`str`/`float` and
record/variant names are admissible as arg/return types (stricter than S1,
sound; `bytes`/`list`/`dict`/`set`/`Any`/nested-`Callable`/ellipsis rejected
with `PYCSL-TY3-CALLABLE-SCOPE`).

**Runtime plane** (Shimmed): `Callable[[...], R]` constructs an introspectable
alias object (R1); `callable(x)` / `isinstance(x, Callable)` is a PRESENCE
check (R2), signature-agnostic; NO signature enforcement at runtime (R3 — S3's
negative sentence).

**Divergence / no-blend (D1)**: the static "this value is a function with
signature S" is a proof-time judgment (WhyML arrow parameter + Why3 typecheck);
the runtime `callable()` / `isinstance(x, Callable)` is a presence check. The
static signature obligation must NOT be discharged by the runtime callable
check — the coherent-and-wrong trap, Callable edition.

**Tests**: see the typing-engagement `ty3/conformance_callable/` S5 subset + S4
shim drivers (authored by the conformance-agent, never the core-agent).

