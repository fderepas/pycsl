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
| 8 | Bounded integers | `#@ assumes bounded_int(N)`, **N in {16, 31, 32, 63, 64}** | Function/method | Use `mach.int.IntN` types; auto-generates overflow VCs on `+`, `-`, `*`. The width set is Why3's, not PyCSL's: `mach/int.mlw` defines Int16/Int31/Int32/Int63/Int64 and NOTHING ELSE — in particular there is no `Int8`. Any other N is REFUSED (`PYCSL-SEM-BOUNDED-INT-WIDTH`); before gen #31 it emitted `use mach.int.Int<N>` and the run ended on a why3 LIBRARY error (`Module Int8 not found in library mach.int`) for a directive PyCSL had accepted. |
| 9 | Raises | `#@ raises ExcType when <cond>` | Function/method | Exceptional postcondition: exception raised only when `cond` holds |
| 10 | Thread entry | `#@ thread_entry` | Function/method | Marks function as a concurrent thread entry point; used with `--memory-model concurrent` |
| 11 | _(reserved — `proof` directive removed 2026-05-27)_ | | | |
| 12 | Axiom from proof | `#@ proof <rocq\|lean> <qualname>` | Module-level | Imports a Rocq or Lean theorem as a Why3 axiom in the preamble. When both `rocq` and `lean` directives name the same `pycsl_target`, the `proof2why3 cross-check` tool verifies their canonical forms agree before emission ("Rocq + Lean as Cross-Validated Spec Sources"). See §2.1.12 below. |
| 13 | No-exception | `#@ no_exception E1, E2, ...` or `#@ no_exception \all` | Function/method | Implicit Python exceptions become proof obligations. For each IR operation in the body that could raise a listed exception, Module 6 emits a WhyML `assert { trigger }`. The `\all` form expands to the full Phase 1 set in `exception_model.KNOWN_EXCEPTIONS` and requires `raises { }` to be empty. See §2.1.13. |
| 14 | Abstract | `#@ \abstract` | Function/method | Function is emitted as a **bodyless** WhyML `val` defined SOLELY by its contract (+ any `#@ proof` axioms). Unlike `\trusted` (a present-but-unchecked body), `\abstract` asserts there is no meaningful body — the contract IS the definition. Sound (uninterpreted `val`). Does **not** count as `\trusted`; the canonical 0-`\trusted` model for irreducibly-opaque ops (e.g. `ast.literal_eval`). See §2.1.14 below. |
| 15 | Guarded case | `#@ act <name>:` (with a 4-space-indented body of `#@ given` / `#@ requires` / `#@ ensures`) | Function/method | A named case guarded by its `given`. Desugars to ordinary `ensures \old(<given>) ==> <post>` / `requires <given> ==> <pre>` (no new IR node, 0 `\trusted`). See §2.1.15 below. |
| 16 | Lemma | `#@ lemma` | Function/method (`-> None`) | The function is a PROVED logical fact. Lowers to `let [rec] lemma name (params) : unit requires {H} ensures {C} [variant {m}] = <proof body>`: Why3 verifies the body, then `forall params. H -> C` is usable by later goals. A recursive lemma's self-calls are the induction hypotheses; `#@ \variant` is optional (Why3 infers a structural variant and rejects ill-founded recursion). Must be `-> None` / `assigns \nothing`; may not rest on a `\trusted` fact. Introduces NO axiom that isn't itself checked. See §2.1.16 below. |
| 17 | Uses | `#@ uses <lemma>` | Function/method | Cites a `#@ lemma` whose general fact this function's proof relies on but does not *name* (e.g. a `\forall`-over-a-recursive-datatype goal discharged by the lemma). Forces the lemma to be emitted before this function so its fact is in scope. Ordering-only — emits no WhyML. **The cited name must be a `#@ lemma` IN THIS EMISSION**; one that resolves to nothing used to be dropped in silence (the file still reported success while the fact it was meant to bring into scope was never there) and is now refused with `PYCSL-SEM-USES-UNKNOWN-LEMMA` (witness `1880`, control `1881`). NOTE that a lemma in an IMPORTED module does not count: an imported cited lemma is not emitted at all today, so citing one is the same no-op — measured, and recorded as an open capability. See §2.1.17 below. |
| 16 | Case guard | `#@ given <expr>` | Inside an `act` | The case's pre-state guard (ACSL's `assumes`); only valid inside an `act` block. `\result` is not allowed here. |
| 17 | Complete cases | `#@ complete <name>, ...` | Function/method | Proof obligation that the named acts' guards cover every input — `ensures \old(g1) \|\| ... \|\| \old(gn)`. |
| 18 | Disjoint cases | `#@ disjoint <name>, ...` | Function/method | Proof obligation that at most one guard holds — per pair `ensures not(\old(gi) && \old(gj))`. |
| 19 | No inline | `#@ no_inline` | Method on a module-global instance | **Modular-verification boundary (no-inline.md).** The method's body is verified once against its contract (emitted as a `let`); callers reuse its **contract** (a contract-call to an abstract `val` carrying the result-only `ensures`) instead of splicing the inlined body. Avoids re-proving a large body in every caller's context (the os `sys_write` inlining blow-up). Sound iff the body stays a verified `let` — a false `ensures` makes the *callee* fail. |
| 26 | Sibling concrete | `#@ sibling_concrete` | Method | **Opt-in concrete sibling-call (allocator-frame §2.7).** An intra-class `self.<m>()` call to a method marked `#@ sibling_concrete` is lowered to a CONCRETE call `(<class>__<m> self args)` — so the caller gets the callee's full contract AND its type/class-invariant guarantee on the post-state — instead of the default abstract `val` stub (which conveys neither). Use ONLY on cheap-to-maintain leaf writers whose guarantee the caller can absorb as an atom (e.g. the os bitmap leaves `_set_bitmap`/`_poke`, letting the allocators inherit the disk class invariant). Decoupled from `no_inline`: affects sibling-call lowering only, NOT wrapper inlining. Default off → every existing self-call keeps its abstract-stub lowering (byte-identical). Sound: a concrete call to a verified `let` is the method's real semantics. |
| 27 | Propagate frame | `#@ propagate_frame` | Method | **Opt-in quantified-frame propagation across the call/import boundary (os-roadmap M4).** A method's `#@ assigns self.f` only frames `self.f` as a WHOLE on the abstract boundary `val` — so a caller sees the whole field havoced (only the result-pinned cell survives). With `#@ propagate_frame`, THIS method's QUANTIFIED single-cell self-field FRAME `ensures` (`\forall k. guard -> self.f[k] == \old(self.f[k])`) is carried onto its boundary `val`, letting a caller prove every *other* cell is preserved by the call. Two frame shapes are propagated: param-referencing frames (e.g. the os `_zero_entry` slot frame, trigger pinned on the post-state decode application) and `\result`-referencing single-cell frames (`\forall k != \result. self.f[k] == \old(self.f[k])`, where `\result` lowers to the val's `result` keyword = the call's return value — e.g. the os `sys_open`/`sys_dup` `fd_open` allocator frame, letting "the table is not full" survive a prior open). Opt-in ON PURPOSE: a broad frame trigger can E-match-poison term-rich sibling callers, so mark ONLY methods whose callers need *and* can absorb the frame. Default off → byte-identical emission. Sound: the propagated `\forall` is the SAME frame the callee's body verifies, never a fabricated or broadened one. |
| 28 | Fresh globals | `#@ fresh_globals` | Top-level driver (NOT a method, NOT a callee) | **Opt-in, CONFINED constructor-post-state surfacing for a standalone formal-test driver (fresh-globals.md).** Why3 verifies every importer function with each shared mutable module-global in an ARBITRARY (havoc'd) state — so an internals-blind driver cannot establish the global's freshly-imported initial state (e.g. the os `_filesystem` fd table being ALL-FREE at entry). `#@ fresh_globals` re-establishes, at the driver's body entry, each module-global singleton's CONSTRUCTOR post-state — the class `__init__`'s `#@ ensures` with `self` rewritten to the global — as an ASSUMED fact (`assume { \forall k. (0<=k<64) -> g.fd_open[k] == 0 }`). The assumed fact is NOT an arbitrary literal: it is the constructor's `#@ ensures`, which the transpiler ALSO emits as a checked function (`let g_fresh_init () : C ensures { … } = <constructor literal>`) PROVING the post-state holds of the freshly constructed global — so the assume is proof-backed. **SOUNDNESS (Module4-enforced):** sound ONLY for an independent entry point that runs on a freshly-imported global and is NEVER entered with a pre-mutated one. Module4 REJECTS `#@ fresh_globals` on a method (`self`-receiver) and on any function CALLED by another (a callee inherits its caller's possibly-mutated global) — error `PYCSL-SEM-FRESH-GLOBALS`. It RETIRES a reviewer trust (the os `fd-resolution-fidelity` unconditioned no-ENFILE `\result>=3` — FALSE at table-full) by replacing the false unconditioned body theorem with a free-slot-conditioned one whose side-condition this sound, confined, constructor-backed entry fact establishes. |
| 29 | Verify module | `#@ verify_module <name>` | Method | **Opt-in axiom isolation via separate Why3 modules (module-emission.md).** A method tagged `#@ verify_module <name>` is emitted into its OWN top-level Why3 `module` (shared infra — record type, val-functions, predicates, witness/class-invariant axioms — re-declared per module, the concrete record type shared via a common base `module` `use`d everywhere), so that ONLY the `#@ proof` axioms cited by the functions in that group are in scope for its goals. Methods sharing the same `<name>` co-reside in one module. A cross-module `self.<m>(...)` call (a sibling in a different `verify_module` group, or the flat default module) is lowered to the **proven** contract of the callee via Why3 module **`clone`-refinement** (the interface `module` declares the callee's contract; the owning provider `module` proves the real `let` *implements* it — Why3's synthetic `<fn>'refn'vc`, validated non-vacuous), i.e. a PROVEN cross-module interface, **never** an assumed-`val` boundary, a new `\trusted`, or a new axiom (the net TCB is unchanged — every function proved once, against a proven contract). Resolves the os read+write `field_to_str`/`dir_blit_marker` axiom co-residence that OOMs `_zero_entry` at ~9.5 M steps and blocks the `_dir_lookup` read-side de-trust. Default (untagged) → the single flat `module PyCSL_Program` is emitted unchanged → corpus byte-identical. (Why3 `scope` does NOT isolate axioms — a scope is a namespace; only separate `module`s do.) See §2.1.29 below.  **`<name>` must be a CAPITALIZED identifier** — it is lowered to a Why3 `module <name>` (plus a synthesized `<name>Sig` interface module) and Why3 requires module names to be capitalized; a lowercase name is refused with `PYCSL-SEM-VERIFY-MODULE-NAME-NOT-CAPITALIZED` rather than left to produce a Why3 syntax error naming the synthesized `<name>Sig` (witness `1842`, control `1843`). Cross-group calls: every `<G>Sig` is emitted BEFORE every provider module and each provider `use`s every other group's `Sig`, so two groups may call each other freely (`1844` cross-group, `1845` its negative twin — the boundary conveys the CONTRACT and not the body, `1846` mutually-recursive groups). |

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
preamble. **The prover must be `rocq` or `lean`** — anything else is refused with
`PYCSL-SEM-PROOF-UNKNOWN-PROVER` (witness `1888`). Until gen #31 the keyword was
not read at all: `#@ proof rocqq <qualname>` emitted a BYTE-IDENTICAL `.mlw`, so
the axiom entered the proof while `proof2why3/crosscheck_ir.py` — which selects
citations with `d.prover == "rocq"` / `"lean"` — could not see the citation at
all. A typo therefore hid a citation from the 3-way cross-check. (The axiom BODY
still comes from `_AXIOM_REGISTRY` and an unregistered qualname is refused, so the
reachable outcome was a hidden citation, never an arbitrary axiom.) `#@ proof` has real semantic effect: Alt-Ergo/Z3 may use
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

**The function's own explicit `raise` (route #304).** A `raise E` in the
body that escapes the function (no enclosing handler of the same function
catches it) is COVERED by the claim when the form is `\all` (any class,
including ones outside the Phase-1 set such as `RuntimeError`, `TypeError`
or a user class) or when `E` or one of its ancestors is listed (builtin
hierarchy plus the program's own class bases; a class whose ancestry is
unknown, e.g. imported, counts as covered). A covered raise is NOT added
to the function's inferred `raises`; it is a reachability obligation
(`no_exception: own raise E reachable`): it proves when the raise is dead
under `requires`, and FAILS otherwise. An uncovered raise keeps the
inferred `raises { E }`. Without `no_exception` nothing changes.

**A user class named like a builtin exception (route #305).** Handler
matching and the WhyML exception tag read a builtin exception (its
hierarchy, its implicit raises) by NAME, so a user `class KeyError(Exception)`
or `class LookupError(Exception)` would share the builtin's tag and bases
(a `raise` of the user class "caught" by `except LookupError`, the implicit
`KeyError` of `d[k]` "caught" by `except KeyError` naming the user class).
Any binding of such a name — a `class` statement at any depth, or a
`def` / import binding / assignment target / parameter / `except ... as`
name in a module or function scope, in the main file or a module it
imports — is refused (`PYCSL-R305-BUILTIN-EXCEPTION-NAME-SHADOWED`). The
names are `exception_model.EXCEPTION_BASES`, `KNOWN_EXCEPTIONS`,
`EnvironmentError` and `IOError`; `from builtins import KeyError` is
accepted. A subclass under its own name (`class E(KeyError)`) is unaffected.

**Known exceptions (Phase 1):** `ZeroDivisionError`, `IndexError`,
`KeyError`, `ValueError`, `StopIteration`. The authoritative set lives
in `exception_model.KNOWN_EXCEPTIONS`. Adding a new exception requires
extending both that set and the trigger table in the same module, plus
adding corpus tests under `test-suite/corpus/pycsl-reference/`.

**RecursionError is out of scope (route #269).** It is not in the Phase 1 set and the
interpreter's recursion limit is not modelled, so a terminating (`\variant`) recursion under
`no_exception \all` is proved regardless of its depth. A `#@ \diverges` function declaring
`no_exception \all` that reaches a recursive call cycle is REFUSED
(`PYCSL-SEM-DIVERGES-NO-EXCEPTION-RECURSION`): an unbounded Python recursion ends in
RecursionError, never in silence (corpus 2885–2887; control 2890).

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
  state ≥1 `#@ ensures`, and is not `#@ \diverges`. The `assigns` rule covers the ABSENT
  clause as well as a wrong one: a lemma with no `#@ assigns` at all is refused with
  `PYCSL-SEM-LEMMA-NO-ASSIGNS` (witness `1847`, control `1848`) — until gen #31 the rule
  was enforced only for a lemma that DECLARED a frame, so omitting it was the way past it. A plain lemma may **not** call a
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
| 1 | Class invariant | `#@ class invariant <expr>` | `class` | Assumed at every method boundary, and CHECKED where an instance is CONSTRUCTED. **The constructor's own obligation is emitted as `goal _check_class_inv_<C>`** whenever it can be stated exactly (route #226). Every field must be an `int`, and each must be bound either to a literal or DIRECTLY to an int `__init__` parameter; the goal quantifies over the field labels and those parameters, makes each binding a premise, and carries `__init__`'s own `#@ requires` as further premises — so a constructor whose precondition is what establishes the invariant still verifies (witness 1901). This covers the paramless-literal shape (1890/1891), the `__init__`-parameter shape (1892) and `@dataclass`, whose synthesized `__init__` takes every field (1900). **A control-flow or non-assignment store is REFUSED** (route #342, §7.25: a store inside an `if` / loop, a `for` / `with` / tuple / augmented / `del` target, `setattr(self, ..)`, an alias of `self`, a `self.m()` call or a non-leading `super()` in the constructor of an invariant-carrying class). **NOT covered: a straight-line COMPUTED store** (`self.n = three()`) — Module 5 marks the field unknown, and the honest obligation there needs the callee's postcondition rather than a value. Such a class is still not asked whether its invariant is establishable. |
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
| 5 | Footprint | `#@ footprint <name>(<arg>)` | Function/method | Binds the parameter of the parametric HAPPY `<name>` to the method's own argument `<arg>`, so the per-site region check (row 4) is specialised to the object this method operates on. **`<name>` must be a declared parametric HAPPY** — a typo would silently confine nothing, since the method would appear constrained and get no per-site check. That validation always existed; until gen #31 it sat below an early return and so never ran in a file that declares NO `#@ happy` at all, which is exactly where the user is most likely to be mistaken about what they have (witness `1884`, control `1885`). |
| 6 | HAPPY (reads / H-I1) | `#@ happy <name>:` block (`region LO .. HI` / `reads self.<field> outside region` / optional `except m1, …`) | Module-level | **Read confinement** (the read mirror of row 1). Every READ `self.<field>[i]` (point or slice) in any method **not** in `except` must lie outside `[LO, HI)`. Expands to a per-READ-site `#@ check ({i}) < LO or ({i}) >= HI`. Aliasing the protected field into a non-exempt local (`x = self.<field>`) is a hard error (a read through the alias would evade the check); a non-exempt `\trusted`/`\abstract` method (no checkable body) must be in `except`. The C sibling (macsl) expresses this as `\context(\reading)`. Drivers `0715` (positive) / `0716`–`0718` (negatives). |
| 7 | HAPPY (targets/postcond) | `#@ happy <name>:` block (`targets <method>` / `postcond <expr>`) | Module-level | The general **named-postcondition** form (macsl's `\targets(<m>), \context(\postcond)`). Attaches `<expr>` to `<method>` as an `ensures`, verified in the method's own body. Powers **H-R** (`nonrepud_complete`/`_append_only`) and **H-E** (`priv_monotonic`). A missing `targets` method is a hard error. Drivers `0719` (positive) / `0720` (negative). |
| 8 | HAPPY (targets/precond / H-S) | `#@ happy <name>:` block (`targets <method>` / `precond <expr>`) | Module-level | **Check-before-use capability** (macsl's `\targets(<m>), \context(\precond)`). The target ASSUMES `<expr>` (a precondition on its body); every **call site** must PROVE it — the meta-pass injects `#@ check <expr>` before each `self.<method>(…)` (PyCSL has no WP-style automatic call rule for the abstract self-call stub, so the obligation is injected, equivalent to macsl's WP call-site precondition). A caller that skipped the grant fails IN THE CALLER. Powers **H-S** (`authn`). Drivers `0721` (positive) / `0722` (negative). *Injected at `self.<method>(…)` self-call sites. A call through ANY OTHER RECEIVER (`b.transfer(…)`) is REFUSED rather than left unchecked — the guarding formula speaks about `self`, so it cannot be proved at a foreign receiver, and a silent skip would be the whole policy bypassed by a spelling. Measured gen #31: the self-call form without the grant FAILS on the injected check, the receiver-var form is refused by name.* |
| 9 | HAPPY (targets/total / H-D) | `#@ happy <name>:` block (`targets <method>` / `total`) | Module-level | **Totality / availability** (macsl's `\context(	otal)`). Names PyCSL's default-on termination guarantee (Why3 emits a termination VC; each loop needs a `#@ loop variant`) and forbids the only opt-out: `#@ \diverges` on the target is a hard error. An unbounded (variant-less) loop fails its termination VC — the non-termination/DoS the policy excludes. Powers **H-D** (`availability`). Drivers `0726` (positive) / `0727`–`0728` (negatives). |
| 10 | HAPPY (noninterference / H-I2) | `#@ happy <name>:` block (`targets <method>` / `noninterference secret <p1>, …`) | Module-level | **Noninterference** (macsl's `\context(
oninterference)`). The meta-pass SYNTHESIZES a self-composition twin `<method>__selfcomp` that calls `<method>` twice — public params shared, the listed `secret` params split `_a`/`_b` — and asserts the two results are equal. Discharged modularly from `<method>`'s result-`ensures`: a result that depends on a secret makes `ra == rb` unprovable (a leak). Not a new relational WP mechanism — a synthesized 1-safety driver, exactly macsl's `emit_selfcomp`. Powers **H-I2**. Drivers `0729` (positive) / `0730` (negative). |

**Expansion & soundness.** The obligation is injected at the *actual location written*, so it
needs no caller reasoning (an indirect write through a callee is caught at the callee's own
site — *universal coverage*, not the call graph, is load-bearing) — PROVIDED every write uses
the checked spelling. A list is passed by reference, so (route #266, witnesses `2810`–`2819`)
in every non-exempt body-verified function a non-scalar protected field may appear only as a
subscript base `X.<f>[...]` or `len(X.<f>)` (passing it to a call, aliasing, returning or
calling a method on it is refused; an exempt owner may still pass it to a helper), a write or
`del` reaching `.<f>` through any other receiver/alias/nested-subscript/destructuring spelling
is refused (`__init__` may create `self.<f>`), and a read-form read `X.<f>[i]` with `X` other
than `self` is refused. For `protects d.<f>` this includes the owning class's own methods
writing `self.<f>`: list them in `except`. A `\writing` HAPPY
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
| 1 | Mixin | `#@ mixin` | `class` | Marks the class as a composable mixin. **A name in a `#@ compose_from` list MUST carry it** — `PYCSL-SEM-COMPOSE-FROM-NOT-A-MIXIN` (witness `1857`, control `1858`); until gen #31 the marker had no enforced consequence at all and the flagship `0549` with it deleted composed and verified unchanged. A `#@ mixin` class must ALSO not be **instantiated directly** — `PYCSL-SEM-MIXIN-INSTANTIATED` (witness `1861`, control `1862`); a mixin's methods are verified against the COMPOSER's record, so a direct construction produces an object whose own methods were never proved over it. Only the callee position counts: `isinstance(x, MixinCls)` is not a construction. See §2.7.1. |
| 2 | Provides | `#@ provides <m>` | method | Declares the method `<m>` is a provider satisfying a sibling's dependency. |
| 3 | Shared state | `#@ shared_state <name>: <type>` | method | Declares `<name>` as **deliberately shared** facade state (multiple mixins may read/write it — not a conflict). D1. |
| 4 | Touches field | `#@ touches_field <name>: <type>` | method | Declares `<name>` as an **owned** field the method may touch (at most one owner; two owners → conflict, Tier 2). D1. |
| 5 | Depends method | `#@ depends_method <m>: <sig>` (+ indented `#@ requires` / `#@ ensures` / `#@ assigns`) | method | A **concrete** dependency on a sibling/core method `<m>`; the provider's contract must refine the declared one. D2. |
| 6 | Requires method | `#@ requires_method <m>: <sig>` (+ indented `#@ requires` / `#@ ensures` / `#@ assigns`) | method | An **abstract** operation the composing class must supply (verified once against an abstract `val`). D2. |
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
| 2 | Reveal | `#@ reveal <fn>` | Function (on the revealing caller) | Opts into `<fn>`'s rich definition contract (its facts are otherwise hidden behind the interface). Within the owning unit it is a no-op (the definition is the visible `let`); across modules it cites the exported definition-fact. **SCOPE IS THE IMPORTING MODULE, not the single call site**: the `val` stub for an imported function is emitted once per module, so if ANY function in the module reveals `<fn>` the stub shows the definition. That is strictly more information than the interface and sound for the same reason the narrowing VC is. Until gen #31 the directive was parsed, woven and written into the IR and read by NO Module-6 consumer — both halves of a reveal/no-reveal pair failed and their emitted `.mlw` were byte-identical, so `#@ interface` was a trapdoor. Drivers `1867` (no reveal, FAIL) / `1868` (reveal, PASS). **The name must resolve to a function in this emission** — `#@ reveal no_such_function` used to verify in silence and is now refused with `PYCSL-SEM-REVEAL-UNKNOWN-NAME` (witness `1882`, control `1883`); within the owning unit the directive is still a no-op, but the NAME still has to resolve. |

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
| 4c | `arr[i].field` / `\result[i].field` | `SubscriptFieldAccess` | Field PROJECTION off a subscripted element (cleared-array.md S2). Lowers to `Attribute(Subscript(…), field)` — the consumer of a projection-comprehension content law `\result[k] == a[k].x`. |
| 4d | `self.field[i].sub` | `SubscriptFieldAccess` | Field PROJECTION off an element of an instance ARRAY field — the SELF-FIELD base of §4c (its third base after a `CNAME` and `\result`, not a new operator). Lowers to `Attribute(Subscript(FieldGet(self, field), index), sub)`, the same IR the body path produces for `self.toks[self.i].py_type`, so a `List[<record>]` field projects the real record field instead of the unbound abstract getter `get_<sub>`. Enables the lexer-sentinel class invariant `self.toks[\length(self.toks) - 1].py_type == "EOF"` that a token-cursor `while self.at_op(...)` loop needs for TERMINATION; a `== "<literal>"` invariant of this shape also PINS the record's `by {}` inhabitance witness. Reference corpus: 0900 (positive) / 0901 (negative twin). |
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
| 8 | 8 | `*`, `//`, `/`, `%` | `BinOp` | `//` → floored WhyML `div` (int); `%` → floored `mod` (int); `/` → **real** division (float) |
| 9 | 9 (highest) | `not`, unary `-`, unary `+` | `UnaryOp` | same |

**Note (`/` is TRUE division — WL-02, FIXED):** `/` in a body **and** in a
contract is Python's TRUE division and ALWAYS yields a `float` (`real`), even on
integer operands (`5 / 2 == 2.5`). Two INT LITERALS are FOLDED to the binary64
quotient CPython computes, rendered by the same `repr` normalization a float
literal uses (`5 / 2` emits `2.5`); every other operand shape lowers to one
UNINTERPRETED DETERMINISTIC `val function float_truediv_op (a b: int) : real`
(route #58 — dividing over the EXACT reals decided `1 / 3 > 0.3333333333333333`,
which is False in Python because the two are the same binary64 value). A `/`
result used at `int` type is a
real-vs-int **type error** (fail-closed) — never a silent integer truncation. To
assert an integer quotient, use `//` (floored integer division). Previously `/`
mapped to the floored integer `div`, which unsoundly proved `5 / 2 == 2`.

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
| 1 | ~~`len(...)`~~ | **Now supported** — see below |
| 2 | ~~Function calls~~ | **Now supported** for pure functions (see Section 4.1) |
| 3 | List comprehensions | Not in grammar |
| 4 | `if`/`else` ternary | Not in grammar |

Rows 3 and 4 were re-measured in gen #31 and HOLD (`[x for x in a]` in a `#@ assert` →
`unexpected token in expression (got OP '[')`; `(1 if True else 2)` in an `#@ ensures` →
`expected ')' (got NAME 'if')`).

**Formerly unsupported, now supported:**
- `len(arr)` — accepted in `#@` expressions and FAITHFUL: it is the SAME symbol as
  `\length(arr)`, not an uninterpreted stand-in. Measured gen #31 — `#@ requires
  \length(a) == 3` discharges `#@ ensures len(a) == 3`, `#@ requires len(a) == 3`
  discharges `#@ ensures \result == 3` over `return len(a)`, and the false twin
  (`\result == 4`) FAILS. `\length` remains the spelling the grammar documents and the
  one to prefer; `len` is no longer an error.
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

**SCOPE — THIS IS A STATEMENT ABOUT `array`, NOT ABOUT COLLECTIONS IN GENERAL (route #63,
relaunch #55).** The barrier behind it is Why3's REGION TYPING, which rejects an aliased
array application outright (`This application creates an illegal alias`). Measured: it
fires for lists — `f(xs, xs)` on two `List[int]` parameters really is refused — and it
CANNOT fire for a `dict`/`set`, which lowers to a PURE `map`. A pure value has no region,
so nothing rejects the aliased call. A `@mutable_state` helper mutating one set argument
and reading the other proved `\result == 0` for a call that returns 7 in CPython, with the
aliasing entirely inside the proven unit (`u: Set[int] = set(); return self.helper(u, u)`).
Passing the SAME dict/set in two or more argument positions of one call is now REFUSED;
negative witness `1147`, positive control `1148`. Read the sentence above as: arrays are
separated because Why3 enforces it, and for a dict/set the separation is enforced by that
refusal rather than by the model.

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

**Default frame of an imported / `\trusted` stub (route #317).** A stub's contract is
assumed, but a stub with NO `#@ assigns` does not thereby claim to write nothing: its
default frame is the one a local function gets — the parameters its body may write (a
store rooted at the parameter or at a local aliasing it, an in-place list mutator, or
forwarding it to a callee position that is written; a conservative fixpoint over the
module), emitted as `writes { xs }` on the bodyless `val`. A written parameter that is not
a list cannot be framed and is refused (`PYCSL-VAL-ARG-UNFRAMED`). A stub WITH `#@ assigns`
is taken at its declared frame. Witnesses `4080`-`4081`, `4085`; control `4091`.

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

**Module resolution follows CPython's lookup, or refuses (route #326).** The roots searched
for an absolute import are the script's directory, the working directory, the repo `src/`
and every `--import-path`, in that order; inside one root a PACKAGE (`X/__init__.py`) is
taken before a same-named MODULE (`X.py`), as CPython's `FileFinder` does. A local file whose
top-level name is a standard-library or built-in module (`sys.stdlib_module_names`,
`sys.builtin_module_names`) is REFUSED (`PYCSL-SEM-IMPORT-SHADOWS-STDLIB`) unless it is
byte-identical to the running interpreter's own source of that module (file for file for a
package — the repo-root `json/` copy of CPython's `Lib/json` is the one such case): CPython
never loads a local `math.py` / `time.py` / `os.py` in place of a built-in, frozen or
startup-loaded module, and for the rest which one runs depends on `sys.path` and startup.
A program that edits the import system — any reference to `sys.path`, `sys.modules`,
`sys.meta_path`, `sys.path_hooks` or `sys.path_importer_cache` (any alias of `sys`,
`from sys import ...`, or the `sys` module object used as a value), save pure reads
(`len(...)`, `isinstance(...)`, `hasattr(sys, ...)`, `k in sys.X`) and the idempotent
`sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))`; dynamic-import machinery
(`importlib`, `imp`, `zipimport`, `pkgutil`, `runpy`, `__import__`) beside an import pycsl
resolves locally; or a locally-resolved dependency whose own top-level code edits it — is
REFUSED (`PYCSL-SEM-IMPORT-STATE-MANIPULATED`). See §7.16.

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

Is **not** a proof obligation: a Python `assert` lowers to `()` (translational
reference §T.5.8). Outside a handler that can catch `AssertionError` this is sound
for partial correctness — a failing assert aborts, and contracts speak about normal
return — so a false Python `assert` does not make verification fail. Inside such a
handler the program is refused (static semantics, route 16). To state a fact the
prover must establish, write `#@ assert P` (proved and assumed downstream) or
`#@ check P` (proved only). (Corrected gen #29: this section previously claimed a
`check { ... }` lowering that the emitter has never produced.)
**Exception (route #332, §7.19):** under `#@ no_exception \all` the contract DOES claim
that no AssertionError escapes, so there the assert is an obligation, not an erasure.

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

### 7.6 Augmented Assignment to a Subscript or Field (route #308)

`c[k] op= v` is lowered as `c[k] = c[k] op v` and `p.f op= v` as `p.f = p.f op v`,
which reads the container and the index TWICE and after `v`. Python evaluates `c` and
`k` once, then loads `c[k]`, then `v`. The desugar is kept only where both orders agree:
the container and index contain no call (other than `len`/`abs`), walrus, `await`,
`yield`, lambda or comprehension, AND — when `v` itself has an effect (a call, walrus,
`await`, `yield`) — they read only locals, parameters, `self`, literals and `+ - *`,
with no walrus in `v` rebinding one of them. Anything else is refused with
`PYCSL-SEM-AUGASSIGN-R308` (raised when the body is lowered; `\trusted`/abstract bodies
are never lowered): bind the index first, `i = nxt(cnt); ys[i] += 1`. Witnesses
`3930`-`3936`, controls `3937`-`3939`. (`f().n op= v` and `a[i].f op= v` were already
refused — route #23.)

### 7.7 `getattr(o, name, default)` (route #309)

Python evaluates `o`, `name` and the default BEFORE the lookup, whether or not the
attribute exists. A default that is not a literal, a name, a negative number, an empty
collection or an argument-less builtin constructor (`set()`, `dict()`, ...) is
sequenced first (`let _ = <default> in o.f`) when the receiver's class is known (a
typed parameter / local, `self`, or a constructor-assigned local `a = K(...)`) and
declares the literal attribute name; when it does not declare it, the answer IS the
lowered default. A receiver whose class is unknown, or a non-literal attribute name,
with such a default is refused with `PYCSL-SEM-GETATTR-DEFAULT-R309` (it used to be ONE
constant `pycsl_getattr_default_<hash>` shared by every receiver); with a literal
default it is the per-site, state- and receiver-keyed opaque read of routes
#197/#213/#239. A walrus in such a default is refused (`3950`). Witnesses `3940`-`3946`;
controls `3947`-`3949`.

### 7.8 An erased value is still evaluated (route #310)

Some values have no model and are erased to an unconstrained `(any int)`: a tuple or set
bound to a local (`t = (a, b)`), a tuple/list/set/dict display coerced into an `int`
position (`max((a, b))`, `(a, b)[1]`, `print((a, b))`, a dict-literal value, a stored
element, `ys.append((a, b))`), a display whose `len` folds from its shape, a `for` over a
display, and the argument of `raise E(arg)`. Python still EVALUATES such an expression, so
when it contains a call that is not known pure (route #307's predicate: not an
`assigns \nothing`/raise-free user function, a pure builtin or a query method), a walrus,
`yield` or `await`, the lowering evaluates it at its Python position and erases only the
value (`let _ = <display> in (any int)`; a `for` iterable is materialised once before the
loop). Where that position cannot be reproduced (a conditional-expression arm, a display
after a non-inert operand of the same node) it is refused ("an effectful expression is
erased here (route #310)"); a `raise` whose second/keyword argument, `from` cause or
computed exception contains a call is refused with `PYCSL-SEM-ERASED-EFFECT-R310` (only
the class and first argument are modelled). Witnesses `3960`-`3980`; controls
`3981`-`3989`.

### 7.9 Every erased operand is evaluated; slice bounds in order; method keywords (routes #311-#314)

Route #310's rule covers EVERY effectful operand, not only displays: a slice or
`sorted(..)` coerced to `(any int)` (`ys[0:f()][0]`, `sum(ys[0:f()])`, `for _ in ys[0:f()]`,
`print(..)`, an unannotated or constructor parameter), a dict display lowered to
`(any_map ())`, a dict/set-returning call passed to a `Dict`/`Set` parameter or stored in a
field, are evaluated at their Python position and only the value is erased
(`let _ = <operand> in ...`). The decision is keyed on the IR operand (route #307's
effect predicate), not on the emitted text; an operand whose not-known-pure calls all lower
to effect-free opaque `val`s (`chain(a, b)`, `s.encode()`) has nothing to evaluate in the
model and is left dropped. Slice bounds are operands of the slice (`ys[a:f()]`): the
receiver and the bounds are let-sequenced left to right (route #311). A keyword argument of
a `str`/`bytes`/`list`/`dict`/`set`/`tuple`/`int`/`float` method is REFUSED (its lowering
discards it — value and effects — and a keyword CPython rejects would be modelled as a
normal call), except `list.sort(key=, reverse=)` (its own lowering) and a string-literal
`encoding=`/`errors=` of `encode`/`decode`, rewritten to its positional slot (route #314).
Witnesses `3990`-`4014`; controls `4015`-`4020`.
### 7.10 A constructor is modelled only as a field initialiser (route #315)

`K(args)` is lowered to a record literal built from `__init__`'s `self.<f> = ...` stores
(routes #79/#83/#88/#150/#152/#154 make every field they cannot state UNKNOWN); the rest of
the constructor body is never emitted, so its effects on the arguments and on globals, its
callees' preconditions and its implicit raises are not in the proof. A class's constructor
(its own `__init__` / `__post_init__`, else the nearest base's) is therefore MODELLED only
when it is a field initialiser: statements are stores to `self.<f>` or to a local name,
`if` / `for` / `match` / `raise` / `return` / `pass` / an expression statement; an
augmented store is only `+=` / `-=` of a number; calls go only to total builtins (`len
isinstance issubclass bool list set dict tuple frozenset sorted reversed str repr range sum
any all abs bytearray bytes object type zip enumerate id callable`), builtin exception
classes, `setattr(self, ...)`, `super().__init__(...)` of a modelled base, or the
constructor of another modelled class; no subscript read (a slice is total), no subscript
or non-`self` attribute store, no `/ // % << >>` by anything but a positive int literal,
no `while` / `try` / `with` / `assert` / `global` / `nonlocal`. A non-trusted function of
the main file (or the module body of a `#@ fresh_globals` file) that constructs any other
class is refused with `PYCSL-R315-UNMODELLED-CONSTRUCTOR`; move the work out of the
constructor. A `#@ requires` on `__init__` is still not checked at the construction site
(route #15: the body of a field initialiser cannot observe its violation). Witnesses
`4040`-`4058`, `4063`; controls `4059`-`4062`.
### 7.12 `range` stops, nested parameter rebinds and literal list rebinds (routes #318-#320)

`for i in range(start, stop)` evaluates `start` and `stop` ONCE, before the first iteration.
The counter is initialised from `start` and the `stop` is bound to a fresh immutable
`let _stop_<idx>` ahead of the loop whenever it is not an integer literal, an immutable
name, or `len` of one, so a body that rebinds `n`, `s`, a field or appends to the list a
`range(len(xs))` reads does not move the loop's end (route #318). The source loop
invariants and variant are unchanged; nothing is assumed about the new binding beyond its
value at loop entry.

A formal parameter whose FIRST binding in source order sits inside an `if` / `for` /
`while` / `try` / `with` / `match` block is refused with
`PYCSL-M6-PARAM-REBIND-NESTED-BLOCK`: the lowering is a block-scoped `let`, so after the
block the name would denote the caller's object again (reads and writes, and so the
`assigns` frame, would be the argument's). A rebind at the top level of the body is a
`let` scoping the rest of the function and stays supported (route #319).

Rebinding a list local held as a fixed array plus a length counter to a list literal
overwrites that array in place. It is refused with
`PYCSL-M6-LIST-LITERAL-REBIND-ALIASED` when another holder of the old list may exist:
anywhere in the function the local is used as a value other than an element read/store,
slice, `len`/`sum`/`min`/`max`/`sorted`/`any`/`all`/`list`/`tuple`/`set`/`str`/`repr`/
`print`/`bool` argument, comparison, plain `return` or `for` iterable; it is bound from a
non-literal (`ys = xs; ys = [7, 8]`), a tuple unpack or a `for` target; or the rebind is
inside a `for` that iterates it (route #320). Witnesses `4110`-`4114`, `4117`-`4120`,
`4122`-`4125`; controls `4115`, `4116`, `4121`, `4126`, `4127`.
### 7.11 A method's writes to its arguments (route #316)

A call to a method (instance, `@staticmethod`, a sibling `self.m(...)`, a base-typed
receiver) is lowered through an abstract `val`, so the caller sees only the frame that `val`
declares. That frame is: the `self.<f>` targets of `#@ assigns`, plus `writes { x_i }` for
every list parameter the method's body may write (a store rooted at the parameter or at a
local aliasing it, `+=`, an in-place mutator, or forwarding it to a callee position that is
written — a conservative fixpoint over the module's functions and methods; a call resolved to
no single method takes the union over every method of that name). This is the whole-array
effect Why3 infers for a plain function's `let`. Fail-closed rules:
`PYCSL-METHOD-FRAME` — a method that declares `#@ assigns` but may write a parameter the
frame does not name (`#@ assigns \nothing` / `#@ assigns self.n` with `xs[0] = 5`);
`PYCSL-METHOD-GLOBAL-WRITE` — a method that may write a module-level object (the stub is
declared before the global, so no `writes` can name it); `PYCSL-OVERRIDE-FRAME` — an
override that writes a parameter position its overridden base does not;
`PYCSL-METHOD-ARG-UNFRAMED` — a written parameter that lowers to a non-array type. Writes to
`self` fields stay checked by the method body's frame postconditions. Witnesses
`4070`-`4079`, `4082`-`4084`; controls `4088`-`4090`.
### 7.13 The collections and itertools length models (routes #321 / #323)

`Counter(...)`, `OrderedDict(...)` and `defaultdict(...)` lower to a `map int (option int)`
whose missing-key default is 0. They are MODELLED only as follows, and refused otherwise:
no keyword or starred argument and no arity CPython rejects (`Counter(a=5)` was the empty
map); a seed (`Counter(s)`, `OrderedDict(s)`, `defaultdict(f, s)`) must be a LITERAL —
numbers, strings, bools, `None`, negated numbers and list/tuple/set/dict displays of them —
because the seeded map is an opaque constant keyed on the seed (keyed on a NAME, two
`Counter(xs)` around `xs = [2]` were one map); `Counter` seeds are keyed apart from
`OrderedDict`/`defaultdict` seeds (a `Counter` counts the pairs an `OrderedDict` unpacks);
the `defaultdict` factory must be `int` or `lambda: 0` (any other default is not 0, and no
factory raises `KeyError`). A `defaultdict(...)` must be the value of a plain local
assignment `d = defaultdict(...)` in a function body, and because CPython's `d[k]` READ
INSERTS `k` while the model's does not, `d` may appear only as a subscript base, or else
only as the right operand of `in` / `not in`, in `len(d)`, `del d[k]` and `d.get/keys/
values/items(..)` with every read fused into a store of the same key (`d[k] = d[k] + e`,
`d[k] += e`, `k` a literal or a name, no other mention of `d` in `e`); never aliased,
returned, passed or iterated. The itertools length model (`len(list(chain(..)))`,
`product`, `islice`) applies only when the callee RESOLVES to itertools (`from itertools
import <it> [as a]`, `import itertools [as m]`, not shadowed by a user definition; bare
`list` not shadowed); an unresolved callee is the user's function. A resolved itertools
call with a keyword (`product(xs, repeat=2)`) or a starred argument (`chain(*xss)`) is
refused. Witnesses `4150`-`4169`, `4175`; controls `4170`-`4174`.

### 7.14 Float literals in folds, float module constants, and contract slices (routes #322 / #324)

A constant FOLD evaluates a builtin over literals at emission time. `abs(<lit>)`, `sum([<lits>])`,
`sum(<known local>)`, the known-element map of a list/dict literal and a class/NamedTuple/dataclass
default fold INT literals only (`bool` counts as an int); a float literal is never `int()`-truncated
into an int fact (`abs(2.5) == 2`, `sum([0.5, 0.5]) == 0` and NamedTuple `r: int = 2.5` with
`P().r == 2` were proved). `int(<finite float literal>)` keeps its fold, which IS the truncation.
A float constant of `math` / `cmath` (`pi`, `e`, `tau`, `inf`, `nan`, `infj`, `nanj`, through
`import math [as m]`, `from math import pi [as p]`, `from math import *` or `getattr(math, ...)`) and `sys.float_info` are
REFUSED wherever they are read, in a body, a contract, or a module/class-level binding: they had lowered to an opaque
int, so `math.pi % 1 == 0` was proved. A string slice inside a contract, `s[a:b]`, has Python
slice semantics: a bound that is not a non-negative int literal is normalised as CPython does
(`b < 0` reads `max(b + len(s), 0)`), so `len(s[1:-1])` is `len(s) - 2`, not 0. Witnesses
`4190`-`4202`; controls `4203`-`4211`.

### 7.16 Module resolution: stdlib shadowing, package vs module, import-state edits (route #326)

An import is resolved statically, so a verdict is only as good as the claim that the file
pycsl read is the module CPython runs. Three divergences made it false, each PROVED with
`--verify-imports` (the wrong module verifies too): a local `math.py` next to the script
(`math.floor(3) == 4`; CPython 3 — `math`, `time`, `sys` are built-in, `os` is loaded at
startup, so no path entry is ever consulted); `dup19/__init__.py` beside `dup19.py` (pycsl
took the module, CPython the package); and `sys.path.insert(0, ".../alt")` ahead of an import
(CPython loads `alt/sp19.py`). The rules: package before module in each root; a local
stdlib-named module is refused unless byte-identical to the interpreter's own source
(`PYCSL-SEM-IMPORT-SHADOWS-STDLIB`); an import-state edit is refused
(`PYCSL-SEM-IMPORT-STATE-MANIPULATED`) as listed under "Multi-file imports". Every
non-ambiguous resolution is unchanged (corpus, python-reference and mirror emission
byte-identical). Witnesses `4280`-`4285`, `4287`-`4292`; controls `4286`, `4293`-`4295`.
### 7.15 An unmodelled value is not an int (route #325)

A value PyCSL has no model of falls back to an OPAQUE `int` in the emitted WhyML, whatever
its Python type: a module-level name (`EPS = 0.5`, `T = (0.5, 1)`, `X = mk()`, `M = math`,
`from m import PI`), an attribute of a module or class object (`consts.F`, `C.R`, `self.R`
for a class attribute, `Color.RED.value`, `importlib.import_module("math").pi`), a subscript
of one (`T[0]`), and the result of a call of an imported or builtin callable (`time.time()`,
`random.random()`, `os.getcwd()`, `float.fromhex(...)`, `__import__(...)`). Every value
derived from such a fallback — a local bound to it, a component read from it, a container or
tuple built from it, a function that returns it, a user function's parameter that receives
it, a method called on it — may only be bound, passed on, returned, discarded, or compared
with `==` / `!=` in the BODY against a different value. Any other use (`+ - * // %`, an
ordering, `abs`, `int()`, a contract term, a reflexive `x == x`) is REFUSED
(`PYCSL-R325-OPAQUE-INT-FALLBACK`): there every claim true of all integers (`x % 1 == 0`,
`x * 0 == 0`, `x < e or x >= e + 1 or x == e`) was proved of a float, a string or a list.
A value KNOWN to be an int keeps its int model: an int expression bound at module or class
level in the file (`K = 5`, `N = K * 2 + 1`, `C.R = 5`), `sys.maxsize` / `maxunicode` /
`hexversion` / `api_version` and the int fields of `sys.float_info`, `len` / `id` / `hash`
/ `ord` / `int` / `range` and `random.randint` / `randrange` / `getrandbits`, `os.getpid`,
`time.*_ns`, `math.gcd` / `lcm` / `isqrt` / `factorial` / `comb` / `perm`, and a user
function annotated `-> int` / `-> bool` whose body does not return a fallback. Subsumes
route #322's float-constant bypasses (a re-export, an alias, `importlib`, `__import__`); the
#322 refusal stays as the first, name-keyed layer. Witnesses `4230`-`4263`; controls
`4264`-`4271`.
### 7.22 An inherited class invariant needs the constructor Python actually runs (route #335)

A subclass inherits its bases' `#@ class invariant`s (§3, route #226 checks the constructor's
obligation, route #277 lets a base-typed parameter hold a subclass). Both rest on the
subclass's construction STORING every field an invariant names, with the value the merged
model uses. Python's constructor is the first `__init__` of the C3 MRO; a class without one
is walked through; a class with one runs it and reaches the next only through a leading
`super().__init__(...)` (a later, conditional or explicit `B.__init__(self)` call, a
dataclass's synthesized constructor and an unmodelled class all end the chain); a field's
value is the one stored by the first class of that chain that stores it. A subclass is
REFUSED (`PYCSL-R335-INHERITED-INVARIANT-CONSTRUCTION`) when an invariant field it does not
store itself is (a) stored by no class of that chain (`__init__: pass`, an `__init__`
storing other fields, a store only under `if`, `class S(M, B)` with `M.__init__` not calling
`super()`), (b) stored by a class whose literal is not the merged one (`class S(M, B)` with
`M.__init__` storing `n = -1`), or (c) named by a method, `@property` or non-constant
class-body binding anywhere in the MRO. A class attribute (`n = -1`) is not the instance
field. Controls that keep proving: the subclass storing the field itself (with or without
`super()`), `super().__init__(...)` chains, `class S(B): pass`, grandchildren, a fieldless
mixin without `__init__`. Known over-refusal: `B.__init__(self)` instead of `super()`.
Witnesses `4460`-`4468`; controls `4469`-`4476`.

### 7.19 `assert` under `no_exception \all` is an obligation (route #332)

The §7.1 erasure is partial correctness: it is sound only while the contract claims nothing
about AssertionError. Since route #304, `#@ no_exception \all` claims that NO exception of
any class escapes, and `x = 1; assert x == 2; return 7` PROVED that claim while CPython
raises AssertionError. Under `\all` (and, defensively, under a named set holding
`AssertionError`, `Exception` or `BaseException` — Module 4 currently refuses those names as
unknown, so only `\all` reaches it) `assert c[, msg]` lowers to
`if c then () else assert { [@expl:no_exception: AssertionError reachable] false }`, with
`c` lowered exactly as an `if` test (program code, Python truthiness, so the test's own
IndexError / ZeroDivisionError / KeyError triggers are discharged too). The message is
evaluated by CPython only on the failing branch, which the obligation proves unreachable, so
an effectful message needs no model; a test that cannot be shown effect-free is still
refused (`PYCSL-M6-ASSERT-EFFECTFUL-TEST`). A `for` target read inside such an assert after
its loop now counts as a read (routes #36/#301/#302), so its value is the havocked last
value — sound, but an assert over it may no longer prove. Everywhere else (no
`no_exception`, or a named set without AssertionError) the erasure is unchanged, byte for
byte. Witnesses `4380`-`4388`, `4396`; controls `4389`-`4395`.

### 7.18 More values that are not ints: every module binding, unpacking, fields, encodings (routes #328 / #330 / #331)

§7.15's refusal now also covers: (a) EVERY module- or class-level binding form, at any
nesting: tuple and starred targets (`A, B = 0.5, 1`, `A, *R = [0.5]`), a binding inside a
module-level `if` / `try` / `with` / `while` body, a module-level `for` target, a walrus, an
`except ... as` / `match` capture (a paired `A, B = 1, 2`, `if c: K = 3` and `for I in
range(n)` stay KNOWN-INT); (b) tuple UNPACKING in a function (`a, b = F, 1` taints exactly
`a`); (c) Module 6's own binders are scoped precisely (a `match` / `try` arm's pattern
variables to that arm, a `for` index to its body), so the emitted `with Return r -> r` no
longer hides a global `R`, nor `| Some v_ -> v_` a global `V_`; (d) an INSTANCE FIELD whose
WhyML label is `int` while one of its class-level / `self.f = ..` initialisers or
annotations is shown NOT to be an int (a float / str / bytes / None literal, an f-string, a
display, `/`, `float(..)` / `str(..)` / `repr(..)`, an imported value, a non-int global, a
parameter annotated non-int, an annotation other than `int` / `bool`): `self.r = 2.5` then
`int(c.r) == c.r`, `self.s = "ab"` then `c.s * 0 == 0`; an INTEGRAL float literal (`2.0`)
stays carried as that int (routes #148 / #236); (e) a `None` / `Optional[int]` field: `==` /
`!=` stay admitted, but arithmetic and orderings are refused — under `no_exception \all`,
`c.r * 0` over `self.r = None` proved that no `TypeError` is raised (route #331); (f) the
results of the string-encoding model operations (`repr(n)`, `format(n)`, `f"{n}"`, an
int-model f-string join), which stay comparable `==` / `!=` (a string equals itself);
(g) a `complex` annotation anywhere (it was typed `int`: `z * z != -1` proved at `1j`).
An element of a parameter annotated with a BARE container (`xs: list`, `xs: List`,
`Sequence`, `tuple`) is read as an `int`: the DECLARED MODEL ASSUMPTION BARE-CONTAINER-INT
(listed by `--soundness-report`; `--strict-bare-containers` makes such an element an
unmodelled value, refused in an int position; measured: 90 corpus files rely on it); since
route #334 it also covers a VALUE of a bare `dict` / `Dict` / `Mapping` parameter (§7.21).
Witnesses `4330`-`4353` (`4348` / `4349` under the strict flag); controls `4354`-`4362`;
assumption counterexamples `4363` / `4364`.
### 7.21 A field is an int only when every value stored into it is provably an int (route #334)

§7.18 (d) refused a field whose initialiser had a non-int SHAPE; any other initialiser left the
field an int. Now a field (and, for a dict field, its VALUES) is classified by the TYPE of every
value stored into it, anywhere in the class, its bases and its SUBCLASSES (a receiver typed as a
base may hold a subclass instance): class-level and `self.f = ..` / `self.f: T = ..` stores,
tuple targets paired element by element, starred / `for` / `with` targets, `self.f += ..`,
`setattr(self, "f", ..)`, dataclass `field(default=..)`, and for a dict field `self.d[k] = ..`
/ `.update` / `.setdefault`. A value is PROVABLY int when it is an int / bool literal, an int
operator over provably-int operands (`+ - * // % << >> & | ^`, `**` by a non-negative int
literal), a local of the storing function every binding of which is provably int, a walrus over
one, an `int`-annotated (or unannotated, §7.24) parameter, a known-int global, another provably-int
field, `len` / `int` / `ord` / `hash` / `id` / `bool` / `round(x)`, `abs` / `min` / `max` of
provably-int arguments, or a user function / method annotated `-> int` / `-> bool`. A value SHOWN
non-int (a float / str / None literal, `/`, `2 ** -1`, a display, an f-string, `float(..)`, a
module value, a local bound to one) makes the field an unmodelled value refused in an int
position (`PYCSL-R325-OPAQUE-INT-FALLBACK`): `x = 2.5; self.r = x`, `self.r = (y := 2.5)`,
`self.r = 2 ** -1`, `self.r, self.s = 2.5, 1`, a subclass storing `self.r = 0.5`, a dict field
`{"a": 0.5}`. A value of UNKNOWN type (an attribute of an untyped object, an unknown call)
makes an undeclared field unmodelled too, but is carried under a field DECLARED `int` /
`bool` (`self.n: int = t.n`, class-level `n: int = 0`): the annotation is trusted as it is for an
`int` parameter. An INTEGRAL float literal (`self.r = 3.0`) keeps its int model ONLY as a direct
operand of a comparison (CPython compares an int and a float exactly): `c.r > 1` proves, but
`c.r * 10**17 + 1 != c.r * 10**17`, `"ab" * c.r` and `p.k + p.m` are refused (corpus 2132, a
true claim, is now refused). A VALUE of a bare `dict` / `Dict` / `Mapping` parameter is under
BARE-CONTAINER-INT (§7.18), dropped by `--strict-bare-containers`. Witnesses `4420`-`4439`
(`4427` strict); controls `4440`-`4442`, `4444`, `4445`; assumption counterexample `4443`.

### 7.23 An annotation that is not exactly recognised is never an `int` (routes #336 / #337)

A parameter, return or element annotation PyCSL did not recognise used to fall to the "defaults
to int" lowering, so every int law held of floats, strings, `None` and arbitrary objects
(`def f(x: Fraction): return x % 1 == 0` PROVED `True`; CPython False for `Fraction(1, 2)`).
Now: (1) ALIASES are resolved before any type is read — a module-level `X: TypeAlias = T`,
`type X = T`, `X = TypeAliasType("X", T)` or plain `X = T` (every name in `T` a type name),
bound exactly once, is replaced by `T` in every parameter, return and annotated-local
annotation, and `Annotated[T, ..]` by `T`; `Sequence[T]` / `MutableSequence[T]` /
`tuple[T, ...]` / `Tuple[T, ...]` are read as `List[T]`, `Mapping[K, V]` /
`MutableMapping[K, V]` as `Dict[K, V]`, `Literal[None]` as `None`. The emission is then
byte-identical to the direct spelling (`x: Num` with `Num: TypeAlias = float` is `x: float`).
(2) A READ-ONLY view read as a list / dict (`Sequence`, `tuple[T, ...]`, `Mapping`, through
aliases / `Optional` / `Annotated`) may not be stored into: an element store / `del` / `+=`, a
mutating method call, or passing it to a function other than a pure builtin (`len`, `sum`,
`sorted`, ...) is REFUSED (`PYCSL-R336-READONLY-VIEW-STORE`; the argument may be a tuple or
a mapping proxy, whose store raises `TypeError`). (3) A parameter or return whose tag is still
none of the lowered types (`int bool str float bytes bytearray list tuple dict set frozenset`,
the bare typing containers of BARE-CONTAINER-INT, a record / variant / union / option /
callable, the IR sentinels) — `Fraction`, `Decimal`, `numbers.Real`, `SupportsFloat`, `type`,
`None` as a parameter, `Iterable[T]`, `Collection[T]`, `Deque[T]`, a bare `Sequence` /
`Mapping`, an imported class, a FIELD-LESS user class (route #337: it was `type w = int`, its
own `__sub__` ignored) — is the ERASED arbitrary object of §7.12 (route #249): no law, its
arithmetic and comparisons uninterpreted, refused under `no_exception` or in a builtin-typed
slot; a call of a function so annotated returns an erased value. (4) An element / key / value
type the container readers do not model (`Dict[str, float]` values, `List[Fraction]`,
`Set[float]`, a non-`int`/`str` dict key) is erased the same way. (5) A union arm naming a class
that is not a record (`Optional[Fraction]`, `Optional[P]` for a field-less `P`, `Optional[T]`
for a TypeVar `T`) no longer carries an opaque `int` payload: the whole annotation is erased.
(6) Inside a method, an arithmetic / ordering operator applied to `self` (`self - o`, `-self`,
`self < o`, `self += ..`) is REFUSED (`PYCSL-R337-SELF-OPERATOR`): Python runs the class's own
dunder or raises `TypeError`, while a non-record class is `type <class> = int` for its methods.
Identity (`x is x`) of an erased value still proves. Witnesses `4480`-`4520`, `4524`, `4527`
(`4518`-`4520` REFUSED `PYCSL-R336-READONLY-VIEW-STORE`, `4524` / `4527` REFUSED
`PYCSL-R337-SELF-OPERATOR`); controls `4521`-`4523`, `4525`, `4526`, `4528`, `4529`.

Identity (`x is x`) of an erased value still proves. Witnesses `4480`-`4520` (`4518`-`4520`
REFUSED with the new code); controls `4521`-`4529`.

### 7.24 Overrides keep the base's annotations; field stores from ANY code count (route #338)

Two holes of §7.21 / route #277. (1) OVERRIDE ANNOTATIONS. A caller holding `b: B` types
`b.m()` by `B.m`'s RETURN annotation, and §7.21 trusts a `-> int` method as an int field
initialiser (`self.r = self.m()`), but the default override check (rules R1-R4 of
`PYCSL-SEM-OVERRIDE-REFINEMENT`) compared contracts only: `B.m -> int` overridden `S.m ->
float` gave the goal `true -> true` and `b.m() % 1 == 0` PROVED. Rule R5 now refuses an override
whose return annotation is not a SUBTYPE of the base's (covariance) or whose parameter
annotation is not a SUPERTYPE of the base's at the same position (contravariance). Per member
of a `Union` / `Optional` / `X | Y`: the same type (`List[int]` = `list[int]`), `bool` under
`int`, a class of the file under one of its ancestors, anything under `Any` / `object`. `int` is
NOT taken under `float` (the model types them `int` / `real`). A missing annotation is `Any`:
no constraint on the wider side, refused on the narrower one (an unannotated override of `->
int`, an annotated override parameter where the base's is unannotated). `--assume-class-exact`
turns R5 off with R1-R4 (CLASS-EXACT). (2) EXTERNAL STORES. §7.21 counted the stores of the
class, its bases and its descendants only; `c.r = 0.5`, `setattr(c, "r", .25)`, `c.r += 0.5`,
`del c.r`, `delattr(c, "r")`, `c.d["a"] = 0.5` from module level, `__main__`, another function
or a method of another class now join the census: of the receiver's class when the receiver
is a parameter annotated with a class of the file (or a local every binding of which
constructs one), of NO class when it is annotated with builtin scalar / container types only
(annotation trust), and of EVERY class of the file storing a field of that name otherwise. A
deletion is a non-int store; a dynamic name (`setattr(c, n, v)`, a `__dict__` / `vars()`
store) taints every field. (3) An UNANNOTATED parameter stored into a field (`self.r = v`) stays
int only while every caller is VERIFIED (WhyML types the record literal): when unverified code
of the module (module level, `__main__`, a default, a decorator) names the storing def, its
class or a descendant, the value is of unknown type (`U(0.5)` in `__main__`). A `k.m()` call
on a receiver typed / constructed as a class of the file is int when `m` is annotated `-> int`
there (R5 keeps it so). Witnesses `4530`-`4540`; controls `4541`-`4544`.
### 7.25 A class base is a class name; constructors store invariant fields straight-line (routes #341 / #342)

(1) CLASS BASES (route #341). The verifier reads a class's bases by NAME (`B`, or `mod.B` for
an imported class); any other spelling was silently DROPPED and the class modelled as
unrelated to its real base, so R5 (§7.24), the override refinement, §7.22 and the inherited
invariant all skipped it (`Base = B; class S(Base)`, `class S(base())`, `class S(B if c else
B)`, `Base, Other = B, int`, `Base: Type[B] = B`, all PROVED while CPython inherits). A class
is now REFUSED (`PYCSL-R341-CLASS-BASE-NOT-A-NAME`) when a base is a name the file also binds
otherwise than by its `class` statement or an import (an alias, a tuple / annotated / loop
target, a `def`, a parameter), an attribute not rooted at an imported module name, a
subscript other than `Generic[...]` / `Protocol[...]`, or any other expression. An alias is
refused rather than resolved: some twenty readers of a class header take the base by name,
and the census finds no alias base in either corpus, the mirrors or `pycsl_lib`.

(2) CONSTRUCTOR STORES (route #342). §3's constructor obligation `_check_class_inv_<C>` is
computed from the top-level `self.f = e` stores; a field stored any other way was not seen or
made unknown, and an unknown field means NO obligation, i.e. the invariant ASSUMED. For a
class carrying a class invariant (its own or inherited) and every class of the file on its
base closure (their constructors run for its instances), `__init__` / `__post_init__` is
REFUSED (`PYCSL-R342-CONSTRUCTOR-STORE-FORM`) when it touches an invariant field (every field
when the invariant reads `self` otherwise than as `self.f`) other than by a TOP-LEVEL `self.f
= e` / `self.f: T = e` statement — a `for` / `with` / tuple / augmented / `del` target, a store
inside `if` / `while` / `try` / a comprehension — or when it loads `self` other than as an
attribute root (`s = self`, `setattr(self, ..)`, `vars(self)`, a helper call; `type(self)`,
`isinstance(self, K)`, `id(self)` are reads), rebinds `self`, touches `self.__dict__` /
`__setattr__` / `__delattr__`, calls a method `self.m(..)`, uses `super()` other than as the
leading `super().__init__(..)`, or contains a `return`. No code of the file may store
`__class__` (`x.__class__ = C`, `setattr(x, "__class__", C)`:
`PYCSL-R342-CLASS-REASSIGNMENT`), and module-level / `__main__` code (not verified) may not
store or delete an invariant field (`b.x = 5`, `setattr(b, "x", 5)`:
`PYCSL-R342-EXTERNAL-INVARIANT-STORE`). A class WITHOUT an invariant, and non-invariant fields
of one, keep every store form. Still NOT covered (no goal, invariant assumed, route #226's
open carrier): a straight-line store of a COMPUTED value (`self.n = three()`, `self.n = v` for
a local `v`). Witnesses `4550`-`4571`, `4577`-`4579`; controls `4572`-`4576`.

### 7.26 Enum members are not ints; nested-def defaults bind at def time (routes #339 / #340)

(1) ENUM MEMBERS (route #339). A member `C.M` of a user enum class lowers to an opaque getter
of type `int` (route #325 keeps it an int because its value is an int literal), so every int
operation applied to it: on a PLAIN `Enum` member `x - x`, `x * 0`, `-x + x`, `x < x` and
`a[x]` PROVED under `no_exception \all` (CPython: `TypeError`), and a user `__eq__` / `__lt__`
on an `Enum` / `IntEnum` was ignored (`x == x` PROVED `True`, CPython's `__eq__` returned
`False`). A class is an ENUM when a base is (a dotted name ending in) `Enum`, `IntEnum`,
`Flag`, `IntFlag`, `StrEnum`, `ReprEnum`, or another enum class of the file. An `IntEnum` /
`IntFlag` (or `int`-mixin) enum that defines NO dunder (own or inherited in the file;
`__init__` / `__new__` / `__init_subclass__` and attribute dunders aside) keeps int semantics:
its members are ints. Every other enum is OPAQUE, and an expression denoting one of its members
(`C.M`, `C(v)`, `C[k]`, a name bound to one, a parameter / field / callee result annotated `C`,
`"C"` or `Optional[C]`, a `for` target over `C`) is admitted ONLY bound to a name, compared with
`is` / `is not` (and `==` / `!=` / `in` / `not in` / a `match` value, unless the enum defines
`__eq__` / `__ne__`), tested for truth (unless it defines `__bool__` / `__len__`), read as
`.value` / `.name`, returned / passed / defaulted where the annotation is `C`, or given to
`isinstance` / `id` / `type` (`hash`, unless it defines `__hash__`). Any other use — arithmetic,
unary `-` / `+` / `~`, ordering, an index, an augmented store, a container element or a
container annotation, a builtin or string conversion, an `int` parameter — is REFUSED
(`PYCSL-SEM-ENUM-MEMBER-OPERATION`). The class object handed to a callee (`list(C)`) is refused
likewise. Witnesses `4590`-`4599`; controls `4600`, `4601`. The classifier is refined by §7.30 (bases
resolved through imports, dunders over the whole MRO, flags opaque, `C(v)` and class-object
attributes, routes #352-#356).

(2) NESTED-DEF DEFAULTS (route #340). The def-time rule of route #273 (translational reference, `PYCSL-SEM-DEF-TIME-EVALUATION`) admitted a BARE-NAME
default because it cannot raise or write; but Python binds its VALUE when the nested
`def` / `lambda` runs while the lifted function is called with the name's value at the CALL:
`x = 1; def g(y=x): ...; x = 2; g()` PROVED `\result == 2` (CPython 1). A bare-name default
of a nested def or lambda is now admitted only when that name is bound nowhere in the enclosing
lowered function (no assignment / `for` / `with` / walrus / `except` / `import` / `def` /
`class` / `match` target, no `del`, in any nested scope) and is declared `global` / `nonlocal`
nowhere in the module — a parameter that is never rebound, or a module name — so the def-time
and call-time reads coincide. Otherwise `PYCSL-SEM-DEF-TIME-EVALUATION`. Witnesses
`4602`-`4605`; control `4606`.

### 7.27 A field-less receiver is an arbitrary object; inherited overrides; foreign attribute bases (routes #343 / #344 / #345)

(1) FIELD-LESS RECEIVER (route #343). §7.23 erased a field-less class's PARAMETERS, but inside its
methods `self` stayed `type <c> = int` with every int law, guarded only by the syntactic
`PYCSL-R337-SELF-OPERATOR` refusal: `s = self; return s - s` (a user `__sub__` returning 1),
`(s := self) - s`, `[self][0] - ...`, `abs(self)`, `max(self, 0)`, `h(self)` into an `int`
parameter, `return self` through `-> int`, all PROVED. The receiver of a method of a class the
model does not carry as a record / variant is now the erased object of route #249, exactly like
such a parameter: aliases, walrus targets, container elements and builtin results inherit the
erasure; `==` / arithmetic / ordering on it are uninterpreted (and fail under `no_exception`);
its flow into an `int` / `float` / `str` / `bool` / `bytes` parameter, field or return is
refused (route #252). `self.f`, `getattr(self, "f", d)` and `self.m(..)` are attribute reads /
method calls ON the receiver, not uses of it, and keep their lowering; the WhyML type of
`self` is still the alias. (2) BUILTINS ON AN ERASED VALUE. Under `no_exception` a call of a
builtin that dispatches to a dunder or checks its argument's type (`range`, `abs`, `len`,
`min` / `max`, `sum`, `sorted`, `int` / `float` / `str` / `repr` / `bool` / `hash`, `iter` /
`next`, the container constructors, `round` / `divmod` / `pow`, `chr` / `ord` / `bin` / `hex` /
`oct`, `format`, `print`, ...) with an erased argument is preceded by a failing assertion
(`PyCSL-R343`): `range(x)` for `x: Any` PROVED `no_exception \all` (CPython TypeError).
(3) INHERITED OVERRIDES (route #344). R5 (§7.24) read both defs of a recorded override pair
from the source, so a class with NO def of its own (`class C(B, A): pass`, which runs `B.m`)
was skipped: `A.m -> int`, `B.m -> float` and `a.m() % 1 == 0` PROVED. A side without its own
def is now resolved through Python's C3 linearization of the file's classes to the first class
of its MRO defining the method, and compared. (4) FOREIGN ATTRIBUTE BASES (route #345). A base
`om.B` is read by its tail `B`, so when the file also defines a class `B`, `import rt25other as
om; class S(om.B)` inherited the LOCAL B's contract and invariant (CPython runs
`rt25other.B.m`). Such a base is REFUSED (`PYCSL-R341-CLASS-BASE-NOT-A-NAME`) unless it is a
self-import (`import <this module> [as x]`, used as `x.B`); import the class under a distinct
name instead (`from m import B as OtherB`). Witnesses `4610`-`4625`; controls `4630`-`4634`.

### 7.28 Constructors, immutable records and hashing the record model does not have (routes #346 / #347 / #348 / #349)

Four class shapes whose runtime behaviour the record model (a `@dataclass`, NamedTuple or plain
class lowered to a WhyML record, every field present and mutable, every value usable anywhere)
does not have. Each is a sound REFUSAL on the source; no emission changes.

(1) `__post_init__` ON AN INVARIANT CLASS (route #346). A `@dataclass` construction that runs
`__post_init__` is opaque (route #150: no field value known) and an opaque construction gets
no §3 constructor obligation, so the invariant was ASSUMED: `__post_init__: self.x = -1` under
`#@ class invariant self.x >= 0` PROVED `f(d) >= 0` (CPython -1); even a no-op hook dropped the
obligation for an unverified `D(-5)`, and an inherited hook (`B(A)` over `A.__post_init__`)
did the same. A record carrying a class invariant (own or inherited) whose base closure holds
a `@dataclass` and a class defining `__post_init__` is REFUSED
(`PYCSL-R346-POST-INIT-INVARIANT`). Validate in a verified factory function, or write an
explicit `__init__` (§7.25 (2)). A `__post_init__` on a class WITHOUT an invariant is unchanged
(route #150 already widens its fields to unknown; route #179 refuses its raises).

(2) A FIELD NOT ASSIGNED ON EVERY CONSTRUCTOR PATH (route #347). Every record field has a
value in the model, so a read `r.x` never raises; CPython raises AttributeError when no store
reached `x`. The verifier computes DEFINITE ASSIGNMENT over each class's constructor: its own
`__init__` (an `if` keeps what both branches store; a loop, a `with` body, a `try` body whose
handlers do not all store, a store after an early `return` count nothing on the paths that
skip them; a `raise` path builds no instance; a leading `super().__init__()` / `B.__init__(self,
..)` adds the base constructor's set; a `del self.f` removes `f`), else a `@dataclass`'s /
NamedTuple's synthesized fields (minus a `field(init=False)` without default), else the
first ancestor's. A field of a class (stored on `self` by any of its or its ancestors' methods,
or declared by a dataclass) that is neither definitely assigned nor a class attribute is
MAYBE-ABSENT, and a read of an attribute of that name (any receiver but a module) in a function
whose `no_exception` covers AttributeError (`\all`, `AttributeError`, `Exception`,
`BaseException`) is REFUSED (`PYCSL-R347-FIELD-MAYBE-UNASSIGNED`). Callees without
`no_exception` stay ambient (§ exception model): a read in an unannotated helper is not refused
at its `no_exception` caller.

(3) IMMUTABLE RECORDS (route #348). `typing.NamedTuple` classes, `collections.namedtuple` /
functional `NamedTuple(..)` bindings and `@dataclass(frozen=True)` classes (and their
subclasses) were emitted as `{ mutable x: int }`, so `n.x = 5` PROVED `\result == 5` under
`no_exception \all` (CPython AttributeError / FrozenInstanceError on ANY attribute store or
delete). In every function and method body an attribute store, augmented store, `del`, `for`
/ `with` target, or a `setattr` / `delattr` call is REFUSED (`PYCSL-R348-IMMUTABLE-RECORD-STORE`)
when its receiver is a name annotated with / constructed as an immutable record or `self` in a
method of one, or is of unknown class and the attribute is a field of an immutable record of
the file. Build a new value (`n._replace(..)`, `dataclasses.replace(..)`).

(4) UNHASHABLE RECORDS (route #349). A set / dict of records lowers to an opaque value, so
`s = {d}` PROVED `no_exception \all` for an unhashable `d` (CPython TypeError). Hashability is
decided as Python does, per class in base order: an own `__hash__ = None` -> unhashable, an own
`__hash__` -> hashable, a `@dataclass` with `unsafe_hash` -> hashable, else with `eq` (the
default) -> hashable iff `frozen`, an own `__eq__` without `__hash__` -> unhashable, else
inherited (`list` / `dict` / `set` / `bytearray` bases unhashable); a NamedTuple / frozen record
with a `list` / `dict` / `set` / unhashable-record field is unhashable too. An expression of an
unhashable class (a typed name, `self`, a constructor call, a typed field) in a set element,
set-comprehension element, dict key, dict-comprehension key, subscript index, `hash(..)`,
`set(..)` / `frozenset(..)` / `fromkeys(..)` element, `in` / `not in` against anything but a
list / tuple, or `.add` / `.discard` / `.remove` / `.get` / `.setdefault` / `.pop` argument on
a receiver not known to be a list, and an annotation `Set[U]` / `Dict[U, ..]` (and the other
keyed collection heads), is REFUSED (`PYCSL-R349-UNHASHABLE-RECORD`). Witnesses `4660`-`4685`;
controls `4686`-`4696`.

### 7.29 A default is of its annotation's kind; a read-only view never leaves as a mutable one (routes #350 / #351)

(1) DEFAULTS (route #350). The body of a lowered function is verified with every parameter of
its annotated type, but CPython binds an OMITTED argument to the default VALUE: `def f(x: int =
0.5)` PROVED `\result == 0` for `x % 1` (CPython `f()` is `0.5`) and `def f(s: str = None)`
PROVED `len(s)` under `no_exception \all` (CPython `TypeError`). Every annotated parameter
default of every def in a lowered function tree (module-level functions, methods, nested defs;
positional, positional-only and keyword-only) must now be of the annotation's KIND. The
annotation is split into arms through module aliases, `Optional`, `Union`, `|`, `Annotated` and
string forward references; one arm must admit the default: `None` only under a `None` arm
(`Optional[T]`, `T | None`), `Any`, `object` or a TypeVar; `int` <- an `int` / `bool` literal;
`float` <- `int` / `float` / `bool`; `bool` <- `bool`; `str` <- `str`; `bytes` <- `bytes`;
`Literal[...]` <- one of its values; `List` <- a list display, `tuple` <- a tuple display,
`Dict` / `Mapping` <- a dict display, `Set` <- a set display, `Sequence` <- a list / tuple
display or a string; a container, class or other arm <- a non-literal expression (a
constructor call, a name), never `None` or a scalar literal. A signed numeric literal is a
literal; a bare-name default resolves to a once-bound module constant, or to the enclosing
function's parameter of the same annotation (nested defs); any other non-literal default of a
scalar / `Literal` arm is refused. Display elements are checked against the element type.
Otherwise `PYCSL-SEM-DEFAULT-ANNOTATION-MISMATCH`. `\trusted` / `\abstract` defs are outside
(their contract is assumed). Corpus `0698` (`sep: str = None`, filled `""` at the call) is now
refused. Witnesses `4710`-`4720`; control `4721`.

(2) READ-ONLY VIEW ESCAPES (route #351). Route #336 (§7.23) reads a `Sequence[T]` /
`tuple[T, ...]` / `Mapping[K, V]` parameter as a `List` / `Dict` and refuses a store on it, but
the view could still leave under a mutable type: `as_list(xs: Sequence[int]) -> List[int]:
return xs` PROVED, and a verified `poke(ys: List[int])` storing `ys[0] = 5` PROVED as well
(CPython `poke(as_list((1, 2)))` raises `TypeError`). The VIEW names of a def are its read-only
view parameters plus, to a fixpoint, the names bound to an expression whose value may be a view
(the name, a slice of it, `+` / `*` on it, a conditional / `and` / `or` / walrus / starred /
display position holding one). REFUSED (`PYCSL-SEM-READONLY-VIEW-ESCAPE`): returning such a
value (or a lambda body) unless the return annotation is itself read-only-view-safe
(`Sequence`, `Mapping`, `tuple[T, ...]`, `Iterable`, `Collection`, `Any`, `object`, `None`,
through `Optional` / `Union`) and the view is not wrapped in a display; storing it into an
attribute or subscript target, or binding it to a name annotated otherwise (`ys: List[int] =
xs`); passing it to any call but the read-only builtins of route #336; and a store, `del`,
augmented assignment or mutating method call through an ALIAS of a view. Copy first
(`list(xs)`, `dict(d)`). Witnesses `4722`-`4728`; control `4729`.

### 7.30 Enum classification through imports, the whole MRO, flags, value lookup and the class object (routes #352 / #353 / #354 / #355 / #356)

Five gaps of §7.26 (1)'s enum classifier, each a sound REFUSAL (`PYCSL-SEM-ENUM-MEMBER-OPERATION`);
no emission changes.

(1) BASES ARE RESOLVED THROUGH IMPORTS (route #352). `from enum import Enum as E; class C(E)`
was not an enum, so `x - x` on its member PROVED under `no_exception \all` (CPython TypeError),
and `IntEnum as IE` with a user `__eq__` PROVED `x == x`. Every class base is now resolved
through the file's imports (`from enum import X as Y`, `import enum as e` then `e.X`) and
module-level aliases to a stdlib enum class, a file class, a builtin, a non-enum stdlib import,
or UNKNOWN (a non-stdlib import, an unbound name). An attribute base whose tail names an enum
class but whose module is not `enum` is an enum of unknown origin: OPAQUE. A class with an
UNKNOWN base in its ancestry and a member-shaped body (a plain non-lambda class-body binding)
may be an enum built on an imported member-less enum: it is treated as OPAQUE with every
operator dunder assumed user-defined (0 such classes in the corpus, measured).

(2) DUNDERS OVER THE WHOLE MRO (route #353). Dunders were collected from the class and its
ENUM bases only, so a non-enum mixin's `__sub__` / `__lt__` / `__eq__` (`class C(M, IntEnum)`,
`class C(M, int, Enum)`, `class C(M, Base)`) was invisible. An enum's dunders are now those of
every file class of its MRO, each treated as overriding; an enum is int-like only when its MRO
holds nothing but `IntEnum` / `int` / `Enum` / `ReprEnum` / `object` and file enum classes
(a non-enum mixin, even dunder-free, makes it OPAQUE). A user `__eq__` without `__hash__`
anywhere in the MRO makes `hash(x)` refused (`__hash__` is `None`).

(3) FLAGS ARE NOT INTS (route #354). `IntFlag` / `Flag` define `~` (`~A == B`, not `-2`) and a
`boundary=STRICT` flag raises ValueError on `x | 4` / `x ^ 8`; both were lowered as int. `IntFlag`,
`Flag` (also with an `int` mixin) are OPAQUE now, and so is any enum whose MRO holds a class
keyword (`boundary=`, `metaclass=`).

(4) VALUE LOOKUP `C(v)` (route #355). `C(99)` was emitted as an unconstrained value and PROVED
under `no_exception \all` (CPython ValueError). For EVERY enum (int-like ones too), in every
lowered function, `C(v)` is admitted only when its one positional argument is an `int` / `str`
literal equal, with the same type, to a literal member value of `C` (with `int` for an
int-mixin enum, `str` for a str-mixin one, no `__new__` in the MRO, no other mixin), or a
member `C.M`. Anything else is refused.

(5) THE CLASS OBJECT'S ATTRIBUTES (route #356). `for m in C.__members__.values(): m - m` PROVED
(CPython TypeError): the members reached through `__members__`, `_member_map_`,
`_value2member_map_`, ... were not tracked. A load `C.X` of an enum class, with `X` neither a
member nor a name bound in the body of a file class of `C`'s MRO, is refused, as is any store
or delete through `C.X`.

Witnesses `4750`-`4766`; controls `4770`-`4774` (`import enum as e; class P(e.IntEnum)` keeps
int semantics — the self-annotate mirror's `_Precedence` shape —, an alias-based member bound
and compared by `is`, `class C(int, Enum)` arithmetic, an IntFlag member compared by `is`,
literal-member `C(1)` / `C("b")`).

### 7.31 Field-less values beyond the receiver; protocol operations on erased values; R5 sees every class-body binding (routes #357 / #358 / #359)

(1) FIELD-LESS VALUES (route #357). §7.27 erased a field-less class's receiver and parameters;
other expressions of that static type kept the int laws. Now also erased (route #249): the
result of a method resolved through `self.` (or a typed receiver) whose return annotation the
lowering does not carry — a field-less class, string annotations (`-> "W"`) included; every
expression Module 5 does not represent (`UnknownPyExpr`: `type(self)()`, a computed callee);
and `<e>.__class__(..)`. So `s = self.me(); return s - s`, `type(self)() - ..`, `h(self.me())`
into an `int` parameter are refused (route #252) and `s == s` / `s < s` are uninterpreted.
A construction through the RUNTIME class, `type(<e>)(..)` / `<e>.__class__(..)`, runs the
`__init__` of the value's dynamic class (a subclass's possibly): it is REFUSED
(`PYCSL-R357-DYNAMIC-CONSTRUCTOR`) inside a function declaring any `no_exception` (the
constructor may raise anything, e.g. TypeError for a missing argument) and wherever it passes an
argument that is not a literal constant (the unseen constructor may mutate it). Name the class
explicitly instead. (2) PROTOCOL OPERATIONS ON ERASED VALUES (route #358). Under `no_exception`
(program context) a failing assertion `PyCSL-R358` now precedes, beside §7.27 (2)'s builtins:
a `for` loop or comprehension over an erased value (CPython TypeError, or a user `__iter__`); a
truth test of one (`if` / `while` / `not` / `and` / `or` / conditional expression: a user
`__bool__` / `__len__` may raise); an attribute load the erased value is not known to have
(`self.zz` on a field-less class, `x.foo` on `object` / `Any`; "known" = a name every object has,
or a method of the value's declared file class or a name one of its methods stores on `self` —
a class-body constant of a field-less class is NOT known, fail-closed); a `str` / `list` /
`dict` / `set` / `tuple` / `bytes` method handed an erased argument or element (`"".join([self])`,
`s.startswith(x)`, `xs.count(x)`; `append` and `insert`'s element are exempt). (3) R5 AND THE
WHOLE CLASS BODY (route #359). §7.27 (3)'s MRO walk saw only top-level `def`s. Any class-body
binding of the name — an assignment (`m = _bm`, `m = lambda self: ..`), a `def` under `if` /
`try` / `with`, an import, a loop / `with` / `except` target — defines it for the MRO, and a
pair resolving to one is REFUSED (`PYCSL-SEM-OVERRIDE-REFINEMENT`: R5 cannot read its
annotations). Independently of recorded pairs (a non-`def` binding records none), for every file
class K and every method a later file class A of K's MRO defines by a top-level `def`, the first
MRO class binding the name must be a file class with a top-level `def`: a non-`def` binding, or
a class from outside the file (an import, a builtin class that owns the name, directly or
through a file mixin `B(Bf)`) before A, is refused. `object` and a builtin class not owning the
name are skipped. Witnesses `4800`-`4827`; controls `4830`-`4832`.

### 7.17 Distinct names stay distinct; `is` is refused in every condition position (routes #327 / #329 / #333)

PyCSL lowers a Python name to a WhyML identifier by lowercasing a leading capital (`N` ->
`n`) and prefixing a WhyML keyword with `py_` (`result` -> `py_result`, `model` ->
`py_model`). That map is not injective, so a program in which two DISTINCT names that can be
in scope together map to the same identifier is REFUSED (`PYCSL-R327-IDENT-COLLISION`):
within one function, its parameters, every name it reads (locals and the module-level
globals it names), every binding target (assignment, tuple, `for`, comprehension, walrus,
contract quantifier) and the emitter's tuple binders `_tu_*`; at module level, the
functions and every module-level value binding; and two classes whose names lowercase
alike (`Ab` / `AB`: one method namespace `ab__m`). Measured: `N = len(xs); n = 0;
return N == n` PROVED `True`, a global `K = mk()` read beside a parameter `k` returned the
parameter, `py_model = 7; model = 3` read 3. A class and its instance (`c = C()`) are not a
collision (the class lowers to the type namespace). Rename one of the two names.

Route #333 closes two namespaces the rule above left open, with the same code. (1)
EXCEPTION TAGS: an exception tag drops its leading underscores (so `from m import Y as _Y`
and `Y` are one `exception Y`). A user exception class (a `class` deriving from a builtin
exception or another such class, or named in a `raise` / `except` / `raises`) whose name
without leading underscores equals that of ANOTHER class of the file, an imported name or a
BUILTIN exception is refused: `class _ValueError(Exception)` raised and caught by `except
ValueError` PROVED `no_exception \all` (CPython propagates); `_E` / `E` shared one tag and
the first `except` arm caught both. A class spelled exactly like a builtin is route #305's
`PYCSL-R305-BUILTIN-EXCEPTION-NAME-SHADOWED`; `#@ raises Y` naming the stripped spelling of
the file's own `_Y` is the same exception and is accepted. (2) GENERATED BINDERS: the
emitter binds its own temporaries in the user's WhyML scope — loop counters `_idx_<v>`,
`_len_idx_<v>`, `_stop_idx_<v>`, `_hv_idx_<v>`, havocs `_any_<v>_<k>`, `_tu_*`, `_pycsl_*`,
inliner / comprehension / lambda / quantifier temporaries (`_inl_*`, `_cc_*`, `_csrc_*`,
`_lf_*`, `_mem_*`, `_dk_*`, `_wl<k>c_*`, `_for_target`, `_alit`, `_ci`, ...; the full list
is the census of route333 REPAIR). A name the user writes (a variable, parameter or a `#@`
binder) in that namespace is refused: a local `_idx_i` beside `for i in range(1)` was read
as the counter (proved `s == 0`, CPython 5) and writing it ended the loop early. Closed
match / let binders that enclose no user expression (`_r`, `_v`, `_k`, `v_`, `r`) are
outside the reserved namespace. Witnesses `4400`-`4403`; controls `4404`-`4406`.

The identity refusals of §7.x (`X is True` / `X is False` unless `X` is a `bool` by
construction, route #42; `is` over a value-typed operand, route #52) apply wherever the
comparison occurs — an `if` / `elif` / `while` test, an if-expression test, under `not`,
inside `and` / `or`, an `assert`, a comprehension filter, a return value. Measured before
route #329: `x = 1; return 7 if x is True else 0` and `if not (x is True): return 0`
PROVED the branch CPython does not take. Witnesses `4300`-`4308`, `4315`-`4323`; controls
`4309`, `4310`, `4326`, `4327`.

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
| 3 | Mutex invariant | `#@ mutex_invariant <mutex>: <expr>` | `<expr>` must hold whenever `<mutex>` is free; checked at critical section exit (`assert { mutex_inv }`)  The INITIAL-state obligation is emitted as `goal _check_initial_<mutex> : <mutex>_inv <module-level initial values>` when every shared variable the invariant mentions has an int-literal module binding (and the shared ref itself is then `let v = ref <init>` rather than an unconstrained `val v : ref int`). Until gen #31 it was an `assert` inside a program function reading the mutable global, which Why3 quantifies over every reachable state — so it was unprovable for any non-vacuous invariant IN EVERY PROGRAM, which is why all 19 corpus drivers that declared one passed `--no-proof`. Drivers `1863` (discharged, prover on) / `1864` (initial state violates it). |
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
- **The NAME is checked, in all three.** A `#@ critical` / `#@ acquires` / `#@ releases`
  whose mutex is bound nowhere in the file is refused with `PYCSL-SEM-MUTEX-UNKNOWN-NAME`
  (witness `1893`, control `1894`, and `1895` for the `#@ critical` case). Before this,
  all three verified silently, and `#@ releases` could never have been caught by anything
  downstream because nothing reads `csl_releases`. The rule is deliberately the WEAKEST
  one that catches the typo — bound SOMEWHERE in the file, not "in the mutex registry" —
  because a lock protecting an invariant PyCSL does not model is legitimately annotated
  and legitimately absent from the registry. A file with a star import is exempt.
  NOTE what this is NOT: an unknown name in a block that WRITES a protected shared
  variable was already refused, by the protection analysis ("held mutexes are
  ['no_such_lock']") — a statement about protection, not about the name. Take the shared
  access out of the block and the old behaviour was silence.

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
**A TYPE KEYWORD THAT IS NOT IN THE TABLE BELOW IS REFUSED** with
`PYCSL-SEM-GHOST-UNKNOWN-TYPE` (witness `1886`, controls `1887` and `1889`). Until
gen #31 an unrecognised keyword fell through to that same `int` default in silence,
so a mistyped `ghost_dict` gave an int ghost and no message; the DEFAULT is
documented, the fallback from a misspelling was not. The UNTYPED form is unaffected
— it is `int` by design, and `1889` is the control that says so.

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
> **CONTENT-faithful, not just length (cleared-string.md):** concatenation and slicing prove their
> exact content via Why3's rich native `string.String` theory with NO new axiom — `(a+b)[:len(a)]
> == a` (`0765`), `s[0:2]+s[2:4] == s[0:4]` (`0766`); `startswith`/`endswith`/`find` accept a
> DERIVED string receiver too (`(a+b).startswith(a)`, `0767`), not only a simple name. A false
> content claim is correctly rejected (`0768`, `# pycsl-expected: FAIL`).
> **`upper`/`lower` and `replace` (cleared-string RESIDUALS):** `.lower()`/`.upper()` lower to
> DETERMINISTIC `str_lower_op`/`str_upper_op` (`val function`) with a non-emptiness length law +
> IDEMPOTENCE (fold-marker predicate, no new axiom), so `s.lower().lower()==s.lower()` PROVES
> (`0791`) while `s.lower()==s.upper()` stays UNKNOWN (`0793`, `# pycsl-expected: FAIL`); a
> STRING-LITERAL receiver is constant-folded by Python's own method (`"Hello World".upper()=="HELLO
> WORLD"`). `.replace` (`val function str_replace_op`) keeps the char-for-char `len pat=len rep →
> len result=len s` law and gains a NOT-CONTAINS identity (`pat not in s ⇒ result=s`, `0792`);
> all-literal calls constant-fold (`"a.b.c".replace(".","_")=="a_b_c"`).
> **Out of scope / residual (documented, honest boundary):** code points (`ord`, char ordering),
> the per-char ASCII case-MAP on a SYMBOLIC string (needs a codepoint bridge + `is_ascii` contract
> surface, zero demand) and full-Unicode folding (`"ß".upper()=="SS"`, not length-preserving), the
> general grow/shrink `replace` CONTENT (CPython all-occurrences ≠ Why3 first-occurrence `replace`;
> no faithful `replaceall` content axiom — `0794` rejects the false grow length claim), `strip`
> (`len result ≤ len s`), `split` (list-of-strings), `.decode`/`.encode` (bytes↔str boundary),
> `%`/f-string content. **A `str`-keyed dict/set is
> now faithful** — `dict[str, ν] ~ map string (option ν)` with the native, injective Why3 string key
> (`String.(=)`, no `str_hash_op`), so distinct keys are provably non-aliasing (cleared-hash.md,
> drivers `0755`–`0758`; κ inferred for `Dict[str,_]` params/locals, string-key literals, and
> string-key usage). A string **set** local is likewise native (`set() ~ map string (option int)`,
> present ≡ `Some 0`): `s.add(x)` and `x in s` agree on the raw string element (`0759`). A **record
> FIELD** declared `Dict[str, ν]`/`Set[str]`/`FrozenSet[str]` is now native too (cleared-hash.md S4):
> the WhyML record field is `map string (option ν)` and every field op site — store `self.d[k]=v`,
> subscript `self.d[k]`, `.get`, membership `k in self.d`, set `.add`/`.discard` — reads/writes the raw
> string key in lockstep (`0772` distinct-key non-aliasing, `0773` absent-key, `0774` literal↔variable,
> `0775` set field, `0776` NEGATIVE false-claim; existing field tests `0746`/`0750` now native).
> κ inference also covers a string **concatenation** key `a + b` (both operands `str`): its native key
> `str_concat_op a b` is pinned to Why3 `concat` (left-cancellative), so `a != c ⇒ d[a+b]` non-aliasing
> is provable (`0795`) — a distinct-key property the opaque hash cannot give.
> **Residual (κ-unknown, CLOSED honest boundary):** a dict/set whose key the model cannot pin to a
> decidable/injective string — a non-`str` key, an un-annotated field from `{}`, or a derived-string
> key with no injectivity content (`s.upper()`, whose native form is an opaque `str_upper_op` and which
> is genuinely non-injective) — keeps the `map int` + opaque `str_hash_op` fallback. This is honest, NOT
> collision-sound: a distinct-key non-aliasing claim on such a dict stays UNPROVABLE (`0796`,
> `# pycsl-expected: FAIL`) — NO false injectivity axiom is placed on `str_hash_op`
> (`proof_axiom_allowlist` unchanged). **Out of scope — a SEPARATE opacity (non-dict-key hashing):**
> a bare `hash(s)` (`0485`) and a decode-result string equality (`0425`) route through `str_hash_op`
> but are NOT dict/set key operations (no `Map.get`/`map` in either); `hash()`'s `int` result is the
> real Python semantics, so it is correctly left opaque (tracked in `we-are-getting-better.md`).

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
| `del d[k]` (DelSubscript) | `d := map_update_none !d k` | Wrapper `val` whose `ensures` equals `Map.set m k None` (key cleared). **LOCAL** dict/set only; on a **STANDALONE** dict/set PARAMETER the same op runs on the caller-visible `ref (map …)` (WL-05c, seeded like `d[k]=v`). On a dict/set **METHOD** parameter `del d[k]` is REJECTED — the WL-05 caller-visible-mutation boundary (see §7.9 / wrong-lowering §WL-05c) |

**Forbidden** (still): `d.items()`, `d.keys()`, `d.values()`, iteration over
`for k in d:`. (`d.get(k, default)` was listed here and is NOT forbidden — it has been
interpreted, and FAITHFULLY, for some time: measured on `{1: 10, 2: 20}`,
`d.get(3, 99)` proves `== 99` and refuses `== 0`, `d.get(1, 99)` proves `== 10` and
refuses `== 99`, matching CPython in all four. Fifteen corpus files already use it. The
line is corrected rather than the behaviour: a `Forbidden` list that names a working
construct sends a reader to write around something that works, and it is the same class of
staleness as the `del d[k]` entry the sentence below records.) (`del d[k]` was previously listed here as a blanket
no-op; WL-05c made it FAITHFUL for a local/standalone-param dict/set — `map_update_none`
— and a clean REJECTION on a method param. It used to be a silent no-op that unsoundly
proved a deleted key survived.)

**Tests**: 0345 (round-trip), 0346 (in / not in), 0854/0855 (WL-05c `del` faithful
local + standalone-param), 0856/0857 (WL-05c `del` method-param rejection + false-twin).

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
become a nullary `Arm_<idx>_None` constructor. A Union with an `Any`
arm (or `object`, an unknown name, a nested `Optional`/`Union`, an unmodelled generic) is
not a variant at all: the whole annotation lowers to the erased `Any` value (route #258 —
dropping the arm made `Optional[Any]` a None-only type and `x is not None` dead).
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

### §12.5a Content-faithful list / dict / set comprehensions

A list comprehension `[elt for t in src (if cond)]` is content-faithful when
the element lowers to a pure `int` logic term over the loop target only —
identity `[x for x in a]` gives `result[i] == a[i]`, `+ - *` arithmetic
`[x + 1 for x in a]` gives `result[i] == a[i] + 1`, **field projections**
(cleared-array.md S2) `[p.x for p in a]` give `result[i] == a[i].x`
(`[p.x + p.y for p in a]` → `result[i] == a[i].x + a[i].y`), and — **calls**
(cleared-array item 1) `[g(x) for x in a]`, where `g` is a PURE module function
(`assigns \nothing`, non-diverging → emitted as a Why3 `let function`, a logic
symbol) — give `result[i] == g(a[i])`; all with `\length(result) == \length(a)`.

A **filter** `[x for x in a if cond]` always keeps `\length(result) <=
\length(a)`; when the element is the IDENTITY and every predicate `cond` lifts to
a pure-bool logic term over the target (a comparison, or `and`/`or`/`not` of
such), it ALSO carries the content-SUBSET law (cleared-array item 4): each
survivor satisfies `cond` AND appears in `a`.

A **dict** comprehension `{x: v for x in a}` with an IDENTITY key + pure-int
value is content-faithful (cleared-array item 3): every source element is a KEY
mapping to the transformed value — `\has_key(\result, a[i])` and
`\map_get(\result, a[i]) == v[t:=a[i]]` (identity key pins soundness — colliding
sources map to the same key AND value). A **set** comprehension `{f(x) for x in
a}` (pure-int element) gives the membership law `\has_key(\result, f(a[i]))`
(every produced element is present; sound under-approximation).

Projection requires two enabling pieces: the contract grammar parses
`a[k].field` (§3.1.4c `SubscriptFieldAccess`) so a driver can STATE the claim,
and the abstract getter `get_<field>` is emitted as a pure `val function` in
spec context so it is logic-usable and denotes one deterministic value across
both mentions (a field read *is* deterministic — a faithful refinement). Calls
reuse the pre-existing `emits_as_logic_symbol` path (a pure module function is
already a `let function`); the content-law val is deferred and spliced in after
the callee so it is in scope.

**Subscript projection** `[x[k] …]` is now content-faithful over a NESTED source
(nested-list.md S4): a `List[List[τ]]` param lowers to `array (seq τ)` (a
`List[Dict[..]]` param to `array (map κ (option ν))`), so `x` is a real `seq`/`map`,
`x[k]` a faithful `Seq.get`/`Map.get`, and `[x[k] for x in a]` carries
`result[i] = Seq.get (a[i]) k` (driver 0799). **DEEPER reads + TARGET-DEPENDENT index
(nested-list.md §8/§9 EXTENSION):** `a[i][j][k]` reads content-faithfully to the depth-4
bound (`_nested_access_type`; drivers 0805/0806, beyond-cap rejected 0807), and a
target-dependent index `[x[len(x)-1] for x in a]` that lifts to a pure int term over
`len(x)` (`_lift_target_seq_index`) carries `result[i] = Seq.get (a[i]) (Seq.length (a[i]) - 1)`
(driver 0808, NEGATIVE 0809). Residual opaque shapes (never a false content claim):
non-identity dict key / non-pure-int dict value or set element, string/emit_ir elements,
multi-generator, a subscript index that does NOT lift (a `g(x)` call over the seq), a read
deeper than depth 4, an un-annotated/too-deep leaf (cleared-array.md S1–S5 + items 1,3,4;
nested-list.md).

**In-place inner mutation** `a[i][j] = v` (nested-list-mutable.md): a `List[List[int]]`
param that the body inner-mutates routes to the MUTABLE built-in `matrix int` model
(not the read-only `array (seq int)`), a per-param usage/mutation analysis so the two
representations coexist. `a[i][j]=v`→`Matrix.set`, `a[i][j]`→`Matrix.get`, `len(a)`→
`a.rows`, `len(a[i])`→`a.columns`. The update reads back and is non-aliasing (drivers
0802/0803). RECTANGULAR + int-leaf only; a non-int-leaf inner mutation is REJECTED
(driver 0804), `a[i].append(..)` stays opaque, ragged in-place mutation is out of the
rectangular `matrix` model. No new axiom (Matrix laws are Why3 stdlib).

**Tests**: 0761 (identity), 0762 (arithmetic), 0769 (projection),
0770 (arithmetic-over-projection), 0783 (call), 0763 (filter bound),
0789 (filter subset), 0785 (dict), 0787 (set); NEGATIVE — false content claim
rejected: 0764 / 0771 (list/projection), 0784 (call), 0786 (dict value),
0788 (set membership), 0790 (filter over-strong).

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
record literal — in EVERY position: a `return` in a `-> Pt` function, a
`Pt`-typed parameter, and (since gen #31) an ANNOTATED LOCAL `p: Pt = {…}`.
The local form used to be BUILT as a generic body dict and READ as a record, so
the two halves of one variable disagreed about its type and Why3 rejected the
file; drivers `1865` (local, verifies) / `1866` (its false twin).

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
list with `(C__m, P__m)` pairs, TAGGED `from_conforms_to`; the per-method refinement
goal `((pre_P -> pre_C) /\\ (post_C -> post_P))` (P2/P4 — per-method behavioural
refinement, NOT attribute presence) is emitted for those pairs **whether or not
`--check-behavioral-subtyping` is passed**: the DIRECTIVE carries its own obligation.
Until gen #31 the goal was flag-gated, so a declared conformance whose contract did
NOT refine the protocol's reported `All contracts formally proven` by default with no
warning (route #224, CLOSED; witness `1855`, control `1856`). The flag still governs
the IMPLICIT inheritance overrides, which nobody wrote down and which stay opt-in. A class missing a member raises a static
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
class/function parameterized by a type variable `T`. **Both class spellings are
monomorphized identically and subject to the same GT1–GT4 loud-fails** — until gen #31 the
legacy `Generic[T]` form produced no IR `type_params` (the recogniser existed but its call
site was guarded on the PEP 695 attribute, so its legacy branch was dead code), the
monomorphization pass early-returned, and `T` was silently modelled as `int`. Drivers:
`1849` (legacy + `Any` → GT1), `1850` (legacy + a violated bound → GT2), `1851` (legacy,
un-instantiated → still verifies, GT8).

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
with `PYCSL-TY3-CALLABLE-SCOPE`). The collection names are refused in their BARE
spelling too (`Callable[[bytes], int]`, `Callable[[list], int]`, …), not only when
written as a subscript — until gen #31 a bare collection name fell through to the
class-name branch, no record or variant matched, and the arrow domain silently became
`int`, so `Callable[[bytes], R]` and `Callable[[int], R]` emitted the same arrow
(witness `1852`, controls `1853` scalar / `1854` record). **AND THE UNKNOWN-CLASS HALF
IS CLOSED TOO (gen #31):** a name that is neither a primitive tag nor a class, `#@ datatype`
or TypeVar declared or imported into this module was ALSO silently `int` — so
`Callable[[Rekt], int]` for a `Rekt` that does not exist verified, emitting `int -> int`,
and the only backstop was Why3 rejecting the APPLICATION, a type error about the argument
naming nothing the user wrote. Now refused with the same `PYCSL-TY3-CALLABLE-SCOPE`
(witness `1877`, control `1878`). The admissible set is the four primitive tags plus every
`type_decls` name (records, variants, and IMPORTED classes — import resolution puts them
there) plus TypeVars (`typevar_registry` and PEP 695 `type_params`), because
`Callable[[T], int]` over a TypeVar verifies and a narrower set would have forbidden it.

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

