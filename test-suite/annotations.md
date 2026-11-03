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
| 30 | Declared in | `#@ declared_in <relpath>.py::<Class>.<method>` | Method (self-annotation mirror ONLY) | **A certified cross-mixin DECLARATION (cross-mixin-declaration-stubs B4).** Parses to the SAME node as `\trusted` (the method is emitted as the identical bodyless WhyML `val`; the target rides in the IR `reviewer` field as `declared_in:<target>`, so pycsl's own trust accounting still counts it as trusted). It may stand only on a bodyless stub, in a self-annotation mirror class, of a method the live class does NOT define (the live MRO dispatches it to `<Class>.<method>` in `<relpath>`); `bin/check-declaration-conformance.py` certifies that the named target EQUALS the live-MRO resolution and that the declaration claims no more than that definition (frame ⊇, raises ⊇, trivial pre/post, signature) and is RED otherwise. Outside `src/self-annotate/src/` it is REFUSED (nothing would check it: it would be an unreviewed `\trusted`; witness `7827`, control `7828`); a malformed target is a parse refusal (`7829`); the near-miss `# @declared_in` is refused (`7830`, control `7831`). Counted by `bin/count-trusted-directives.py` as its OWN class, apart from the `\trusted` markers. See §2.1.30 below. |

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

#### §2.1.30 Declared in (`declared_in <relpath>.py::<Class>.<method>`)

```python
class ControlFlowStmtMixin:
    #@ declared_in module6_whyml/expressions.py::ExpressionEmissionMixin._coerce_to_int
    #@ ensures True
    def _coerce_to_int(self, val: str) -> str:
        return ""
```

A **cross-mixin declaration** in the self-annotation mirror. Each mirror file is transpiled on
its own, so a mixin that calls a SIBLING mixin's method carries a local bodyless stub of it;
until B4 that stub was marked `#@ \trusted`, indistinguishable from an unverified body. The
directive names the definition the live composite's MRO dispatches the call to.

Grammar (concrete-syntax reference §2.1.30):

```
declared_in_decl ::= "declared_in" DECL_TARGET ;
DECL_TARGET      ::= /[A-Za-z0-9_][A-Za-z0-9_.\/-]*\.py::[A-Za-z_]\w*\.[A-Za-z_]\w*/
```

**Semantics.** `declared_in` parses to the SAME `Trusted` node as `\trusted`, with
`reviewer = "declared_in:<target>"`: the emitted WhyML is byte-identical to the `\trusted`
stub's (a bodyless `val` carrying the declaration's own contract), and pycsl's own TCB report
counts it as trusted. What changes is WHO vouches for it: not a reviewer but the repo plane
`bin/check-declaration-conformance.py`, which requires (g) the named target to EQUAL the
live-MRO resolution of the declaration, and (a)-(f) frame ⊇ the definition's (projected onto the
records the declaration reaches), raises ⊇, requires/ensures trivial on both sides, every other
clause also on the definition, and a refining signature. A `declared_in` that does not conform,
names another target, sits on a ledgered non-conforming or base-override declaration, carries a
`\trusted` marker too, or governs a def that is not a cross-mixin declaration of the census is
RED.

**Refusal outside the mirror.** `_run_pipeline` refuses any `declared_in` in a file outside
`src/self-annotate/src/` (`7827`, control `7828`): nothing checks it there, so it would be a
`\trusted` under another name. A malformed target is a parse error (`7829`). `# @declared_in`
(the near-miss spelling) is refused by the ingestor like every other directive keyword (`7830`,
control `7831`).

**TCB accounting.** A `declared_in` stub removes a `\trusted` MARKER (gross) but reduces the
trusted base only when its definition is itself VERIFIED (net); otherwise the trust moves to the
definition, which stays counted. `bin/count-trusted-directives.py` reports `declared_in` as a
separate column; `getting-better/trusted-reasons.tsv` does not list it.

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
         | diverges_decl | trusted_decl | declared_in_decl | abstract_decl | preserves_decl
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
declared_in_decl: "declared_in" /[A-Za-z0-9_][A-Za-z0-9_.\/-]*\.py::[A-Za-z_]\w*\.[A-Za-z_]\w*/

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

### 7.32 `__slots__`, dataclass pseudo-fields and explicit `super(X, self)` (routes #360 / #361 / #362 / #363)

Four more class shapes whose runtime behaviour the record model does not have (§7.28). Sound
REFUSALS on the source plus a sharper §7.28 (2) definite-assignment summary; no emission change.

(1) `__slots__` (route #360). An instance of a class whose every class declares `__slots__` has
no `__dict__`: CPython raises AttributeError on a store of any name outside the union of the
slots over the MRO, while the record model lowers `self.f = e` as an ordinary field store, so a
store outside the slots PROVED (tuple, list, empty `()` and inherited forms). Slots are read
from a literal `__slots__` (a string = one slot, a tuple / list / set of strings, a dict with
string keys) or `@dataclass(slots=True)` (its annotated fields). A class whose C3 MRO consists of
file classes that each declare slots, plus `object` / `Generic` / `Protocol`, with no
`__dict__` slot, is FULLY SLOTTED. In every function / method body, an attribute store,
augmented store, `del`, `for` / `with` target, or a `setattr` / `delattr` call whose receiver is
`self` of a method of a fully slotted class (not a `classmethod`'s class) or a name annotated
with / constructed as one, and whose name is outside the slot union, is REFUSED
(`PYCSL-R360-SLOTS-STORE`); so is a non-literal `__slots__` (its slot set is unknown). A class
with a base without `__slots__` (or an imported base) keeps a `__dict__` and is unchanged.

(2) DATACLASS PSEUDO-FIELDS (route #361). `k: InitVar[T]` (an `__init__` parameter handed to
`__post_init__`) and `_: KW_ONLY` (a sentinel) are not instance attributes, but they joined the
record and §7.28 (2)'s synthesized field set, so `d.k` / `d._` read under `no_exception`
PROVED and `D(1, 5).k == 5` PROVED (CPython AttributeError; a defaulted `InitVar` reads the
CLASS default). Pseudo-fields (bare, `dataclasses.`-dotted and string spellings) are excluded
from the definite-assignment sets as `ClassVar` is, and any attribute access (load, store,
`del`; `getattr` / `setattr` / `delattr` by literal name) of a pseudo-field NAME of a file
`@dataclass`, any receiver but an imported module, in a function that is not `\trusted` /
`\abstract`, is REFUSED (`PYCSL-R361-DATACLASS-PSEUDO-FIELD`). Keep the value in a real field.

(3) PSEUDO-FIELDS DROP THE CONSTRUCTOR GOAL (route #362). §3's constructor obligation
`_check_class_inv_<C>` is stated only over `int` fields and `int` / `bool` parameters; an
`InitVar[T]` parameter (or the `KW_ONLY` sentinel field) puts the synthesized constructor
outside that scope, NO goal was emitted and the invariant was ASSUMED: `invariant x >= 0`
PROVED `f(d) >= 0` with `D(-1, 0)` (CPython -1). A record carrying a class invariant whose base
closure holds a `@dataclass` declaring an `InitVar` or `KW_ONLY` pseudo-field is REFUSED
(`PYCSL-R362-INITVAR-INVARIANT`), as §7.28 (1) refuses `__post_init__`.

(4) `super(X, self).__init__()` (route #363). §7.28 (2) credited the DIRECT base's constructor
whatever `X` was; Python runs the constructor of the class AFTER `X` in the C3 MRO
(`super(A, self)` in `B(A)` runs `object.__init__`). The definite-assignment summary now
resolves `super(X, self)` (second argument the constructor's own `self`) through the class's
C3 linearisation; an `X` not on that MRO, a failed linearisation or any other argument shape
credits NOTHING (the sound direction), so a read of a field only the skipped constructor
stores is refused by `PYCSL-R347-FIELD-MAYBE-UNASSIGNED`. The constructor itself is already
opaque for route #150 and, on an invariant class, refused by §7.25 (2) (`self` escapes as an
argument of `super(..)`). Witnesses `4850`-`4869`; controls `4880`-`4886`.

### 7.33 Hashability decided over every class-body binding, through tuples, as a fixpoint; enum members as `Enum` builds them (routes #364 / #365 / #366 / #367)

Four gaps of §7.28 (route #349's unhashable-record refusal) and §7.30 (4)/(5) (the enum member
set), each a sound REFUSAL (`PYCSL-R349-UNHASHABLE-RECORD`, `PYCSL-SEM-ENUM-MEMBER-OPERATION`);
no emission changes.

(1) EVERY CLASS-BODY BINDING COUNTS (route #364). Only a top-level `def __eq__` and a literal
`__hash__ = None` were seen, so `__eq__ = lambda ..`, `__eq__` under `if`, `__hash__ = NOHASH`,
`__hash__ = None if .. else ..` and `__hash__, tag = None, 1` all PROVED `{r}` under
`no_exception \all` (CPython TypeError). Now any binding of `__eq__` in the class scope (any
statement, target form or nesting, an import, a `del`; nested `def` / `class` / `lambda` bodies
are other scopes) defines it, and a class binding `__hash__` is hashable only when every such
binding is a top-level undecorated `def __hash__`; any other binding may be `None` and the class
counts as unhashable (so `__hash__ = object.__hash__` is refused too — write a `def`).

(2) TUPLES ARE HASHED COMPONENTWISE (route #365). In every hashing position of §7.28 (set
element, dict key, subscript, `hash(..)`, `in` a non-list, `set(..)` / `frozenset(..)` /
`fromkeys(..)` / `.add` / `.discard` ... argument, and a `Set[..]` / `Dict[..]` annotation) the
check now enters tuple displays (any depth, through `:=` and `x if c else y`), names bound to a
tuple display, and `Tuple[...]` / `tuple[...]` annotation arguments (through Optional / Union):
`{(d, 1)}`, `hash((d, 2))`, `t: Tuple[D, int]; {t}`, `{(d, 1): 0}` are refused, and so is a
list / dict / set display or a list-typed name inside a hashed tuple (`{(xs, 1)}`).

(3) RECORD FIELDS, AS A FIXPOINT (route #366). Unhashability is the least fixpoint over every
class and functional namedtuple of the file (a field class declared later is seen). A record
whose hash hashes its fields (NamedTuple / namedtuple, frozen or `unsafe_hash=True`
`@dataclass`, or a subclass) is unhashable unless EVERY field annotation is provably hashable:
`int` / `str` / `float` / `bool` / `bytes` / `complex` / `None` / `Literal[..]` / `frozenset[..]`
/ `type[..]`, a hashable file class, or an Optional / Union / `|` / Tuple / Annotated / Final /
ClassVar of those. `object`, `Any`, a TypeVar, an imported or unknown name, any other container
and an untyped `namedtuple` field are possibly unhashable.

(4) THE ENUM MEMBER SET (route #367). Names listed in `_ignore_` and private `__x` names were
"members", so `C(2)`, `C(1)` and `C.B` were admitted (CPython ValueError / AttributeError). A
top-level class-body binding is now a member unless its name is in `_ignore_` (list / tuple /
string form, comma or space separated), private (`__x` not ending `__`), a dunder / sunder, an
annotation without value, or its value is a descriptor (`def`, `class`, `lambda`, builtin
`property(..)` / `classmethod(..)` / `staticmethod(..)`) or `nonmember(..)`; `member(v)` is a
member of value `v`. Ignored, private and value-less names are not class attributes (`C.B`,
`C.__B` are refused). An `_ignore_` that is not one top-level binding to a literal is refused
(the member set is unknown). The enum's user dunders and `__new__` are read from every
class-scope binding, as in (1) (`if ..: def __eq__`, `__eq__, x = ..`).

Witnesses `4900`-`4933`; controls `4940`-`4943` (`__eq__` under `if` with a top-level
`def __hash__`; tuples of a hashable frozen record; frozen / unsafe_hash records with hashable
fields; an enum with `_ignore_`, `member(2)` and a lambda attribute).

### 7.34 The constructor-invariant goal is stated over the int fields the invariant reads (route #226, gen #37)

Route #226's goal `_check_class_inv_<C>` (the constructor establishes the `#@ class invariant`)
was stated only when EVERY field of the record is an `int` bound to a literal or to an int
`__init__` parameter. A class whose invariant reads only int fields but which also has a
`str` / `List` / record field, or an `__init__` parameter of such a type, therefore got NO goal
and the invariant was ASSUMED by every method and every reader (measured: `@dataclass` `x: int;
s: str` under `self.x >= 0` proved `ensures \result >= 0` on `d.x`; CPython `D(-1, "a").x` is
-1). Now the goal is stated over the fields the invariant reads, which must all be int fields
bound to an int literal (or the constructor's literal default) or directly to an int `__init__`
parameter; the other fields cannot occur in the invariant and are unconstrained. `__init__`'s
`#@ requires` are premises conjunct by conjunct (a top-level `and` is split), keeping only a
conjunct over those int parameters: `#@ requires x >= 0 and len(xs) == x` keeps `x >= 0`, and a
`#@ requires len(xs) > 0` alone adds nothing (dropping a premise only makes the goal harder).
A synthesized `@dataclass` `__init__` has no contract, so its goal is premise-free over the
parameters feeding the invariant's fields (a field with `field(init=False, default=3)` is bound
to its literal). An `__init__` PARAMETER NAMED LIKE A DIFFERENT FIELD (`self.x = y; self.y = x`)
would make the goal's binders read one value as another (the increment-2 goal stated `forall x
y. x = y -> y = x -> (x = y)` and PROVED `self.x == self.y`, CPython `D(1, 2)`): REFUSED
(`PYCSL-R226-INIT-PARAM-FIELD-NAME-CLASH`); rename the parameter. NOT COVERED (no goal, the
invariant is still assumed; recorded in route #226's file): an invariant reading a non-int
field (`\length(self.toks)` -- now stated, §7.37 --, a `str` / record / element term, a quantifier, a predicate call), and
a field the constructor computes (`self.n = three()`). Witnesses `4950`-`4956`; controls
`4960`-`4964`.

### 7.35 Dataclass specifiers resolved by origin, constructor arity, the enum member set by `Enum`'s descriptor rule, hashability along the MRO and through fields / subscripts (routes #369 / #370 / #371 / #372)

Four gaps of §7.32 (dataclass pseudo-fields), §7.33 (4) (the enum member set) and §7.28 /
§7.33 (route #349's unhashable-record refusal), each a sound REFUSAL; no emission changes.

(1) DATACLASS SPECIFIERS BY ORIGIN, NOT SPELLING (route #369, `PYCSL-R369-DATACLASS-SPECIFIER`).
The dataclass model recognises `ClassVar` / `InitVar` / `KW_ONLY` / `field` / `dataclass` by
their literal names, so `from dataclasses import InitVar as IV`, `CV = ClassVar`, `field as
fld` or `KW_ONLY as KO` made a pseudo-field an ordinary field (`d.k`, `D(1, 5)` and `fld(default=7)`
read as 0 all PROVED; CPython AttributeError / TypeError / 7). Every `@dataclass` annotation
head (through a string annotation and one subscript) and default call is now RESOLVED through the file's imports and module-level aliases: a stdlib origin, a file
class / function, a builtin, an unbound name (never a specifier), or UNKNOWN (a non-stdlib or
relative import, a star import, a name bound by anything but a plain alias). REFUSED: a
specifier spelled other than by its own name (an alias), a specifier spelling that resolves
elsewhere, an UNKNOWN head or default callee, a default call to a file function (it may return
a `Field`: `x: int = mk()` with `mk` returning `field(default=7)` PROVED `D().x == 0`, CPython
7), and an annotated member nested in class-body control flow. (A decorator that is not the
literal `dataclasses.dataclass` — `dataclass as dc`, a rebound `dataclass` — was already refused
by the decorator-binding rule of routes #130-#133, measured.) A `field(..)` call takes only its keywords
(`default`, `default_factory`, `init`, `repr`, `hash`, `compare`, `metadata`, `kw_only`, `doc`),
with `init` / `kw_only` as `True` / `False` literals and never both defaults.

(2) CONSTRUCTOR ARITY (route #369, `PYCSL-R369-CONSTRUCTOR-ARITY`). A construction's argument
list was never checked against the constructor: `D(1, 5)` of a one-field dataclass, of a
dataclass past a `ClassVar`, of an explicit `__init__(self, x)`, a positional argument for a
keyword-only field and a missing required `field(kw_only=True)` all PROVED (CPython TypeError).
For a call `C(..)` of a file class whose constructor is known — the first class of its C3 MRO
defining a plain `def __init__`, else a `@dataclass`'s synthesized `__init__` (the fields of the
MRO's dataclasses in CPython's order: positional, then keyword-only by `kw_only=True`,
`field(kw_only=..)` or after a `KW_ONLY` sentinel; `InitVar` included; `ClassVar` and
`init=False` excluded), else `object.__init__` — too many positional arguments, an unknown or
repeated keyword, a positional-only parameter by keyword, or a missing required parameter is
REFUSED in every function that is not `\trusted` / `\abstract`. A `*` / `**` argument, a
`__new__` or class keyword anywhere in the MRO, a non-file base, or an unknown linearisation
skips the check.

(3) ENUM MEMBERS BY `Enum`'S OWN RULES (route #370, `PYCSL-SEM-ENUM-MEMBER-OPERATION`). The private
test now runs on the MANGLED key as `enum._is_private` does (an explicit `_C__B = 2` is private:
`C(2)` and `C._C__B.value` are refused). A value is a member value only when it provably has no
`__get__` / `__set__` / `__delete__`: a literal, a display, an operator / f-string over those, an
alias of an earlier member, `auto()` / `member(..)`. Any other value (`staticmethod(len)`,
`functools.partial(int)` — a descriptor since 3.14 —, `types.DynamicClassAttribute(..)`, a
module constant, any call) is neither a member nor an admitted class attribute, and the
literal value list becomes unknown (`C(v)` refused). A load `C.X` of a class-body name that is
NOT a member (a nested class, a `def`, a property, a descriptor, a private name) is refused,
except as the callee of a call to an own `def` / `staticmethod` / `classmethod`. An `_ignore_`
READ in the class body (`_ignore_.append("B")`) makes the member set unknown: refused.

(4) HASHABILITY ALONG THE C3 MRO (route #371, `PYCSL-R349-UNHASHABLE-RECORD`). The inherited
`__hash__` lookup stopped at the first base already decided, so `D(N, M)` with an unhashable
mixin `M` (`__hash__ = None`, an `__eq__`, an eq-dataclass; a third base; via an intermediate;
as a frozen record's field) was hashable. `__hash__` is now looked up along the C3 MRO: the
first class whose own body decides wins (`D(N, M)` with `N.__hash__` defined stays hashable); a
class whose linearisation is unknown counts as unhashable.

(5) THE HASHED ELEMENT'S CLASS FROM FIELDS AND SUBSCRIPTS (route #372,
`PYCSL-R349-UNHASHABLE-RECORD`). `{r.d}` / `{self.d}` (a field stored by `__init__` from a typed
parameter), `{t[0]}` (`t: Tuple[D, int]`), `{m[0]}` (`m: Dict[int, D]`) and `{xs[0]}` (`xs:
List[D]`) were never checked. A field's classes now come from its class-body / `self.f: T`
annotations and every `self.f = e` store of a method (a typed parameter, a constructor call, a
literal; anything else may be any class: with an unhashable class in the file such a field is
refused in a hashing position); a subscript of a name / field annotated `List` / `Sequence` /
`Deque` gives the element, `Dict` / `Mapping` / ... the value, `Tuple` the indexed component
(every component for a non-literal index); a `for` / comprehension target over such a name or field
takes the element (`List` / `Set` / `Sequence` / `Iterable` ...), the key of a `Dict` / `Mapping`,
every component of a `Tuple`.

Witnesses `4990`-`5039` and `5045` (NEW latents: `5008` / `5009` / `5037` / `5038` arity of an
explicit `__init__`, a plain dataclass, a literal `KW_ONLY`, a literal `field(init=False)`; `5036`
a `field(..)` returned by a helper; `5039` / `5045` a loop element and a field of a field); controls `5040`-`5044` (literal specifiers with `t.ClassVar`,
well-formed constructor calls, an enum with `_ignore_` / an alias / a `def`, `D(N, M)` with
`N.__hash__` first, hashable fields / components / values).

### 7.36 Nested-def calls in methods, private-name mangling in slots, erased augmented assignment and star-unpacking, `getattr` against class bodies (routes #373 / #374 / #375 / #376)

Four gaps around routes #337 / #343 / #357 / #358 (erased values) and #360 (slots), and the
`getattr` default of routes #22 / #197 / #309. No new contract syntax.

(1) A DEF NESTED IN A METHOD (route #373). Such a def is lifted to a METHOD of the class, so
its bare call `g()` resolves to no unit and lowers to the opaque call stub `g_0 ()`: an `int`
with every int law whatever `g` returns. `t = g(); t - t == 0`, `t == t`, `t != t` and
`t * 0 == 0` PROVED for `g` returning a field-less `self` (`-> "W"`, a default parameter, no
annotation) or a `str` / `List[int]` (CPython 1 / False / True / False). The call's result is
now the erased arbitrary object of §7.27 (route #249) unless every method of that name is
annotated `-> int` or `-> bool` (an unconstrained `int` over-approximates those): no int law,
refused into a builtin-typed slot (route #252), uninterpreted `==` / `!=` / arithmetic. A
nested def in a plain function is lifted to a module function and keeps its own contract.

(2) `__slots__` NAMES ARE MANGLED (route #374). CPython mangles every `__slots__` entry `__x`
(two leading underscores, not a dunder) by the class that declares it (`_A__x`; leading
underscores of the class name are dropped), and an attribute spelling `self.__x` / `o.__x` by
its innermost lexically enclosing class (none at module scope; a `setattr` string is never
mangled). §7.32's slots check (`PYCSL-R360-SLOTS-STORE`) now compares the two after mangling:
`self.__x` in a subclass (`_B__x`) and `a.__x` outside the class are refused (CPython
AttributeError, PROVED before), and the real slot `self._A__x` is admitted.

(3) ERASED AUGMENTED ASSIGNMENT AND STAR-UNPACKING (route #375). Under `no_exception`, an
augmented assignment `t op= v` whose target or value is erased (an alias `t = self`, a
field-less-class parameter, an `Any` value) is preceded by the failing assertion
`PyCSL-R375` (its `__iadd__` / `__add__` may raise; route #337 refuses only `self op= v`
spelled on `self`). A starred element of an erased value in a list / set / tuple display or a
starred call argument (`[*x]`, `{*x}`, `(*x,)`, `f(*x)`) carries the same failing assertion in
ANY program context: the starred node was lowered as the bare element, so `[*self]` was the
one-element array (`no_exception \all` PROVED, CPython TypeError) and `len([*x]) == 1` PROVED
for `x: Any`.

(4) `getattr` FINDS CLASS-BODY BINDINGS (route #376). `getattr(o, "k", d)` / `getattr(o, "k")`
on a known record whose instance fields do not include `k` answered `d` (or the per-site
"missing" opaque). CPython's lookup finds a class-body binding of `k` first — a class
attribute, method, property, nested class or import, own or inherited — and every name
`object` has (any dunder): `k = -1` proved `getattr(r, "k", 0) >= 0`, a method `k` proved
`getattr(r, "k", 0) == 0`. Such a `getattr` is now REFUSED
(`PYCSL-R376-GETATTR-CLASS-BINDING`), as is any `getattr` of a non-field name on a class whose
file MRO has a `__getattr__` / `__getattribute__`. A name no class body of the file binds still
answers the default (a base class outside the file is not read: residual).

The nested-def rule (1) applies to the names of defs nested in a method of the file; a starred
CALL argument (`f(*x)`) of an erased value is asserted under `no_exception` only (outside it,
the callee's vararg sequence is a recorded residual).

Witnesses `5050`-`5081`; controls `5090`-`5093` (a nested `-> int` def in a method and in a
plain function; mangled real slots; int augmented assignments under `no_exception \all`; an
absent attribute's default).

### 7.38 A class-body name bound once, `*` / `**` call arguments, `init=False` / `super().__init__` arity, metaclass `__call__` (routes #377 / #378 / #379 / #380)

Four more places where the model read a class body or a call otherwise than CPython does, each a
sound REFUSAL; no emission changes.

(1) A NAME BOUND TWICE IN A CLASS BODY (routes #377 / #378; the shared Module 3 refusal of
routes #122 / #130-#133, "a name's runtime binding is not the `def` the model resolves it to").
CPython's class namespace keeps the LAST binding, while the method tables, the constructor
reader and the dataclass field reader took the FIRST: two `def __init__` gave the constructor
goal (and a `requires` premise) from the dead first one, two `def get` resolved `c.get()` to the
first contract over the last body, and `n: int = field(default=3, init=False)` followed by
`n = -1` (or a second annotated `n`) read the default 3 (CPython -1). In every class body, a
name with two or more binding sites (defs, stores, imports, except-as / match captures; nested
function / lambda bodies excluded) of which one is a `def` / `class` statement or an annotated
member is REFUSED, except a property accessor chain (`@property def x`, then only `@x.setter` /
`@x.getter` / `@x.deleter` defs) and an `@overload` chain (every def but the last decorated
`overload` / `typing.overload`, whose stubs' `ensures` already bind the implementation). The
module scope is unchanged (a duplicate module `def` is fail-closed: the model agrees the last
wins).

(2) `*` / `**` CALL ARGUMENTS (route #379, `PYCSL-R379-STARRED-CALL-ARGUMENT`). The lowering
dropped a `*` / `**` argument (or counted `*xs` as ONE positional), so `D(**{"x": 5}).x == 0`,
`D(1, **kw).y == 0` and `h(1, **kw)` / `C(**{"y": 1})` under `no_exception` all PROVED (CPython 5,
7, TypeError). In a function that is not `\trusted` / `\abstract`, a call with a `*` or `**`
argument of a file class (a construction), a module-level `def`, or a method name defined in a
file class is REFUSED, except a `*xs` that lands entirely in the `*args` parameter of every
candidate callee whose contract does not name that parameter (the contract then holds for any
tuple there). Calls of imported / builtin callees are unchanged.

(3) CONSTRUCTOR ARITY, CONTINUED (route #380, `PYCSL-R369-CONSTRUCTOR-ARITY`). §7.35 (2)'s
constructor is now found past a `@dataclass(init=False)` (which writes no `__init__`: the MRO
walk goes on, ending at `object.__init__`, so `D(1)` is refused); a `super().__init__(..)` /
`super(X, self).__init__(..)` is checked against the `__init__` of the class after `X` in the
MRO of `X` and of every file subclass of `X` whose MRO tail after `X` is that class's own MRO
(`object.__init__` at the end: no argument); an explicit `C.__init__(self, ..)` is checked
against `C`'s constructor.

(4) A METACLASS `__call__` (route #380, `PYCSL-R380-METACLASS-CALL`). A metaclass `__call__`
decides what `C(..)` returns (one returning 42 made `C(1).x == 1` PROVE; CPython
AttributeError). A construction `C(..)` of a file class whose MRO names a `metaclass=` other
than `type`, `abc.ABCMeta`, or a file metaclass whose MRO (over `type` / `ABCMeta` only) binds no
`__call__`, is REFUSED.

Witnesses `5140`-`5157` (red team 29) and `5158` / `5159` (NEW latents: `super().__init__(5)` over a no-argument `__init__` and over `object`); controls `5170`-`5174`
(`init=False` with `D()`, a metaclass without `__call__`, a matching `super().__init__(3)`, an
`@overload` chain, distinct method names).

### 7.37 The constructor-invariant goal states `\length(self.f)` over list fields (route #226 increment 2c, gen #37)

§7.34's projection stated the goal `_check_class_inv_<C>` only over INT fields, so an invariant
reading `\length(self.f)` of a LIST field got NO goal and was assumed by every method and reader
(measured: `#@ class invariant \length(self.xs) >= 1` over `self.xs = xs` from an `__init__`
parameter proved `#@ no_exception \all` on `self.xs[0]`; CPython `D([]).first()` raises
IndexError). Now a `\length(self.f)` term is allowed in the projected invariant when `f` is a
list field (emitted as `array <T>`) that the constructor does not compute: `f` is bound in the goal
at its array type, either to the `__init__` parameter it is stored from (quantified, nothing
assumed of it) or, with no parameter binding, to the literal LENGTH of its initialiser (`[0] * 8`,
`[1, 2, 3]`, `[]`), stated as `Array.length f = N`. `__init__`'s `#@ requires` conjuncts over the
bound parameters are premises, now including `len(p)` / `\length(p)` of a list parameter. So a
constructor that takes a list and claims `\length(self.toks) >= 1` must say so:
`#@ requires len(toks) >= 1` on `__init__`. An invariant that is true of every list
(`self.pos <= \length(self.toks)` with `self.pos = 0`) needs no precondition. A synthesized
`@dataclass` `__init__` has no contract, so a dataclass list field under a `\length` lower bound
cannot establish it. NOT COVERED (no goal, the invariant is still assumed; route #226's file): a
list field whose initialiser the constructor COMPUTES (`[Tok(0)] * 3`, `bytearray(N)` over a
module constant, a call), an element / subscript / quantifier / predicate term, `bool` fields.
Witnesses `5100`-`5109`; controls `5110`-`5114`.

### 7.40 The `\length` constructor goal reads the list field at the END of `__init__`; an unstatable one is refused (routes #384 / #385, gen #37)

§7.37's goal bound a list field at its STORE, so a later change in `__init__` was invisible
(`self.disk = [0] * 4; self.disk.pop()` under `\length(self.disk) == 4`, or
`self.toks = toks; toks.clear()` through the parameter alias, PROVED a `no_exception` read of
`self.disk[3]` / `self.toks[0]`; CPython raises IndexError), `[] * 4` was read as length 4, and a
computed initialiser (`default_factory`, `[0] * 2 + [0]`, a comprehension, a slice) or a subclass
whose field comes from `super().__init__(..)` left NO goal, so the invariant was assumed. Now the
goal uses the field's value at the end of `__init__`:
- a FRESH list of known length — a display, `[..] * K` (length `len * max(K, 0)`, so `[] * N`
  and a negative repeat are EMPTY), `bytearray(K)` / `bytes(K)` / `list()`, K an int literal or
  a module constant bound exactly once — followed only by top-level `self.f.append(x)` /
  `insert(i, x)` / `extend([..])` / `pop()` / `pop(i)` / `clear()` / `reverse()` / `sort()`
  (arguments call-free) is stated as `Array.length f = N` for the final N;
- a field stored from an `__init__` parameter p keeps §7.37's binding only when neither p nor
  `self.f` is otherwise named in `__init__` (`len(..)`, `x[i]` reads and `x[i] = v` element
  stores are allowed) and no call follows the store;
- anything else (a later `remove` / alias / second or tuple store / loop / branch / walrus, a
  `return`, another `__init__` call after the store, a computed initialiser, no binding at all)
  has no statable goal: a class whose `\length` invariant is otherwise statable is REFUSED
  (`PYCSL-R384-INVARIANT-GOAL-UNSTATABLE`), never assumed.
A `super().__init__(..)` / `super(X, self).__init__(..)` / `B.__init__(self, ..)` call reaching a
file class whose `__init__` has a `#@ requires` and a parameter that is not `int` / `bool` /
unannotated is REFUSED (`PYCSL-R385-DELEGATED-INIT-REQUIRES-UNCHECKED`): that requires is a premise
of the goal and of `B(..)` constructions but nothing checks it at the delegating call (over int
parameters route #335 already substitutes the arguments into the subclass's own goal). NOT
COVERED: an invariant whose goal also stops at an element / quantifier / string / predicate term
(route #226's residual, including two mirror parsers) is still assumed; an unverified caller that
keeps an alias of the list it passed and mutates it later (`c = Cur(DEF); DEF.clear()` in
`__main__`). Witnesses `5240`-`5259`; controls `5270`-`5275`.

### 7.41 A builtin name rebound by a nested def / class / import / lambda / comprehension; class-body members CPython may never bind (routes #386 / #387, gen #37)

Two more places where a name's runtime binding is not the one the model reads, each a sound
REFUSAL in the shared Module 3 checks of routes #122 / #130-#133 and #377; no emission changes.

(1) A BUILTIN NAME REBOUND LOCALLY (route #386; "a name's runtime value is not the one the model
reads"). Route #131 refused a builtin name rebound by an assignment, a loop / with / except target
or a parameter and then read. A `def` or `class` nested in a function or METHOD, an import
(function-local or module-level, other than an unaliased `from builtins import X`), a LAMBDA
parameter and a COMPREHENSION target named like a builtin were still lowered to the builtin model:
`def max(x, y): return -100` in a method, then `max(self.a, 1) >= self.a` PROVED (CPython -100);
`from operator import sub as max` then `max(3, 1) == 3` PROVED (CPython 2); `g = lambda max:
max(1, 2)` then `g(min) == 2` PROVED (CPython 1). Each of these bindings now joins route #131's
rule: a read of the name in the binding's scope (nested scopes included) is REFUSED. A
module-level `def len` keeps route #75's user-shadowing model; a METHOD named like a builtin
(`def max(self)`, called as `self.max()`) is a class attribute, not a shadow, and is unchanged.

(2) A CLASS-BODY MEMBER CPython MAY NEVER BIND (route #387; "a name's runtime binding is not the
`def` the model resolves it to"). The method tables take every def / class / annotated member of
a class body as an attribute. `global get` (or `nonlocal get`) in the body sends the def's
binding to the module scope (`c.get()` raises AttributeError; `global __init__` leaves
`object.__init__`, so the constructor goal was proved over a body CPython never runs), and a def
under `if False:` / `while False:` / `if sys.version_info < (3, 0):` / `for _ in range(0):` or
after a `raise` inside `try:` is never executed. In every class body, a `global` / `nonlocal`
naming a name the body binds is REFUSED, and so is any def / class / annotated member nested under
a compound statement (`if` / `while` / `for` / `try` / `with` / `match`) — whether it runs is not
modelled — except in the BODY of an `if True:` (which always runs; control 4940 binds `__eq__`
there; its `else` arm is refused). No other corpus, mirror or library class body has one outside
witnesses already refused. Write the member at the top level of the class body.

Witnesses `5290`-`5310`; controls `5320`-`5325` (a nested def not named like a builtin beside the
builtin `max`, a method named `max`, plain class-body members, an `if True:` inside a method, a
function-local `from builtins import max`, a method under a class-body `if True:`); witness `5310` is the `else` arm of
that `if True:`.

### 7.42 A base class the model has no entry for is refused by default (systematic rule S1, closes route #381's stdlib-base share, gen #37)

Every reader of a class's MRO (hashability, `getattr` defaults, constructor arity, the override
checks, inherited invariants) walks the classes of the file and a few bases with a dedicated
model, and SKIPPED every other base: the attributes, `__eq__` / `__hash__`, `__init__` and
`__getattr__` a standard-library or builtin base contributes were absent from the model.
Measured (red team 29, route #381, all PROVED at `7bf752d4e`, CPython TypeError): `class
D(collections.UserList)` (also `UserDict`, `deque`, `OrderedDict`, `Counter`, `defaultdict`,
`types.SimpleNamespace`, `array.array`, `argparse.Namespace`, `collections.abc.Set` /
`Mapping`, a second base, a subclass of such a class) hashed in a set under `no_exception`.
RULE (one check where route #341 resolves every base, `PYCSL-S1-UNMODELLED-BASE`): a base that
resolves through the file's imports, or as a builtin name, to a standard-library / builtin class
is admitted only if it is in the BASE-MODEL table -- `object`, `type`, a builtin exception class,
`enum.Enum` / `IntEnum` / `Flag` / `IntFlag` / `StrEnum` (with `int` / `str` admitted as the mixin
of an enum base, route #353), `typing.NamedTuple` / `Protocol` / `Generic` / `TypedDict`,
`abc.ABC`, `ast.NodeVisitor` / `NodeTransformer`. Any other is REFUSED when the class is named by
code outside the `__main__` driver (a subclass names it in its bases, so the closure is refused
too). Every class of a DEPENDENCY module the file's imports reach (resolved like route #181) is
checked with no reference filter (it is importable: `from m import D` with `class D(UserList)`
unreferenced in `m` PROVED `{d}`), and an unresolved base name in a file with a standard-library
star import (`from collections import *`) is refused. File classes, user-module classes and other
unresolved names are routes #341 / #345's.
Census (both corpora, the 53 mirrors, `pycsl_lib`): 4 such bases, none refused (classes named only
by `__main__`, or an int-mixin enum). Witnesses `5420`-`5435` (`5434` / `5435` new two-level latents), `5448`-`5452` (star import, dependency module, re-bound import, star import in a dependency, transitive re-export); controls `5460`-`5463`. See
`getting-better/systematic-soundness-r3.md` for why the rule is a polarity flip (admit what is
modelled) instead of another deny-list entry.

### 7.43 `getattr`'s default is the answer only when the whole lookup is modelled (systematic rule GD, routes #388 / #389, gen #37)

Route #376 refused `getattr(o, "k", d)` on a known record when a class body of the file's MRO
binds `k`; every OTHER place CPython looks was assumed empty, so the default was answered
(measured, red team 30, all PROVED at `7bf752d4e`): a base the file does not define --
`getattr(e, "args", 0)` over `class E(Exception)` (CPython `()`), `getattr(r, "_abc_impl", 0)`
over `R(ABC)`, `getattr(p, "count", 0)` over a `NamedTuple` (a method) -- an attribute created
by `setattr(self, "k", 5)` in `__init__` / `__post_init__` or with a computed name (CPython 5), and
the mangled `_R__k` of a `self.__k` store (CPython 5). RULE (polarity flip, one place: the
`class_binds_r376` map built in `_run_pipeline`): a class answers UNKNOWN (so a `getattr` default
on it is refused, `PYCSL-R376-GETATTR-CLASS-BINDING`) when its MRO reaches a STANDARD-LIBRARY or
builtin base other than `object` (resolved through the imports; an unresolved name in a file with
a standard-library star import counts), or when any code outside the `__main__` driver calls `setattr` /
`delattr` / `vars` or touches `.__dict__` / `.__setattr__` / `.__delattr__`; and a `self.__x`
attribute of class `C` binds `_C__x`. A base from a USER module is still not read (residual of
route #376: marking it unknown refuses the mirror's `getattr(self, .., default)` over emitter
mixins defined in sibling modules, 2 mirrors GONE when measured). Census (both corpora, 53
mirrors, `pycsl_lib`): no PASS file affected. Witnesses `5436`-`5442`; controls `5464`, `5465`.

### 7.44 A `Protocol` / `TypedDict` class is a type, not a value (systematic rule TC, route #391, gen #37)

A class one of whose bases resolves to `typing` / `typing_extensions` `.Protocol` or `.TypedDict`
(or that derives from a file `TypedDict` class) is a TYPING CONSTRUCT with no runtime model. It is
admitted where a type is written -- an annotation, a class base, the type argument of `cast` /
`TypeVar` / `NewType` -- and any other load of its name outside the `__main__` driver is REFUSED
(`PYCSL-TC-TYPING-CONSTRUCT-VALUE`). Measured (red team 30, all PROVED at `7bf752d4e`): `P()` and
`Q()` for `class Q(P, Protocol)` under `no_exception` (CPython TypeError), `TD(a=1).a` (the call
returns a `dict`: AttributeError), `isinstance(x, TD)` / `isinstance(x, P)` (TypeError). A concrete
class `C(P)` deriving from a protocol without listing `Protocol` is an ordinary class. Census (both
corpora, 53 mirrors, `pycsl_lib`): no PASS file uses a typing construct as a value. Witnesses
`5443`-`5447`; control `5466`.

### 7.45 `*` / `**` arguments to a builtin (systematic rule SB, route #390, gen #37)

Route #379 refused a `*` / `**` argument at a call of a file class, a module `def` or a file
method; the builtin models read explicit arguments only, so at a BUILTIN callee the starred
argument was dropped: `sorted(xs, **{"reverse": True})` proved ascending and `sum([1, 2],
**{"start": 10}) == 3` proved (red team 30, PROVED at `7bf752d4e`; CPython reversed / 13). RULE
(the same polarity flip: a starred argument is admitted only where the callee's binding is
modelled): a `*` / `**` argument at a call of a builtin name the file does not bind or import is
REFUSED (`PYCSL-R379-STARRED-CALL-ARGUMENT`). Census (both corpora, 53 mirrors, `pycsl_lib`): 0
such calls. Witnesses `5453`-`5455`; control `5467`.
### 7.46 Hashability of outside bases and stdlib values, containers in every hashing position, element classes through aliases / calls / views (routes #381 / #382 / #383, gen #37)

Three more gaps of route #349's unhashable-record refusal (§7.28 / §7.33 / §7.35 (4)-(5)), each a
sound REFUSAL (`PYCSL-R349-UNHASHABLE-RECORD`, message extended); no emission changes.

(1) OUTSIDE BASES AND STDLIB VALUES BY THEIR REAL CLASS (route #381). §7.35 (4)'s MRO lookup
SKIPPED every base outside the file, so `class D(UserList)` / `D(deque)` / `D(OrderedDict)` /
`D(Counter)` / `D(defaultdict)` / `D(SimpleNamespace)` / `D(array.array)` / `D(argparse.Namespace)`
/ `D(collections.abc.Set)` / `D(collections.abc.Mapping)` / `D(N, UserList)` were hashable (`{d}`
PROVED; CPython TypeError). Every base and annotation name not defined in the file is now RESOLVED
through the file's imports (and the builtins) to its qualified name, and an allow-listed
standard-library module (loaded only from the interpreter's stdlib directory) is imported to read
the REAL class: a base whose `__hash__` is None, or that is UNKNOWN (a non-stdlib or relative
import, a name bound otherwise), decides UNHASHABLE in the MRO walk; a hashable one (`object`,
`Exception`, `int`, `ABC`, `Generic`, `NamedTuple`, `UserString`, `abc.Sequence` ...) is skipped
as before. A class whose `__hash__` DELEGATES to its contents — `types.MappingProxyType`,
`weakref.ref`, `slice`, `memoryview` (a writable one raises ValueError) — counts as unhashable.

(2) CONTAINERS IN EVERY HASHING POSITION (route #382). A set element / dict key / `add` /
`hash(..)` argument annotated by a stdlib container (`deque`, `Deque[int]`, `Set[int]`,
`MutableSet`, `SimpleNamespace`, `UserList`, `OrderedDict`, `defaultdict`, `Counter`,
`array.array`, `list`, `dict`, `List[..]`, `Dict[..]`), a list display bound to a local, a
`List[List[int]]` element is REFUSED at any depth, not only inside a tuple. A value annotation
admitting a list / dict / set / bytearray / deque (`Sequence`, `Iterable`, `Mapping` ...) is
unhashable; a value DECLARED `Any`, `object`, a TypeVar, an unknown import or an
un-parameterised `tuple` may be any class of the file.

(3) ELEMENT CLASSES THROUGH ALIASES, CALLS AND VIEWS (route #383). §7.35 (5) derived a hashed
element's class from typed names, fields and one subscript only. A per-function TYPE PROPAGATION
now follows module type aliases (`DD = D`, `DL = List[D]`), `m.get(..)` / `pop` / `setdefault`,
loops over `.keys()` / `.values()` / `.items()` (tuple targets componentwise), comprehensions and
displays, slices then subscripts, `{*ds}`, a method's or module function's `-> T`, constructor
calls and the common builtins (`sorted`, `list`, `tuple`, `iter`, `enumerate`, `zip`, `min` ...),
and fields typed by the parameter they are stored from (a field absent from a class and its
file bases counts only through the file subclasses defining it, unless the attribute may be
bound otherwise). A local read before its bindings are typed is a least fixpoint (`i = 0 .. i =
i + 1` is `int`). With an unhashable class in the file, a value declared `Any` / `object` / a
TypeVar (a parameter, a local, a field) is refused in a hashing position.

Witnesses `5330`-`5385` (47 red-team witnesses plus NEW latents `5377`-`5385`: `s.add(d)` and
`{d: 1}` with `d: deque`, `types.MappingProxyType` (two spellings), `memoryview`, `slice`,
`weakref.ref`, a field defined only by a file subclass, a base from `from collections import
*`); controls `5390`-`5393` (hashable outside
bases, hashable values and components, every #383 source over a FROZEN element class in a file
with an unhashable class, hashable stdlib values `Fraction` / `Decimal` / `date` / `FrozenSet`).
Residuals (the rule is still a DENY-list): an UNDERIVABLE value (an unknown callee or receiver, an
un-annotated return, an `Any` reached through a container such as `Dict[str, Any]`'s `.get(..)`)
is not checked; a value declared `Any` / `object` / a TypeVar / an un-parameterised `tuple` is
checked only against the FILE's unhashable classes — a builtin container reaching it (`d: Any`
called with a list, `t: tuple` holding a list) is not seen. A class imported from a non-stdlib module (`from mylib import
D`, `D(UserList)` there) is an unknown value class, also checked only against the file's own.

### 7.47 A value of an unknown class is refused in a hashing position (allow-list polarity, route #383 addendum, gen #37)

§7.46 checked a value DECLARED `Any` / `object` / a TypeVar, or of a class imported from a
non-stdlib module, only against the file's OWN unhashable classes (a DENY-list: refuse only what
is proved unhashable), so `def g(d: Any): {d}` called with a list, `m: Dict[str, Any]` with
`{m["a"]}`, `{d: 1}` with `d: object`, `s.add(d)` with `d: Any`, and `{d}` with `d: D` where
`from mylib import D` defines `__eq__` without `__hash__`, all PROVED `no_exception \all`
(CPython TypeError). Such a value is now refused in every hashing position (a set display /
comprehension element, a dict key, the argument of `add` / `discard` / `remove` / `get` /
`setdefault` / `pop` / `__contains__` / `__getitem__`, an `in` test or subscript, `hash(..)`, the
elements of `set` / `frozenset` / `Counter` / `fromkeys` over a display) unless its
class is KNOWN hashable (`PYCSL-R349-UNHASHABLE-RECORD`, same message). Exception: in the FIRST
statement of the body of `if A in B:` (the test, or a conjunct of an `and` test whose later
conjuncts run no code), `B[A2]` with `A2` the same value as `A` (`x.get(K)` and `x[K]` for a
`Dict`-annotated local `x` and a constant `K`), and no call / walrus / yield / await / lambda in
that statement, is the value `A in B` has just hashed, and keeps the §7.46 check only (the
mirror's `func.get("return_value_type") in self._record_types` then
`self._record_types[func['return_value_type']]`).

Witnesses `5500`-`5506`; controls `5510`-`5511` (int / str / `Tuple[str, str]` / `Optional[str]`
values and a frozen file dataclass PROVE). Residuals: an UNDERIVABLE value (an unknown callee
or receiver, an un-annotated return, `.get(..)` of a `Dict[str, Any]`, an `Any` element of a
declared container) is still unchecked (under a TypeError claim it is refused since §7.131, run #3); an UN-PARAMETERISED `tuple` / `Tuple` keeps the §7.46
check only (`t: tuple` holding a list PROVES — the self-annotation mirror `pycsl.py` keys
`_merge_records_best_of_n` by `_record_key(..) -> Tuple` whose components are why3 JSON values,
genuinely `Any`; refusing it would lose that proved mirror); a HASHABLE class imported from a
non-stdlib module (a frozen dataclass of `mylib`) is now refused in a hashing position
(over-refusal: its module is not inspected; measured 0 corpus / mirror / `pycsl_lib` users).

### 7.48 A base name is resolved by SCOPE (route #392, gen #37)

S1 (§7.42), its standard-library star-import rule, and §7.46's hash MRO took a base name for a
FILE class whenever a class of that name was defined ANYWHERE in the file, so `from collections
import UserList` + `def _unused(): class UserList: ...` (a LOCAL of `_unused`) + `class
D(UserList)` hashed `{d}` PROVED `no_exception` (also `UserDict`, a shadowing class nested in a
method, `from collections import *` + a nested `class OrderedDict`; red team 31, all PROVED at
`7859e8fb0`, CPython TypeError). RULE (one resolver, inline where S1 resolves bases; every reader
reads its result): a base head name is resolved as CPython evaluates a class header -- in the
scope enclosing the `class` statement (a class body only when it is the immediately enclosing
scope), then the enclosing function scopes (a `global` declaration jumps to the module), then the
module (through `if` / `try` / `with` / loop bodies; nested def / class / lambda bodies are other
scopes), then the builtins, then a standard-library star import. It resolves to a file class only
when the scope that binds the name binds it only by `class` statements; an import / builtin / star
import there is read as that outside class by S1 (refused when unmodelled,
`PYCSL-S1-UNMODELLED-BASE`) and by the hash MRO (classified through the imports like any outside
base, §7.46 (1); NEW latent: `from typing import TypedDict` + a nested `class TypedDict` + `class
T(TypedDict)` hashed `{t}` PROVED, an instance is a `dict`; now `PYCSL-R349-UNHASHABLE-RECORD`).
Census (both corpora, 53 mirrors, `pycsl_lib`): 0 emission changes. Witnesses `5550`-`5554`;
control `5590` (a module-level `class UserList` without an import, a base from the same def, a
module `class E(object)` beside a nested `class object`).

### 7.49 The hashed value's class from module globals, class attributes, copies and any iterable (route #394, gen #37)

§7.46 (3)'s propagation had no SOURCE for a module global, a class attribute or a copy, and
`set` / `frozenset` / `Counter` / `fromkeys` read only a display or an annotated name, so the
hashed value had no class and was ADMITTED: `{K}` with `K = D(1)` (D an eq dataclass), `{XS}`
with `XS = [1]`, `{G[0]}` / `{G["a"]}` / `set(G)` of a global display, `{(G, 1)}`, `{C.K}`,
`{self.K}`, `C.XS in s`, `frozenset(C.XS)`, `set(d.values())` / `set(d.items())` /
`frozenset(m.values())` of a `Dict[str, D]` / `Dict[str, List[int]]`, `{copy.copy(x)}`,
`{dataclasses.replace(x)}`, `b = copy.copy(a); {b}` (red team 31, 22 witnesses, all PROVED at
`7859e8fb0`, CPython TypeError). RULE (sources added to the derivation, each precise; a
`PYCSL-R349-UNHASHABLE-RECORD` refusal): (1) a module name bound ONCE (no `global` of it) has
the class of its initializer -- a literal, an f-string, a tuple of such, a file-class
constructor, a builtin `frozenset` / `str` / `int` / `float` / `bool` / `bytes` / `complex` /
`range` call, another such global, a class / def / lambda (a hashable object), primitive
arithmetic; a list / set / dict display is that container, with its elements' classes when the
name is READ-ONLY (every load is the receiver of a subscript load, of `get` / `keys` / `values`
/ `items` / `copy` / `count` / `index`, an `in` container, an iterable, or the argument of `len`
/ `sorted` / `list` / `tuple` / `set` / `frozenset` / `iter` / `enumerate` / `min` / `max` /
`sum` / `any` / `all`) and UNKNOWN elements (refused when hashed) otherwise; (2) a class-body
name bound once at the top of the body the same way (a method / nested class is a hashable
object, a `@property` its `-> T`, an `Enum` member an instance of the enum), read for `C.k` along
C's MRO and, when no field `k` exists, for `o.k` over o's class and every file subclass (not when
`k` is stored through a receiver other than `self` or the file adds attributes dynamically); (3)
a standard-library import or a builtin name, by the real object (a primitive constant by its
type, a hashable object as hashable); (4) `copy.copy(x)` / `copy.deepcopy(x)` /
`dataclasses.replace(x, ..)` has x's class; (5) `set` / `frozenset` / `Counter` / `fromkeys` /
`dict` over ANY other iterable hash its ELEMENTS (the propagation's element types; `dict(..)`
the first component of each pair; a mapping argument of `dict` hashes nothing new). Census
(both corpora, 53 mirrors, `pycsl_lib`): 0 emission changes, `pycsl_lib` screen identical.
Witnesses `5555`-`5576`; control `5591`. MEASURED AND NOT LANDED -- the full allow-list flip
("a value no recognised source derives is unknown, and unknown is refused"): refusing every
underivable (`#UND`) hashed value REFUSES 27 of the 53 mirrors (679 sites: `node.get('name')`
/ `node['target']` of `Dict[str, Any]` IR, values derived from them, un-annotated parameters),
(first scan, before a declared annotation dominated a binding's underivable value) 7 root / pyref PASS files (`0882`, `0883`, `1318`, `3600`, pyref `0091`, `0212`,
`stdlib/collections/counter_proves`) and 1 `pycsl_lib` file (`syscfg`); refusing only values
with NO source at all still refuses 7 mirrors (19 sites: attributes of `ast` nodes and of
imported user-module records, un-annotated parameters). Residual (as §7.47): an underivable
value (an unknown callee or receiver, an `Any` reached through a container, an un-annotated
parameter) is still checked only against what the derivation finds.

### 7.50 A hashed value may be an instance of any file subclass of its static class (route #395, gen #37)

The hash check read the STATIC class only: `b: B` (hashable) hashed by `{b}` PROVED although
`__main__` passed an instance of a file subclass `@dataclass D(B)` (eq, not frozen), `D(B)` with
`__eq__` only, `D(B)` with `__hash__ = None`, or `D(B)` whose `def __hash__` raises ValueError
(red team 31, PROVED at `7859e8fb0`). RULE (closed world: a value of static class B may be an
instance of any class of the file that derives from B): B counts as unhashable at a hashing site
-- a fixpoint step of §7.33's unhashability -- when one of its proper file subclasses is
unhashable, or defines its own `def __hash__` that is not a verified method carrying `no_exception
\all` (`PYCSL-R349-UNHASHABLE-RECORD`, message extended). Census (both corpora, 53 mirrors,
`pycsl_lib`): 0 emission changes. Witnesses `5577`-`5580`; control `5592` (a plain, a frozen
dataclass and a verified-`__hash__` subclass). Residual: a class's OWN `def __hash__` is not
required to be verified (a raising `__hash__` on the static class itself still PROVES `{d}`;
requiring it refuses PASS controls `4694`, `4940`, `5043`, whose `__hash__` carry no contract);
`__eq__` raising on a hash collision is not modelled.

### 7.52 A builtin exception base is modelled with its constructor; a construction is checked against it (route #393, gen #37)

§7.42 (S1) admitted EVERY builtin exception class as a base, and a subclass construction was
lowered as an arbitrary instance with no signature check: measured (red team 31, all PROVED at
`7859e8fb0`, CPython TypeError) `class D(ExceptionGroup)`; `D()`, `D(UnicodeDecodeError)`;
`D("x")`, `D(SyntaxError)`; `D("m", 1)`, and `class D(Exception)`; `D(x=1)` under
`no_exception`. RULE (allow-list polarity, two places): (1) the BASE-MODEL table admits a
builtin exception only if its constructor is modelled: the classes whose constructor takes ANY
positional arguments (`BaseException`, `Exception`, `ValueError`, `KeyError`, `OSError`, ... —
the classes a subclass without `__init__` accepts with every arity 0..7, measured on CPython
3.14), and the `SyntaxError` family (`IndentationError`, `TabError`), whose shape is checked in
(2); `BaseExceptionGroup` / `ExceptionGroup` and `UnicodeDecodeError` / `UnicodeEncodeError` /
`UnicodeTranslateError` are refused like any unmodelled base (`PYCSL-S1-UNMODELLED-BASE`); (2)
route #369's constructor-arity check reads an any-arity base as the signature `(self, *args)` —
NO keyword — so `D(x=1)`, `super().__init__(msg=x)` reaching the base, and
`Exception.__init__(self, msg=x)` are refused, and a `SyntaxError`-family base as `()`, `(msg)`
or `(msg, details)` with `details` a 4- or 6-element tuple DISPLAY (so `D("m", 1)` is refused;
the self-annotation mirror's `pure_ast.PyCSLSyntaxError(SyntaxError)` raised `(msg, (file, line,
col, text))` is admitted: refusing the base GONEs that mirror, measured)
(`PYCSL-R369-CONSTRUCTOR-ARITY`); a file `__init__` in the MRO is checked as before (§7.38); and a
construction of a class deriving from a builtin exception whose signature the check cannot read
(a `__new__` in the file MRO, a class keyword, a decorated or non-`def` `__init__`) is REFUSED
with the same code. Witnesses `5620`-`5623`,
`5650`-`5653` (latents: `super().__init__(msg=x)`, a `__new__` override, a grandchild's keyword,
`raise D(k=1)`); controls `5680` (positional construction, and `F(code=3)` against a plain user
`__init__`) and `5686` (a `SyntaxError` subclass built with a details tuple). Residual: a construction through `cls(..)` / `type(self)(..)` / `functools.partial`
is not checked; a class imported from a user module is checked in its module only by S1.

### 7.53 `getattr`'s default: the whole subclass closure and every store form (routes #396 / #397, gen #37)

§7.43 (GD) answered the default when the receiver's MRO did not bind the name, and its census
saw only `def` / `class` names, `Name` stores and imports in a class body plus `self.k = v`
instance fields. Measured (red team 31, all PROVED at `7859e8fb0`, CPython 5 / 6 / a bound
method): `getattr(r, "k", 0) == 0` for `r: R` while a SUBCLASS `S(R)` stores `self.k = 5`,
binds a class attribute `k`, a dataclass field `k: int = 5`, a property / method `k`, a
grandchild does, `self.__k` is stored in `S` (`_S__k`); and `for self.k in ..`, `(self.k,) = ..`,
`[self.k] = ..`, `with .. as self.k`, `self.k, self.j = ..`, a `for` target in `__post_init__`.
RULE (one place, the `class_binds_r376` map of `_run_pipeline`): a class answers the union of
the bindings of EVERY class in its closed-world subclass closure (it and each file class
deriving from it), each with its file ancestors. A class's bindings: every identifier a
class-scope node carries UNLESS the node kind is known not to bind (an allow-list of
NON-binding forms: a `Name` / `Attribute` load, a constant, a call keyword, a parameter, a class
pattern's attribute names, an import's module; so `except .. as k`, `case k`, `global k`, an
annotation-only member, a type parameter all bind), every attribute STORE / DELETE in any
target position of any of its methods on the method's first parameter (not a `@staticmethod`'s,
nor one rebound or shadowed in the method), and the `_C__x` spelling
of each `__x` it binds. An attribute store on any OTHER receiver, or outside every class (module
functions and module code; the `__main__` driver excluded), binds that name for EVERY class. A
call of `exec` / `eval` joins the dynamic stores of §7.43. Refusal: `PYCSL-R376-GETATTR-CLASS-BINDING`
(message extended). Witnesses `5624`-`5638`, `5654` (latent: `except .. as k` in a subclass body); control `5681`. Residuals: a
subclass defined in ANOTHER module, and a base from a user module (§7.43), are still not read.

### 7.54 A TypedDict value is a `dict`: no attribute access, no read of an optional key (route #398, gen #37)

The model lowers a TypedDict as a record holding EVERY key and `d["k"]` as the field `d.k`.
Measured (red team 31, all PROVED at `7859e8fb0`): `d.a` on `d: TD` under `no_exception`
(CPython AttributeError), `d["b"]` with `b: NotRequired[int]`, under `class TD(TypedDict,
total=False)`, and for a functional `TypedDict("TD", {"b": NotRequired[int]})` (KeyError); the
functional form `TD = TypedDict("TD", {"a": int})` also escaped §7.44 (`TD(a=1).a` PROVED). RULE:
(1) a functional `X = TypedDict(..)` (any import spelling of `typing` / `typing_extensions`) is
a typing construct for §7.44; (2) a key is REQUIRED only when declared in a TypedDict whose
totality is the literal default / `True` and not wrapped in `NotRequired` (or wrapped in
`Required`); inherited keys keep their class's totality; every other key of a file TypedDict
(`NotRequired`, `Annotated`, `total=False`, a non-literal totality or key set, a base that is not
a file TypedDict) is OPTIONAL. In a verified function (contracts included) REFUSED
(`PYCSL-R398-TYPEDDICT-ACCESS`): in a function BODY, `X.k` for a key `k` of a file TypedDict unless
`X` is `self` / `cls` or a variable of a known non-TypedDict type (in a CONTRACT `r.k` is the spec
notation for the key, e.g. corpus `0889` / `0890`, and is refused only for an optional key); `X["k"]`, `X.get("k", ..)`, `X.pop("k")`,
`X.setdefault("k", ..)` and `"k" in X` for an OPTIONAL key unless `X` is a variable of a known
type that is not a TypedDict having `k` optional. No guard is admitted (the record model has no
presence bit for `"k" in d` to establish; at base the guarded `in` / `try` forms were ill-typed in WhyML and `.get` of an optional key
failed, so the refusal costs nothing measured). Witnesses `5639`-`5643`; control `5682`
(required key in a contract and a body). Over-refusal: an optional key read after the function
itself stored it.

### 7.55 Builtins imported from `builtins` (route #399, gen #37)

§7.45 (SB) refused a `*` / `**` argument at a builtin name the file does not bind or import, so
`from builtins import sorted` / `sum` escaped it while the call still lowered to the builtin model
(red team 31, PROVED at `7859e8fb0`: `sorted(xs, **{"reverse": True})` ascending, `sum([1, 2],
**{"start": 10}) == 3`; CPython reversed / 13). The callee is now resolved through the imports
first: a name imported `from builtins` (any alias), an attribute of a name bound by `import
builtins [as b]`, and `__builtins__.X` are builtins for §7.45 (`PYCSL-R379-STARRED-CALL-ARGUMENT`).
Witnesses `5644`, `5645`; control `5683` (`b.sum(.., **..)` through `import builtins as b` was ill-typed in WhyML at base; now refused by SB).

### 7.56 `ast.NodeVisitor` dispatch is not modelled: `visit` / `generic_visit` refused where it would run code (route #400, gen #37)

S1 admits `ast.NodeVisitor` / `ast.NodeTransformer` as bases (the self-annotation mirror's
`Module3_Weaver`, `Module5_IREmitter`, `desugar`, `exec_splice` derive from them), but their
`visit` / `generic_visit` have no model: the call lowered to an abstract operation with no
effect, dropping the dispatch to the class's `visit_*` methods. Measured (red team 31 n32,
PROVED at `7859e8fb0`): a contracted `visit_Constant` doing `self.n += 1`, then `v.visit(ast.
parse("1")); return v.n` proved `\result == 0` (CPython 1). RULE: when a file class derives
(through file classes) from the standard-library `ast.NodeVisitor` / `NodeTransformer` and it
or a file ancestor defines a `visit_*` method, or it is a transformer (which rewrites the tree
in place), a `.visit(..)` / `.generic_visit(..)` call in a verified (non-`\trusted`) function is
REFUSED (`PYCSL-R400-NODEVISITOR-DISPATCH`). Removing the two bases from the table instead was
not taken: the mirror files above use them. Witness `5646`; controls `5684` (a visitor with no
`visit_*` method) and `5685` (the advice followed: `visit_Constant` called directly). Residual: the havoc model (`visit` assigns the union of the `visit_*`
methods' frames) is not built, so a verified caller of a dispatching visitor is refused.

### 7.57 A hashing site calls the class's `__hash__`, and `__eq__` on a collision: both must be verified (route #402, gen #37)

A class that defines `__hash__` counted as hashable, and the call to that `__hash__` at a hashing
site (§7.33's positions: a set element, a dict key, a membership test or subscript of a set /
dict, `hash(..)`, a set / dict built from an iterable) was never emitted, so its exceptions and
preconditions were invisible: `class D` whose `def __hash__` raises ValueError when `self.x == 1`,
then `s = {d}` under `no_exception \all`, PROVED (driver-reproduced at `526d534de`, CPython
ValueError). Likewise a set / dict calls `__eq__` between a value and an element already in it
whose hash is equal: a raising `__eq__` under `{a, b}` PROVED. Option (a), lowering every hashing
site as a call to the class's `__hash__` / `__eq__` with their contracts, was measured against
(b) and not taken: (b) moves no emission (root, pyref, 53 mirrors, `pycsl_lib`) and refuses only
three PASS controls, which are given honest contracts. RULE (b): a `__hash__` / `__eq__` is
VERIFIED when it is ONE top-level undecorated `def` whose IR function is neither `\trusted` nor
`\abstract`, carries `#@ no_exception \all`, has no `requires` (a hashing site discharges none)
and returns `int` / `bool` (a non-`int` hash is a TypeError). Then

* along the C3 MRO, a class whose deciding `__hash__` is a `def __hash__` that is not verified
  counts as unhashable (the §7.33 fixpoint, so a frozen record with a field of such a class, a
  subclass of it, and with §7.50 every file base of it, are unhashable too):
  `PYCSL-R349-UNHASHABLE-RECORD` (message extended). This also tightens §7.50's subclass rule (a
  subclass `__hash__` with a `requires` no longer counts as verified);
* a class is EQ-RISKY when the first class of its MRO that decides `__eq__` binds it otherwise
  than by one verified `def __eq__`, or is a `@dataclass` with `eq` / a NamedTuple / a functional
  namedtuple (field-wise equality) with a field whose annotation is not eq-safe (`int`, `str`,
  `float`, `bool`, `bytes`, `complex`, `None`, `Literal` / `type`, a non-eq-risky class of the
  file, or Optional / Union / `|` / Tuple / List / Set / FrozenSet / Dict / Annotated / Final /
  ClassVar of those); an unknown linearisation is eq-risky, and a class with an eq-risky file
  subclass is eq-risky (closed world). At a hashing site that may compare -- every site but
  `hash(x)`, a one-element set display and a one-key dict display -- a value of an eq-risky class
  (or of an unknown class, when any class of the file is eq-risky) is REFUSED
  (`PYCSL-R402-UNVERIFIED-EQ`).

Census: root corpus 0 MOVED / 0 APPEARED and 3 GONE before the corpus edit (`4694`, `4940`,
`5043`: their `__hash__` bodies are total and now carry `#@ no_exception \all`; re-proved at base
and candidate), pyref 0/0/0, mirrors 53/53 0/0/0, `pycsl_lib` screen identical. Witnesses
`5780`-`5789` (own / inherited / `requires`-guarded / tuple-element / frozen-field raising
`__hash__`; raising `__eq__` on a collision in `{a, b}`, a tuple pair, a starred display, a
dataclass field, a file subclass); controls `5800` (verified methods, an inheriting subclass, a
frozen `int` / `str` record and a plain identity class in multi-element displays) and `5801` (an
unverified `__eq__` at sites that never compare). Residuals: a cyclic value compared by a
field-wise `__eq__` (RecursionError) is not modelled; `__eq__` reached through a stdlib container
element (a `frozenset` of user objects inside a set) is not traced; an unverified `__eq__` at a
`hash(x)` / one-element site is admitted because CPython never calls it there.
### 7.58 A class invariant is admitted only when its constructor goal is stated; otherwise the class is refused (route #226 polarity flip, run #3)

§7.34 / §7.37 / §7.40 state the constructor goal `_check_class_inv_<c>` for the shapes they model
and, for every other shape, emitted NO goal while every method still ASSUMED the invariant (a
bool field, a computed int store `self.n = three()`, an element / quantifier / string /
predicate term, a `default_factory` field, a `ClassVar` read through `self`: red team 29
a04..a46 and route #384's element-term carrier, each PROVED a false postcondition). The
polarity is now flipped: a `#@ class invariant` of a class defined in the verified file is
admitted only when its goal is emitted; otherwise the file is REFUSED
(`PYCSL-R226-INVARIANT-GOAL-NOT-STATED`). The goal is stated (goal stage 2d) from `__init__`'s
END state when every field the lowered invariant names is, when `__init__` returns:
- an int / bool literal, or an int (bool) `__init__` parameter never re-bound in `__init__`;
- an int expression over int parameters and literals with `+`, `-`, `*`, unary `-` and
  two-argument `max` / `min` (`self.t = year * 365 + day`, `self.line = max(line, 0)`; `//` / `%`
  are not stated, Python floors);
- a list of literal length (§7.40) — and, when the invariant reads ELEMENTS, a fresh
  `[c] * K` / `bytearray(K)` (c an int literal) that `__init__` then only reads (`len(..)`,
  `x[i]`), stated `forall k. 0 <= k < K -> f[k] = c`; or a list parameter (§7.37), whose
  elements are constrained only by `__init__`'s `#@ requires`.
Each binding is the LAST top-level store `self.f = <value>`; any other store or mutation of
`self.f` (augmented, tuple, under control flow, in a nested scope) leaves no goal, and so does a
whole `__init__` that lets `self` escape (a bare `self` other than `type(self)`), calls `super()`
other than as its leading statement, stores an attribute of another object, returns / yields, or
makes any call other than `len` / `type` / `int` / `bool` / `abs` / `min` / `max` after a field is
stored. `__init__`'s `#@ requires` (a class without `__init__` uses its first file base's) are
premises, conjunct by conjunct over the bound parameters. A class whose `__init__` is
`#@ \trusted` is admitted without a goal: its establishment is the declared, counted TCB (the
mirror parsers `_ContractParser`, `pure_ast._Parser`, corpus `0900`). A class imported from
another module is stated, or refused, when that module is run. The mirror `errors.py`'s invariant
`self.line >= 0` is NOT established by `PyCSLError.__init__` (`line=-1` is accepted) and no raise
site constructs the error record in the model, so neither a goal nor a `#@ requires` can be
checked: its `__init__` is now `#@ \trusted` (`cost-scale:exception-payload-model`; one marker,
the measured cost of this rule on the mirrors); corpus `0661` / `0662` gained `#@ requires \length(initial) == 18`
(`\valid(initial, 18)` only gives `>= 18`, their invariant says `== 18`). A `#@ requires` used as a
premise is not a call-site obligation (route #15 residue), but a construction in verified code
still raises the record's type-invariant VC (witness `5885`). OVER-REFUSAL: none measured (0 root /
python-reference / mirror / `pycsl_lib` files refused). NOT COVERED (refused, not stated): a
`@dataclass` (no `__init__` in the source) whose invariant needs stage 2d, `str` / record /
`Optional` fields read by the invariant, a field computed from another field or by a call;
an unverified caller that keeps an alias of a list it passed (§7.40). Witnesses `5870`-`5880`,
`5883`-`5885`; controls `5890`-`5896`.

### 7.59 A bespoke lowering may replace a function only when it establishes the declared contract (route #420)

Module 6 recognizes many function SHAPES (folds and walkers over the `pyval` / `term`
models, the crosscheck readers, the emitter's own handlers) and replaces the function's body
with a hand-built WhyML group. Almost every such group carries a fixed `requires { true }` /
`ensures { true }`, so the function's declared `#@ requires` / `#@ ensures`, a conditioned
`#@ raises E when C` and a `#@ no_exception` claim were silently DROPPED: measured at
`b8bd00a9d`, 15 probes over the user-reachable shape families (`#@ ensures False`, or
`#@ no_exception IndexError` over a body that raises it) printed `Verification SUCCESS`.
RULE: a recognized shape is lowered by its bespoke group only when every `requires` and
`ensures` clause is the literal `True` (or the family threads that clause onto its group as a
checked obligation: the set/stmt folds, `_substitute`-style maps and the emitter's
comprehension/compare handlers), every `raises` is unconditioned, and no `no_exception` is
declared. `\trusted` / `\abstract` functions are exempt (their contract is assumed). Otherwise
the function is lowered by the generic path, which checks the contract or refuses the file.
Nothing new is refused by name: a declining shape that the generic lowering cannot model is
refused or fails to type-check there. Witnesses `5920`-`5934` (`5926`: a dropped callee
`requires` left a call site unchecked); controls are the
shape files they derive from (`0883`, `0942`, `0943`, `0945`, `0948`, `0950`-`0964`), still
proved and byte-identical.
### 7.60 A verified `__eq__` is verified for ANY `other` (route #403, gen #37)

§7.57 counted a `def __eq__` carrying `#@ no_exception \all` as verified whatever its `other`
parameter's annotation, and a body is verified under that annotation: `def __eq__(self, other:
"A") -> bool: return self.x == other.x` was proved for `other` of class `A` only, while a set
or dict compares a value with ANY element of equal hash. Measured (red team 32, PROVED at
`085ee3dcc`, CPython AttributeError): `{a, 1}`, `{a, b}` with `b` of another file class whose
verified `__hash__` collides, `{a, False}`, `{(a, 1), (0, 1)}` (a tuple compares its
components). RULE: a `def __eq__` counts as verified only with the signature exactly `(self,
o: object)` (two positional parameters, the second annotated by the builtin `object`; no
other parameter, no `*` / `**`), so its body is proved for any `o`; any other `__eq__`
leaves the class EQ-RISKY and every site that may compare is refused
(`PYCSL-R402-UNVERIFIED-EQ`, message extended). Witnesses `5970`-`5973`; control `6020`.
Over-refusal: a body that reads an attribute of `o` is not verifiable today, even under
`isinstance(o, A)` (the parameter is erased; `PyCSL-R358` fails the load), so a useful
field-wise `__eq__` in a comparing hashing position is refused until `isinstance` narrowing
of an `object` parameter is modelled.

### 7.61 `type` is a modelled base only for a metaclass that defines nothing (route #404, gen #37)

S1 (§7.42) admitted `type` as a base, so a FILE metaclass was modelled as nothing: a class is a
value of its metaclass, and the metaclass's `__eq__` / `__hash__` / `__bool__` / `__init__` and
class-body names were ignored. Measured (red team 32, PROVED at `085ee3dcc`, CPython TypeError /
ValueError): `class M(type)` with `__eq__` only, then `{K}` for `class K(metaclass=M)`; a
raising `M.__hash__`; `{C.K}` with a nested `K`; `{type(k)}`; `{(C, 1)}`; `if C:` with a raising
`M.__bool__`; `{C.K}` where only `M` binds `K = [1]`, or `M.__init__` stores `cls.K = [1]`.
RULE (S1, `PYCSL-S1-UNMODELLED-BASE`): (1) a base `type` is admitted only when the class body
holds nothing but a docstring / `pass` / `...` and no code stores an attribute on the class
(`M.k = ..`, `setattr(M, ..)`); (2) a `metaclass=` keyword must name `type`, `abc.ABCMeta`,
`enum.EnumMeta` / `EnumType` or a class of the file (checked by (1) through its own bases) --
a function or any other value is refused (NEW latent: `class K(metaclass=mk)` with `mk`
returning `[1]` hashed `{K}`, CPython TypeError; ill-typed in WhyML at base). Witnesses `5974`-`5981`,
`6015`, `6018`; control `6021` (a metaclass with only a docstring, `metaclass=abc.ABCMeta`) and the
existing `5171`; NEW latent `6018` (`M2(M)` with `M(type)` empty and `M2` binding `__eq__`: a class deriving from `type` through file classes must define nothing too), and the metaclass of a checked class is checked wherever it is named (the `__main__` driver included). Route #380's `__call__` refusal is now reached only through an admitted stdlib metaclass (`6017`, `metaclass=enum.EnumMeta`; its old witness `5156` refuses at S1). Census (both corpora, 53 mirrors, `pycsl_lib`; the whole landing): root 2441 -> 2449 (+8 controls), 0 MOVED / 0 GONE / 0 APPEARED; pyref 2186 -> 2186 0 / 0 / 0; mirrors 53 / 53 0 / 0 / 0; `pycsl_lib` --no-proof screen identical (104 files); refusal rows moved: `5156` only.

### 7.62 A class created by a call is outside the closed world: refused (route #405, gen #37)

Routes #277 / #395 / #396 read a value of static class B as an instance of B or of any file
class deriving from B, the subclasses being the file's `class` statements. A class created by a
CALL escaped that closure. Measured (red team 32, PROVED at `085ee3dcc`): `D = type("D", (B,),
{"__hash__": None})` in the `__main__` driver then `{b}` for `b: B` (CPython TypeError),
`dataclasses.make_dataclass("D", [], bases=(B,))`, a `type(..)` subclass whose `__eq__`
raises, `getattr(r, "k", 0) == 0` with `type("S", (R,), {"k": 5})` (CPython 5), and an
override `{"g": lambda s: 2}` of a contracted method (`\result == 1`, CPython 2). RULE: anywhere
in the file, the `__main__` driver included, a call of the builtin `type` with two or more
arguments (or `type.__new__(..)`), `types.new_class(..)` and `dataclasses.make_dataclass(..,
bases=..)` is REFUSED unless its bases argument is the literal `()`
(`PYCSL-R405-DYNAMIC-SUBCLASS`). Witnesses `5982`-`5986`; control `6022` (`type(x)`, `type("T",
(), {})`, `make_dataclass` without bases). Census (both corpora, 53 mirrors, `pycsl_lib`; the whole landing): root 2441 -> 2449 (+8 controls), 0 MOVED / 0 GONE / 0 APPEARED; pyref 2186 -> 2186 0 / 0 / 0; mirrors 53 / 53 0 / 0 / 0; `pycsl_lib` --no-proof screen identical (104 files).

### 7.63 A call the model does not read may store attributes on its arguments (route #406, gen #37)

GD (§7.43 / §7.53) and the field / class-attribute sources of a hashed value (§7.49 (2)) saw
attribute stores written as stores, `setattr` / `delattr` / `vars` / `__dict__`, and `exec` /
`eval`; a standard-library CALL that sets attributes on an argument was invisible. Measured
(red team 32, PROVED at `085ee3dcc`, CPython 5 / TypeError): `argparse.Namespace.__init__(self,
k=5)` in `__init__` or in a module function, `functools.update_wrapper(self, S(), ..)`,
`p.parse_args([], namespace=self)`, `optparse.Values.__init__(self, {..})`,
`mock.patch.object(self, "k", 5, create=True).start()`, `object.__getattribute__(self,
"__dict__")["k"] = 5`, then `getattr(r, "k", 0) == 0`; and the same calls rebinding a field
`x = [1]` (`{r.x}`) or shadowing a class attribute (`{c.K}`). RULE (allow-list of callees
whose effect on an argument is known): the file is DYNAMIC when, outside the `__main__` driver
(§7.43's convention: the driver is not verified code; counting it refuses control `5464`, whose
driver calls `setattr`, measured), a call passes an object-valued argument (a name, attribute,
subscript, starred or walrus value) to a STANDARD-LIBRARY callee (resolved through the file's
imports) of a module outside a fixed list of modules whose functions never store attributes on
an argument (`math`, `json`, `re`, `os`, `sys`, `itertools`, `collections`, `copy`, `ast`,
`functools`, `logging`, `subprocess`, ...; minus `ast.copy_location` / `fix_missing_locations`
/ `increment_lineno`, `functools.update_wrapper` / `wraps` / `partial`, `types.SimpleNamespace`,
`importlib.import_module`, ...; `argparse`, `optparse`, `unittest` are not in it); to a method
of an object such a call returned (`argparse.ArgumentParser().parse_args(.., namespace=self)`,
directly or through a name bound to it) other than a container / `str` method; to a dunder of
a builtin class other than a read-only one (`object.__getattribute__`); or when a string
constant names `__dict__` / `__setattr__` / `__delattr__` / `__class__`. Then every class
answers UNKNOWN for GD (`PYCSL-R376-GETATTR-CLASS-BINDING`) and a field or class attribute read
is UNKNOWN as a hashed value (`PYCSL-R349-UNHASHABLE-RECORD`). Witnesses `5987`-`5995`; control
`6023` (`math.floor(self.x)` and a file function called on `self`). Residuals: a callee of a
USER module and a local callable are read only by their own module's census (§7.43's residual);
`setattr` / `vars` / `__dict__` keep their GD-only effect -- `setattr(self, "x", [1])` then
`{r.x}` still PROVES (counting them for hashed values refuses the `frontend/pure_ast.py`
mirror, measured); the `__main__` driver's own calls are not counted. Census (both corpora, 53 mirrors, `pycsl_lib`; the whole landing): root 2441 -> 2449 (+8 controls), 0 MOVED / 0 GONE / 0 APPEARED; pyref 2186 -> 2186 0 / 0 / 0; mirrors 53 / 53 0 / 0 / 0; `pycsl_lib` --no-proof screen identical (104 files); with the driver counted, control `5464` GONE; with every unread callee counted, 6 mirrors GONE (measured, not landed).

### 7.64 The hashed value's sources, tightened: container expressions, driver stores, stdlib objects, copies (routes #407-#410, gen #37)

Four §7.49 sources admitted a value they do not model (red team 32, all PROVED at `085ee3dcc`,
CPython TypeError). (1) ROUTE #407: a module / class-body name bound to an expression over a
container -- `K = A * 2`, `A + B`, `A or 1`, `A | {..}`, `A - {2}`, `A[:]`, `A if A else (1,)`,
`[1] * 2`, `.. if False else B + [3]`, the same in a class body -- was UNDERIVABLE (admitted).
Now arithmetic / a unary operator with a container operand is a container of its kind with
UNKNOWN elements; a BoolOp / IfExp is the union of its operands' classes; a slice of a list /
tuple is that container, an index of a list / tuple / dict display its elements' classes
(when read-only, §7.49 (1)); an attribute, method call or unary operation over a container is
UNKNOWN; a class-body name read in the same body is that binding. (2) ROUTE #408: a subscript
store `XS[0] = [5]` in the `__main__` driver was recorded as a second BINDING of `XS`, so `XS`
had no initializer (underivable): a global's bindings are now its store-context names only, and
the store makes it not read-only (its elements UNKNOWN). (3) ROUTE #409: a standard-library
object was hashable when `hash(..)` of the live object succeeded and UNDERIVABLE otherwise:
`{os.environ}`, `from os import environ`, `E = os.environ`, `{sys.argv}`,
`{logging.root.handlers}`, `{os.environ.copy()}`. Now an object whose class has `__hash__ =
None`, is a mutable container (`MutableMapping` / `MutableSequence` / `MutableSet`, `list` /
`dict` / `set` / `bytearray`), or whose hash raises is UNKNOWN; a name reached through an
attribute of a non-module, non-class object (`logging.root.handlers`) is UNKNOWN; the result of
a method called on a standard-library object is UNKNOWN; a module global bound to a
standard-library name has its class. (4) ROUTE #410: `copy.copy(x)` / `copy.deepcopy(x)` /
`dataclasses.replace(x, ..)` / `copy.replace(x)` has x's class only when no class a value of
x's static class may be (its MRO and every file subclass's) binds `__copy__` / `__deepcopy__` /
`__replace__` / `__reduce__` / `__reduce_ex__` (and no such name is stored dynamically);
otherwise UNKNOWN. Every UNKNOWN is refused in a hashing position
(`PYCSL-R349-UNHASHABLE-RECORD`). Witnesses `5996`-`6014` and the NEW latent
`6016` (`K = A.copy()`, PROVED at base); controls `6024`-`6027`. Census (both corpora, 53 mirrors, `pycsl_lib`; the whole landing): root 2441 -> 2449 (+8 controls), 0 MOVED / 0 GONE / 0 APPEARED; pyref 2186 -> 2186 0 / 0 / 0; mirrors 53 / 53 0 / 0 / 0; `pycsl_lib` --no-proof screen identical (104 files).
### 7.70 True division by zero is an obligation for float and int operands (route #412, gen #37)

`x / y` over floats lowered to the uninterpreted `float_div_op` with no obligation, and int
`a / b` (true division, `float_truediv_op`) was the one int division path not wrapped by the
`("binop", "/")` trigger row: `x / 0.0`, `1.0 / (x - x)` and `a / b` without `b != 0` PROVED
`no_exception \all` (CPython ZeroDivisionError). RULE: in a body under a `no_exception` covering
ZeroDivisionError, the divisor of a float `/` owes `y <> 0.0` and of an int `/` owes
`no_div_zero (b)`, exactly as `//` and `%` do. The obligation wraps the right operand, so the
term keeps its head. Witnesses `6056`-`6059`; control `6060`.

### 7.71 Int true division owes `|a / b| <= DBL_MAX` under `no_exception \all` (route #413, gen #37)

CPython raises OverflowError ("integer division result too large for a float") when an int
quotient exceeds the largest double: `(10**400) / 1`. It PROVED under `no_exception \all`
with `requires b != 0`. FLOAT-FINITE (route #250) is a claim about float VALUES (finite,
non-NaN), not about a raised exception, so it does not cover this. RULE: under `\all`
(OverflowError is not a Phase 1 exception; §7.19's rule for AssertionError, route #332), int `a / b`
owes `-DBL_MAX * b <= a <= DBL_MAX * b \/ DBL_MAX * b <= a <= -DBL_MAX * b` with DBL_MAX =
`(2**53 - 1) * 2**971` written as a literal, i.e. `|a| <= DBL_MAX * |b|`, after which
CPython's correctly rounded quotient never overflows. Linear in `a` and `b`. Witness `6061`;
control `6062`.

### 7.72 Py_ssize_t limits are obligations under `no_exception \all` (route #414, gen #37)

A size that does not fit a Py_ssize_t (sys.maxsize = 2**63 - 1 on the 64-bit platform) raises
OverflowError: `len(range(10**20))`, `"a" * 10**20`, `[0] * 10**20`, `1 << 2**64`. These were
not obligations, while the 4300-digit `str(int)` limit already is (route #281). RULE, under `\all`
(route #332's rule, as §7.71): `len(range(stop))` owes `stop <= 2**63 - 1`, `len(range(start,
stop))` owes `stop - start <= 2**63 - 1`, `len(range(start, stop, step))` owes `|stop - start| <=
2**63 - 1`; `s * n` (str) owes `-2**63 <= n <= 2**63 - 1` and `n <= 0 \/ len(s) * n <= 2**63 - 1`
("repeated string is too long"); `[x] * n` owes `n <= 2**63 - 1` (`Array.make` already owes
`n >= 0`); `x << n` owes `x = 0 \/ n <= 2**63 - 1`. Each obligation wraps the size operand, so
the term keeps its head. NOT MODELLED: MemoryError below these bounds (`"a" * 2**40`, `1 << 2**40`
raise MemoryError on a real machine). Like RecursionError (route #269, §2.1.13) it is a resource
limit outside the Phase 1 set; no memory-cap assumption is declared (a decision recorded in the
route file). Witnesses `6063`-`6067`; control `6068`.

### 7.73 `%` string formatting is admitted under `no_exception` only when positively checked (route #415, gen #37)

`s % x` with a str left operand lowers to the opaque `str_mod_op`, and routes #281 / #284 only
discharge its ValueError rows, so `"%d" % s` with `s: str` (TypeError) and `"%(k)s" % {"j": a}`
(KeyError) PROVED `no_exception \all`. RULE (allow-list): under `\all`, and under a named set
holding KeyError when the format has a mapping key or is not a literal, a `%` is REFUSED
(`PYCSL-R415-UNCHECKED-PERCENT-FORMAT`) unless the format is a string LITERAL whose conversions
are only `%s` / `%d` / `%i` / `%r` (and `%%`), with optional flags and a literal width / precision
(their size stays route #284's obligation) but no mapping key and no `*`, the right
side is a tuple display with exactly one operand per directive (or, for one directive, a single
operand), and every `%d` / `%i` operand is an int / bool and every `%s` / `%r` operand an int / bool /
str / float by the static readings route #281 uses (a literal, a typed parameter / local, `len` /
`int` / `abs` / `ord` / `hash` / `sum`, a str or float expression). Witnesses `6069`-`6070`;
control `6072`.

### 7.74 A dict view is the dict for UB-7.1 (route #416, gen #37)

UB-7.1 (§2.2.3, `ir_scanner.find_iteration_mutations`) refuses a `for` loop whose body mutates the
iterated collection, but it matched only a bare name: `for k in d.keys(): d[k + 100] = 0` (and
`.values()` / `.items()`) PROVED `no_exception \all` while CPython raises RuntimeError
("dictionary changed size during iteration"). RULE: the iterable `<recv>.keys()` /
`<recv>.values()` / `<recv>.items()` counts as iterating `<recv>`; the same mutation rules and the
same `#@ allow_iteration_mutation` opt-out apply (inline in `_run_pipeline`, whose mirror twin is
`\trusted`; `ir_scanner.find_iteration_mutations` and its recognised mirror model are unchanged).
Witnesses `6073`-`6075`; control `6076`.

### 7.80 Sequence repetition is modelled only for `[x] * n` (route #417, run #3)

The `[default] * size` lowering kept the FIRST element of the list display and dropped the rest:
`[1, 2] * 3` became `Array.make 3 1` (length 3; CPython 6) and `[] * 3` `Array.make 3 0` (CPython
length 0), so `len(xs) == 3` and `xs[1] == 1` PROVED. A tuple display operand fell to Why3 INT
multiplication: `(0,) * 3` became `(0) * 3`, a falsy `0`, so `if t: return 1` was decided False
(CPython `(0, 0, 0)` is truthy), and `(1,) * n` was returned as `n`. RULE (polarity: only the
modelled shape is admitted): `*` with a list display on the left is admitted only when the display
has exactly one element; any other list display on the left, and a tuple display on either side,
is REFUSED (`PYCSL-R417-SEQUENCE-REPEAT`), in bodies and contracts. Likewise a STARRED element of a
list display lowered to its operand as ONE element (`len([*range(n)]) == 1` PROVED, CPython n): in a
body such a display is now an UNCONSTRAINED list, fresh per evaluation (list-ness kept, length and
contents unknown; route #299's answer for the hval carrier), and an erased operand keeps route #375's
failing assertion. A contract cannot spell one (the contract grammar rejects `*x`, measured on
`ensures` / `assert` / `loop_invariant`). Measured, not changed: `3 * [1, 2]`, `ys * 3` (a list
variable), `[1] * 2 * 3` and `n * [1]` are refused at base and candidate alike (no false proof);
`t * 2` of a typed tuple variable fails its proof at both. Witnesses `6100`-`6105`, `6114`; control
`6120`.

### 7.81 A contract string literal has Python's escape semantics (route #417, run #3)

The contract lexer kept a string token's RAW text, so `"a\nb"` in a `#@` clause reached the model
as backslash + `n` (four characters) while the same literal in the body is three: `#@ ensures
\result == "a\nb"` PROVED of `return "a\\nb"` (CPython False). RULE: a contract string literal is
decoded exactly as Python decodes the double-quoted literal (`ast.literal_eval` of the token):
`\n`, `\t`, `\\`, `\"`, `\xNN`, `\uNNNN`, `\N{..}`; an undecodable escape is a contract syntax
error. Witnesses `6106`-`6107`; control `6121`.

### 7.82 `list(range(..))`, `sorted(range(..))` and `float(int)` owe their OverflowError bounds under `no_exception \all` (route #417, run #3)

Route #414's Py_ssize_t rule (§7.72) covered `len(range(..))` but not the other range
materializations that take its length: `list(range(10**20))` and `sorted(range(10**20))` raise
OverflowError ("Python int too large to convert to C ssize_t") and PROVED `no_exception \all`
(`for x in sorted(range(n))` erased the iterable to `(any int)` altogether). `float(n)` of an int
raises OverflowError ("int too large to convert to float") for `|n|` past the largest double and
had no obligation. RULE, under `\all` only (route #332's rule, as §7.71 / §7.72): `list(range(..))`
and `sorted(range(..))` (one positional argument, no keyword; `sorted(range(n), reverse=True)` is
refused at base and candidate alike) owe §7.72's bound on the range operands (`stop <= 2**63 - 1`, `stop - start
<= 2**63 - 1`, `|stop - start| <= 2**63 - 1`); when a `for` iterable's coercion erases the term,
the obligation is asserted where Python evaluates the iterable, before the loop. `float(x)` owes
`-DBL_MAX <= x <= DBL_MAX` (DBL_MAX = `(2**53 - 1) * 2**971`, §7.71's literal) when `x` is read as an
int (an int literal, an `int`-typed name, `len` / `int` / `abs` / `ord` / `hash` / `sum`); it owes
nothing for a str / float / bool argument; any other argument is REFUSED
(`PYCSL-R417-UNCHECKED-FLOAT-CONVERSION`). NOT MODELLED: `tuple(range(10**20))` (and a
comprehension over a huge range) raises MemoryError, a resource limit (§7.72). Each obligation
carries a tag stable per call node (a hash of the call's IR). After emission the driver requires
every registered tag to occur in the module at least once AND at least as often as its call occurs
in the IR: textually identical calls share a tag, so a kept twin must not hide an erased occurrence
(measured: a bounded `for x in sorted(range(n))` beside an unbounded `set(sorted(range(n)))`, and a
guarded `float(n)` beside `isinstance(float(n), float)`, PROVED with a presence-only check). Fewer
occurrences is an obligation a later coercion ERASED with the term (measured: `set(sorted(range(n)))`
-> `set_1 (any int)`), REFUSED (`PYCSL-R417-ERASED-OBLIGATION`). Witnesses `6108`-`6110`, `6113`,
`6115`-`6117`; controls `6118`, `6122`-`6123`.

### 7.83 Constant-name dynamic stores and standard-library function results in hashing positions (route #417, run #3)

Two residuals of §7.63 / §7.64. (1) `setattr(self, "x", [1])` stores a value in field `x` that
the field sources of a hashed value never saw: `{r.x}` PROVED `no_exception \all` (CPython
TypeError). RULE: an attribute name written by a CONSTANT-name dynamic store anywhere in the file
(`setattr(o, "x", v)`, `o.__setattr__("x", v)`, `object.__setattr__(o, "x", v)`, `o.__dict__["x"] =
v`, `vars(o)["x"] = v`) is UNKNOWN when a field of that name is read in a hashing position
(`PYCSL-R349-UNHASHABLE-RECORD`). A non-constant name keeps §7.43's GD-only effect: OPEN RESIDUAL,
`setattr(self, nm, [1])` then `{r.x}` still PROVES `no_exception \all` (CPython TypeError; probe
`q09_setattr_dyn`, run #3 r417b); folding it in GONEs the `frontend/pure_ast.py` mirror, whose
`setattr(self, name, value)` is route #406's measured cost. (2) The result of
a standard-library FUNCTION was underivable and admitted: `{shlex.split("a b")}` PROVED (CPython
TypeError, a list). RULE: a call whose callee resolves to a standard-library function (not a class,
not a builtin name) has a class only when the function is on a fixed list of functions that always
return a hashable `str` / `int` / `float` / `bool` (`os.getcwd`, `os.path.join` / `basename` /
`dirname` / `abspath` / ..., `shlex.quote` / `join`, `re.escape`, `json.dumps`, `math.sqrt` / ...,
`time.time`, ...); any other is UNKNOWN when hashed. Witnesses `6111`-`6112`; controls `6124`-`6125`.


### 7.110 A module-global / class-body name is UNKNOWN unless every binding is derived (route #421, run #3)

§7.64's global / class-body derivation answered "underivable" (no class: ADMITTED when hashed) for
every initializer form it did not list, while the same initializer bound to a local is refused:
`K = json.loads("[1]")`, `K = collections.deque()`, `K = bytearray(2)`, `K = A = [1]`, `K, A = [1], 2`,
`(K := [1])`, `K = 1; del K; K = [1]`, a binding under `if` / `try`, a class-body `K = bytearray(1)`
read as `C.K` or `self.K` -- then `{K}` PROVED `no_exception \all` (red team 33, 55 probes; CPython
TypeError). POLARITY: a module-global or class-body name has a class only when EVERY one of its
bindings is a single-target assignment (or a `def` / `class`) whose initializer a row of the
derivation recognises -- a literal, an f-string, a tuple / list / set / dict display, arithmetic over
operands with a class (unary minus included), a file-class construction, a builtin
`frozenset` / `str` / `int` / `float` / `bool` / `bytes` / `complex` / `range` / `list` / `sorted` /
`set` / `dict` call, an ANNOTATED module function's `-> T` (§7.46), a standard-library function of
§7.83's list (any other standard-library function result is UNKNOWN), another derived global, a
class / function, a standard-library name by its real object (§7.64 (3)); several such bindings are
the UNION of their classes. Any other form -- and a name declared `global` in a function, or both
imported and assigned -- is UNKNOWN (`#UNK`), refused in a hashing position
(`PYCSL-R349-UNHASHABLE-RECORD`), as is an element of a container whose elements no row derives.
A name only IMPORTED keeps §7.64 (3) (a user-module import stays the documented §7.46 residual).
Witnesses `6250`-`6281`; control `6330`.

### 7.111 Three local value-class rows (route #422, run #3)

The local derivation (§7.46) left three forms with a known class underivable: `k = str.split("a b")`,
`k = E.A.value` (an Enum member initialised to `[1]`) and the result of a nested `def g() -> list`,
each then hashed under `no_exception \all` PROVED (CPython TypeError). RULES: an unbound
`str.<m>(x, ..)` / `bytes.<m>(x, ..)` is read as the method row of its first argument; the `str` /
`bytes` method rows are now an allow-list (a method not listed, e.g. `str.maketrans`, which returns a
dict, is UNKNOWN; a name `str` / `bytes` does not have raises AttributeError and contributes no class); `<member>.value` / `._value_` of a file `Enum` is the union of the classes of its
members' initializers when every class of its MRO is a file or standard-library enum class (no
data-type mixin) and no file class there binds `__new__` / `__init__` / `value` / `_value_` /
`_generate_next_value_` (else UNKNOWN); a call of a nested `def g(..) -> T` (undecorated, a statement
of the function's own scope and the only binding of `g` in it) answers `T`. Witnesses `6282`-`6284`;
control `6331`.

### 7.112 Every class-creating value is confined (route #423, run #3)

§7.62 recognised the spellings `type(name, bases, ns)` / `type.__new__(..)`, so every other callee
that creates a class escaped the closed world: `T = type; T("D", (B,), ns)`, `type.__call__(type,
..)`, `tn = type.__new__; tn(type, ..)`, `abc.ABCMeta(..)` (also `from abc import ABCMeta`, and
`abc.ABCMeta.__new__(abc.ABCMeta, ..)`), a file metaclass `M(type)` called as `M(..)` / `M.__new__(M,
..)` / `MM = M; MM(..)` -- then `{b}` for `b: B` PROVED (CPython TypeError), and a getattr default
PROVED wrong. RULE (anywhere in the file, the driver included; type annotations aside): a
CLASS-CREATING value -- `type`, a standard-library class deriving from `type` (`abc.ABCMeta`,
`enum.EnumMeta`, ...) resolved through the file's imports, a file class deriving from one -- may be
referenced only as a `class` base or `metaclass=`, an argument of `isinstance` / `issubclass` (or of
a tuple there), a comparison operand, the receiver of `__name__` / `__qualname__` / `__module__` / `__instancecheck__` /
`__subclasscheck__` / `__mro__` / `__bases__` / `__doc__`, the callee of a call whose second argument is the literal `()`, or (for `type` itself)
the callee of the one-argument `type(x)`. Any other reference is REFUSED
(`PYCSL-R405-DYNAMIC-SUBCLASS`); so is a call with two or more arguments (or a keyword) of a standard-library
class whose METACLASS overrides `__call__` (`enum.Enum("D", "A", type=B)`, the functional API, creates a
subclass of `B`). Witnesses `6285`-`6296`; control `6332`.

### 7.113 `K[i]` of a class with `__class_getitem__` is refused (route #424, run #3)

A subscript of a class value calls `__class_getitem__`: `{K[1]}` (and `G = K[1]; {G}`) with
`def __class_getitem__(cls, item) -> list` PROVED (CPython TypeError). RULE: a file class whose file
MRO binds `__class_getitem__` may not be subscripted or aliased (`A = K`) outside type annotations
(`PYCSL-R424-CLASS-GETITEM`); the subscript of any other class / function value is UNKNOWN in the
value-class derivation (refused when hashed). Witnesses `6297`-`6298`; control `6333`.

### 7.114 An explicit `__init__` call is refused outside constructor chaining (route #425, run #3)

`a.__init__(-4)` lowered to a frame-less opaque call -- no `requires`, no `writes`, the class
invariant kept -- so `a.where() >= 0` PROVED under `invariant self.n >= 0` (CPython -4); likewise
`a.__class__.__init__(a, -4)`, `a.__init__(n=-4)`. RULE (outside the `__main__` driver): the
attribute `__init__` may be read only as the callee of `super().__init__(..)` / `super(C,
self).__init__(..)` or `Base.__init__(self, ..)` (with the enclosing method's own first parameter)
in the body of an `__init__`; `getattr(.., "__init__")` (also `methodcaller` / `attrgetter`) is
refused too (`PYCSL-R425-EXPLICIT-INIT`). Witnesses `6299`-`6302`; control `6334`.

### 7.115 f-string format specs owe their value-dependent bounds (route #426, run #3)

§7.71 checks a literal spec's VALUE-INDEPENDENT validity (it is tried on a sample of the operand's
type). For an operand SHOWN to be an int, three presentation families depend on the value: decimal
(none / `d` / `n`: §7.36's 4300 digits), a FLOAT type (`e E f F g G %`: the int is converted to a
float, OverflowError past DBL_MAX -- `f"{n:f}"` with `n = 10**400` PROVED `no_exception \all`) and
`c` (`chr`: ValueError outside `range(0x110000)`, OverflowError past a C long -- `f"{n:c}"` with
`n = -1` PROVED). RULE: a float presentation type owes `-DBL_MAX <= n <= DBL_MAX` (§7.82's bound for
`float(n)`) under `no_exception \all`; `c` owes `0 <= n < 0x110000` under `\all`, else the `chr`
ValueError row when ValueError is covered. `b o x X` owe nothing. Each obligation is registered with
§7.82's erased-obligation check (`PYCSL-R417-ERASED-OBLIGATION`). An operand not shown to be an int
keeps §7.71's sample test (these specs are invalid on a str: the `format_spec` row). Witnesses
`6303`-`6309`; control `6335`.

### 7.116 UB-7.1 sees through generator expressions (route #427, run #3)

`for k in (x for x in d): d[k + 100] = 0` PROVED `no_exception \all` (CPython RuntimeError); also
over `d.keys()`, with a filter, nested `(x for x in (y for y in d))`, and a set with `add` /
`discard`. RULE: the collections a `for` loop iterates are read through every generator of a
generator expression (recursively) and through a view (`.keys()` / `.values()` / `.items()`, §7.74);
a loop body mutating any of them is UB-7.1. A list / set / dict comprehension or `list(..)` is a
snapshot (evaluated before the loop). Witnesses `6310`-`6315`; control `6336`.

### 7.117 §7.63's safe modules vouch for their FUNCTIONS only (route #428, run #3)

`logging.Logger.__init__(self, "n")`, `collections.UserList.__init__(self, [1])`,
`json.JSONEncoder.__init__(self)`, `string.Template.__init__(self, ..)` ... store attributes on
`self`, yet the callee's module was on §7.63's list: `getattr(r, "level", 7) == 7` and `{r.data}`
PROVED (CPython 0 / TypeError). RULE: a standard-library callee taking an object-valued argument is
known to set no attribute on it only when it RESOLVES (by import) to a callable reached through
modules only -- never through a class (a method, `Cls.__init__`) -- and is not a class, unless the
class is one of a fixed list of constructors that keep no reference to and set nothing on an argument
(`collections.OrderedDict` / `Counter` / `deque` / `defaultdict` / `ChainMap`, `decimal.Decimal`,
`fractions.Fraction`, `datetime.*`, `pathlib` paths, `io.StringIO` / `BytesIO`, `array.array`,
`struct.Struct`, `uuid.UUID`); any other makes the file DYNAMIC (§7.63). Witnesses `6316`-`6322`;
control `6337`.

### 7.130 A jump inside a `finally:` block is refused (route #431, run #3)

When a try body raises and its `finally:` block executes `return`, `break` or `continue`, CPython
DISCARDS the in-flight exception: the function returns (or the loop goes on) normally. The model
lowers the jump on the normal path only, so an exception PyCSL treats as ambient (an implicit raise
outside every claim: a hash TypeError, an un-claimed KeyError, a callee's) became a normal return
that the proved `ensures` misdescribes: `out[0] = 2; try: hash(m.get("a")); out[0] = 1 finally:
return` PROVED `ensures out[0] == 1` (CPython leaves 2), also around `d["a"]` and around a call of
an un-claimed hashing callee. RULE: in a function that is not `\trusted` / `\abstract`, a `return`
anywhere in a `finally:` block, and a `break` / `continue` in it that is not inside a loop nested in
the block, is refused (`PYCSL-R431-FINALLY-JUMP-SWALLOWS-EXCEPTION`); a nested `def` is its own
function. PEP 765 makes the same shape a SyntaxWarning in Python 3.14. Measured cost 0 (no such jump
in the root corpus, pyref, the mirrors or `pycsl_lib`). The other channels that turn an exception
into a normal return were measured REFUSED by their own routes (probes in
`getting-better/systematic-soundness-r3/h430-r430-431/probes/`): an `except` an un-modelled exception
can reach, in the raising function, a caller or a nested `def` (route #174, incl. `except
BaseException` / `Exception` / bare); a claimed caller of a callee raising KeyError / IndexError /
ValueError implicitly (route #178); `contextlib.suppress` (route #257) and a file context manager whose
`__exit__` returns True (routes #38 / #39); `except*` (the desugar refusal); a generator's own
handler or `finally` (route #271: a generator call is not modelled). Witnesses `6450`-`6454`,
`6457`; controls `6455`, `6456`.

### 7.131 An underivable hashed value under a TypeError claim is refused (route R-gate, run #3)

§7.47's residual: a hashed value whose class cannot be DERIVED (`#UND`: an unknown callee or
receiver, an un-annotated return, `.get(..)` of a `Dict[str, Any]`, an `Any` element of a declared
container; or a value with no source at all) may be a list / dict / set at run time, and was
admitted. `{m.get("a")}`, `seen.add(f2.get("name"))` (`seen: Set[Any]`), `v = m.get("a"); {v}`,
`seen.add(f.get("name"))` over `List[Dict[str, Any]]`, `v in seen` over `m.values()` and
`{m.get("a"): 1}` all PROVED `no_exception \all` (CPython TypeError). TypeError is outside
`KNOWN_EXCEPTIONS`, so outside a claim it is AMBIENT: it ends the function abnormally, and since
§7.130 (route #431) nothing turns it into a normal return, so an un-claimed function's `ensures`
stays true of every normal return. RULE: in a function that is not `\trusted` / `\abstract` and
claims TypeError (`#@ no_exception \all`, or a list naming `TypeError` / `Exception` /
`BaseException`), a hashed leaf (§7.47's positions, tuple components, both arms of `x if c else
y`, a walrus's value, the elements of a hashed iterable) whose derived classes contain `#UND`, or
are empty, is refused (`PYCSL-R349-UNDERIVABLE-HASH-UNDER-CLAIM`), unless §7.47's `if A in B:`
guard has already hashed it. A slice of a value derived as a sequence / tuple / `str` hashes
nothing and is not counted. A hashed site inside a nested `def` / lambda also counts for the
enclosing function (fail-closed). The derivation now reads `list(x)` / `set(x)` as holding the
elements of `x` (a mapping's keys), as it did `sorted(x)`, so `for k in list(d.keys()):
d[k + 100] = 0` over `d: Dict[int, int]` is `int` (control `6336`). Witnesses `6470`-`6475`;
controls `6480` (the same bodies un-claimed), `6481` (claimed, derivable: `Dict[str, int]`
values, `str`, `int` arithmetic over `list(d.keys())`, typed tuples), `6336`.

### 7.132 A claimed caller of a callee that may hash an underivable value is refused (route #430, run #3)

Route #178 refuses a `no_exception` caller of a same-file callee that may raise KeyError /
IndexError / ValueError implicitly without declaring it; a callee's hash TypeError (§7.131's
`#UND` leaf in an un-claimed function) was not in its summary, so `#@ no_exception \all`
`caller(m): return h(m)` with an un-claimed `h(m): s = {m.get("a")}; return 1` PROVED (CPython
TypeError). RULE: the §7.131 pass records every function holding such a site (claimed or not,
`\trusted` included); route #178's transitive callee summary gives each of them, unless it
claims `\all` itself, the bit "may raise TypeError", and a `no_exception \all` caller of one,
directly or through further same-file calls, is refused
(`PYCSL-R430-CALLEE-UNDERIVABLE-HASH`). A named claim cannot carry TypeError (it is not a known
exception), so only `\all` is concerned. Witnesses `6460`-`6462`; controls `6463` (the callee
hashes a `str`), `6464` (an un-claimed caller).

### 7.90 A string literal's characters reach the solver as the characters they are (route #411, run #3)

A Python `str` is a Why3 `string`, and Z3 decides it with its native string theory. Why3 1.8.2's
SMT-LIB printer writes every literal character outside printable ASCII -- and `"` and `\` -- as
`\xHH`, which SMT-LIB 2.6 (Z3 4.13) reads as FOUR characters; and a Latin-1 code point (`"é"`,
U+00E9) was emitted as its two UTF-8 bytes. So `len("é")`, `len("\n")`, `len("a\"b")` were 2 / 4 / 6
in the model: `"é"[1]` and `"\t"[1]` PROVED `no_exception \all`, `requires s == "\n"; ensures
\result == 4` over `len(s)` PROVED (CPython: IndexError, 1). RULE: a code point 0..255 is ONE
character of the model (a code point above 255 keeps its UTF-8 bytes: declared assumption
LATIN1-STR), and a literal holding any character other than printable ASCII without `"` / `\` is
emitted as the concatenation of its printable runs and one `pystr_chr N` per other character, a
one-character string of code `N` distinct from every printable one-character string. The same holds
for a literal in a contract (§7.81) and for every literal the emitter writes itself. A literal of
printable characters is unchanged. No refusal. Witnesses `6200`-`6207`; controls `6208`-`6209`.

### 7.133 An attribute of a receiver that may be `None` or of several classes is refused under an AttributeError claim (route #432, run #3)

An OPERATOR on an `Optional` / `Union` value (`x + 1`, `x < "a"`, `x[0]`, `abs(x)`, ...) was
already refused: §12.4 lowers the annotation to a union variant and Why3 rejects it where an
`int` / `string` is expected. An attribute load had no such check: `x.strip()` on
`x: Optional[str]` lowers to the input-blind opaque `x_strip_0 ()`, so `len(x.strip())`,
`c.m()` on `Optional[C]`, `d.get("a", 0)` on `Optional[Dict[str, int]]`, `n.bit_length()` on
`Optional[int]`, `x.upper()` on `Union[int, str]` and on `str | None` all PROVED
`no_exception \all` (CPython AttributeError). RULE: in a function that is not `\trusted` /
`\abstract` and claims AttributeError (`\all`, or a list naming `AttributeError` / `Exception` /
`BaseException`), an attribute load `R.a` (a field read or a method call) is ADMITTED only when
the classes `R` may have at that point -- the classes derived for `R` (the hashing pass's
`_ex346` / `_eh372`; `Optional[T]` now derives `None` as well, as `Union[T, None]` always did,
and a parameter defaulted to `None` holds `None`), refined by FLOW NARROWING -- are (i) at most
one class and not `None`, or (ii) only builtin classes (`NoneType` included) each of which has `a`
(`hasattr` on the real type, so `x.__class__` on an Optional and `x.real` on `Union[int, float]`
stay admitted); otherwise it is refused (`PYCSL-R432-OPTIONAL-RECEIVER-ATTRIBUTE`). Underivable
receivers (`#UND` / `#UNK`, `Any`, `object`) are refused by §7.150 (route #443).

NARROWING applies to a receiver that is a name or an attribute path `n.f.g`. A guard holds at
the access when it is the test of an enclosing `if` (body: true; `else`: false), `while` (body:
true), `x if T else y`, an earlier operand of `and` (true) / `or` (false), a comprehension's
`if` (true), an earlier `assert T`, or an earlier `if T:` whose block ends in `return` / `raise`
/ `continue` / `break` (false). A guard decomposes through `not`, `and` (true) and `or` (false)
into leaves: `R is not None` / `R != None` and a bare `R` (not None), `R is None` / `R == None`
(when false: not None), `isinstance(R, C)` / `isinstance(R, (C, D))` (exactly those classes, when each
is RESOLVED as §7.150 states -- route #442).
The search stops -- guards farther out no longer hold -- at a nested `def` / lambda / generator
expression (each runs later) and at code
that may rebind `R` between the guard and the access: a store / `del` of `R`'s root name, and,
for an attribute path or a `global` / `nonlocal` name, a store of any attribute on the path or
ANY call; a loop crossed on the way -- or a `while` whose test holds the access -- may not contain
such code anywhere (a later iteration runs it first). Two rebinding shapes give a fact instead: `R = v` (`R` has `v`'s derived classes when
they are derived and exclude `None`) and `if R is None: ...; R = v` (not `None`, or `v`'s
classes). Witnesses `6500`-`6514`, `6548`, `6549` (`6509`-`6513` and `6549` exercise the rule's stop conditions
on shapes another refusal or Why3 already rejected at base); controls `6515`-`6518`, `6520`-`6524`; `6519`:
an `assert x is not None` narrows, and the assert's own AssertionError obligation then FAILS (expected FAIL).

### 7.134 `str.join` / `bytes.join` over elements not derived `str` / `bytes` is refused under a TypeError claim (route #433, run #3)

`"".join(xs)` lowers its elements as opaque values, so `xs: List[int]`, `List[Optional[str]]`,
`List[Union[str, int]]`, `List[Any]`, `List[bytes]`, `Tuple[str, Optional[str]]`, the values of
a `Dict[.., Optional[str]]` and `b"".join(List[Optional[bytes]])` all PROVED
`no_exception \all` (CPython TypeError). RULE: in a function that is not `\trusted` /
`\abstract` and claims TypeError, `S.join(it)` (one positional argument) whose receiver `S` is
derived exactly `str` is ADMITTED only when the element classes of `it` (the derivation's
iteration elements `_ei383`) are derived and all `str`; a receiver derived `bytes` /
`bytearray` admits only `bytes` / `bytearray` elements. Any other element class, `None`, `Any`
or an underivable element is refused (`PYCSL-R433-JOIN-ELEMENT-CLASS`). A join on a receiver not
derived as `str` / `bytes` (`os.path.join`, an unknown receiver) is not judged by this rule.
Witnesses `6525`-`6533`; controls `6534`, `6535`.

### 7.135 `sorted` / `list.sort` / `min` / `max` over values not totally ordered are refused under a TypeError claim (route #437, run #3)

`sorted(xs)` lowers the comparison as opaque, so `List[Optional[int]]`, `List[Optional[str]]`,
`List[Tuple[int, Optional[int]]]`, tuples ending in a `dict`, a `List[Dict]` or a user class
without `__lt__`, and `List[List[Optional[int]]]` all PROVED `no_exception \all` (CPython
TypeError as soon as two such values are compared). RULE: in a function that is not `\trusted`
/ `\abstract` and claims TypeError, `sorted(it)`, `L.sort()` (`L` derived a list), `min(it)` /
`max(it)` and `min(a, b, ..)` / `max(a, b, ..)` are ADMITTED only when the compared values are
derived and TOTALLY ORDERED among themselves: all numbers (`int` / `bool` / `float`), all `str`,
all `bytes` / `bytearray`, all parameterised tuples whose components at each position are again
admitted (`Tuple[T, ...]`: `T` at every position), or all parameterised lists whose elements are
admitted. The `.items()` of a mapping compares only its (distinct) keys. A `key=` must be `len` /
`abs` / `int` / `float` / `str` / `ord` (its result class) or a lambda whose body's classes are
derived and admitted; `reverse=` / `default=` do not matter. `None`, a user class (with or
without `__lt__`), a dict / set, `Any`, an un-parameterised tuple / list, a mix of groups and an
underivable value are refused (`PYCSL-R437-UNORDERED-ELEMENTS`). Witnesses `6536`-`6545`;
controls `6546`, `6547`.

### 7.136 `ord(x)` owes `len(x) == 1` under `no_exception \all` (route #434, run #3)

`ord` raises TypeError unless its argument is a str (or bytes) of length 1, and the model's
`ord_op` / `pycsl_vord_op` read `Char.get c 0` of ANY string: `ord(s)` for `f("ab")`, `ord("")`,
`ord("ab")`, `ord(s[0:2])`, `ord(s.upper())` (`"ß"` -> `"SS"`), `ord(s.strip())` and
`ord("".join([s, s]))` all PROVED `no_exception \all`. RULE, under `\all` only (TypeError is not a
Phase 1 exception; §7.19's rule): `ord(s[i])` of a str owes nothing more than its IndexError row (a
character has length 1); a str literal is decided at emission (one character: nothing; otherwise
REFUSED, `PYCSL-R434-ORD-LENGTH`); any other str-read argument owes `len(x) == 1`; a non-str
argument (`ord(b[0])` of a bytes is an int: TypeError) is REFUSED (`PYCSL-R434-ORD-LENGTH`). The
three rows of §7.136-§7.138 are FAIL-CLOSED: the driver recounts every site of every verified
`\all` body from the IR (comprehension and lambda bodies included) and refuses
(`PYCSL-R434-UNCHECKED-SITE`) a site whose obligation is not in the module and that the emitter
did not record as checked -- `[ord(w) for w in ws]` is refused (the comprehension is lowered
opaque), as is `for w in s.split(",", n)` (the `for` iterable path; `k += len(s.split(",", n))`
verifies). An un-claimed same-file callee holding such a site makes a `\all` caller refused
(`PYCSL-R434-CALLEE-UNCHECKED-SITE`, route #178's summary with §7.132's TypeError token).
PATH VALUES: the front end erases a `pathlib.Path` annotation to `str` (a Path is a Why3 `string`),
so `ord(p)` of a `p: Path` under `requires len(str(p)) == 1` PROVED (CPython TypeError whatever the length),
as did `ord(p[0])` and `q = p.parent; ord(q)`. The driver reads the SOURCE: in a function claiming `\all`,
`ord` of a Path value (a name annotated `*Path*` or bound from a Path value, `x.parent`, a `/` join, a
`Path(..)` / Path-only method call, a subscript / conditional / walrus of one) is REFUSED
(`PYCSL-R434-ORD-PATH`); `ord(str(p)[0])` verifies.
Witnesses `6550`-`6556`, `6570`-`6573`, `6579`, `6586`; controls `6580`, `6583`, `6587`.

### 7.137 An unbound builtin method `T.m(x, ..)` needs `x` of class exactly `T` (route #435, run #3)

`str.upper(x)` with `x: bytes`, `bytes.lower(s)` with `s: str`, `str.upper(xs)` with a list, ...
lowered to an opaque `str_upper_1 x` and PROVED `no_exception \all`; CPython raises TypeError
("descriptor 'upper' for 'str' objects doesn't apply to a 'bytes' object"). RULE (allow-list),
under `\all`: a call `T.m(x, ..)` with `T` one of `str bytes bytearray int float complex bool list
dict set frozenset tuple type object` (the class-level `maketrans` / `fromhex` / `from_bytes` /
`fromkeys` / `from_number` excepted: they take no receiver) is admitted only when `x`'s class is
EXACTLY `T` by its form: a name annotated `T` (`str bytes bytearray int list dict set tuple
frozenset`; NOT `float` / `complex`, which admit an int under PEP 484), a str / int / bool literal
of `T`, an f-string for `str`, or a call of a builtin returning `T` (`str(..)`, `len(..)`,
`bytes(..)`, ...). `object` admits every `x`; a `Path` (erased to `str` by the front end) is refused by §7.136's
source pass (`str.upper(p)`, witness `6588`). Anything else -- an un-annotated local, a display
(`b".."` and `[..]` share one IR form), an attribute, `float.m(x)` of a `float` name -- is REFUSED
(`PYCSL-R435-UNBOUND-DESCRIPTOR`). Only the method names route #161 admits under `no_exception`
(or a file class's method names) reach this rule at all. Witnesses `6557`-`6564`, `6574`; control
`6581`.

### 7.138 C `ssize_t` / `int` method parameters owe their range (route #436, run #3)

CPython converts some method arguments to a C `Py_ssize_t` or `int` and raises OverflowError
("Python int too large to convert to C ssize_t") outside its range: `s.split(" ", n)` with `n =
10**20` PROVED `no_exception \all` (also `maxsplit=`, a negative `n`, in a `for` iterable).
ENUMERATED under CPython 3.14 (measured): `split` / `rsplit` maxsplit, `replace` count, `insert`
index (list / bytearray), `center` / `ljust` / `rjust` / `zfill` width and `int.to_bytes` length
are `ssize_t`; `expandtabs` tabsize and `bytes.hex` bytes_per_sep are C `int`. `find` / `rfind` /
`index` / `count` / `startswith` / `endswith` start / end and `list.index` CLAMP (no error);
`splitlines` keepends is a truth value; `pop(i)` past `ssize_t` is out of range (its IndexError
row). Reachable under `no_exception` today (route #161): `split`, `replace` (whose 3-argument form
does not type-check: it fails), `insert` (refused as an unmodelled mutation); the others only
through a same-named method of a file class (route #161 admits the NAME). RULE, under `\all`, by
method NAME whatever the receiver (route #72's convention: a file class's own `split` owes the
bound too): an int literal is decided at emission (out of range: REFUSED,
`PYCSL-R436-SSIZE-ARGUMENT`); a str / float / bool argument owes nothing; an argument of a PURE int
form (a name, an int literal, `+ - *` / unary `-` of those, `len(name)`) owes `-2**63 <= n <
2**63` (C int: `-2**31 <= n < 2**31`), asserted before the call; any other argument is REFUSED
(`PYCSL-R436-SSIZE-ARGUMENT`: bind it to a local first). §7.136's fail-closed census and callee
summary cover these sites too. Witnesses `6565`-`6569`, `6575`-`6578`; controls `6582`, `6584`,
`6585`.

### 7.139 An un-parameterised `tuple` is underivable when hashed (route #438, run #3)

§7.47 kept an UN-PARAMETERISED `tuple` / `typing.Tuple` on the deny-list check only (its
components checked against the FILE's unhashable classes), so `t: tuple` holding a list was
hashed as if hashable: `hash(t)`, `{t}`, `{(1, t)}`, `{t if c else ()}`, `{(u := t)}`, a
callee `-> tuple` / `-> Tuple` bound to a local or hashed directly, a method parameter, a field
annotated `tuple`, a `Tuple[int, tuple]` component, all PROVED `#@ no_exception \all` (red team
34; CPython TypeError for `([1],)`). RULE: such a value's components are UNKNOWN, so its class
set (the `#UNKT` marker) counts as UNDERIVABLE for §7.131 and §7.132: refused in a hashing
position of a function claiming TypeError (`PYCSL-R349-UNDERIVABLE-HASH-UNDER-CLAIM`), as is a
hashed iterable of such elements (`set(xs)`, `xs: List[tuple]`), and a function holding such a
site makes a `\all` caller refused (`PYCSL-R430-CALLEE-UNDERIVABLE-HASH`). Admitted: a
PARAMETERISED tuple whose every component class is admitted (`Tuple[int, str]`, a display of
typed values), and any tuple hashed in an UN-claimed function (its TypeError is ambient, §7.131).
Not `#UNK` (refused everywhere): the self-annotation mirror `pycsl.py` keys
`_merge_records_best_of_n` by `_record_key(..) -> Tuple` in an un-claimed function (§7.47's
residual), which the claim-gated rule leaves proved. Witnesses `6600`-`6613`; control `6640`.

### 7.140 Structural types, imported user-module callees and computed-name stores in hashing (route #439, run #3)

Three sources of a hashed value's class were read as known (red team 34, PROVED
`#@ no_exception \all`, CPython TypeError). (1) A value declared by a STRUCTURAL type: a file
class listing `Protocol` (`typing` / `typing_extensions`, by name or `typing.Protocol`) among
its bases, a `typing` Protocol (`SupportsInt` ...), or a standard-library ABC with its own
`__subclasshook__` (`Callable`, `Hashable`, `Iterator`, `Awaitable`, `os.PathLike` ...): a list,
or a class with `__hash__ = None`, satisfies it. Such a value is now of an UNKNOWN class
(`#UNK`, as `Any`, §7.47): refused in every hashing position (`PYCSL-R349-UNHASHABLE-RECORD`).
(2) A call into an IMPORTED USER MODULE (`import m` / `from m import h`, resolved to a source
file that is not a standard-library module or a `Lib/` stub; transitively through the user
modules that module imports): the #430 summary came from this file's hashing pass only. Each
function (method) of such a module that does not carry `#@ no_exception \all` and MAY HASH
(syntactically: a set / dict display or comprehension, a subscript, an `in` test, `hash(..)`, a
call of `add` / `discard` / `remove` / `get` / `setdefault` / `pop` / `update` / `__contains__` /
`__getitem__` / `set` / `frozenset` / `dict` / `Counter` / `fromkeys`, a call of a name the module
imports from a user module, or of such a function of the module) now carries §7.132's bit, so a
`\all` caller of it is refused (`PYCSL-R430-CALLEE-UNDERIVABLE-HASH`). (3) A dynamic store with a
COMPUTED name (`setattr(o, nm, v)`, `o.__setattr__(nm, v)`; §7.63's GD-only residual): every
field / class-attribute read of a file class gains an UNDERIVABLE class, refused when hashed
under a TypeError claim (§7.131); not `#UNK` (refused un-claimed too): §7.63 measured that
counting these stores as UNKNOWN for hashed values GONEs the `frontend/pure_ast.py` mirror. Witnesses `6615`-`6624` (helpers
`multi_file_lib/r439_hashlib.py`, `r439_hashmid.py`); controls `6641`-`6643` (helper
`multi_file_lib/r439_okhash.py`).

### 7.141 A builtin or method call is admitted only by its row in ONE signature table (routes #440 / #441, run #3)

Route #161 (`module6_whyml/functions.py`) admits a call under a `no_exception` claim when its callee is a
function of the program or on a short whitelist, and its METHOD arm looked at the NAME only:
`R.m(..)` passed when `m` was whitelisted or when ANY function / method of the file had the tail
name `m`, whatever `R`'s class; a builtin passed whatever its arity and argument classes. The call
lowers to an opaque `val` with no `raises`, so nothing was owed. Red team 35 (860 probes) measured
150 such false proofs under `#@ no_exception \all`: a file `def rindex` admitted
`path.rindex(".")` (ValueError), `n: int; n.upper()` (AttributeError), `len(n)`, `len(s, s)`,
`len()`, `sorted()`, `int(n, 10)`, `s.strip(t)` with `t: Union[str, int]`, `s.find(b)` with
`b: bytes` (TypeError). RULE (allow-list, refuse by default): in a function that is not
`\trusted` / `\abstract` and claims `no_exception`, every call is checked against ONE table:
`_FT440` keyed by the 36 builtin names of #161's list, `_MT440` keyed by (receiver class, method)
for #161's 39 method names on the builtin classes that have them (100 rows; 136 with `_FT440`) (`str` / `bytes` / `bytearray`
strip / lower / upper / is* / startswith / endswith / find / rfind / count / replace / join /
split; `int` / `bool` bit_length; `list` / `deque` append / extend / count / copy / clear /
reverse, `list` insert / sort; `tuple` count; `dict` / `Mapping` get / keys / values / items,
`dict` copy / clear / setdefault / update; `set` / `frozenset` union / intersection /
difference / issubset / issuperset / copy, `set` add / discard / clear / update). A row gives the
positional arity range, the accepted keywords, an accepted-class code per position (a number, an
int, a `str`, `str` or `None`, a `str` or tuple of `str`, bytes-like, an iterable / sized /
reversible value, a mapping or iterable of pairs, an iterable of numbers, a class or tuple of
classes, a callable, anything) and the obligation rows that still speak for its value-dependent
exceptions (#66 / #163 `int(<str>)`, #72 / #436 `split`, #160 / #259 `range` / `pow` / empty
`min` / `max`, #281 big-int `str`, #349 / #438 / #439 hashing, #433 join elements, #434 `ord`,
#437 orderability). A call is ADMITTED iff: a builtin `f(..)` (not shadowed) matches its row with
every constrained argument's classes DERIVED (the hashing pass's `_ty383` / `_ei383`; a call the
table admitted contributes its row's result class) and accepted; a method call `R.m(..)` has,
for EVERY class `R` may have here (`_ty383`, refined by §7.133's guards when they decided it;
`None` is §7.133's), either a file class whose file MRO defines `m` (method, class-body binding
or field) -- or whose non-file base is a builtin with a row for `m` that the call matches -- or
a builtin class with a row `(class, m)` that the call matches; an unbound `str.m(s, ..)` is
`str`'s row with `s` derived exactly `str`. A file name collision never admits a builtin
method: an UNDERIVABLE receiver (`Any`, `object`, `#UND`) is refused for a name only the file
defines (`x.rindex(..)` beside a file `rindex`), and a module function `m.f(..)` beside a file
`f` is refused unless the program itself defines `m.f`. Refusals: `PYCSL-R440-METHOD-NOT-ADMITTED`
under a claim covering AttributeError (the class has no such method), or under ANY claim (a
builtin method without a row -- `rindex`, `index`, `partition`, `rsplit`, `format`, `to_bytes`,
`fromhex`, `maketrans` ...: its exceptions are not modelled, as #161 refuses an unlisted callee);
`PYCSL-R441-BUILTIN-SIGNATURE` under a claim covering TypeError (arity, keyword, `*` / `**`
argument, or an argument class outside the row). Two precision rules of the derivation serve it:
`seq * n` (a list / tuple / str / bytes by an int) is the sequence, not the int; a method
call's result is that of the receiver's non-`None` classes (a call on `None` raises, it returns
nothing). An `assert`'s message is not checked (it is evaluated only when the assertion fails,
route #332). Residual (not judged): a builtin method name on an underivable receiver (§7.133's
`Any` residual, route #443); `super().m(..)` and module functions (#161's by full name).
Witnesses `6650`-`6682`; controls `6690`-`6695`. Measured cost: 0 of the 366 claimed corpus
files that emit at base became refused but four expected-FAIL witnesses that already failed to
verify (`4614`, `4622`, `4826`, `6576`) are now refused earlier; the mirror, `python-reference`
and `pycsl_lib` carry no `no_exception` claim.

### 7.150 isinstance narrows only by RESOLVED classes; an UNDERIVABLE receiver is refused under an AttributeError claim (routes #442 / #443, run #3)

Two gaps in §7.133 (red team 35, PROVED `#@ no_exception \all`, CPython AttributeError).
(#442) The narrowing leaf `isinstance(R, E)` trusted ANY `E` whose spelling was not literally
`object` / `Any`: `isinstance(x, Hashable)` (None is hashable), `typing.Hashable`, the aliases
`T = object` / `O = object`, a tuple variable `T = (str, object)` and a class attribute `H.t =
object` all narrowed `x: Optional[str]` to a class without `None`. RULE (allow-list): the leaf
narrows only when `isinstance` itself is never bound in the file (no def / store / import / class
of that name, no star import) and every class of `E` (a name, or a literal tuple of names) is
RESOLVED: a name never bound in the file (no store, def, argument, class, import, star import)
that names a real builtin class whose metaclass is `type` and that `NoneType` does not subclass
(`issubclass(type(None), C)` on the real class: `object` is excluded). An attribute
(`typing.Hashable`, `H.t`, `builtins.str`), an alias, an imported name, a tuple variable, a PEP
604 union or a FILE class (an `Optional` / `Union` of file classes does not type-check after
narrowing at base, so no proved program relies on it) does not narrow (the receiver keeps its derived classes).
(#443) §7.133 did not judge a receiver whose class is UNDERIVABLE: `xs[0].strip()` on `xs:
List[Any]`, `d["a"].upper()` on `Dict[str, Any]`, an element of `List[object]`, of a bare `list` /
`dict` / `tuple`, of `List[List[Any]]`, `d.get("a", "").upper()`, a `for` target over
`d.values()` all PROVED (the element lowers as an opaque int-erased value and the method as an
input-blind `val`); a direct `x: Any` receiver was not proved only by accident of its lowering
(Unknown). RULE: in a function covered by §7.133's claim test, an attribute load `R.a` is
REFUSED (`PYCSL-R443-UNDERIVABLE-RECEIVER-ATTRIBUTE`) when the classes `R` may have at that point
(after §7.133's flow narrowing) are empty, contain an underivable mark (`#UND` / `#UNK` / `#UNKT`
/ `#UB`), `Any` or `object`, or a class name that is not KNOWN: a builtin of §7.133's table, a
class of the file (never otherwise bound), or a name imported by `from M import C` from one of
`pathlib` / `decimal` / `fractions` / `collections` / `datetime` / `io` / `re` / `array` /
`ipaddress` / `uuid` that is a real class with metaclass `type` (a module alias `PyVal = Any`, a
TypeVar, a `typing` / `collections.abc` name is not). Derived container marks (`#list`,
`#dict`, `#keys` ...) and `#H` (a class / module / function object) stay known, and a receiver
that is a name bound only by `import m` / `import m as x` (a module object) is not judged. ONE
shape is owed instead of judged: the receiver-form `(N.get(k) or {}).get(k2, D)` / `N.get(k).get(k2, D)`
for `N` a `Dict[str, PyVal]` name of the IR's `dict_value_types` (`hval`), which Module 6 lowers
with the `PyCSL-DVW-R5` assertion that the receiver IS a map (in the function's own code, not
a nested def / lambda; control `3282`). The type
propagation (§7.131, `_ty383`) now gives a method call on the `None` arm of a receiver whose
`NoneType` lacks the method no class (AttributeError before any use, as for `str`), not `#UND`,
so `w = v.strip()` after `if v is None: return` stays `str` (control `6522`). An element bound
to a local and narrowed by `isinstance(v, str)` is admitted by this rule, and the erased value's
own obligations (route #343 / #358) then FAIL (`6784`, expected FAIL), so the refusal's advice
is a concrete source type or dropping the claim. Witnesses `6750`-`6755` (#442), `6756`-`6779`
(#443; `6775` / `6777` / `6778` / `6779` -- an alias-of-`Any` parameter, a `for` target over
`List[Any]`, a direct `Any` / `object` parameter -- were not proved at base either: rule
witnesses); controls `6780`-`6782` (#442), `6783`, `6785`, `6786` (#443).

### 7.160 A term transform may thread a read-only `Dict[str, str]` (lv2, run #3)

A Term->Term transform over a frozen-dataclass union (the `isinstance`-dispatch shape of
§T.6.170, e.g. the mirror's `proof2why3/canonical.py::substitute`) may take a SECOND
parameter `m: Dict[str, str]` that it only reads: `m.get(t.F, t.F)` on a `str` field,
recursion `f(t.G, m)` on a sub-term, `tuple(f(a, m) for a in t.L)` on a `tuple` of terms, and a
local `x = {k: v for k, v in m.items() if k not in t.B}` (a `tuple` of strings `B`) passed to
a recursive call. The dict is an ABSTRACT value: `get` and the filtering comprehension are
uninterpreted DETERMINISTIC functions of their inputs, so nothing about WHICH entries a lookup
or a restriction returns is claimed (an over-approximation, no axiom). As for every term
recognizer, it fires only when the function claims nothing (no `requires` / `ensures` other
than `True`, no raises / `no_exception`); a claim declines to the generic lowering. Witness
`6800` (PROVES); `6801` (the same function with `#@ ensures False`, must NOT prove).

### 7.170 `for x in re.split(<literal>, s)` and the no-arg `s.split()` as a list (lv3, run #3)

A loop `for x in re.split(P, s)` (also `_re.split`, from `import re as _re`) over a `str`
`s`, with no keyword argument, is modelled when `P` is a STRING LITERAL that compiles and
has either no capture group or exactly one group spanning the whole pattern (`r"(\W+)"`).
Those are the patterns for which every piece Python returns is a `str` (a group that need
not take part in a match, as in `r"(a)|b"`, yields `None` pieces) and the call cannot
raise `re.error`. The pieces are an unmodelled list of strings: the loop terminates, `x`
is a `str` in the body, and an accumulator of the pieces can be `"".join`ed, but nothing
is claimed about how many pieces there are or what they contain. Any other `re.split`
keeps the old behaviour (no model; refused under route #325).

The no-arg `s.split()` (split on runs of whitespace) used as a whole list is likewise an
unmodelled list of strings of its own (it is not `s.split(" ")`), and its truth test
`if s.split():` is list non-emptiness, which the model leaves undecided. Witnesses `6820`
(PROVES), `6821` (false claim, must NOT prove), `6822` (`(a)|b`, declined), `6823`
(PROVES), `6824` (false claim, must NOT prove).

### 7.171 A term transform may call `str -> str` functions and rename through a dict transform (lv3, run #3)

A one-parameter Term->Term transform over a frozen-dataclass union (§7.160's shape, e.g.
the mirror's `proof2why3/canonical.py::_normalize_names`) may also apply a function of the
same file with signature `(x: str) -> str` to a `str` field (`Var(g(t.name))`,
`App(head=g(t.head), args=..)`), and its two-constructor binder arm may be the block

    nb = tuple(g(b) for b in t.binders)
    m = {o: w for o, w in zip(t.binders, nb) if o != w}
    br = S(t.body, m) if m else t.body       # S: a §7.160 Dict[str, str] transform
    ty2 = g(t.ty)
    kind = A if isinstance(t, A) else B
    return kind(binders=nb, ty=ty2, body=f(br))

The dict is abstract: which entries it holds and whether it is empty are not modelled
(an over-approximation, no axiom). The recursion `f(br)` is not on a sub-term; it is
accepted only in a file whose term transforms already use the proved size measure (one
transform there recurses on the result of an arrow-chain flatten), and then `S` carries
the PROVED fact that renaming preserves the size. Elsewhere the transform declines
to the generic lowering. As for every term recognizer, a `requires` / `ensures` other than
`True`, a raises or a `no_exception` claim declines. Witnesses `6825` (PROVES), `6826`
(`ensures False`, must NOT prove), `6827` (no size measure in the file: declined).

### 7.200 An augmented assignment owes its operator's obligation (route #447, run #3)

`c <<= b` / `c >>= b` on a local or parameter lowered to `c := (bit_lshift !c b)` without the
shift-count row (`b >= 0`, ValueError) or route #414's ssize_t bound (`c = 0 \/ b <=
2**63 - 1`, OverflowError) that the expression `c << b` owes: red team 36 PROVED `#@
no_exception \all` for `mask <<= width` (CPython ValueError for `width = -1`). RULE: an
augmented SHIFT on a name target is lowered as the expression `c = c << b` / `c = c >> b` (the
same `_handle_binop` path, so the two cannot drift). AUDIT of every augmented operator against
its plain BinOp row: `//=` / `%=` / `/=` on a name owe `b != 0` and the floored semantics, which
only the expression form carries (the augmented form was an ill-formed `c := !c div b`, refused
by Why3 by accident of syntax): it is now REFUSED (`PYCSL-R447-AUGASSIGN-DIVISION`; write `c = c
// b`, control `7009`); `**=` keeps route #259's `requires { y >= 0 }` on `py_pow` (no `0 ** -n`);
`+ - * & | ^` have no row. Field / element targets were already lowered through their own
obligation paths. Witnesses `7000`-`7007`; controls `7008`, `7009`.

### 7.201 A field default or annotated field store is of the field's annotation (route #451, run #3)

A field's derived class is its annotation, so `name: str = None` in a `@dataclass` /
`NamedTuple` / class body, and `self.s: str = s` with `s: Optional[str]`, gave a `str` field
holding `None`: `c.name.strip()` PROVED `no_exception \all` (CPython AttributeError). RULE: §7.29's
default-kind check (route #350) also judges, as the value `None` against the field's annotation,
(i) a class-body `x: T = None` (or `field(default=None)`) of a `@dataclass` / `NamedTuple` class
and (ii) an annotated attribute store `o.f: T = v` inside a lowered function whose `v` is `None`
or a parameter whose annotation has a `None` arm (`Optional[..]`, `.. | None`) or whose default
is `None` -- in each case only for a field NAME that some function claiming `no_exception`
covering AttributeError / TypeError (`\all`, `Exception`, `BaseException`) reads as an
attribute. Refused when no arm of `T` admits `None` (`PYCSL-R451-FIELD-DEFAULT-ANNOTATION`).
NARROWED BY MEASUREMENT: the first, wider rule (every kind mismatch of every class-body default
and store) refused 33 corpus files (PASS 0900 / 1190 / 2128 / 4444, the mirror's mixin
declarations `x: Dict[str, str] = None` and un-annotated-parameter stores `self.t: int = t`); a
plain class attribute default, a non-`None` kind mismatch and a field never read under a claim
are residuals (route #236 judges dataclass defaults by value). Witnesses
`7010`-`7014`; control `7015` (`name: str = ""`, `alt: Optional[str] = None`, `retries: int =
3`).

### 7.202 A byte search of a `bytes` value takes a byte (route #452, run #3)

`R.find(n)` / `rfind` / `count` / `index` / `rindex` and `n in R` / `n not in R` with `R`
derived `bytes` / `bytearray` raise ValueError ("byte must be in range(0, 256)") for an int `n`
outside 0..255; §7.141's `BI` code admits the int arm with no range, and `b'abc'.find(n)` with
`n: int` PROVED `no_exception \all`. RULE (allow-list over the classes of §7.141's derivation): the
argument is ADMITTED iff its classes are all `bytes` / `bytearray` / `bool`, or it is an int
literal in 0..255 (a sign included); an int / underivable argument is REFUSED under a claim
covering ValueError, any other class under one covering TypeError (`PYCSL-R452-BYTE-RANGE`). A
computed int is not judged in range even under a guard (residual: an obligation would need the
receiver class in Module 6). Witnesses `7016`-`7022`; controls `7023`, `7024`.

### 7.203 A starred element unpacks a derived iterable (route #454, run #3)

`(*n,)` with `n: int` lowered as `n` itself (`iter_length n`), PROVED `no_exception \all` (CPython
TypeError "Value after * must be an iterable"). RULE: under a claim covering TypeError, every
starred element `*x` of a tuple / list / set display (not an assignment target) and of a call's
positional arguments needs every class of `x` DERIVED iterable (§7.141's `IT` code: `str` /
`bytes` / `bytearray` / `list` / `tuple` / `dict` / `set` / `frozenset` / views / iterators /
`range` / `deque`, or a file class whose MRO binds `__iter__`), and every `**m` (a call keyword
or a dict display) needs `m` derived `dict` / `Mapping`; the function's own `*args` / `**kwargs`
are a tuple / dict. Else REFUSED (`PYCSL-R454-STARRED-NON-ITERABLE`). Witnesses `7025`-`7027`;
control `7028`.

### 7.204 A set method hashes the elements of its arguments (route #456, run #3)

`s.difference(d.values())` with `d: Dict[str, List[str]]` PROVED `no_exception \all` (CPython
TypeError, unhashable type: 'list'): only `set(..)` / `frozenset(..)` / `Counter(..)` / `dict(..)`
/ `fromkeys(..)` arguments were hashed positions. RULE: on a receiver derived `set` / `frozenset`,
each positional argument of `union` / `intersection` / `difference` / `symmetric_difference` /
`issubset` / `issuperset` / `isdisjoint` / `update` / `intersection_update` /
`difference_update` / `symmetric_difference_update` is a HASHED ITERABLE exactly as `set(x)`'s
(§7.28 / routes #349 / #394 / #430 / #438: an unhashable element class is refused
(`PYCSL-R349-UNHASHABLE-RECORD`), an underivable one under a claim covering TypeError
(`PYCSL-R349-UNDERIVABLE-HASH-UNDER-CLAIM`)). `dict.update(x)` is not a new position (residual).
Witnesses `7029`-`7034`; control `7035`.

### 7.205 A module name read under a claim is bound definitely before any call (route #459, run #3)

Module-level names were collected from every top-level binding whatever its control flow, so
`G` bound only under `if TYPE_CHECKING:` / `if False:` / `if sys.platform == ..:`, in a `for _ in
[]:` / `while False:` body, by a `try` body that raises, or AFTER the `__main__` block that calls
`f`, was read by `f` as defined: `return G + n` PROVED `no_exception \all` (CPython NameError).
RULE (module-level definite assignment): walking the top-level statements in order up to the
CALL FRONTIER (the first `if __name__ ...` statement, or a statement holding, outside a def /
lambda / class body, a call of a claimed function or of a file def / class that transitively
calls one), a name is definitely bound by an unconditional assignment (with a value), def,
class or import; through an `if` when every arm binds it (a constant test selects its arm;
`TYPE_CHECKING` is False at run time); through a `try` when the body and every handler bind it
(or the `finally` does); a `for` / `while` / `with` / `match` body binds nothing definitely;
`del` unbinds. A function claiming `no_exception` covering NameError (`\all`, `NameError`,
`Exception`, `BaseException`), neither `\trusted` nor `\abstract`, that loads a free name the
module binds somewhere but not definitely (not local, not a builtin, not in an annotation) is
REFUSED (`PYCSL-R459-CONDITIONAL-MODULE-BINDING`). A `from m import *` stops the judgement.
Witnesses `7036`-`7044`; controls `7045`, `7046`.

### 7.210 A caller's claim is owed in every body it may run (route #460, run #3)

A `#@ no_exception` claim is an assumption about every body the claiming function may run, but
each body's claim-gated checks and trigger obligations read that body's OWN claim only, so an
un-claimed callee's exceptions were owed nowhere: `#@ no_exception \all` `f(n): return g(n)`
with an un-claimed `g(n): return math.factorial(n)` PROVED (CPython ValueError for `f(-1)`),
and so did an un-claimed `g` holding `assert n > 0` (AssertionError for `f(0)`). RULE (the
REACHED claim): the effective claim of a def is its own joined with the claims of every def
that may call it, through the file's call graph -- route #444's closure (by name, method tail,
property load, constructor, file-class dunder; `\trusted` / `\abstract` defs are not entered,
their contracts speak at the call site). A reached def's BODY is judged under it: its trigger
assertions are emitted in its body and discharged by ITS OWN `requires` (so a reached `g`
dividing by `n` now owes `n <> 0` in `g`), and the claim-gated refusals (#64 / #65 / #66 / #71
/ #72 / #160 / #161 / #173 / #178's walk / #207, the #434 site census, #451, #459) fire there.
Its SPECIFICATION keeps its declared claim: an explicit (modelled) raise and a callee's declared
`raises` still escape into its `raises` clause and are judged at its call sites, so a caller
that guards a declared raise still proves. A refusal raised inside a reached def carries a
`NOTE (route #460)` naming the reached defs. ROWS (the over-refusals the reach exposed, each
narrower than the default): a zero-argument `super()` in a plain method of a file class with a
positional first parameter, and `super().__str__()` / `super().__repr__()` in a `__str__` /
`__repr__` of a class whose bases are builtin exception classes or `object`, are admitted by
#161. The front-end #432 / #437 / #440 / #443 / #447 / #452 rows read the reached claim too
(an un-claimed callee's `b.find(n)` with an int `n` is now refused), with two rows: a
CONSTRUCTOR (`__init__` / `__post_init__` / `__new__`) keeps its own claim there (every file-class
dunder is reached, so a constructor no claimed caller runs would be judged: 12 accepted corpus
files measured), and a `super()` receiver in a def whose AttributeError claim is only reached is
judged by #450 rather than #443. Not reached (own claim only): #347, #357, #395 / #402, #439
(another file's defs). Witnesses `7050`-`7053`, `7057` (an un-claimed `@property` getter reading
a missing key, reached through the attribute load), `7059`; controls `7054`-`7056`, `7058`, `7060`.

### 7.240 Every written `#@` claim is attached or refused (route #463, run #3)

A `#@` line binds to the construct that FOLLOWS it (a `def` / `class` / loop / `with` for its contract, any
statement inside a function body for `assert` / `check` / `ghost` / `label`), or, written as the last line
of a body, to the end of that body. Red team 37 measured "All contracts formally proven" for files whose
only written claim was false because the claim was never attached: a `#@` block indented (spaces or a tab)
above a column-0 `def`; a second module-level `def f` replacing the claimed first one; `# @ensures` (a
near-miss spelling). Each of the following is now REFUSED, naming the line:
- a `#@` written after code on its line (`x = f()  #@ assert x > 0`) -- write it on its own line;
- a NEAR-MISS spelling: `#`, then spaces / tabs or further `#`, then `@` and a directive keyword or a
  `\`-name (`# @ensures`, `#\t@requires`, `##@assert`). Prose such as `# @dataclass` and a quoted
  directive inside a comment (`#     #@ ensures ...`) stay plain comments;
- a `#@` block indented DEEPER than the statement that follows it, which belongs to no body (the
  F6 shape above a column-0 `def`, or an over-indented `#@ assert` between two statements of a body).
  Indent a contract block exactly like the construct it sits above;
- `#@` lines above the first statement of a file with no `def` / `class` / loop / `with` to consume them
  (module-scope directives -- `shared`, `datatype`, `mutex_invariant`, `lock_order` -- excepted), and a
  column-0 `#@` line after the last statement (a block running to end-of-file was already refused);
- a statement-level directive (`assert`, `ghost`, `label`, `check`, a loop's `loop invariant`, a `with`'s
  `critical`) whose statement is outside every function body -- module level, a class body,
  `if __name__ == "__main__":` -- which is never lowered;
- in the module or a class body, a name bound two or more times (def / class / assignment / import) of
  which an EARLIER binding is a `def` / `class` carrying a `#@` claim: CPython keeps the last binding, so
  that claim would describe nothing. A property accessor chain (`@property def x`, `@x.setter def x`) and
  an `@overload` chain are one binding each. An unclaimed earlier binding is allowed (the claimed last one
  is the function CPython calls).
Witnesses `7180`-`7193`; controls `7194`-`7197`.

### 7.241 Private names are mangled as CPython mangles them (route #464, run #3)

An identifier `__x` (two leading underscores, not ending in `__`) written lexically inside class `C` --
its methods and anything nested in them, but not a nested class, which uses its own name -- is
`_C__x` (`C` stripped of leading underscores; no mangling if `C` is all underscores), exactly as CPython
compiles it: attribute names, plain names, def / class names, parameters, keywords, `global` /
`nonlocal`, `except .. as`, match captures. Strings (`getattr(o, "__x")`, `__slots__` entries) are not
mangled. A `#@` claim is mangled by the class its anchor sits in (a class invariant by its own class), so
`#@ ensures self.__x == n` on a method of `C` reads the field the body writes. Consequently `self.__x` in
a subclass `D` of `C` is `self._D__x` (not `C`'s field; under `no_exception` route #445 refuses the read,
and a claim over its value FAILS), `C.__K` outside any class reads `__K` (not `C`'s `_C__K`), and
`self._C__x` in `D` reads `C`'s field. Witnesses `7200`-`7204`; controls `7205`-`7207`.

### 7.330 An augmented assignment on a collection-typed parameter is refused under every memory model (route #478, run #3)

Route #49's refusal of `a += ...` on a list parameter was keyed on the default model's local
tables. Under `--memory-model typed` / `store` a list parameter is a heap location (`type loc =
int`) plus an immutable `a_len`, so `a *= 2`, `a -= 1`, `a &= 1`, `a **= 2` ... lowered to integer
arithmetic on the LOCATION: `a *= 2; return len(a)` proved `\result == 2` (CPython 4), and `a -= 1`
proved `no_exception \all` (CPython TypeError). RULE (allow-list on the parameter's DECLARED type,
judged on the IR once for every memory model): an augmented assignment whose target is a formal
parameter of a verified function is admitted only when the parameter is an immutable scalar
(`int`, `float`, `bool`, `complex`, `str`, `bytes`, a tuple, or unannotated); any other type
(`list`, `List[..]`, `Dict`, `Set`, `bytearray`, a class ...) is REFUSED
(PYCSL-R478-COLLECTION-PARAM-AUGASSIGN). Mutate the elements through the modelled element store
(`a[i] = a[i] * 2`, every model), or build a local list (`[x * 2 for x in a]`, default model). Census at 8aaa864ca: no corpus, mirror or stdlib file
augments a non-scalar parameter outside route #49's own witness. Witnesses `7530`-`7537` (PROVED
under typed / store at base, refused now); controls `7538`, `7539`, `7546`.

### 7.331 A module name rebound after the call frontier is refused (route #476, run #3)

The model resolves a module name to its textually LAST binding (the import view); a file run as a
script executes its call frontier -- the first `if __name__ == ...` statement (either operand
order) or module-level call of a verified function (or of a file function / class that reaches
one) -- with the bindings made so far. `def g(x): return 1 // (x - x)`, a verified `f` returning
`g(n)` called from the `__main__` block, and a second `def g(x): return x` after it proved
`no_exception \all` (CPython ZeroDivisionError). RULE: when the module has a call frontier, a
module name read by a verified function -- directly, or through the bodies of every file def /
class of that name, transitively -- or the verified function's own name, that is bound both by a
top-level statement before the frontier and by the frontier statement or one after it, is REFUSED
(PYCSL-R476-REBOUND-AFTER-FRONTIER). Two bindings both before the frontier stay admitted (the
last one is live there, and is the model's). Census at 8aaa864ca: 0 corpus, mirror or stdlib
files rebind such a name across a frontier. Witnesses `7540`-`7545`; controls `7547`, `7548`.

### 7.350 A name the file never binds is never a known int (route #485, run #3)

Route #480 made every builtin object an origin of route #325's opaque-int rule, keyed on
`dir(builtins)`; the module-instance globals CPython inserts into every namespace (`__file__` a str,
`__cached__` None in a script, `__builtins__` a module, `__annotations__`, `__path__`) and the
class-body / method implicit names (`__module__`, `__qualname__`, `__class__`) are not attributes
of `builtins`, so `__file__ + n`, `__file__ < n`, `-__file__`, `x = __file__; x += n` proved
`no_exception \all` and `__file__ * 0` proved `\result == 0` (CPython TypeError / `''`). RULE
(allow-list polarity): a Python name that is LOADED but bound NOWHERE in the file -- no
assignment, augmented / annotated / walrus / for / with / except / match / del target,
parameter, def, class, import, `global` / `nonlocal`, in any scope -- is resolved by CPython in the
module's own namespace or in builtins, never computed by the file, so its fallback is an origin:
any int operation on it is refused (PYCSL-R325-OPAQUE-INT-FALLBACK). Only the known-int `__debug__`
keeps its int model, and a dunder-style name the file itself binds (`__version__ = 3`) keeps
#325 / #328's classification. Witnesses `7590`-`7595`; control `7596` (and route #480's `7517`, `7521`).

### 7.351 An augmented assignment is judged by the static type of its target (route #486, run #3)

Route #478 judged only a bare formal-parameter target. Under `--memory-model typed` / `store` a
list element is an `int_mem` cell and a nested list / str / tuple / dict / set element is itself a
location (`type loc = int`), so `a[0] -= 1` on `a: List[List[int]]`, `t[0] *= 2` on a tuple slot
and `(b := a); b *= 2` / `b = a if c else a; b *= 2` (a local alias of a list parameter) were
integer arithmetic on a heap cell and PROVED (CPython TypeError, or `a` extended in place). RULE
(allow-list on the TARGET's source type, judged on the Python AST of every verified function):
the type of a name / subscript / attribute target is derived from the parameter annotations, the
bindings of each local (assignment, annotated, walrus, `for`, ternary, `and` / `or`, displays,
arithmetic; fixpoint), container element types (`List[E]`, `Sequence[E]`, `Dict[K, V]`, tuple
slots), user-function return annotations and class field annotations. A target of a modelled
scalar type (`int`, `float`, `bool`, `complex`; `str` / `bytes` only for `+=`, `*=`, `%=`, and
only as a name under typed / store, where a str cell is an int) is admitted. Under typed /
store every other target -- a list, dict, set, tuple, Optional / None, class instance, or a type
the judgement cannot establish -- is REFUSED (PYCSL-R486-NONSCALAR-AUGASSIGN-TARGET). Under the
hoare-family models (a list / dict / record is not a Why3 `int` there, so integer arithmetic on
it fails Why3 typing -- fail closed) only what CPython itself rejects on the known target type is
refused: an item store into a tuple / str / set, and an operator the type lacks (`list -= ..`,
`dict += ..`, `str -= ..`); a type's own in-place operators (`list +=` / `*=`, `dict |=`, set
`|=` / `&=` / `-=` / `^=`) stay with the emitter. A bare formal-parameter target stays route
#478's (7.330). Update a scalar instead: a local with a
scalar annotation (`x: int = len(a); x *= 2`), or an int element through the element store
(`a[i] = a[i] - 1` on a `List[int]`). Witnesses `7600`-`7610`;
controls `7612`-`7616`.

### 7.352 `x or y` / `x and y` over a non-bool operand is a truth test only (route #487, run #3)

Python's `a or b` returns one of its OPERANDS. For an operand that is neither a Python bool nor an
int selected raw (a list, str, dict, set, float, Optional, record), the body lowering selected the
int encoding of its TRUTH VALUE (`if Array.length a <> 0 then 1 else 0`), so `b = a or a; b *= 2`
was int arithmetic (CPython extends `a` in place), and `(a or a) < 3`, `-(a or a)`, `b -= 1` proved
`no_exception \all` (CPython TypeError). RULE (refuse by default): such a BoolOp is lowered only
in a TRUTH position -- an `if` / `while` / `assert` condition, `not`, a nested `and` / `or` operand
of one -- where its truth value is exact; used as a VALUE (bound, returned, passed, compared,
arithmetic) it is REFUSED (PYCSL-M6-BOOLOP-VALUE). Pure-bool operands (`a == b or c == d`), int
operands (`n or 5`), two str operands and two IR-node operands keep their value-preserving
lowerings. Spec context (`and` / `or` as connectives) is unchanged. Test the operand and use each
one in its own branch (`if a: return len(a)` / `return len(c)` for `return len(a or c)`). Witnesses `7620`-`7624`; controls `7626`-`7629`.

### 7.300 An empty list is EMPTY across a call boundary (route #473, run #3)

`c = []` (also `c: List[int] = []`, `c = list([])`) used to lower to the fixed-size placeholder
`let c = (Array.make 1024 0) in`, and a later `g(c)` handed the callee an array of length 1024:
`g`'s `requires len(c) >= 1` was discharged against 1024 and the call PROVED while CPython raises
IndexError; a callee's `ensures \result == len(c)` gave the caller `1024`, and `list([])`'s own
`len(c)` read 1024. Routes #195 / #196 had corrected only the direct argument `g([])`.
RULE: an empty list literal is the genuinely EMPTY array `(Array.make 0 0)` wherever the IR can
attribute the placeholder to it -- every placeholder of a function that builds no real
1024-element list (`[v] * 1024`, `bytearray(1024)`, a constructor whose record default is 1024
elements), and, in a function that does, every `let` / `ref` / `:=` binding of a local whose every
assignment is `[]` (and the remaining placeholders too when each real-list producer is the whole
value of a local the emission names). A real 1024-element list keeps 1024; an append target's
capacity (`X_len` sidecar) is untouched. No new refusal: the positions an unattributable
placeholder can still occupy (a direct field store beside a 1024-default constructor) were measured
fail-closed. Length obligations only get harder; CPython's own `\result == 0` now proves.
Witnesses `7380`-`7389`, `7396` (PROVED at base, FAIL now); controls `7391`-`7395`.

### 7.320 Builtin objects are not ints; `...` stays opaque in every position (routes #479 / #480, run #3)

A Python value Module 6 does not model falls back to an OPAQUE INT. Route #325 restricted such a
fallback to identity uses (bind, pass, return, discard, `=` / `<>` against a different value) only when
it stood for a module-level value of THIS file, so the fallbacks with no such origin kept int theory:
a builtin NAME used as a value (`max + n`, `int < n`, `x = len; x += 1`, `len & 1`), the
`NotImplemented` singleton (`NotImplemented + n`, `NotImplemented ** 2`, and its truth value, a
TypeError since CPython 3.14), `...` / `Ellipsis` as an operand, an attribute of a builtin type
(`int.real + n`, `str.upper + n`), and an UNCALLED attribute of an int (`n.bit_length + 1`,
`n.__add__`, `n.__class__`) all PROVED under `#@ no_exception \all` while CPython raises TypeError;
`len.zz` / `NotImplemented.zz` proved while CPython raises AttributeError. Separately (#479), `...` in
a conditional-expression test, a `not` / `or` operand inside it or a ternary arm reached the emitter
as the opaque carrier of route #40's marker, was re-read as the literal `0`, and was FALSY:
`1 // (n - n) if ... else 1` proved `no_exception`.
RULE: a builtin name the file does not bind IS that builtin object (a function, a type, a singleton),
never an int, so its fallback is an origin exactly like a module-level value's (only `__debug__`, a
bool, is known int); `...` is one too; of an int VALUE's attributes only `real` / `imag` / `numerator` /
`denominator` are ints, so an uncalled attribute of any other `int` attribute name is an origin (unless
a class of this file defines that name). An operand of the bitwise / shift / power model operations
(`&` `|` `^` `<<` `>>` `**`) is an int use like `+`. The truth value of `NotImplemented` (`if`,
ternary, `not`, `and` / `or`, `bool(..)`, `any` / `all`) is refused. A builtin object (a builtin name
the file does not bind, `...`) is one fixed object, so a reflexive identity (`x is ...`,
`r is NotImplemented`) stays admitted. Under a `no_exception` claim covering AttributeError, an
attribute chain rooted at a builtin name is judged on the REAL builtin object (route #445). `...` is
recognised by its marker whichever carrier (dict or typed opaque node) reaches the emitter, so it is
`pycsl_ellipsis` (opaque) in every position and a truth test of it no longer decides.
Witnesses `7490`-`7510` (PROVED at base, FAIL / refused now); controls `7515`-`7522`.

### 7.230 A claimed module must IMPORT without raising; `__init__` returns None (routes #461 / #462, run #3)

A claimed function of a module whose import raises is never callable, yet red team 37 measured PROVED
`no_exception \all` for `f` beside `class Z(int, str)` / `class Z(bool)` / an Enum member bound twice / a
NamedTuple with a non-default field after a default or a field `_x` / `@dataclass(order=True)` over a user
`__lt__` / a frozen dataclass over a non-frozen one / a mutable or misordered dataclass default / a
dataclass `x = field(..)` without an annotation / `__slots__ = ('x',)` beside `x = 1` / two `__slots__`
bases / an MRO conflict / `class Z(B, flag=1)` / a base `__init_subclass__` that raises, and beside a
module-level `X = 1 // 0`, `V = {}['k']`, `V = int('x')`, `assert 1 == 2`, a class body `K = 1 // 0`
(#461); and a claimed `C(n)` over `def __init__(..): ..; return n` (#462, CPython TypeError).
RULE (allow-list, refuse by default) when a verified def of the file carries any `#@ no_exception` claim:
the module top level and every class body it reaches are RUN on a synthesized equivalent, statement by
statement. Expressions are evaluated over real values (literals, builtins, standard-library module
objects, earlier bindings; a module attribute that is run-time state -- `os.environ`, `sys.argv` -- is
unknown), calling only side-effect-free standard-library callables, builtin-type methods, the classes
being synthesized and two shapes of file code (a `def` whose body is `return <constant>`, a class whose
own `__init__` only stores constants / parameters on `self`); any other file code -- method bodies, a
metaclass, `__init_subclass__`, an Enum member constructor, `__class_getitem__`, a non-identity
decorator -- is a placeholder whose call is refused (code run at import is not judged). Each class is
created by CPython's own `types.new_class` on its synthesized namespace and its decorators applied for
real, and the C3 order `_mro363` must exist: whatever CPython raises there is the verdict. Admitted
statements: imports of modules that exist (standard library: imported; otherwise found next to the file,
on `--import-path` or installed, a `from` name bound by that module), `def`, `class`, assignments /
augmented / annotated assignments to names, docstrings, `pass`, `assert` of a true test, `if` (the arm
the real test selects -- `if __name__ == "__main__":` and `if TYPE_CHECKING:` are not run), a `try`
whose body is itself admitted, `del` of a bound name, `type X = ..`. Anything else (`for`, `while`,
`with`, `raise`, an attribute store, a walrus) is REFUSED (`PYCSL-R461-IMPORT-RAISES`). (#462) an
`__init__` with a `return <expr>` other than `None`, a `yield`, or `async` is REFUSED under any claim in
the file (`PYCSL-R462-INIT-RETURNS-VALUE`). Witnesses `7130`-`7150`; controls `7151`, `7152`.

### 7.340 A `\trusted` def's list parameter keeps its length only if its body does (route #481, run #3)

A same-file (or imported) `#@ \trusted` function is emitted as a bodyless `val`; with no `#@ assigns` its
frame is route #317's INFERRED `writes { xs }`, and a Why3 `array`'s length is immutable under `writes`, so
`k(xs); return len(xs)` kept the entry length while the trusted body appended (`\result == \old(len(xs))`
PROVED, CPython 1 for `f([])`). The user trusts the CONTRACT, not a length the tool infers; a declared
`#@ assigns xs` lowers to the same length-keeping `writes { xs }`. RULE: §7.282's allow-list now judges an
explicit `#@ \trusted` def too, exactly as an imported or `\abstract` one -- one rule for every bodyless
boundary. Boundary kinds checked (witness REFUSED or not proved, store-only control still PROVED): same-file
`\trusted` with no `assigns`, with `assigns xs`, with `assigns \nothing`, with no `ensures`; a `\trusted`
METHOD's list parameter; an imported `\trusted` def; a `\trusted` def returning its argument after `+=`;
`\abstract` (already §7.282); verified callees -- plain, recursive, `#@ interface`, `#@ no_inline` -- (route
#49's Module 6 refusal); `heapq` / `bisect` mutators (route #162). Refusal: `PYCSL-R468-VAL-LIST-LENGTH`.
Witnesses `7560`-`7564` (PROVED at base, REFUSED); controls `7565`-`7567`. Not covered: a list FIELD written
by a bodyless method (`self.xs.append`), §7.282's residual.

### 7.341 A dependency constant folds only if no module of the program writes it (route #474 residual, run #3)

`from h import K` copies the dependency's `K = 1` into the importer's `module_constants`, and the importer
folds `K` to `1` -- a fact about `h` alone. Under an `ensures`-only claim (route #466's real import run only
happens under `no_exception`) a PEER module of the program doing `import h; h.K = 0`, a package `__init__`
doing `from . import sub; sub.K = 0`, or `setattr(h, "K", 0)` left the fold in place: `\result == 1`
PROVED, CPython 0. RULE (allow-list, flow-insensitive, no refusal): a folded dependency constant stays folded
only when NO module of the program -- this file, every module its imports resolve to, transitively, and every
package `__init__` on their dotted paths -- stores or deletes an attribute of that name (any receiver, any
depth; the names of a `from M import K as J` alias chain count as one) or holds a namespace writer (`setattr`,
`delattr`, `vars`, `globals`, `exec`, `eval`, `__import__`, `.__dict__`, `.modules`). Otherwise the fold is
dropped and the importer sees the opaque `val constant` (a claim that needs the value is NOT PROVED; route
#325 refuses an opaque int under `no_exception`). Code: `_run_pipeline`, before the IR is serialized;
it composes with route #474's per-dependency binding-site guard in `frontend/ir_resolve.py` (both must
pass). Witnesses `7570`-`7572` (PROVED at base, NOT PROVED); controls `7573` / `7574`. Conservative: a peer
FUNCTION that writes `h.K` after the importer bound `K` drops the fold although CPython's from-import read
`1` (NOT PROVED, honest). Not covered: a module OUTSIDE the program's import closure (one that imports this
file as a library) -- the same modular assumption as this file's own constants.

### 7.390 A value that may be a number or a hashed literal is never used as either (route #490, run #3)

The model has one Why3 type per value. A value that is SOMETIMES an int and sometimes a str / bytes / tuple
literal is lowered as an `int` in which the literal is its integer HASH (`_coerce_to_int`), and a `None`
literal the opaque int `pycsl_none`: `y = 1 if n > 0 else 'a'; z = y + 1`, `d = {'a': 1, 'b': 'x'};
d['b'] + 1`, `d.get('b', 0) += 1`, `-{'a': 1, 'b': None}['b']`, `for v in {1: 1, 2: 'x'}.values(): s += v`,
`g(None)` for `g(x: int)`, `x: int = 'a'` and a helper `-> int` returning `1 if n > 0 else 'a'` were integer
arithmetic and PROVED `no_exception \all` (CPython TypeError); `1 if n else ''` was a non-zero int in a
truth test (CPython falsy). Route #486 left a value of unknown type to Why3 typing, which does not catch a
hashed literal (it IS an int).

RULE (judged on the Python AST of every verified function, in every memory model; the emitter is unchanged,
so a file without such a value emits byte-identically). Every expression gets the set of LITERAL KINDS it
may evaluate to -- number, str / bytes / f-string, None, tuple / list / dict / set display, object; unknown
for anything else (parameters, calls, attributes) -- joined over ternary arms, `and` / `or` operands, every
binding of a local (assignment, walrus, `for` / comprehension targets, `.items()` / `enumerate` pairs;
flow-insensitive, all scopes, fixpoint) and the ELEMENTS of a local container (displays, comprehensions,
item stores, `append` / `add` / `insert` / `extend` / `update` / `setdefault`, read back through `[..]`,
`.get(k, d)`, `.pop`, `.values()`, a constant tuple index). A use is REFUSED (PYCSL-R490-LITERAL-INT-HASH)
when the operand may be a NUMBER and also:
- any non-number (str, None, tuple, list, dict, set, object) -- for an operand of a binary operator, an
  ordering comparison (`<` `<=` `>` `>=`) or an augmented assignment (target or value), and of a unary
  `-` / `+` / `~`;
- a hashed str / bytes / tuple -- for an equality / membership comparison, a truth test (`if`, `while`,
  ternary test, `assert`, `not`, an `and` / `or` operand), a subscript receiver or index, an attribute
  receiver, an iterable, an f-string field, a call argument (or its elements), a return value of an
  unannotated function, a value stored into an attribute / nested item / global.

ALLOW-LIST (no observation as a number): binding and storing the value, `is` / `is not` and `== None` /
`!= None`, `print(..)`, the container mutators above, the return of a function annotated `Optional[..]` /
`Union[..]` / non-scalar. A None is removed where a guard proves it absent and the guarded region does not
rebind the name (`if v is not None:` / `if v:` body, the `else` of `if v is None`, a later `and` / `or`
operand, the statements after `if v is None: return` or `assert v is not None`). A container's DIRECT `None`
element read straight off a local stays route #230's value fence (`d[k] - d[k]` is NOT PROVED there); under
a unary operator it is refused here. SLOT CHECK: a str / None / tuple literal kind in a NUMERIC slot -- an
annotated binding `x: int = ..`, the argument for (or the omitted default of) an `int` / `float` / `bool` /
`complex` / `Optional[int]` parameter of a file function or class constructor, the return value of a function
so annotated -- is refused (a bare `return None` and a dataclass field default stay routes #227 / #236's).
Give the value ONE type (`y = 1 if n > 0 else 0`, `{'a': 1, 'b': 2}`), or test the None case before use
(`if y is not None: z = y + 1`). Witnesses `7770`-`7786`; controls `7790`-`7796` (an int-only ternary, an
int-valued dict, a guarded and an early-returned None arm, a str-only ternary, a constant tuple index, int
slots).

### 7.360 A bodyless `val`'s INFERRED frame must follow every alias of a mutable root (route #482, run #3)

A `#@ \trusted` / `#@ \abstract` def (here or in an imported module) with NO `#@ assigns` gets
its caller-visible frame from routes #316 / #317's syntactic alias analysis of a body the tool never verifies.
That analysis follows a reference only through `=`, `for`, tuple unpacking, walrus and an access chain, and a
`\trusted` method's call stub takes `writes` from `#@ assigns` ONLY. Red team 40 measured PROVED `xs[0]` /
`o.v` / `c.xs[0]` unchanged across the call, CPython changed it, for a store reached through a fresh container
(`ys = (xs,)[0]`, `ys, = [xs]`, `zs = [o.xs]; zs[0][0] = 7`, `for p in [o]`), a `with ... as` / `match` /
comprehension binder, a nested def / lambda / class body (dropped from the IR of a `\trusted` body), a record,
dict or set parameter, and `self` in a `\trusted` method -- where even a DIRECT `self.xs[0] = 7` was invisible.
RULE (allow-list, refuse by default; `_run_pipeline`, on the source of the def): every MUTABLE root -- a
parameter whose annotation is not a scalar (`int`, `float`, `bool`, `str`, `bytes`, `complex`, `None`,
`Optional` of one), `*args` / `**kw`, and `self` of a method other than `__init__` -- and every name bound from
one may occur only (1) in an access chain read into a scalar position (comparison, test, index, `len`-like pure
builtin, f-string, discarded or returned value); (2) bound to a plain name by `=` / `for` / tuple unpacking /
walrus (the name is checked the same way) -- through `a + b` / `s += y` the name is FRESH and may only be read
into a scalar position; (3) as the target chain of a store `r.f = v` / `r[i] += v` / `del r[k]`, a write the
inference charges; (4) as the receiver of a list / dict mutator, a read-only method (`get`, `count`, `items`,
...) or a method of the program; (5) as the argument of `next` / `iter` / `reversed` / `enumerate` / `zip` /
`min` / `max`, or of a function / method of the program (then judged by this rule too, or verified); a store the
source shows on a parameter must also be in the frame the inference computed from the lowered IR. `self` and a dict / set parameter are READ-ONLY roots (no inferred frame carries a write to them;
a dict parameter may be stored directly, `d[k] = v`). Anything else -- a container display, an argument of
another call, a `with` / `match` / comprehension / `except` binder, a nested scope, a `yield` -- is refused
with `PYCSL-R482-TRUSTED-FRAME-UNTRACKED`: declare the frame with `#@ assigns` (`#@ assigns self.<f>` for a
method) or verify the function. Only a `val` the verified code of the file reads is judged (route #468's
filter); a `\trusted` caller forwarding a root to it is itself judged (a call argument is not admitted). A
list parameter is also under §7.340's length rule, which refuses most of the same spellings first.
Judged: defs whose own `#@` block says `\trusted` / `\abstract`; a def the tool AUTO-trusts (a body it cannot
lower) or an un-marked imported def is NOT judged by this rule (measured: 6 mirror files would be refused --
route #482's named residual). Witnesses `7630`-`7638` (PROVED at base, REFUSED), `7639` (route #468 at base and candidate), `7653` (the advice
followed: NOT PROVED); controls `7650`-`7652`, `7654`, `7655`. Not covered: a user-WRITTEN `#@ assigns` on a
trusted def is assumed, never compared with its body (only the mirror's `bin/check-trusted-frame-honesty.py`
ledger compares `self.<f>` stores of mirror stubs).

### 7.361 Bodyless-`val` judgements see route #316's statement-level SSA split (D3 parity, run #3)

§7.340's length rule (routes #468 / #481) and §7.360's frame rule judge a `\trusted` / `\abstract` / imported
body on the SAME statement-level SSA copy as route #316's frame analysis (cv6 D3, §Module 6 `transpile`): a plain
`v = ...` that is a statement of the def's own body (not nested in a block) starts a new version of a
non-parameter local `v` for every later top-level statement, its right-hand side reading the previous version;
a name read in a nested scope (lambda, def, class, comprehension) or declared `global` / `nonlocal` is never
split. A version bound by a top-level `v = x` of a judged list parameter is an ALIAS judged by the same rows as
`x`; a store of the version's own name rebinds it (never writes `x`). So cv6 7448 (`ys = xs; ys = [0]; ys[0] =
7`, expected PASS) is accepted again, while 7442 (`ys.append` after a conditional rebind) and 7446 (walrus) stay
refused, and 7444 / 7445 (a second alias / an alias after a fresh binding) emit and are NOT PROVED (the frame
charges `xs`).

### 7.370 Every module of the import closure runs only allow-listed code at import time (routes #483 / #484, run #3)

A cross-module fact -- a folded dependency constant (`from h import K`, §7.310 / §7.341), the binding of a
function this file calls (its own `g`, an imported `g`, `h.g`), this file's own globals -- is a WHOLE-PROGRAM
fact: any module of the program can rewrite another's namespace while it is imported. Red team 40 measured
PROVED `ensures \result == n` (no `no_exception`, so route #466's real import run never ran; CPython returns 0)
for a dependency reaching `exec` / `setattr` through its `__builtins__` MAPPING (`__builtins__['exec']('K =
0')`, `.get('exec')`, an alias, a `for` over `.items()`, inside a function it calls; #483), a dependency doing
`import __main__; __main__.K = 0` (an alias, a package `__init__`, `__main__.g = lambda x: 0` on the callee;
#484) and a PEER module rebinding another dependency's FUNCTION (`h.g = ...`, `setattr(m, 'g', ...)`, inside
a function it calls; #484). Route #474's writer list and the Weaver's rules key on spellings.

RULE (allow-list, refuse by default; every claim kind): over the program's import closure (this file and every
module its imports resolve to, at any depth, package `__init__`s included), the code that RUNS AT IMPORT TIME --
each module's statements outside `def` bodies (this file's `if __name__ == "__main__":` block excepted: it runs
after every import), decorators, defaults, annotations, class bodies, lambdas, and, closed BY NAME, the body of
every `def` named in that code (a class named there: its dunder methods; named as a base: its
`__init_subclass__` / `__set_name__` / `__mro_entries__` / `__class_getitem__`; a metaclass: every method) --
must, in every module but this file, stay in the fragment whose effects on other namespaces are understood:
imports only of program modules, installed libraries and the allow-listed standard library (never
`__main__`, never this file; `sys` only through allow-listed attributes); no `exec`, `eval`, `compile`,
`globals`, `vars`, `locals`, `setattr`, `delattr`, `getattr`, `__import__`, `breakpoint`, `help`, `input`,
annotation evaluators, or dunder name outside a small allow-list (`__builtins__` ...) -- except
`getattr(x, "<literal, not dunder, not a program module>")`, `setattr` / `delattr` on the enclosing
method's own `self`, a `g = globals()` bound once at the top level that no import-time code reads, and a
WRITE-ONLY sink of the module's own namespace (a top-level `F(globals())` whose top-level `def F` only ever
stores `P[k] = v` through that parameter, never with a literal key naming a program binding); no dunder attribute outside a small read-only allow-list, no frame /
code attribute (`f_*`, `gi_*`, `cr_*`, `ag_*`, `tb_*`, `co_*`), no `.modules` / `._getframe` / `.meta_path` /
`.builtins` on any receiver; a plain-`import`ed module name only as the receiver of an attribute read; and no
attribute store / delete whose NAME is bound at a module's top level or in a class body anywhere in the
closure (except on the enclosing method's own `self`: an instance field); a program module
never used as a value (a plain-imported name, a from-imported submodule, `h.sub`). The closure by name is
import-resolved for top-level functions (a bare name in its own module or a module from-importing it, an
attribute of an imported receiver; this file: any receiver), and an imported module's `if __name__ ==
"__main__":` block is not run unless the module rebinds `__name__`. Otherwise the file
is REFUSED (`PYCSL-R483-IMPORT-TIME-NAMESPACE-WRITER`), judged after route #466 (whose own refusal keeps
precedence under `no_exception`). Code: `_run_pipeline`, after route #466; inline, mirror twin `\trusted`.

Over-refusal (byte-diff vs base `e3b3711a2`, root corpus + python-reference + the 53-file mirror sweep, and the
red team's PASS controls): 0 honest files; the only files it newly refuses are route #474's NOT PROVED witnesses
`7570`-`7572` (now REFUSED). The alternative (route #466's real import run claim-free for ensures-only files too)
refuses at least the 14 mirror files whose closure reaches the verifier's own `frontend/pure_ast.py` (its
top-level `_build_nodes(globals())` is a call its runner does not admit) and 3 corpus files with a relative
import, and runs the program's code inside the verifier. Witnesses `7670`-`7678` (PROVED at base, REFUSED); controls `7680`-`7682`.
Not covered (named residuals): a dependency function the claimed code calls at RUN time (its effects are its
contract's -- route #119 / the Weaver's rebinding rules); a dependency method invoked unbound with a CLASS
as `self` (`C.m(D)`) storing an attribute of `D`; file-system writes at import (`os` / `pathlib` /
`subprocess` are allow-listed) that change a module the verifier already read; the write-only own-namespace
sink with a COMPUTED key (the verifier's own `pure_ast._build_nodes` shape) may overwrite one of that module's
own names; an installed library's own import-time code.

### 7.380 An implicit dunder position on a user-class value is a CALL of that class's dunder (route #489, run #3)

`len(o)`, `bool(o)` / `if o:` / `not o` / `o and x`, `o == 1` / `o < 1` (with reflection), `1 in o`, `o in xs`,
`-o`, `o + 1` / `1 + o` / `o += 1`, `str(o)` / `repr(o)` / `print(o)` / `format(o)` / `f"{o}"` / `'%s' % o`,
`int(o)` / `float(o)` / `abs(o)` / `round(o)` / `divmod(o, 2)`, `[5][o]` / `range(o)` (`__index__`), `o[0]`,
`o.missing` (`__getattr__`), `next(o)`, `for _ in o` / `x, = o` / `any(o)`, `with o:` ... run a PROGRAM method
of `o`'s class when that class (or a base / subclass) defines the dunder. The lowered IR has no call there, so
the frame route #316 infers for a bodyless `val` (a `\trusted` / `\abstract` def with no `#@ assigns`, a
`\trusted` method, an imported marked or UN-marked def) and §7.360's source rule (which reads these positions
as scalar reads) charged nothing to `o`. Red team 41 measured 184 (probe, mode) pairs in the default, typed and
store models PROVED `o.v == 0` after `k(o)`, CPython returns 7 (route #489). A VERIFIED body with the same
positions fails closed (Why3 typing: a record is not an `int`; measured on 13 more probes, incl. element
dunders `1 in [o]`, `[o].count(1)`, `str([o])`).

RULE (allow-list, refuse by default; `_run_pipeline`, after §7.360, on the source of the def): when some class
of the program (this file and every module its imports resolve to) defines a dunder NOT declared `#@ assigns
\nothing`, every bodyless `val` with no `#@ assigns` that the verified code reads (transitively through the
judged bodies) is judged. Each occurrence of a non-scalar root -- a parameter whose annotation is not a scalar
(a container of scalars, `List[int]`, is no root), `*args` / `**kw`, `self` of a method other than `__init__`,
and every name bound from one -- is classified by the dunders its POSITION dispatches to: on the value itself
(S) and on another object that receives it as an argument (A: the other operand's `__eq__(o)` / `__radd__(o)`,
an element's `__eq__` in `1 in [o]`). A container root (`xs: List[C]`, a display `[o]`) dispatches to its
ELEMENTS' dunders (`str(xs)` -> `__repr__`, `xs.count(1)` / `in` -> `__eq__`, `sorted` -> `__lt__`). The
value's classes are the annotated class with every subclass of it and their bases (`self`: the enclosing
class), else every class of the program (an unannotated / `Union` / `Any` root, a field that is not
scalar-typed, a container element). An explicit method call (`o.m()`) and an argument of a program function
are left to routes #316 / #317 / §7.360; an `is` / `is not` / `isinstance` / `id` / `type` is no dunder; any
UNLISTED position counts as every dunder. The occurrence is ADMITTED only when each S dunder is, in every one
of those classes that defines it, `#@ assigns \nothing`, and each A dunder is, in every class of the program,
`#@ assigns \nothing` or a VERIFIED method whose frame names only `self` (it cannot write its argument: rt41's
`max(o, C())` control, where only the other item's `__gt__` runs). Otherwise REFUSED with
`PYCSL-R489-IMPLICIT-DUNDER`: declare the callee's frame with `#@ assigns` (then the user's trusted frame is
read, as for any `\trusted` def), or declare the dunder `#@ assigns \nothing` (verifying such a callee fails Why3 typing). Charging the
dunder's declared frame to the argument instead of refusing is not implemented (an over-refusal, not a gap).

Witnesses `7730`-`7742` (PROVED at base, REFUSED; incl. typed `7736`, store `7737`, imported un-marked `7737`
and marked `7738`, `self` `7735`, alias `7741`, `__getattr__` fallback `7742`) and `7743` (unannotated) / `7744`
(list elements): a Why3 type error at base (fail closed), REFUSED by the rule's arms; controls `7750`-`7754` (a `#@ assigns \nothing` dunder, an int field read with another
class's writing `__eq__`, `max(o, C())`, `o is None`, an imported pure `__len__`). Not covered (named
residuals): a dunder bound as a class attribute (`__len__ = f`) or installed by a metaclass / decorator; a
function the tool AUTO-trusts (a body it cannot lower: not a `val` with an inferred frame here); a `\trusted`
callee WITH a user-written `#@ assigns` (its frame is the user's claim, as in §7.360).

### 7.400 Route #489's judge, refuse by default: every position, every binding, every bodyless val, every returning call, the woven frame (routes #491-#495, run #3)

Red team 42 measured 139 (probe, mode) pairs PROVED `o.v == 0` across a `\trusted` / `\abstract` / imported
callee that runs a writing dunder of `o` (CPython returns 7), each a gap of §7.380's judge: (#491) its
position table omitted the dunders a position runs -- sequence repetition `[1] * o` / `'ab' * o` / `s *= o`
and `round(x, o)` run `__index__`, `isinstance(1, o)` / `issubclass(int, o)` run `__instancecheck__` /
`__subclasscheck__`, `iter(o, s)` runs `__call__`; (#492) the program-dunder table read only top-level `def
__x__` members (`__len__ = _l`, a chain `_m = _l; __len__ = _m`, a `def` nested in a class-body `if True:`);
(#493) a val was judged only when the verified code spelled its name or the suffix `name.rsplit('__', 1)[-1]`
(`''` for `k____init__` / `k____call__`, `it` for `c__do__it`), and a `\trusted` / `\abstract` / imported
`__init__` is no IR function at all; (#494) the upward walk stopped at a program call / method call / listed
builtin, so `len(ident(o))`, `o.me() == 1`, `len(max(o, o))` were never classified; (#495) a dunder was
`pure` when the TEXT `assigns \nothing` occurred in its `#@` lines, while the verifier proves it against the
UNION of its clauses (`#@ assigns \nothing` + `#@ assigns self.v`: 13 probes x hoare / typed / store).

RULE (`_run_pipeline`, §7.380 rewritten in place): (a) on a record of a KNOWN class (an annotated program
class, `self`) every implicit position counts as EVERY dunder of the value's classes (with its subclasses and
bases) -- the position table no longer bounds soundness there; on a value of UNKNOWN class (unannotated / `Any`
/ a field or call result: every program class) a position counts as its own dunders, the table completed for
the rt42 spellings (a BinOp / AugAssign runs `__op__` / `__rop__` / `__iop__` / `__index__` / `__int__` /
`__float__`; `round` arg 2 `__index__`; `iter(o, s)` `__call__`; `x in o` `__contains__` + iteration); only an
attribute read / store (`__getattr__` / `__getattribute__` / `__setattr__` / `__delattr__`, then the field),
`is` / `is not`, `id` / `type` / `callable` of it, the object / name / value arguments of `isinstance` /
`issubclass` (arg 1) / `hasattr` / `getattr` / `setattr` / `delattr`, a binding to a name (tracked as an
alias), a `return` / expression statement, a program-call argument and the first item of a two-item `max` /
`min` are precise; the class argument of `isinstance` / `issubclass` is every dunder; a field read stops the
walk only when the field's type -- the IR's, else the class source (`self.f: T`, `f: T`, `self.f = p` with
`p: T`, a scalar literal; any other store: unknown) -- names only scalars / builtin containers in every class of
the value that declares it; (b) the class's dunders are every binding of the class NAMESPACE, at any depth of
the class body (`def`, `__x__ = name` resolved through alias chains to the def(s) of the same class body,
anything else -- a lambda, a call, a loop / `with` / walrus / import binding, a nested class -- `other`),
inherited through the program bases; (c) a bodyless val with no `#@ assigns` is judged when the verified code
(or a judged body) reads its name or its METHOD name (`do__it`), and a constructor-side one (`__init__` /
`__new__` / `__post_init__` ...) or `__call__` when its class (or a program subclass) is CALLED -- incl. each
`\trusted` / `\abstract` / imported `__init__`, which is no IR function; (d) a call of a program def / class /
method whose return annotation names more than scalars / builtin containers, a builtin that may return its
argument (`max`, `min`, `next`, `iter`, `abs`, `round`, `getattr`, ...), a container method that may return an
element, an operator, a unary `-` / `+` / `~`, a rich comparison, a subscript and a walrus continue the walk
from that node with a value of unknown class (a builtin container's `items` / `keys` / `values` / `copy` keeps
the element view); (e) a dunder is `pure` iff its WOVEN frame (the IR's parsed `assigns`) is `\nothing` alone
(the `#@` clauses one by one only for a def with no IR entry), and a function of the woven IR whose `assigns`
mixes `\nothing` with another clause is REFUSED with `PYCSL-CONTRADICTORY-ASSIGNS` (the bodyless-val emitter
already refused it for a val, route #103; the frame is self-contradictory, and the fix is to delete `assigns
\nothing`). The message names the position route #489's walk ended at.

Witnesses `7800`-`7817` (PROVED at base, REFUSED; `7816` typed, `7817` store); controls `7820`-`7826` (an int
field as repetition count -- REFUSED at base by the single-class field quirk, now PROVED; an alias to a pure
def; a judged `\trusted` `__init__` over a pure `__len__`; a scalar-returning program def and method; a
`\nothing`-alone dunder; the advice followed: `\nothing` deleted and the callee's frame declared). The cost is
an over-refusal: a `\trusted` body that uses a record of a known class in any implicit position is refused as
soon as that class has ANY dunder not declared `#@ assigns \nothing`, even one that position never runs.
Residuals (named): a value of unknown class is judged by the (completed) position table, not every dunder; a
dunder val is reached only through an implicit position or an explicit name read.

### 7.410 A callee's implicit raise summary is refuse-by-default: any call not known never to raise carries every modelled exception (route #496, run #4)

Route #178 (§ its comment in `module6_whyml/functions.py`) gives each same-file / `\trusted` / imported function a
summary of the implicit exceptions its body may raise where its own context does not check them, and refuses a
caller whose `#@ no_exception` claim -- or whose exception HANDLER (route #171's widening) -- relies on freedom
from one. That summary was an ALLOW-LIST of raising operations (subscript, `int()` / `float()`, an unpack, `<<` /
`>>`, division in a bodyless callee), so every other builtin or library call in a callee lowered to a `val` with
no `raises` and the caller's handler was dead in the model. Red team 44 measured 96 (probe, mode) pairs PROVED
(76 probes; hoare / typed / store): `#@ ensures \result == 1` `f(s): try: return g(s) except ValueError: return
2` with `g(s): y = s.index("z"); return 1` (CPython 2), and the same through `str` / `list` / `tuple` / `range`
`.index`, `chr`, `split("")`, `partition("")`, `math.*`, `divmod`, `pow(_, _, 0)`, `str.format`, `encode` /
`decode`, `operator.*`, `statistics`, `random.choice`, `datetime`, `next`, an un-contracted void callee, depth 3,
`\trusted` and imported callees, a keyword call, a call in a condition, `try ... else`, nested handlers.

RULE (route #161's polarity, inline in the route #178 summary): a call in a callee body is admitted (adds nothing
to the summary) only if it is (i) a function, method or class of the program (its own summary is joined
transitively; a program function NAMED as an argument -- `map(g, xs)` -- counts as a call of it, at the callee
and at the caller), (ii) a builtin exception constructor (`raise ValueError(..)`) or `super()`, or (iii) on #161's
never-raises list with the partial cases of #66 / #72 / #160 syntactically excluded: `chr` of a literal in
`[0, 0x110000)`, `range` with a nonzero literal step (or fewer than three arguments), `pow(b, e)` with a literal
`e >= 0` or nonzero literal base and no keywords, one-iterable `min` / `max` only with `default=` or a non-empty
display, `bytes` / `bytearray` of nothing or one non-negative literal, `dict` of nothing or a dict display,
`zip` without `strict=`, `split` with no separator or a non-empty literal one, `update` of a name or dict display.
Any other call (incl. a call of a computed callable) carries EVERY modelled implicit exception (`KeyError`,
`IndexError`, `ValueError`, `ZeroDivisionError`, `StopIteration`) minus what the callee itself declares
`#@ no_exception` for; a caller whose active context meets that set is REFUSED with
`PYCSL-R496-CALLEE-UNLISTED-CALL`, the message naming the call and the chain. `StopIteration` joins route #178's
active set. Repair: declare `#@ no_exception` for the exceptions on the callee (its calls are then judged by #161
there), or remove the handler / the claim.

Witnesses `7847`-`7864` (PROVED at base, REFUSED; `7860` typed, `7861` store, `7859` / `7860` imported through
`multi_file_lib/u3_h496a.py` / `u3_h496b.py`); controls `7870`-`7875` (never-raising methods, literal partial
builtins, a program chain with a constructor, a callee declaring `#@ no_exception ValueError` over `chr(n)` under a
range `requires`, a handler around a never-raising helper, an explicit `raise ValueError(..)` caught). Residuals
(named): an int-to-decimal-string conversion (`str(x)`, `print(x)`, f-string) past 4300 digits (route #281's
`int_str` row) and `round` of a NaN in a callee are not summarised. (The former residual "a method call whose
tail names any program method is admitted as that method" is closed by §7.501: the callee is resolved.)

### 7.498 An identity test whose operand may be a freshly computed value is refused (route #498, run #4)

Module 5 narrows every `is` / `is not` to `==` / `!=` (keeping the `py_is` marker) and Module 6 keeps that
VALUE equality except against a bool literal (§ route #42, `PYCSL-R42-IS-BOOL-SINGLETON`) and over a
value-typed literal or annotated name (route #52, `PYCSL-R52-IS-VALUE-TYPED`). A value COMPUTED at run time
is a new object whose identity CPython does not tie to its value: red team 44 measured `(n + 1) is (n + 1)`,
`(n * 2) is (n + n)`, `-n is -n`, `s + "x" is s + "x"`, `s[0:2] is s[0:2]`, `s.upper() is s.upper()`,
`"".join([s, s]) is "".join([s, s])` and `a = n + 1000; b = n + 1000; a is b` PROVED `\result == True`
(CPython False for n = 1000 / s = 'ab'), and a `no_exception \all` division guarded by such a test (14
witnesses).

RULE (refuse by default; `_run_pipeline`, before Module 6, on every function and class declaration --
`__init__` body, field defaults, constants -- of the IR): an `is` that is not
against a singleton (`None` / `Ellipsis` / `NotImplemented`; a bool literal is route #42's), not of one name
with itself or with a chain of single plain assignments `b = a` of it, and not one route #52 refuses, is
REFUSED with `PYCSL-R498-IS-ON-FRESH-VALUE` when either operand MAY BE FRESH: an arithmetic / bitwise /
concatenating operator, a unary `-` / `+` / `~`, a slice, an f-string, a container display / comprehension /
lambda / literal, any call except `type(x)` / `isinstance` / `issubclass` / `hasattr` / `callable` / `bool`
(method calls included), an index of a str / bytes (or of a fresh receiver), an if-expression / `and` / `or`
with a fresh arm, a parameter not annotated with a class (`Any`, unannotated, `bool`, a value type, a
`Union` / `Optional`), and a local bound by anything but plain assignments of non-fresh values (a loop /
unpacking / `with` / `except` / walrus / augmented binding counts as fresh). A comparison or `not` (a bool
singleton), an attribute / field read, an outer name (global, class, builtin, `self`) and a class-typed
parameter are not fresh. Write `==` if you mean equality.

Witnesses `7900`-`7907` (PROVED at base, REFUSED), `7908` (`object`-annotated parameters under `requires a ==
b`: NOT PROVED at base, refused by the parameter arm) and `7909` (store model: a Why3 type error at base,
now refused by name); controls `7915` (`x = C.A; y = x;
z = y; z is x` on an enum member), `7916` (`c.a is c.a`, two reads of one stored field). Over-refusal by design: `a = 10 ** 30; b = 10
** 30; a is b` (True in CPython only by constant folding, rt44 control k52114) is refused. Named
residuals: a field or module global that STORES a computed int / str (`self.a is self.b`) is read as an
existing object; an element of a list / dict read by index is not fresh unless its receiver is.

### 7.499 A constant `exec(...)` is spliced only where it runs against the real namespace (route #499, run #4)

`frontend/exec_splice.py` replaces a constant `exec("<src>")` expression statement by the parsed statements
(07-1839 P5b), which is inline-equivalent at module level and in a module-level class body. Inside a
FUNCTION, CPython (PEP 667) runs the text against a SNAPSHOT of `locals()`: a name it binds is never seen by
the function. Red team 44 measured `x = 1; exec("x = 2"); return x` PROVED `\result == 2` (CPython 1), on a
parameter, augmented, multi-statement, tuple-unpacking, list and str rebinding, and `d = 0; exec("d = 5");
return 10 // d` PROVED `no_exception \all` (11 witnesses). The old corpus `0642` (`exec("x = 5\ny = x + 1");
return y` in a function, `\result == 6`) was the same false proof: CPython raises NameError.

RULE (refuse by default; `_run_pipeline`, before the splice, on the woven AST): a constant exec in a
function scope whose text parses and passes the splice whitelist is admitted only when every name it binds
(an assignment / augmented / annotated / unpacking target that is a name, a walrus) is named NOWHERE else in
the function (its snapshot binding is then unobservable) and the function reads no namespace (`locals` /
`vars` / `dir` / `globals` / `eval` / another `exec`), and the text contains no lambda /
comprehension (free names resolve in the globals) and no `yield` / `await`; a constant exec in a class body
nested in a function is refused (it cannot read the function's names); a constant exec passing `globals=` /
`locals=` by keyword is refused at every scope (the splicer reads only the positional text). Otherwise
REFUSED with `PYCSL-R499-EXEC-IN-FUNCTION-SCOPE`. Element / attribute stores and calls (`exec("xs[0] = 5")`)
mutate the same objects in CPython and stay spliced. A text the whitelist rejects or that does not parse
keeps the splicer's own refusal (`0643`, `1756`, `1757`, `1802`).

Witnesses `7920`-`7924`, `7926` (the module-level keyword form), `7927` (class body in a function)
(PROVED at base, REFUSED) and `7925` (typed model: a Why3 type error at base, now refused by name); `0642`
is now expected FAIL. Controls `7930` (`exec("xs[0] = 5")` in a function), `7931` (a module-level
`exec("y = 6")`), `7932` (`exec("t = 2")` binding a name the function never mentions). Cost: an honest class-in-function exec that reads no enclosing name is refused.

### 7.500 A method spliced by `ir_inline` may `return` only as its last top-level statement (route #500, run #4)

`frontend/ir_inline.py` splices a method called on a module-level global instance into the caller and
refused a non-tail `return` only among the method's TOP-LEVEL statements, so a `return` nested in an `if` /
loop / `with` / `try` / `match` was spliced as a return of the CALLER: red team 44 measured `r = g.m(5);
return r + 10` PROVED `\result == 1` (CPython 11), a field write after a statement-position call skipped,
two nesting levels, and a method calling such a method on `self` (6 witnesses).

RULE (`ir_inline._expand`, refuse by default): every `Return` node at ANY depth of the method body is
refused with `PYCSL-R500-INLINE-NESTED-RETURN` except the single top-level tail `return` the splice binds.
Call the method on a LOCAL instance (its contract is used) or write one tail `return`.

Witnesses `7940`, `7941`, `7943` (PROVED at base, REFUSED) and `7942` (a `return` in a `for`: a prover
Timeout at base, now refused by name); controls `7946` (one tail `return`, a result variable
assigned in each branch), `7947` (the nested-return method on a LOCAL instance, by contract).

### 7.501 Route #496's admission resolves the callee: a bare name shared with a program def / method / class admits nothing (route #501, run #4)

Route #496 (§7.410) admits a call in a callee body when it is a function, method or class of the program. The
test matched the call BY NAME against every program name, its `__` / `.` tail and the lower-cased class names,
so a benign program name equal to a raising builtin's admitted it: red team 45 measured PROVED (CPython 2) a
callee's free `divmod(5, n)` next to a method `K.divmod` or a class `Divmod`, `math.sqrt(n)` next to a free
`def sqrt`, `s.index("z")` on a `str` next to a method `K.index`, and `"{x}".format(n)` next to a method
`K.format`, each inside a caller's `try ... except` of the raised exception.

RULE (inline in the route #178 / #496 summary, refuse by default): a call is a program call only when the callee
is RESOLVED. A free call `n(...)` is admitted only if `n` is exactly a module-level (non-method) def or a class of
the program. A method call `r.m(...)` (or `C.m(...)`, or `e.m(...)` on an expression receiver) is admitted only
if its receiver resolves to a program class `C` -- a class name (not shadowed by a local), `self` in a method of
`C`, a parameter or local whose declared type is `C` / `Optional[C]`, a local bound ONLY by `= C(...)` or `=
d(...)` of a def annotated `-> C` (any other binding of the name, a loop / unpack / `with` / walrus target,
leaves it unresolved), or a `C(...)` / `d(...)` receiver -- and `C` defines `m` or inherits it from a program
base; `super().m(..)` in a method of `C` resolves to a program base of `C` (transitively) defining `m`. Anything else is judged by #496's never-raises lists (and otherwise carries every modelled exception,
refused as `PYCSL-R496-CALLEE-UNLISTED-CALL`). The transitive join of program summaries keeps its
over-approximating tail match (every override of `m` is joined). This closes #496's named residual "a method
call whose tail names any program method is admitted".

Witnesses `7950`-`7954` (PROVED at base, REFUSED), `7960` (a local `k: str` calling `k.index` beside a class `K`:
the `k__index` spelling), `7961` (a local rebound from `K()` to a `str`); controls `7970` (program methods named
`index` / `format` on a `K` parameter and on `K()`, under ValueError / KeyError handlers), `7971` (`self` calls and
a free `def sqrt` called by name under a ValueError handler).

### 7.502 A callee's lambda / comprehension / generator expression joins its implicit raise summary (route #502, run #4)

Routes #177 / #285 / #287 refuse a lambda or comprehension whose element operations may raise only when the
function ITSELF claims the exception: those bodies are lowered WITHOUT per-element obligations. Route #178's
callee summary assumed a same-file callee's divisions are checked in its own body (true of a plain `10 // n`),
so a division inside a callee's lambda / list / set / dict comprehension / generator expression was neither
checked there nor summarised: red team 45 measured PROVED (CPython 2) `g(xs): ys = [10 // v for v in xs];
return 1` inside `try: return g(xs) except ZeroDivisionError: return 2`, and the `sorted` key lambda, `sum` of a
generator expression, `%` and dict-comprehension forms.

RULE (inline in the route #178 summary, driven by `exception_model.TRIGGERS` / `TRIGGER_EXPR_SHAPES` exactly as
#285): for every `Lambda` / `ListComp` / `SetComp` / `DictComp` / `GenExp` node of ANY callee, every row whose
shape occurs anywhere under it adds its exceptions to the callee's summary, a tuple generator target adds
`ValueError`, and a row with no census shape adds its exceptions to every such node (fail-closed for a row added
later). Only `/` `//` `%` (`div` / `mod`) by a non-zero numeric literal and `**` of a non-negative int literal
are exempt (they cannot raise `ZeroDivisionError`). Minus what the callee declares `#@ no_exception` for (#177
then judges the node there), a caller whose claim or handler meets the set is REFUSED with
`PYCSL-R502-CALLEE-COMPREHENSION-OBLIGATION`, naming the operation and the chain. Repair: remove the handler or
drop the exception from the claim (a ZeroDivisionError handler around a same-file callee that divides is
rejected by Why3 anyway: "raises unlisted exception", measured on a guarded explicit loop).

Witnesses `7955`-`7959` (PROVED at base, REFUSED), `7962` (`map` of a dividing lambda), `7963` (a set
comprehension `%` at depth 2), `7964` (a method's list comprehension reached through a `C` parameter); controls
`7972` (literal divisors / non-negative literal power in comprehensions, a key lambda without division, under a
ZeroDivisionError handler), `7973` (a dividing comprehension under an unrelated KeyError handler).

### 7.503 An alias's identity exemption needs a root bound once (route #503, run #4)

Route #498 (§7.498) exempts an `is` between a name and a chain of single plain assignments `b = a` of it.
The chain was followed to the NAME `a`, not to the object `a` held when `b = a` ran: red team 45 measured
`a = n + 1000; b = a; a = n + 1000; return a is b` (and the `is not` twin) PROVED (CPython False / True; 2
witnesses); a rebound parameter (`b = a; a = b + 0`) is the same class.

RULE (refuse by default; in route #498's pass in `_run_pipeline`): one name with ITSELF (`a is a`) stays
exempt; a common root of the two alias chains exempts the site only when the root is bound once for the
whole call -- a parameter never rebound, an outer name the function never binds, or a local with exactly one
plain assignment. Otherwise the site is judged by route #498's freshness walk and, when an operand may be
fresh, REFUSED with `PYCSL-R503-IS-ALIAS-ROOT-REBOUND`. (A root bound once inside a loop needs no extra arm:
an alias read in a later iteration is bound twice or not definitely assigned, route #264.) Write `==`, or
give the rebound value its own name.

Witnesses `7980`, `7981` (PROVED at base, REFUSED), `7982` (a rebound unannotated parameter: NOT PROVED at
base, refused by name); controls `7990` (a root bound once, an unrelated name rebound), `7991` (`a is a` on a
rebound name).

### 7.504 An identity test on a value read from a field is judged by the field's declared type (route #504, run #4)

Route #498 (§7.498) read every attribute / field as an existing object (its named residual): red team 45
measured `self.a = n + 1000; self.b = n + 1000` then `k = K(n); return k.a is k.b` PROVED `\result == True`
(CPython False), and on a class-typed parameter whose int fields are equal (`k.b = int("1000")`; 2
witnesses).

RULE (refuse by default; in route #498's freshness walk): two reads of ONE stored location (the same path
of names and attribute reads, no call: `c.a is c.a`) are one object and exempt. Any other field / attribute
operand -- directly or through the locals bound to it -- is an existing object only when it is a class
constant / enum member (`Color.RED`: an attribute of a program class name; a class-body binding read through
an instance) or when EVERY declaration of that field in the program's classes (the receiver's class when its
type is known) names a program class or `Optional` of one. A value-typed, container-typed, unannotated or
undeclared field (a module attribute too) may store a freshly computed value: REFUSED with
`PYCSL-R504-IS-ON-STORED-VALUE`. The other operand being an outer name is no exemption (`k.a is G` with `G =
1000` PROVED at base, CPython False), except a module-level name bound once to `object()` -- in this file or
imported by `from M import X`, M on the program's path -- and never rebound or named `global`: a sentinel
whose `__eq__` is identity is a singleton operand. Write `==`.

Witnesses `7984`, `7985`, `7986` (locals bound to the two field reads), `7989` (a field against a module-global
literal) (PROVED at base, REFUSED); control
`7992` (`k.a is k.a` on a local instance; `7916` keeps `c.a is c.a` on a parameter). Named residual: a
module global holding a computed int / str (measured opaque, NOT PROVED, at e5237469f); a computed class
constant is likewise opaque.

### 7.505 A method spliced by `ir_inline` may use `self` only as a field receiver or a `self.m(...)` head (route #505, run #4)

`ir_inline._substitute` renames the receiver only in `FieldGet` / `FieldAssign` / `FieldAugAssign` objects
and in `self.X(...)` call heads; any other `self` kept its spelling and, spliced into a caller METHOD, named
the caller's receiver: red team 45 measured `m(self): return getv(self)` spliced into `run(self): return
g.m()` PROVED `c.run() == 2` on `c = C(2)` (CPython 1, `g.v`; 1 witness). Renaming it to the global would
pass the global as a value, which inline.md Phase 3 (`_check_no_aliasing`) forbids.

RULE (`ir_inline._expand`, refuse by default, Phase 3's polarity): a spliced method that reads `self` as a
value, calls `self`, rebinds `self`, or holds `self` in any node the renaming does not cover is REFUSED with
`PYCSL-R505-INLINE-BARE-SELF`. Pass the fields the method needs, or call the method on a LOCAL instance.

Witnesses `7987` (PROVED at base, REFUSED), `7988` (`x = self; return x.v`: a Why3 type error at base, now
refused by name); controls `7993` (the field passed, `getv(self.v)`), `7994` (`getv(self)` on a LOCAL
instance, by contract).

### 7.506 A trigger site must reach its own lowering, whatever expression surrounds it (route #506, run #4)

Every implicit-exception obligation of `exception_model.TRIGGERS` (§ the `pycsl-exception-model` skill) is
attached by the expression HANDLER of the operation -- `_handle_binop` (`/` `//` `%` `<<` `>>` `**`),
`_handle_subscript` (list / str index, dict read), `_handle_call_expr` (`divmod`, `chr`, `str` / `repr` /
`format` / `print` of an int, `.pop`, `.index`, `.format`), `_handle_fstring_expr` (int parts, format specs) --
and, in a body with no claim, the raising `pycsl_div` / bounds-checked access that makes a caller's handler
live comes from the same handler. A surrounding expression modelled by size or truth only, or not at all,
never asks that handler, or asks it and discards the text. Executors u5 / u7 measured at cc65d3ba6, PROVED
while CPython raises: under `#@ no_exception ZeroDivisionError` / `\all`, `s = {10 // n}`, `t = (1, 10 // n)`,
`(10 // n,)`, `((10 // n, 1), 2)`, `[*xs, 10 // n]`, `(*xs, 10 // n)`, `len([10 // n])`, `len((10 // n, 1))`,
`isinstance(10 // n, int)`, a dict display inside a `try`, the receiver of a method call (`d["b"].upper()`,
`xs[3].size()`), and -- under a NAMED claim, where a Python `assert` is a no-op -- `assert 10 // n >= 0 or
True`; the same for `%`, `/`, `<<`, `**`, `xs[i]`, `d[k]`, `'ab'[i]`, `str(<big int>)`, `f"{n:s}"` (12 rows x
42 positions: 156 lost cells); and with no claim the same callee made a caller's `except ZeroDivisionError`
arm dead (`f` proved `\result == 1`, CPython 2 / 0).

RULE (refuse by default; inline in `_run_pipeline` around `transpiler.transpile()`, mirror twin `\trusted`, no
new def, no axiom, emission byte-identical): the four handlers, `_maybe_emit_no_exception_assert` and
`_emit_function_block` are observed through instance attributes; every PROGRAM-context lowering (not
`_in_spec`, not an invariant) is recorded with its IR site key (the node's canonical dict without the
emitter's `_`-prefixed annotations) and the trigger rows its handler consulted itself. After emission, every
SITE -- an expression of a `TRIGGER_EXPR_SHAPES` shape in an executable position of a verified def's body
(the last def of a name; not a loop invariant / variant, ghost or `#@ assert` code; not the receiver of an
element store / `del` / slice store, which the statement lowers; a comprehension / lambda body is route
#177 / #285 / #287's census) -- that is RELEVANT must be lowered: its own lowering's text occurs in the def's
emitted block at least as often as the site occurs, or its nearest kept handler ancestor consulted one of
its rows (`ord(s[i])`: the call states the index bound), or it is the receiver of a kept 2-D subscript that
names it. RELEVANT: one of its exceptions is claimed by the def (declared or REACHED, route #460), or may be
caught -- a `try` of a VERIFIED def catches it (`handler_catches`; a bare / dotted / non-builtin class or a
`finally` that returns / breaks / continues catches everything) and the def holds that `try` or is called
(transitively, by last name component) from its protected body. Else `PYCSL-R506-TRIGGER-SITE-UNLOWERED`.
Repair: bind the operation to a local in a plain statement (`q = 10 // n` then `s = {q}`).

Witnesses `8000`-`8019` (PROVED at base, REFUSED; `8016` typed / `8017` store: a Why3 error of the mode at
base, now refused by name); controls `8020`-`8029` (bound first, dict / list displays and an `\all` assert
that keep their elements, a bound division in a `try`, a size-only display without trigger, a dropped
element no handler can observe, a tuple of names, the advice applied to 5044 / 6783). Refused by design
(honest only through guards / data the model never checks; expected PASS -> FAIL): `5044`, `6024`, `6025`,
`6783`, `6785`. Residuals (named): a site whose lowered text also occurs because an identical site of the same
def is lowered twice is counted kept; a callee reached only through an implicit dunder call is not on the
handler's call graph.

### 7.507 Under `no_exception \all`, every OverflowError obligation reaches its lowering; an int -> float promotion is refused (routes #507 / #508 / #509, run #4)

Route #506's census covers the `exception_model.TRIGGERS` rows. The OverflowError obligations that
`no_exception \all` alone carries -- route #414 (`s * n`, `[x] * n`: the count is a Py_ssize_t;
`len(range(..))`) and route #417 (`list(range(..))` / `sorted(range(..))`; `float(<int>)`: |n| <= DBL_MAX) --
are inline asserts in `_handle_binop` / `_handle_call_expr`, and an expression modelled by size or truth
(`(any T)`) never asks those handlers. Red team 46 measured at e9d24a6c2, PROVED while CPython raises
OverflowError at n = 10**20 / 10**400: (#507, 71) `{"ab" * n}`, `(1, [0] * n)`, `(x,)`, nested / starred
displays, `len([..])`, `sorted((..))`, a dict display value, `id` / `type` / `max` / `reversed` of a display,
in the claimed def, a REACHED callee (#460) and a method; (#508, 29) an int -> float promotion in an
arithmetic operation (`n * 1.5`, `n + 0.5`, `0.5 * n`, `x + n`) -- it has NO obligation anywhere: the plain
form only failed as a Why3 type error and, inside an `(any T)` display, proved; (#509, 34) the same
operations in a comprehension / generator element, condition or iterable or a lambda body, whose census
(#177 / #285 / #287) refuses the Phase-1 rows only.

RULE (refuse by default; inline in `_run_pipeline` right after route #506's census, mirror twin `\trusted`,
no new def, no axiom, emission byte-identical). In every verified def judged under `\all` (declared, or
REACHED, route #460) each operand is read at a numeric KIND -- a small int literal (|v| <= 2**63 - 1, or a
bool), an int, a float, a known non-number, or unknown -- from the IR symbol table, the SOURCE annotations
(the table erases `List[int]` to `list`; a name two same-named defs disagree on is unknown), comprehension
targets (`range(..)` -> int, a typed container -> its element kind) and unannotated locals bound only by
plain / augmented assignments of one kind (any other binding form leaves them unknown):
- `PYCSL-R508-INT-FLOAT-PROMOTION-UNMODELLED`: an arithmetic operation (`+ - * / // % **`) with a float
  operand and an int or unknown operand, WHEREVER it occurs. Repair: state the bound and convert explicitly
  (`#@ requires` a bound, then `float(n)`, which owes |n| <= DBL_MAX), or keep one numeric type.
- `PYCSL-R509-COMPREHENSION-OVERFLOW-SITE`: inside a comprehension / generator / lambda, an OverflowError
  SITE -- `a * b` unless an operand is a small int literal or both are ints / both floats; `len` / `list` /
  `sorted` of `range(..)`; `float(x)` of anything but a float / small literal / str. Repair: an explicit loop.
- `PYCSL-R507-OVERFLOW-SITE-UNLOWERED`: elsewhere, a SITE whose handler lowering (route #506's observation)
  does not occur in the def's emitted block at least as often as the site occurs. Repair: bind the operation
  to a local in a plain statement (`t = "ab" * n` then `v = {t}`).
Comparisons (`n < x`, `n == x`) are exact in CPython and are not sites.
A `list` / `sorted` / `float` site lowered by a statement-level form (`for x in sorted(range(n))`) counts as
kept when its route #417 tag `[@r417_<h>]` is in the def's block as often.

Witnesses `8050`-`8065`, `8067`-`8074`, `8076` (PROVED at base by default -- `8076`, the plain `w = n * 1.5`,
was a Why3 type error -- now REFUSED by name; `8066` typed / `8075` store: a Why3 error of the mode at base);
controls `8080`-`8087` (bound first in plain statements, small literal counts, same-kind int / float
arithmetic in displays, comprehensions over a `List[int]` and float literals, `float(n)` under a bound then
float arithmetic, a reached callee binding first under its own requires, an inferred-int local, int / float
comparisons; PROVED at base and HEAD). All 134 red-team-46 witnesses (`witnesses-r507/` 71, `-r508/` 29,
`-r509/` 34) are refused under default / typed / store. Residuals (named): an OverflowError raised for a
huge int with NO claim is not modelled as a raise, so a caller's `except OverflowError` arm stays dead
(OverflowError is not a nameable `no_exception` exception); `int(<float>)` (inf / nan) and float `**`
overflow are outside this table; the kind reader trusts declared annotations (a `x: int` bound to a float at
run time is read as an int).

### 7.510 A PEP 695 `type` statement and a type-parameter list bind their names: a value read of such a name is refused (routes #510 / #517, run #4)

`type X = T` binds X (in its scope, when it runs) to a `typing.TypeAliasType`, and `def f[K](..)` /
`class C[K]:` bind K inside the def / class to a `typing.TypeVar`. Neither binding was seen by any binding
walk: `pure_ast` builds the alias target with Load context and the lowering drops the statement, and the
binding-site censuses (route #132's `_nb_sites`, `module_collect`'s constant folder, Module 5's local
collectors, the program-call resolver) record def / store / import / except / match binders only. Red team
47 measured, PROVED while CPython reads the alias / TypeVar: (#510, 34) `K = 5` then `type K = int` -- after
the def, in an `if` / `try` / `for` body, generic `type K[T]`, function-local -- under `ensures \result == 5`
over `return K`, `no_exception \all` over `n // K`, a `#@` contract naming K; `type n = int` over a parameter,
local, loop variable, callee (`type g = int`), module object, `self`, a builtin (`type len = int`); (#517, 10)
`def f[K](n): return n // K`, `def f[S](): return len(S)`, `def f[g](n): return g(n) + 1`, `def f[len](s)`,
`def f[K: int]()`, `class C[K]:` around a method reading K, `def m[K](self)`.

RULE (refuse by default; inline in `_run_pipeline` right after route #215's check, i.e. after `_ir_resolve`
so the TY3 monomorphization refusals fire first; mirror twin `\trusted`, no new def, no axiom, emission
byte-identical). Neither object is modelled, so such a name may be read only where CPython reads it as a
TYPE: a parameter / return / variable annotation, a type alias's value, a type parameter's bound, the
subscript of a class base (`class C[T](Base[T])`).
- `PYCSL-R510-TYPE-STATEMENT-NAME-READ`: a Load (or an augmented-assignment target), anywhere in the file,
  of a name some `type` statement of the file binds, or that name as an identifier of any `#@` line;
  for a `type` statement directly in a class body (it rebinds a class attribute), also an attribute read
  `<e>.X` (code or `#@`). Name-keyed over the whole file. Repair: rename the alias (`type KT = int`).
- `PYCSL-R517-TYPE-PARAM-NAME-READ`: such a read of a type-parameter name inside its def / class
  (decorators, defaults and nested scopes included) or in the `#@` lines from the def's / class's contract
  block through its last line. Repair: rename the type parameter (`def f[T](...)`).
One exemption, exact in CPython: the statement `assert X is not None` where X has no binding but `type`
statements (a TypeAliasType is never None; python-reference `0183` / `0212`).

Witnesses `8100`-`8116`, `8120`-`8127` (PROVED at base, REFUSED), `8117` (a class-body `type K` read as
`C.K`: PYCSL-R325-OPAQUE-INT-FALLBACK at base, now refused by name) and `8128` (a def's own contract naming its type parameter);
controls `8130` (an alias read only in annotations), `8131` / `8134` (the advice: the alias / class type
parameter renamed), `8132` (a local alias annotating a local, `assert V is not None`), `8133` (a generic def
never reading T, beside the module constant its body reads). All 44 red-team-47 witnesses
(`witnesses-r510/` 34, `witnesses-r517/` 10) are refused under default / typed / store. Residuals (named): a
dependency module's `type K` rebinding a name this file imports (`from dep import K`, `dep.K`) is not judged
here (measured NOT PROVED at base, red team 47 g811 import_*); a module-level `type K` before `K = 5`
(CPython reads 5) is refused (name-keyed, not flow-sensitive).

### 7.511 A `class` / `type` statement inside a function binds a name the whole file leaves free (route #511, run #4)

A `class` (or `type X = ...`) statement in a function body is not lowered as a statement: the class is modelled
as ONE program-wide class under its bare name, and a read of the name resolves through the module-constant,
function, parameter and local tables first. Red team 47 measured PROVED (CPython violates) `K = 5`, then
`class K: pass; return n // K` under `no_exception \all` (lowered `n // 5`; CPython TypeError), `return K`
under `ensures \result == 5`, a `@dataclass` / attribute-bearing / method-local class, `class g: pass; return
g(n) + 1` over a program `g`, `class n` over the parameter `n`, `x = 5; class x: pass; return x` (17 witnesses);
the repair's own audit added a local `type K = int` (PROVED at base) and, NOT proved at base but resolved
to the wrong binding, two functions each with their own `class Q`, a local `class Q` beside a module `class
Q`, and a local class read from ANOTHER function (CPython NameError).

RULE (`Module3_Weaver.process`, both pipelines, refuse by default): a `class` / `type` statement whose nearest
enclosing scope is a function is admitted only when its name has NO other binding site anywhere in the file
(def / class / parameter / lambda parameter / any store target / import / except-as / match capture / `global`
/ `nonlocal`) and, unless it names a builtin (route #386 owns those), is read nowhere outside that function.
Otherwise REFUSED with `PYCSL-R511-LOCAL-CLASS-NAME-NOT-UNIQUE`. Give the local class a name used nowhere
else in the file, or move it to module level. Route #460 refuses the nested-`def` twin; route #264 a read on a
path where the statement did not run.

Witnesses `8140`-`8147` (PROVED at base, REFUSED) and `8148` / `8149` (not proved at base, REFUSED by name); controls `8150` (a uniquely named local class constructed and read in its
function), `8151` (local classes under distinct names beside a module constant), `8152` (a uniquely named local
`type` alias). Cost: two honest functions that each define a local class under the same name are refused.

### 7.518 A walrus in a definition-time expression is refused (route #518, run #4)

The defaults and keyword-only defaults of a `def` / `lambda`, the decorators of a `def` / `class` and the bases
and keywords of a `class` are evaluated in the ENCLOSING scope when the definition runs, so a walrus there
rebinds an enclosing name; the binding-site walks of the weaver (routes #118, #132, #377, #463) skip a lambda
whole. Red team 47 measured PROVED `K = 5`, `ensures \result == 5` over `return K`, then a module-level `_l =
lambda a=(K := 0): a` (CPython 0), with keyword-only defaults, a lambda in a list display, before or after the
claimed def, and `len(S)` after `lambda a=(S := "abc"): a` (14 witnesses); the repair's audit added (PROVED at
base) a lambda in a lambda's default and `lambda a=(inc := dec): a` rebinding a program FUNCTION (`inc(3) == 4`,
CPython 2), and (not proved at base) a class-body lambda rebinding a class constant.

RULE (`Module3_Weaver.process`, every scope, both pipelines): a `NamedExpr` anywhere inside one of those
expressions is REFUSED with `PYCSL-R518-WALRUS-AT-DEFINITION-TIME`. Bind the value in a statement of its own
before the definition (`T = 0`) and use that plain name in the default.

Witnesses `8160`-`8164`, `8166` (PROVED at base, REFUSED), `8165` (not proved at base, REFUSED by name) and
`8167` (the `def`-default twin, refused before by route #350); controls
`8170` (a plain-name default and a walrus in the lambda BODY, which binds the lambda's own local), `8171` (the
binding moved to its own statement).

### 7.512 Route #507's census refuses by default: byte counts, any range value, element kinds by position, unknown operands, immediately-invoked lambdas (routes #512-#516, run #4)

Route #507 (§7.507) read its sites by SPELLING and its operand kinds optimistically. Red team 47 measured at
ef45a0426, each PROVED `no_exception \all` while CPython raises: (#512, 31) `bytes(n)` / `bytearray(n)` /
`bytes([v])` in a dict display, a dict store, a dict comprehension or a field initialiser (erased to `(any int)`),
and the faithful plain `Array.make n 0`, which owed only `n >= 0` (OverflowError past 2**63-1, ValueError for a
negative count or an element outside 0..255); (#513, 10) a comprehension over a `Dict[K, V]` / `Mapping` / a
`Tuple[A, B]` read every target at the kind of the LAST type argument (`[k * 0.5 for k in d]` over
`Dict[int, float]`); (#514, 17) a range bound to a name, reached through a walrus / if-expression / list element,
or unpacked (`r = range(n); len(r)`, `len(rs[0])`, `(*range(n),)`), lowered to `iter_length` with no Py_ssize_t
bound; (#515, 37) an immediately-invoked lambda `(lambda m: "ab" * m)(n)` / `(lambda m=n: m * 0.5)()`, erased to
`(any int)` and its body never seen; (#516, 22) an arithmetic operation whose two operands have UNKNOWN kind
(`for k, v in d.items(): w = k * v`, `p.ga() * p.gb()`, `p.a * p.gb()`): #508 fired only on a known float.

RULE (refuse by default; inline in `_run_pipeline` in route #507's block, mirror twin `\trusted`, no new def, no
axiom). Under `\all` (declared, or REACHED, route #460):
- KINDS (#513 / #516). A declared type is read at its TOP-LEVEL arguments: iterating a mapping yields its FIRST
  argument, a subscript its value (last of two); `Tuple[A, ...]` is A, `Tuple[A, B]` the common kind or unknown;
  `bytes` / `bytearray` / `range` elements are ints, `str` elements strings; `Optional[X]` / `X | None` is X (its
  None raises TypeError, never OverflowError). The targets of `for k, v in d.items()` / `.keys()` / `.values()` /
  `enumerate(xs)` take the declared kinds. A method result / field read is typed through its RECEIVER's class
  (`self` in a method, a local / parameter declared with the class, a local bound only to `C(..)`, the class
  name itself for a class constant), inherited members included: the return / field annotation, or -- for an
  undeclared field -- the kind every store of it agrees on (a literal, a declared parameter, `self.f +/- <int
  literal>`; a store through another receiver anywhere leaves it unknown). A def of the file (at any depth) or of
  an imported USER module (resolved as route #439 does) has its return annotation; `min` / `max` / `sum` /
  `round` / `math.floor`-like functions, declared `str` / `list` / `dict` methods and bit operations on ints have
  their result kinds; a module constant bound once its literal kind; a local bound to `None` and an int keeps
  the int kind.
- `PYCSL-R508-INT-FLOAT-PROMOTION-UNMODELLED` (#516) also refuses an arithmetic operation with an operand of
  unknown kind beside an int or another unknown when one of them is OPAQUE -- produced by an erased source: a
  call / method result, a field / attribute read of a user-class (or unknown) receiver, a name bound by a loop /
  unpacking target or to an opaque value, a name the def does not know (a comprehension's tuple target), or an
  operation over one. A declared parameter or plain local of unknown kind (`x: Any`, an element of an
  un-parameterised `list`, an `Optional`), a global / builtin name and an attribute of an int / str / ... is NOT
  opaque: the model reads it as declared (residual). Repair: declare the operand's type.
- SITES (#512 / #514). A `len` / `list` / `sorted` / `bytes` / `bytearray` of ANY value that may be a range (a
  `range(..)` call; a name bound by any binding form -- assignment, walrus, loop / comprehension target over a
  container holding one -- to such a value; a parameter declared `range` / `Sequence` / `Iterable` /
  `Collection` / `Sized` / `Reversible` / `Any` / `object` or undeclared; an if-expression / `and` / `or` /
  element of a container holding one; a field or a def result bound to one) and a `*` unpacking of one;
  `bytes(x)` / `bytearray(x)` unless `x` is a literal count in 0 .. 2**63-1, a display of literal ints in 0..255
  or a bytes literal. A repetition `*` / range-length / byte-count site is credited ONLY by a kept lowering that
  STATES the Py_ssize_t bound (`9223372036854775807` in its text): `len(r)` -> `iter_length !r` and `k * v`
  over erased dict values -> int multiplication are kept lowerings without the obligation. The count form of
  `bytes(n)` / `bytearray(n)` now states that bound under `\all` (`_call_named_builtins`, as route #414 does for
  `[x] * n`). Inside a comprehension / generator / lambda such a site is `PYCSL-R509-COMPREHENSION-OVERFLOW-SITE`,
  elsewhere unlowered `PYCSL-R507-OVERFLOW-SITE-UNLOWERED`.
- CONSTRUCTORS (#512). Route #315's "total builtins" no longer include `bytes(x)` / `bytearray(x)` (unless `x` is
  as above, or a module constant bound once to a literal count) or `len` / `list` / `sorted` of a `range` with a
  non-literal bound: such a constructor is not a field initialiser (`PYCSL-R315-UNMODELLED-CONSTRUCTOR`).
- `PYCSL-R515-IMMEDIATELY-INVOKED-LAMBDA` (#515): a def judged under `\all` whose source holds a call of a lambda
  where it is written. Repair: write the body inline (or make it a `def` with its own contract).

Witnesses `8180`-`8203` (PROVED at base by default; now REFUSED by name -- `8185`, the plain count form under
`requires n >= 0`, is NOT PROVED: the stated bound does not discharge); controls `8210`-`8215` (bounded byte
counts read and displayed, comprehensions over float keys / a `Tuple[float, ...]`, a range bound to a name and never sized plus a
spelled bounded `len(range(n))`, the lambda body inline, `.items()` over `Dict[int, int]`, method results /
fields through a declared receiver; PROVED at HEAD, and at base except `8211`, which base REFUSED because it read the float keys
as ints). Over-refusal: a first draft refused 11% of the 1314 `\all` corpus files (un-parameterised `list` elements, `Optional`
values, None-merged locals, bit operations, enum constants, inherited / ctor-bound fields, imported / nested defs). Restricting #516 to
OPAQUE operands and widening the kind reader brought it to byte-diff root 0 MOVED / 0 GONE / 0 APPEARED, pyref 0/0/0, mirror 53/53
0/0/0, rt43 / rt44 CPython-honest probes 0/150 changed. All 117 red-team-47 witnesses (`witnesses-r512/` 31,
`-r513/` 10, `-r514/` 17, `-r515/` 37, `-r516/` 22) are refused (or NOT PROVED / a Why3 error of the mode) under
default / typed / store. Residuals (named): the kind reader trusts declared annotations; an un-parameterised `list` / `dict` element, an
`x: Any` parameter and a plain local of unknown kind are NOT opaque (read as the model reads them: an int), so `xs[0] * n`
over a bare `list` holding strs is admitted as before; a range passed as an argument is tracked only through the callee's
declared parameter type (`range` / `Sequence` / ... / undeclared); a constructor's other OverflowError forms (`"ab" * n`,
a range reaching `len` by a name) are fenced only by route #315's existing table and the mode's type checker.

### 7.519 Route #315's field-initialiser judge refuses every value-dependent raise by default; a `default_factory` is judged; a dependency's `type` statement rebinds what it exports (routes #519 / #520 / #510 residual, run #4)

A construction `C(args)` is lowered to a record literal of the constructor's `self.<f>` stores (§7.10): the
`__init__` / `__post_init__` body is never emitted, so no route that judges a function body (route #506's
`TRIGGERS` sites, routes #414 / #417 / #507-#516's OverflowError sites, route #508's int -> float promotion, a
TypeError of mixed kinds) ever sees it, and a dataclass's synthesized `__init__` calls each field's
`default_factory`, which nothing judged. Red team 48 measured at 412817ab8, PROVED `no_exception \all` over the
caller while CPython raises: (#519, 59) `len("ab" * n)`, `n * "ab"`, `[0] * n`, `(0,) * n`, `b"ab" * n`,
`[*range(n)]`, `str(n)` / `repr(n)` / `f"{n}"` past 4300 digits, `str(n ** 10)`, `sorted([n, "a"])`,
`sum([n, 0.5])`, in `__init__` / `__post_init__` / an `if` or `for` body / a user exception's constructor, the
object built and discarded, a nested constructor, a dataclass field argument `P(C(n))`; (#520, 17)
`field(default_factory=lambda: 1 // 0)`, `[1][5]`, `{"a": 1}["b"]`, `int("x")`, `next(iter([]))`, a generator
`.throw`, a def doing `assert False` (plain / `kw_only` / `slots` / `frozen` dataclasses, a field argument, a loop).
And (#510 residual, red team 48 g900) a DEPENDENCY module defining `def g` / `class C` and then, at module scope,
`type g = int` (after the def, in an `if` / `try` body): `from dep import g`, `import dep` + `dep.g(3)`, `C(3)`
PROVED while CPython raises TypeError.

RULE (refuse by default; inline in `_run_pipeline`, mirror twin `\trusted`, no new def, no axiom, emission
byte-identical where admitted):
- (#519) Route #315's judge reads each expression of a constructor at the DECLARED kinds of the hook's
  parameters (a parameter the body rebinds is undeclared) and of the class's annotated fields (a field the
  hooks store is undeclared); a parameter / field annotated with a program class has the kind "object". A node
  is admitted only if it is a constant, name, attribute, display, comparison, boolean / unary operation,
  if-expression, slice (step a non-zero literal), comprehension, lambda, walrus, keyword or call already
  admitted by §7.10, and: `a * b` only with a small int literal operand (|v| <= 2**31) or two operands of the
  same declared number kind; `a ** b` only for small int literals (|b| <= 64, no `0 ** -k`) or a declared int
  base and a literal exponent 0..64; `a / b` only of a declared float or small literal by a non-zero literal;
  `%` formatting only of declared str / float / small-literal values; an arithmetic operation with a float
  operand only beside a float or a small literal; `str` / `repr` / `ascii` / `format` and f-string parts only of
  a declared str / float / object, a non-int constant or a small literal (or a display of them); `abs` only of a
  declared number / object; `sum` / `sorted` / `min` / `max` never of a display, comprehension, unpacking or
  call, and over several arguments only of one declared kind; `range` with a non-literal bound only as a `for` /
  comprehension iterable; no sizing builtin (`len list tuple set frozenset sorted sum min max bytes bytearray
  reversed dict`) of, and no `*` unpacking of, a parameter that may hold a range (undeclared, `range`,
  `Sequence`, `Iterable`, `Collection`, `Sized`, `Reversible`, `Any`, `object`, `Iterator`, `Generator`,
  `Container`) or a field bound straight from one. Anything else makes the constructor unmodelled.
- (#520) a `field(default_factory=X)` in a class body is admitted only for a builtin container / scalar type
  (`list dict set tuple frozenset str bytes bytearray int float bool complex object`, not rebound by the
  program), a program class (its constructor is judged with no argument), or a parameterless lambda whose body
  passes the judge above. A def, a method, a call result is not modelled.
  An unmodelled constructor constructed by a non-trusted function is `PYCSL-R315-UNMODELLED-CONSTRUCTOR`, which
  names the site and the route (`route #519` / `route #520`).
- (#510 residual) each module the main file imports (resolved as the import resolver does; transitively through
  re-exporting `from X import Y` and `*`) EXPORTS the names its module-scope `type` statements bind (any depth of
  `if` / `for` / `while` / `try` / `with` / `match` bodies, not a def / class body). Such a name imported here
  (`from dep import g [as h]`, `from dep import *`) is read like an in-file `type` name (§7.510), a module
  reference `dep.g` / `pkg.dep.g` spelled as imported is refused like it, and a dependency class-body `type X`
  joins §7.510's `<e>.X` set: `PYCSL-R510-TYPE-STATEMENT-NAME-READ`. An annotation-only read stays admitted.

Witnesses `8270`-`8285` (#519), `8286`-`8293` (#520), `8294`-`8297` (#510 residual; dependencies
`multi_file_lib/u12_r510_{after,if,cls}.py`): PROVED at base, REFUSED by name. Controls `8300`-`8305` (a
dependency alias read only as an annotation, small-literal repetitions, conversions / products at declared kinds,
`len` / `sorted` / `sum` / `list` of a `List[int]` parameter and a `for` over `range(n)`, builtin / lambda
factories, a `__post_init__` over a declared int field): PROVED at base and HEAD. Refused by design (expected
FAIL -> REFUSED): `1431` (a def factory), `2016` (`[0] * n` over a defaulted parameter), python-reference `0091`
(`list(data)` of an undeclared parameter). Residuals (named): the kinds trust declared annotations (a `str`
parameter bound to an int at run time); user dunders reached by `str` / `abs` / comparisons of an object are the
implicit-dunder routes' (#489-#495); a field bound to a range-holding parameter in ANOTHER method is not
tracked; MemoryError is outside the model; a dependency's `type` statement inside a def body, and a function
body of a dependency reading its own rebound name (imported dependency bodies are trusted stubs), are not judged.

### 7.523 A str-list literal is iterated as its literal only when nothing can reach the list (routes #523 / #525, run #4)

Two lowerings bind a `for` loop to the LITERAL a str list was bound to instead of to the list object: a local
`a = ["abc", "defg"]` iterated by `for p in a` (Module 6 `_collect_str_literal_seq_locals` -> `_str_lit_seq_elts`,
a `Seq.cons` chain) and a module-level `OPS = [...]` read only as a `for` iterable (`module_const_str_lists`, the
proved `let function _OPS_lit ()` of lex-char-class inc 2). Neither looked at what may write the object first:
red team 49 measured `a.append("z")` (a literal / parameter / None / computed value, twice, under an `if` / loop /
`try`) then `for p in a: if p == "z": return 1` PROVED `ensures \result == 0`, and `p[2]` / `len(p)` PROVED
`no_exception \all` (32 witnesses); at module level `globals()["OPS"].append("z")`, `locals()` / `vars()`,
`import __main__; __main__.OPS`, `__import__(__name__).OPS`, `sys._getframe().f_globals`, `gc.get_objects()`,
before or after the def, in a class body or the driver block, PROVED the same early-return claim (21 witnesses).

RULE (Module 5 `visit_Module`, refuse the shortcut by default):
- NAMESPACE ACCESS. The module reaches a binding or an object other than by its name when it uses `globals` /
  `locals` / `vars` / `__import__` / `eval` / `exec` / `compile` / `breakpoint` / `__builtins__`; `getattr` /
  `setattr` / `delattr` other than a direct call with a constant, non-dunder, non-frame attribute name; a dunder
  attribute outside a value-level allow-list (`__globals__`, `__dict__`, `__self__`, `__closure__`,
  `__getattribute__` ... are out); a frame attribute (`f_globals`, `f_locals`, `f_back`, `gi_frame`, `cr_frame`,
  `tb_frame`, ...); an import of `gc` / `inspect` / `ctypes` / `__main__` / `importlib` / `builtins` / `traceback` /
  `operator` / `pickle` / `string` / ... ; `sys` other than `import sys` read through a plain value attribute
  (`sys.argv`, `sys.exit`, `sys.maxsize`, ...; never `sys.modules` / `sys._getframe`, never an alias); an import
  of the module's own name (file stem, set by `_run_pipeline`). Then neither shortcut is recorded.
- MODULE LIST (#525): with namespace access, `module_const_str_lists` is not recorded and `for x in OPS` keeps the
  general (opaque) lowering, as before inc 2: the early-return claim is NOT PROVED.
- LOCAL LIST (#523): `str_lit_seq_locals_ok` records the (name, literal) pairs that qualify: bound by a statement
  DIRECTLY in its function's body, no other binding of the name anywhere in the function (nested defs included:
  rebinding, augmented, `del`, `for` / `with` / `except` / match / walrus / import target, parameter, `global` /
  `nonlocal`), every read after the binding, and for a LIST every read the iterable of a `for` (so no
  `.append(..)`, alias, argument, subscript or closure); a TUPLE may be read anywhere. Module 6 iterates the
  literal only for a recorded pair; a `for` over any other local bound to an all-str literal is REFUSED with
  `PYCSL-R523-STR-LITERAL-LIST-MUTATED` (the general lowering int-erases the elements: after `a.append(None)`,
  `len(p)` would still prove). Repair: bind the final list as one literal, or use a tuple.

Witnesses `8380`-`8387` (#523) and `8390`-`8399` (#525), PROVED at base. Controls `8400` (a local list bound once,
read only by `for`), `8401` (a local tuple also read by `len`), `8402` (a module list, no namespace access), `8403`
(`import sys` read as `sys.argv`), PROVED at HEAD and at base.

### 7.527 An operand that may be `None` of a TypeError-raising operator is judged like an attribute receiver (route #527, run #4)

An `Optional[str]` record field (a `@dataclass` field `s: Optional[str]`, or `self.s: Optional[str]`) is lowered
as a plain Why3 `string` with no None case, and route #432's receiver rule only judged ATTRIBUTE loads. Red team
49 measured PROVED `no_exception \all` (CPython TypeError on `R(None, ..)`): `w = r.s + "x"`, `"x" + r.s`,
`r.t + r.s`, `v = r.s; v + "x"`, `"a" in r.s`, `"a" not in r.s`, `for c in r.s`, and the `self.s` twins whose
None is stored in `__init__` (11 witnesses).

RULE (inline in `_run_pipeline`, in route #432's engine; mirror twin `\trusted`, no new def, no axiom,
emission byte-identical): in a function that is neither `\trusted` nor `\abstract` and claims TypeError (`\all`,
`TypeError`, `Exception`, `BaseException`, declared or reached), every OPERAND whose derived classes (`_ex346` /
`_eh372`) hold `None` -- an arithmetic operand (`%`: the left one only; `|` is not judged, it is also a type
union), either side of an ordering comparison, an `in` / `not in` haystack, a subscripted value, a `for` /
comprehension iterable; a literal `None` is not judged -- is a synthetic attribute load judged by #432's FLOW
NARROWING (an enclosing `if O is not None:` / `isinstance`, an earlier `assert`, an early `return` / `raise`
when `O is None`, with no rebinding -- and, for an attribute path, no call -- in between). It is admitted iff
its narrowed classes hold no `None`; otherwise REFUSED with `PYCSL-R527-OPTIONAL-OPERAND`. Narrow the operand
first, declare the field without `None`, or drop the claim.

Witnesses `8410`-`8418` (PROVED at base, REFUSED); controls `8420` (`if r.s is not None:`), `8421` (early
`return` when `r.s is None`), `8422` (the `self.s` guard), `8423` (a plain `str` field beside the Optional one),
`8424` (no claim: route #431).

### 7.528 A split piece read owes its index: `[0]` / `[-1]`, or `[1]` / `[-2]` when the separator occurs (route #528, run #4)

`<str>.split(<sep>)[i]` (also `split(sep, k)[i]`, `rsplit`) lowers to the total `val str_split_elem_op (s sep:
string) (i: int) : string` (faithful-string-op §3.4); the piece list is never materialised, so the list read's
bounds obligation never existed. Red team 49 measured PROVED `no_exception \all` (CPython IndexError on
`"ab".split(",")[1]`): `len(s.split(",")[1])`, `x = ..`, `== "a"`, `+ "x"`, `.upper()`, `.startswith`, an
f-string, a `-> str` return, a parameter / expression / `[-2]` / big index, `split(",", 1)[1]`, `split(",",
0)[1]`, a loop over lines, and the lex-char-class lowerings `s.split(",")[1].isdigit()` / `.isalpha()` (computed
receiver) and `s.split(",")[1] in "ab"` (enumerated-substring fold) (41 witnesses).

RULE (inline in `_handle_subscript`'s split arm, program context, every body -- the polarity of the list read,
whose Why3 array access carries its bounds precondition claimed or not; mirror twin `\trusted`, no new def, no
axiom): the read binds its receiver and index once and asserts `[@expl:PyCSL-R528 ..]`
`i = 0 \/ i = -1` for a NON-EMPTY string-literal separator, extended by `(i = 1 \/ i = -2) /\ <sep occurs in
s>` (the `str_contains_op` law, so `if sep in s:` / an early return discharges it) when no maxsplit or a
literal maxsplit >= 1 is given; any other separator (no-arg split, a variable, `sep=` keyword) owes `false`. A
literal `[0]` / `[-1]` on such a separator, and on the no-arg `N.split()` in the TRUE arm of `.. if N.split()
else ..` (a plain name, the arm free of walrus / lambda / comprehension), keeps its lowering byte-identical.
A read the assertion cannot discharge is NOT PROVED (fail closed).

Witnesses `8425`-`8432` (PROVED at base, NOT PROVED); controls `8435` (`[0]`), `8436` (`[-1]`, `split(":", 1)[0]`),
`8437` (a parameter index under `requires i == 0 or i == -1`).

### 7.533 A `default_factory` program class must be callable with no argument and raise-free; a factory lambda's literal operands are kind-checked; a factory name resolves through the class body; a tuple / list ordering compares its components (routes #533 / #534 / #535 / #538, run #4)

Route #520 (§7.519) admitted a `field(default_factory=X)` for a builtin type, a program class or a parameterless
lambda whose body passes route #519's judge. Red team 50 measured at 9bdb8cf32, PROVED `no_exception \all` over the
caller while CPython raises in the synthesized `__init__`: (#533, 33) a program class whose `__init__` needs an
argument (positional, keyword-only, inherited), an `enum.Enum` / `IntEnum`, a dataclass with a required field or
`InitVar`, a user exception needing arguments, an `__init__` / `__post_init__` that `raise`s (plainly or under an
`if` on a default), a constructor body doing `[*5]`, a nested dataclass factory, in plain / frozen / kw_only /
slots / order / eq=False dataclasses, loops and nested constructors; (#534, 79) a parameterless lambda built from
literals of the wrong kinds (`"a" + 1`, `[*5]`, `1 < "a"`, `{[1]}`, `-"a"`, `"%d" % "a"`, `f"{'a':d}"`,
`1 << 9223372036854775808`, `len(5)`, `None + 1`, `(1, 2) < (1, "a")` ...); (#535, 10) a class-body binding of
the factory's name before the field (`dict = 0`, `list = lambda: 1 // 0`, a nested `class complex`, a ClassVar,
`object = staticmethod(..)`), which is what the field expression evaluates in the class body. And (#538, 1) `t <
u` of two `Tuple[int, Any]` parameters in a plain function, which compares the `Any` components on equal heads.

RULE (refuse by default; inline in `_run_pipeline`, mirror twin `\trusted`, no new def, no axiom, emission
byte-identical where admitted):
- (#535) a factory NAME is admitted only when it is bound nowhere in the field's class body, the program has no
  `from M import *`, and at module scope (assignments, imports, `def` / `class`, `except .. as`, match captures,
  a `global` / `nonlocal` store anywhere) a builtin factory name is never bound and a program-class factory is
  bound exactly once, by its one `class` statement (a class defined inside a function is not admitted).
- (#533) a program class X is admitted as a factory only when its base chain is a single chain of program
  classes (`object` aside; no class keyword / metaclass; no decorator but `dataclass` / `dataclasses.dataclass`
  without positional arguments or `init` other than `True`; no `__new__`), the first `__init__` of the chain
  (own, or synthesized from the dataclass fields of the chain: a field without a default / `default_factory`
  and not `init=False`, an `InitVar` included, is required) has no required parameter (positional or
  keyword-only), and no `__init__` / `__post_init__` / `__new__` of the chain or of a class those constructors
  depend on (constructed, a base, a field factory) holds a `raise` or `assert`.
- (#534) the body of a parameterless factory lambda, and every closed (name-free) sub-expression of the
  constructors a factory class runs, is admitted only when each node has a kind among: a constant; a list /
  tuple display (a `*` of a sequence / set / dict); a set / dict display of hashable keys; `not`; unary `-` /
  `+` of a number, `~` of an int; `+` of two numbers / str / bytes / lists / tuples; `-` of numbers or sets;
  `*` of numbers or of a sequence by a small int literal; `/` `//` `%` of a number by a non-zero number literal
  (a float never beside an int that may be large); `**` of a small int by a literal 0..64; `<<` / `>>` by a
  literal 0..64; `&` `|` `^` of ints / sets; `==` / `!=` / `is` anywhere, `<` `<=` `>` `>=` only of two numbers /
  str / bytes / sets, `in` of a list / tuple, of a hashable in a set / dict, of a str in a str, of bytes in
  bytes; `and` / `or` / `x if c else y`; an f-string of scalars without a format spec; a slice (small int
  bounds, non-zero literal step) of a sequence; a builtin type the program does not rebind called with no
  argument. Anything else (a name, an attribute, a subscript, a call with arguments, a comprehension) is not
  modelled.
  A factory that fails any of these makes the class's constructor unmodelled: a non-trusted function
  constructing it is `PYCSL-R315-UNMODELLED-CONSTRUCTOR`, naming the site and the route (`route #533` /
  `#534` / `#535`).
- (#538) under a claim covering TypeError (§7.135's scope), an ordering comparison (`<` `<=` `>` `>=`) any of
  whose ordered operands is derived a tuple / list joins route #437's orderability judge over the operands of
  its ordering operators: admitted only when their components are derived all numbers / all `str` / all
  `bytes` / parameterised tuples / lists of such at each position; `Any`, `object`, `None`, a user class, a
  union of unordered kinds, an un-parameterised tuple and an underivable operand are refused:
  `PYCSL-R538-UNORDERED-TUPLE-COMPARISON`.

Witnesses `8500`-`8510`, `8521` (#533), `8511`-`8520` (#534), `8522`-`8526` (#535), `8527` (#538): PROVED at
base, REFUSED; `8528` (#538, `List[Any] >= List[Any]`): NOT PROVED at base, REFUSED. Controls `8530` (program
class factories with defaulted / inherited / dataclass-defaulted / absent `__init__`), `8531` (literal lambdas
of matching kinds), `8532` (class-body bindings of other names), `8533` (ordering of int components of tuples):
PROVED at base and HEAD. Residuals (named): the kinds of a NAMED operand inside a constructor stay route #519's
judge (only closed sub-expressions are kind-checked there); an ordering of whole typed tuples (`Tuple[int, str]
< Tuple[int, str]`) is admitted by the rule but is not lowered by the model (Why3 type error, NOT PROVED at base
and HEAD); MemoryError of a large literal repetition is outside the model.

### 7.529 Route #519's constructor judge also runs a refuse-by-default KIND-FLOW pass: every read resolves, every kind-dependent operation is total at the kinds it reads (routes #529 / #530 / #531 / #532 / #536 / #537 / #539, run #4)

Route #519 (§7.519) read a constructor's expressions at declared kinds but never checked what they iterate,
unpack, sort, read as an attribute or pass to a builtin, nor which binding a name reads. Red team 50 measured on
9bdb8cf32, PROVED `no_exception \all` over the caller while CPython raises in `__init__` / `__post_init__` / a
`default_factory` (plain, nested, discarded, built in a method; 219 witnesses): (#529, 78) `for x in n` /
`[x for x in n]` / `[*n]` / `{**xs}` over an int / float / object / Any / List value, `a, b = xs` and `for a, b in`
of the wrong arity, `a, *b = []`, `zip(.., strict=True)`, `range(0, 5, s)` / `range(n, 0, -0)`; (#530, 38)
`sorted(xs)` of List[Any] / List[object] / List[Optional[int]] / List[Dict] / Set[Any] / Tuple[int, str],
`key=len` over ints, `key=str` / `key=repr` over a 10 ** 5000 element, `key=abs` over strs, key lambdas raising;
(#531, 26) `o.nope` / `o.a.b` / `type(o).zz` / `o.__len__` of an object / Any / Optional, `self.j` read before its
store, a class attribute of another kind read through `self` (`k = "a"`; `self.k + n`), a slice of an int local;
(#532, 35) `issubclass(n, int)`, `setattr(self, n, 1)`, `ValueError(x=n)`, `ExceptionGroup("m", [])`,
`UnicodeDecodeError()`, `SyntaxError("m", n)`, a dataclass `__post_init__` whose parameters are not its InitVar
fields (missing / extra / kw-only / swapped / inherited) or that is not a function; (#536, 23) `str(p)` / `repr(p)`
/ `str([p])` of a @dataclass / NamedTuple whose synthesized `__repr__` formats an int field (ValueError past 4300
digits); (#537, 12) a `match` capture (`case n:`, `case str() as n:`, `case n if n:`) rebinding a parameter read
later at its declared kind; (#539, 7) a `default_factory` lambda reading a class-body name (NameError) or a global
rebound / mutated after the class, a constructor `n + Z` with `Z = None`.

RULE (inline in `_run_pipeline`, inside route #315's judge; mirror twin `\trusted`, no new def, no axiom):
- Kinds: int bool float str bytes none range, an instance of a program class, list / Sequence / Iterable / set /
  dict of an element kind, a fixed tuple of slot kinds, a homogeneous tuple; anything else (Any, object,
  Optional, Union, unannotated) is UNKNOWN. A parameter has its annotation's kind; a local, a rebound
  parameter and a `self.<f>` stored in the hook have the kind every one of their plain bindings (`=`, `+=`,
  a `for` target, a tuple-unpacking slot) agrees on -- for a parameter / dataclass field, the declared kind --
  else unknown; a module global has a kind only if bound exactly once, to a constant, and never declared
  `global`; a comprehension variable has its iterable's element kind.
- Every read resolves: a hook local only where definitely bound (straight-line; both `if` branches do not
  count); `self.<f>` only after a store in the hook, as a class attribute, as a dataclass field set by the
  synthesized `__init__` (in `__post_init__`), or after a top-level `super().__init__()` for the fields the
  base definitely stores; `p.<f>` only for a program-class instance whose class / constructor definitely
  defines `<f>`; `m.<a>` only for an imported loaded module that has `<a>`; any other name only if bound at
  module level, a parameter or a builtin (a class-body name is NOT visible in a method or a lambda).
- Every kind-dependent operation is admitted only at kinds that make it total: iteration (`for`,
  comprehensions, `*x`, `list` / `tuple` / `set` / `any` / `all` / `sorted` / `reversed` / `enumerate` / `zip`)
  of an iterable kind (a user `__iter__` counts); `**x` of a dict; unpacking only against a display or a fixed
  tuple of matching length; set elements / dict keys hashable; `len` of a sized kind (a user `__len__`
  counts); `sorted` / one-argument `min` / `max` (the latter only with `default=`) of elements with one total
  order, or with `key=len` / `abs` / `str` / `repr` / a one-parameter lambda total on the element kind and
  yielding ordered values; `sum` of numbers; `abs` of a number (or a class with `__abs__`); `range` of ints with a
  non-zero literal step; `zip` without `strict` (or `strict=False`); `isinstance` / `issubclass` against classes;
  `setattr(self, "<plain literal>", v)`; a builtin exception class without keywords and not one whose
  constructor validates its arguments (`ExceptionGroup`, `BaseExceptionGroup`, `SyntaxError` family,
  `Unicode*Error`, `BlockingIOError`); builtin arities; binary / unary operators, ordering comparisons and
  membership at compatible known kinds; `%` formatting of a literal format whose conversions fit the values;
  an f-string format spec only on a str / float value it fits; a slice of a sequence with int / None bounds; a
  class pattern's positional sub-patterns within `__match_args__`; no `return <value>` in `__init__`; no store
  to `self` in a frozen dataclass hook.
- (#536) the "object" kind of route #519's string conversions holds only for a REPR-SAFE class: no foreign
  base, and every @dataclass ancestor with a synthesized `__repr__` has only str / float / bool / None / bytes /
  repr-safe-class fields (or containers of them); NamedTuple / Enum / exception subclasses are not repr-safe.
- (#537) a `match` capture, a `del`, a lambda parameter rebind the name like a store (§7.519's declared kinds).
- (#532) a dataclass whose `__init__` is synthesized calls the nearest `__post_init__` with its InitVar fields
  (bases first) positionally: the hook must be a function taking exactly those names, in that order, with
  those annotations, no `*args` / keyword-only / `**kw`.
  Anything else makes the constructor unmodelled: `PYCSL-R315-UNMODELLED-CONSTRUCTOR`, naming the site and
  `route #529-#539 kind-flow judge` (or `route #532` for the hook arity).

Witnesses `8440`-`8462` (PROVED at base, REFUSED by name); controls `8480`-`8487` (iteration / unpacking at known
shapes, total sorts, resolved attributes, builtin / exception / InitVar calls at accepted kinds, a repr-safe
dataclass, a `match` that captures no parameter, a constant global read by a factory, a dataclass field read in
`__post_init__`): PROVED at base and HEAD.
Byte-diff: root 0 MOVED / 1 GONE / 0 APPEARED (`2018`, `list(BASE)` of a mutable module global: expected FAIL ->
REFUSED), python-reference 0 / 0 / 0, mirror 53/53 byte-identical. Residuals (named): kinds trust declared
annotations; user dunders (`__iter__`, `__len__`, `__abs__`, `__eq__`, `__repr__` of a plain class) are the
implicit-dunder routes'; the arity of a nested program-class construction and `__slots__` stores are not
judged; a field re-annotated by a dataclass subclass is read at the base's annotation in an inherited hook.

### 7.521 A value that may be None is fenced at every operation that raises on None (routes #521 / #522 / #524 / #526, run #4)

A missing `.get` key and a None stored in a container lower to the opaque `pycsl_none` / `pycsl_none_str` of
the codomain (routes #44 / #50 / #57), an ordinary int / str to the solver. Route #230 asserted `not (v =
pycsl_none)` only for an ARITHMETIC / ORDERING operand in `_handle_binop`, and judged "may be None" only for a
one-dot `<dict>.get(k)`, a one-level read of a container with an Optional element or a stored None, and a local
bound directly from one. Red team 49 measured, PROVED `no_exception \all` while CPython raises TypeError: (#521,
74) unary `-` / `+` / `~`, `t += ..`, `in` / `not in` (either side), an f-string format spec on such a value;
(#522, 30) `r.d.get(k)` / `self.d.get(k)` / `o.r.d.get(k)` on a dict FIELD; (#524, 19) `xss[0][0]` /
`xss[i][j]` of `List[List[Optional[int]]]` / `Sequence[Sequence[Optional[..]]]`; (#526, 47) the None flowing
through a list / dict display, `append`, an item store, a walrus, a tuple unpack, a `for` target, `x or None`,
a None-valued `.get` default, a callee's argument / return, a field store, a constructor argument.

RULE (one value fence, refuse by default; record in `functions.py::_emit_function_block`, no twin; sites in
`_expr_to_whyml` / `_stmts_to_whyml` / `_handle_isinstance`, twins `\trusted`; no new def in a mirrored body, no
axiom, no raise). "May be None" (`mb`) is a fixpoint over the body seeded with route #230's record: a local or a
subscript chain of length L into a container holding None at depth L (Module 5 `r524_optional_depths`); a
`.get` with no / a None / a may-be-None default on a known dict local or parameter, a dict field of int / str
codomain (resolved through the record types; an unresolved dotted receiver counts), and `.get` / `.pop` /
`.setdefault` on a container holding None; a ternary / `and` arm or the right operand of `or` that may be None
(a None literal included); a walrus of one. A binding (assignment, unpack, walrus, `for` / comprehension
target) from such a value taints the local; a display / comprehension element, item store, `append` /
`insert` / `add` / `setdefault` / `extend` / `update` / `+=`, alias, copy or slice taints the container. At
every position that RAISES on None the obligation `not (v = pycsl_none)` is asserted before the operation:
unary, membership (container; needle of a str haystack), arithmetic / ordering operands #230 does not already
guard, string concatenation, subscript receiver / index, the argument of a builtin / method / file function or
constructor whose parameter annotation does not admit None, a format spec, an iterable, an augmented
assignment's value and target, a tuple unpack, a `return` from a function whose return annotation does not
admit None, a field store (unless the field admits None), an item store into a non-local container. It holds
under `is not None` / `isinstance`; a non-pure operand (a call, a walrus) and a container holding None that
leaves the function (return, field, file-function argument) without an annotation admitting None get an
unprovable obligation, as does a comprehension whose element raises on such a value but whose lowering erased
the element (`any(..)` -> abstract `any_1`). Safe (no obligation): `is` / `==` / `!=`, truth tests, `and` / `or`
/ ternary arms, display elements, `str` / `repr` / `print` / `isinstance` / `bool` / `id` / `type` / `hash`,
container mutators' value arguments. IR-node ADT (`emit_ir`) values are exempt (no None in that model).

Witnesses `8320`-`8351` (PROVED at base 1aaa1dfdd, NOT PROVED on a `PyCSL-R521` obligation); controls `8360`-`8372`
(guarded unary / `+=` / `in`, non-None defaults, guarded field and nested reads, guarded list element, `x or 0`,
`isinstance` over an Optional list, equality on `.get`). Residuals (named): a `.get` on a dict of a non-scalar or
float codomain (route #57's unmeasured placeholders); an Optional record FIELD read (`self.x: Optional[int]`)
and a CONTAINER holding None passed to a method or a builtin (`sorted(xs)`, route #437's) are not judged here; a local bound to a None literal
and later rebound is the None-local routes' (#44 / #46 / #227 / #239).

### 7.280 An imported module of the program must IMPORT without raising, on the program's own path (routes #466 / #472, run #3)

Route #461 (§7.230) runs only the claimed file's own top level. Red team 38 measured PROVED `no_exception \all`
for `f` returning `g(n)` imported from a helper module whose top level is `X = 1 // 0` / `{}['k']` / `assert 1
== 2` / `raise RuntimeError` / an MRO conflict / a dataclass mutable default / `import zz_no_such_mod` / a
compile-time SyntaxError (`def g(x): global x`), from a package whose `__init__` raises, from a helper whose
OWN import raises (m254), from a helper binding `g` only under `if False:` / in a `for` body / after a raising
statement in a `try`, through a circular import reaching the partially initialised helper, and through `h.g(n)`
on a module binding no `g` (#466); and `import frontend` / `errors` / `pycsl` (any module of the VERIFIER, whose
sys.path[0] is src/pycsl) admitted as importable without `--import-path` (#472). CPython raises at import.
RULE (allow-list, refuse by default) when a verified def of the file carries any `#@ no_exception` claim:
modules are resolved on the TARGET program's path -- this file's directory, the `--import-path` roots, then the
interpreter's path MINUS the verifier's own source tree (src/pycsl, src/); a standard-library name is the
standard library; not found is ModuleNotFoundError (`PYCSL-R472-IMPORT-NOT-ON-TARGET-PATH` when the name exists
only on the verifier's path). A module found in this file's directory or on an `--import-path` root is the
PROGRAM's code and is IMPORTED, in CPython's order and with CPython's partial-module semantics (it enters the
module table before its body runs; each package `__init__` on the way first): its source must `compile()`, and
its top level and class bodies are run statement by statement on real values -- imports (recursively), `def`
(decorators and defaults evaluated, the body a placeholder refused if import-time code calls it), `class`
(created by `types.new_class`, its allow-listed decorators applied for real), assignments, `if` (the arm the
real test selects), `try` (body, else, finally; a raise refuses), `assert`, `del`, docstrings; anything else
(`for`, `while`, `with`, an attribute store ...) is REFUSED. Expressions are evaluated by CPython over those
values; the only calls admitted are side-effect-free standard-library callables and builtin-type methods. `from
M import n` needs `n` BOUND in M's namespace at that moment (or a submodule); `M.n` read by a claimed function
needs `n` bound once M is imported; a relative import in the verified file is refused (a script has no parent
package). An INSTALLED module (site-packages) is a declared library: it must exist, its top level is not run.
Refusal: `PYCSL-R466-IMPORTED-MODULE-RAISES`. Witnesses `7260`-`7265`, `7267`-`7269`, `7282`-`7284` (the package
`__init__` case is red-team m250, refused; no corpus fixture, its package would not load in check-corpus-executes); controls `7285`, `7288`,
`7289` (a circular import whose name is bound before the cycle closes).

### 7.281 A claim reaching an imported function needs that function's own claim (route #467, run #3)

An imported function is a bodyless stub: route #460's reached claim (§7.210) stops at the file boundary and
#178's walk of its body is a deny-list. Red team 38 measured PROVED `no_exception \all` for `return g(n)` with an
un-claimed imported `g` whose body holds `assert x != x`, `next(iter([]))`, `pow(2, -1, 4 * x)`, `x.zz`,
`getattr(x, 'zz')`, `len(x)` / `x()` / `iter(x)` of an int, `json.loads('{')`, `open()` of a missing file,
`'a' + x`, `bytes.decode`, `struct.pack`, `range(0, 1, 0)`, or a call of a SECOND un-claimed helper whose assert
fails. RULE (allow-list, refuse by default): under a claim covering E of a def of the file (its own or a
caller's, `_rc444`), a reference to a function of a program module (§7.280: a call, a value, `M.g`, a constructor
of an imported class -- its `__init__` / `__new__` / `__post_init__` / dunders, also through a class of this file
deriving from it, a dataclass `default_factory` --, and any method of an imported class with the same name as an
attribute read) is REFUSED unless that function itself claims `#@ no_exception` covering E (`\all`, or a superset
of the named exceptions: a declared modular assumption, the function is verified when its module is) or its body
is on the exception-free allow-list: `return` / assignments / augmented `+ - * & | ^` / `if` over parameters
annotated `int` / `bool` with `+ - * & | ^`, comparisons and boolean operators, no call, subscript or attribute.
Refusal: `PYCSL-R467-IMPORTED-UNCLAIMED`. Witnesses `7270`-`7274`; controls `7286`, corpus `6642` (`inc(n): return
n + 1`, on the allow-list).

### 7.282 A bodyless `val` must keep the length of a list parameter (route #468, run #3)

An imported, `\trusted` or `\abstract` function is emitted as a bodyless `val` whose frame writes its list
parameter (`val g (x: array int) : unit writes { x }`, route #317's default frame or a declared `#@ assigns x`),
and a Why3 `array`'s length is immutable: `len(a)` after `g(a)` kept the entry length while the body appended /
popped / cleared / `+=` / sliced / `heappush`-ed / `insort`-ed / aliased / closed over the list (34 spellings
PROVED `\result == 2`, CPython 3 or 1). RULE (allow-list, refuse by default, no claim needed): each list
(or `bytearray`) parameter of such a `val` that the VERIFIED code of this file references (a call, a value, a
method tail) -- an explicit `#@ \trusted` def included since route #481 (§7.340) --
must be LENGTH-PRESERVED by the function's SOURCE body (this file and the modules it
imports): it occurs only as an element store `x[i] = v` / element or slice read, the argument of a builtin that
does not mutate it (`len`, `sorted`, `sum`, `min`, `max`, `list`, `tuple`, `set`, `enumerate`, `zip`, ...), an
operand of a comparison or of a fresh-list `+` / `*`, the iterable of a loop, the returned value, or the receiver of `sort()` /
`reverse()` / `copy()` / `count()` / `index()`; any other occurrence (a mutator, an alias, an argument of another
call, a store to the name) is REFUSED, as route #49 refuses the same mutators on a list parameter of a verified
body. Refusal: `PYCSL-R468-VAL-LIST-LENGTH`. Witnesses `7275`-`7281`; control `7287` (`x[0] = 1` only).

### 7.310 An imported constant is folded only when the dependency binds it exactly once (route #474, run #3)

The importer used to fold a dependency's module constant from `collect_module_constants`, a scan of
TOP-LEVEL single-Name `Assign` / `AnnAssign` statements only, so a `K = 1` the dependency rebinds by an
augmented assignment (`K -= 1`, `K *= 0`, `S += 'b'`), an unpacking target (`K, = (0,)`, `[K, J] = [0,
1]`) or inside an `if` / `else` / `try` / `finally` arm was folded to its FIRST value: `n // K` PROVED
`no_exception \all` and `len(S) == 1` PROVED, while CPython raises ZeroDivisionError / returns 2 (the
in-file twin is refused by the Weaver's binding-site guard, which fires only for a name the module itself
reads). RULE (allow-list the export): a dependency constant is folded into the importer only when
CPython's own parse of the dependency binds that name at EXACTLY ONE site of any form anywhere in the file
(a name stored or deleted at any depth -- augmented, annotated, unpacking, `for`, `with`, walrus,
`except`, `match` targets --, a `def` / `class` name, an import alias, a `global` / `nonlocal`), and the
file has no namespace writer the table cannot see (`from M import *`, `globals()`, `vars()`, `locals()`,
`exec`, `eval`, `setattr`, `delattr`, `__import__`, `.__dict__`, `.modules`). Otherwise the name stays an
opaque `val constant`, and the claim must hold for every value. No new refusal. Witnesses `7450`-`7455`
(PROVED at base, NOT PROVED now); controls `7457` / `7458` (a constant bound once still folds).

### 7.311 Every resolved module is read as CPython decodes it (route #475, run #3)

The frontend read every resolved dependency with `open(path).read()` (UTF-8) while CPython decodes a source
file by its PEP 263 coding cookie / BOM, so a `latin-1` / `cp1252` / vim-style / post-shebang cookie over
non-ASCII bytes gave the verifier other string constants than CPython (`len(S) == 1` PROVED, CPython 2),
and a `utf-7` dependency hid the statement `K = 0` in the comment `# +AAo-K = 0` (CPython decodes `+AAo-`
to a newline). RULE (route #465's gate applied to every resolved module, at `_resolve_module_path`, the one
place every frontend reader obtains a dependency's path): the file's BYTES are decoded by CPython's own
`tokenize.detect_encoding`, and that text must equal its UTF-8 reading (newlines and BOM normalised);
otherwise the import is REFUSED (`PYCSL-R475-DEPENDENCY-ENCODING`), as is a file CPython cannot decode.
A `utf-8` cookie, or any cookie over ASCII-only text that decodes identically, is accepted. Witnesses
`7460`-`7462`; controls `7463` (`utf-8` cookie, non-ASCII text), `7464` (`latin-1` cookie, ASCII text).

### 7.312 A module-level `__getattr__` is not run by the import check (route #477, run #3)

Under a `no_exception` claim, route #466 bound `from h import g` to UNKNOWN as soon as the program module
`h` defines a PEP 562 `__getattr__`, without calling it; CPython's from-import first probes `h.__path__`
through it (only AttributeError is suppressed), then reads an unbound `g` through it, so a `__getattr__`
raising KeyError, or AttributeError for `g`, fails the import -- even next to a real `def g`. RULE (refuse
by default, inside #466's run): a from-import (any name, `*` included) of a program module whose namespace
holds `__getattr__` is REFUSED, and so is a claimed function's read `h.g` of a name such a module does not
bind (`PYCSL-R466-IMPORTED-MODULE-RAISES`). Witnesses `7470`-`7473`; control `7474` (a module without
`__getattr__`).

### 7.220 A term transform's binder arm may run a `while True:` scan loop down the spine (lv4, run #3)

A one-parameter Term->Term transform (§7.160's shape, e.g. the mirror's
`proof2why3/canonical.py::_flatten_foralls`) may have a single-class block arm that
binds fresh lists and runs a scan loop:

    bs = list(t.binders)                  # a NEW list
    cur = nb                              # nb = f(t.body), bound above
    hyps = []                             # a NEW list, typed by its appends
    while True:
        if isinstance(cur, C) and <str> == <str>:
            bs.extend(cur.binders)        # / hyps.append(cur.lhs)
            cur = cur.body                # the spine step, once, to a field of cur
            continue
        if isinstance(cur, B) and cur.op == "->":
            inner = cur.rhs               # a loop-local look-ahead
            while isinstance(inner, B) and inner.op == "->":
                inner = inner.rhs
            if isinstance(inner, C) and inner.ty == t.ty:
                hyps.append(cur.lhs)
                cur = cur.rhs
                continue
        break
    out = cur
    if hyps:
        out = mk_chain(hyps, cur)         # a list builder of the file
    return C(binders=tuple(bs), ty=t.ty, body=out)

The loop lowers to a local recursive function over the loop state (`continue` is the
recursive call, `break` returns the state). It is accepted only when exactly one state
variable is a term and every `continue` path has stepped it once to a term field of its
own loop-entry value, under an `isinstance` test. That makes termination provable from
the structure of the term. A path that reaches the end of the loop body without
`continue` / `break` declines. String `==` is the uninterpreted `pystr_eq`, so both
branches stay possible. The mutated lists must be created by the block (`[]` /
`list(..)`) and not read before the loop, so no alias can see the mutation. Anything else
declines to the generic lowering, which refuses the in-place `.extend` / `.append`. As
for every term recognizer, a contract other than `True` declines. Witnesses `7100`
(PROVES), `7101` (`ensures False`, must NOT prove), `7102` (an aliased list, declined),
`7103` (a `continue` that does not step the spine, declined).

### 7.221 A term transform may flatten, sort and re-fold an associative operator chain (lv4, run #3)

A one-parameter Term->Term transform (§7.160's shape, e.g. the mirror's
`proof2why3/canonical.py::_ac_normalize`) may have one guarded arm, placed before the
general arm of the same class:

    if isinstance(t, C) and t.op in ("l1", "l2"):
        operands = []
        def collect(node):
            if isinstance(node, C) and node.op == t.op:
                collect(node.lhs)
                collect(node.rhs)
            else:
                operands.append(f(node))
        collect(t)
        operands_sorted = sorted(operands, key=lambda x: x.pp())
        out = operands_sorted[-1]
        for o in reversed(operands_sorted[:-1]):
            out = C(t.op, o, out)
        return out

The nested `collect` is folded into the arm, so the lifted sibling emits nothing. The
call `f(node)` is on a proper descendant of `t`: the root call `collect(t)` always
descends, because `t.op == t.op` holds. So the call terminates by the file's term-size
measure. The arm is accepted only in a file whose term transforms already use that
measure. `sorted` is a defined stable insertion sort. Its key `x.M()` and the key
comparison are uninterpreted: deterministic, and nothing is claimed about them. The
length law of the sort is proved, which proves that `operands_sorted[-1]` is in range.
Any other closure shape declines. As for every term recognizer, a contract other than
`True` declines. Witnesses `7104` (PROVES), `7105` (`ensures False`, must NOT prove),
`7106` (a closure that does not descend, declined).

### 7.250 A term transform may thread a one-cell counter (lv5, run #3)

A two-parameter Term->Term transform `f(t, c)` whose second parameter is a `List[int]`
cell (the mirror's `proof2why3/canonical.py::_alpha_rename`, a fresh-name supply) is
recognized when its arms are identity arms, rebuild arms over `t.F`, `f(t.G, c)` and
`tuple(f(a, c) for a in t.L)`, and one binder block of exactly this shape:

    new_names = []
    mapping: Dict[str, str] = {}
    for old in t.binders:
        new = f"v{c[0]}"
        c[0] += 1
        new_names.append(new)
        mapping[old] = new
    r = S(t.body, mapping)                # S: a Dict[str, str] transform of the file
    r = f(r, c)
    kind = A if isinstance(t, A) else B
    return kind(binders=tuple(new_names), ty=t.ty, body=r)

`f` is emitted as a recursive WhyML function that takes the cell and writes it in place,
with each recursive call made at its own point in source order. Python evaluates call
arguments left to right, so the counter values are the ones the program produces. The
declared frame must be exactly `assigns c`. A precondition must be `True` or exactly
`len(c) >= 1`, and it is carried into the WhyML, so every caller must prove it. Without
it the read `c[0]` cannot be proved, because Python raises IndexError on an empty list.
The f-string, the empty dict and the dict store are uninterpreted functions of their
inputs, so nothing is claimed about the names they build. The call `f(r, c)` recurses on
the result of `S`. It terminates by the file's term-size measure, because `S` has the
proved postcondition that it preserves term size. Any other body shape declines, and so
does any `ensures` other than `True` or any `raises` / `no_exception` claim.
Witnesses: `7230` proves. Each of the following must NOT prove: `7231` (`ensures
False`), `7232` (no `len` precondition), `7233` (a caller forwards an unconstrained
counter), `7234` (the increment comes before the read, declined).

### 7.290 A verified module must COMPILE under CPython, decoded as CPython decodes it (route #465, run #3)

The file used to be read only with `ast.parse`, which stops before CPython's future / symbol-table /
compiler passes, and decoded as UTF-8 whatever its PEP 263 coding cookie says, so red team 38 measured
PROVED `no_exception \all` beside `def f(n): global n`, a `global x` of a parameter in an uncalled helper,
a late `from __future__`, an assignment to / parameter named `__debug__`, `await` outside `async def`,
`yield` in a comprehension or a type alias, `return <value>` in an async generator, a duplicate type
parameter, 25 statically nested blocks, and an `ascii` / unknown coding cookie over non-ASCII text --
modules CPython refuses with SyntaxError before any code runs. RULE (every file, no claim gating): the
file's BYTES are decoded by CPython's own `tokenize.detect_encoding` (cookie, BOM); the decoded text must
equal the verified text (newlines normalised); CPython's own `compile(bytes, file, "exec",
dont_inherit=True)` must succeed. Any SyntaxError / ValueError (or a compiler RecursionError) is REFUSED
(`PYCSL-R465-COMPILE-ERROR`, CPython's message and line). A SyntaxWarning is CPython's default behaviour
(the module runs) and is not refused. Witnesses `7330`-`7341`; control `7369`.

### 7.291 The module dunders are unknown at import (route #469, run #3)

Route #461's top-level run bound `__name__` / `__package__` to the IMPORTED view (the file stem, `''`),
while the file also runs as a script (`'__main__'`, `None`) or inside a package (`'pkg.m'`, `'pkg'`):
`X = 1 // (__name__ != '__main__')`, `__package__.upper()`, `C.__module__ != '__main__'`, `'__main__' not
in repr(C)` PROVED. RULE (inside #461's run): `__name__`, `__package__`, `__spec__`, `__loader__` read as a
name are UNKNOWN (a statement whose value depends on one is refused), except the canonical `if __name__ ==
"__main__":` test, whose arm is not run at import and is not judged (an `else` arm is refused: it binds
names the script view lacks); a class's `__module__` is unknown, and so is any string that exposes the
private module name a class is created under (`repr(C)`, `str(type(C()))`, `f"{C}"`); a factory that
records its caller's module (`namedtuple`, functional `Enum`, `NewType`) is given that private name.
`getattr(o, "__module__")` is refused. Witnesses `7342`-`7349`; control `7370` (`X = __name__` unused,
`C.__name__` / `C.__qualname__`). Code `PYCSL-R461-IMPORT-RAISES`.

### 7.292 A file def's or class's unsynthesized dunders are not read at import (route #470, run #3)

A file def is a placeholder in #461's run and a file class is created on a synthesized namespace, so
`g.__annotations__` (CPython 3.14 evaluates PEP 649 annotations on first access: NameError /
AttributeError / ZeroDivisionError for an undefined / bad annotation) PROVED. RULE (inside #461's run, an
attribute read or `getattr` / `hasattr` with a constant name): `__annotations__` / `__annotate__` /
`__annotate_func__` / `__annotations_cache__` of anything; any dunder except `__name__` / `__qualname__` /
`__func__` / `__self__` / `__wrapped__` of a placeholder def or of an object wrapping one (bound method,
`staticmethod`, `classmethod`, `property`, an object whose static `__wrapped__` is one); `__doc__` /
`__firstlineno__` / `__static_attributes__` / `__type_params__` / `__dataclass_fields__` (its `Field.type`
is m1's source string for an annotation that did not evaluate, a ForwardRef in CPython) of a synthesized class or its
instance,
and the class's `__dict__` -- are REFUSED (`PYCSL-R461-IMPORT-RAISES`). Witnesses `7350`-`7355`, `7373`; control
`7371` (`g.__name__`, `C.m.__qualname__`).

### 7.293 Every class statement is created by CPython, wherever it is nested (route #471, run #3)

#461's creation check reached only the module top level and the class bodies it runs; a class statement
inside a claimed def, a nested def, an un-claimed callee, a method or an `if` arm (`class Z(bool)`, a
`@dataclass` with a mutable default, a NamedTuple `_x` / misordered field, an Enum duplicate, `__slots__`
vs a class variable, `metaclass=5`, an unknown class keyword) PROVED although CPython raises each time the
def runs. RULE (gate: #461's): after the module top level, every class statement whose nearest enclosing
scope is a function is a JOB run by #461's statement machine on the module's final bindings: its
decorators / bases / keywords / body are evaluated, the class created by `types.new_class` and decorated
for real. Unknown there: every name an enclosing function binds (parameters, locals, nested defs /
classes, imports, handler / match names, `global` / `nonlocal` names), every name any function declares
`global`, and a module value of a mutable type (list / dict / set / bytearray / an instance of a file
class); a class whose creation depends on one is refused. Refusal: `PYCSL-R471-LOCAL-CLASS-RAISES` (names
the def). Witnesses `7356`-`7368`; control `7372` (a plain local class, a local dataclass / Enum /
NamedTuple / Exception subclass, a class in a method and in an `if` arm, `__slots__` without conflict).

### 7.190 A call BINDS its callee's signature; `super()` resolves through the file MRO; builtin rows carry cross-constraints; builtin decorators are admitted per definition site (routes #448 / #449 / #450 / #455, run #3)

Red team 36 measured four call-binding families PROVED under `#@ no_exception \all` while CPython raises.
(#449) A call of a FILE function bound its arguments by position / name and silently DROPPED the rest:
`parse(path, mode, True)` over `def parse(path, mode)` lowered `parse path mode`, `total(items, start=1)`
over `def total(items, initial=0)` dropped `start` and used the default, `g(1, 2, b=3)`, a nested def,
a later-defined module function, `C.s(n, n)` of a `@staticmethod`, `self.m(n, n)`. (#450) `super().m(..)`
lowered as an opaque value whether or not a base binds `m`, with any arity, and `super().v` read an
instance field (not visible through `super`). (#448) #441's `max` / `min` row checked each keyword alone,
so `max(a, b, default=0)` passed (CPython ties `default=` to ONE positional). (#455) `@property` /
`@typing.overload` on a module-level or nested `def` were ignored (CPython binds a property object, not
callable, or the overload dummy, NotImplementedError). RULES (allow-list, refuse by default), in EVERY
function that is neither `\trusted` nor `\abstract` -- a claim of the CALLER covers what an unclaimed
callee raises (measured: the mismatch in an unclaimed `h`, `f` claiming `no_exception \all` and calling
`h`, PROVED), so these checks are NOT keyed on the function's own claim:
(#449) a call whose callee resolves statically -- a module-level `def` bound once (no other module
binding, no `global`), a `def` of the function's own scope bound once, `C.m(..)` of a file class,
`self.m(..)` (every file class whose MRO holds the enclosing class: dynamic dispatch), `p.m(..)` of a
parameter annotated with file classes (and their file subclasses) -- reaching a plain / `staticmethod` /
`classmethod` `def` (the argument-forwarding `lru_cache` / `cache` / `contextmanager` kept) must bind
by CPython's algorithm: no surplus positional unless `*args`, every keyword a parameter not already
bound (a positional-only one only into `**kwargs`) or absorbed by `**kwargs`, every parameter without a
default bound (`PYCSL-R449-CALL-SIGNATURE`). A `*` / `**` argument stays route #379's; a callee that does
not resolve is #440 / #441 / #161's. (#450) `super()` is admitted only as the receiver of an attribute,
in a method of a file class (zero-argument: not a staticmethod, not inside a lambda) or as `super(X,
self)`; for every file class S whose MRO holds X, the first class after X in S's MRO whose CLASS
NAMESPACE binds the name (a file class body; a builtin / stdlib base by its real `__mro__`, `object`
last) must exist and a call must bind against it (a file `def` as in #449, a real base method by its
published `inspect.signature`); an unknown MRO or base, a store / `del` through `super()`, or a bare
`super()` value is refused (`PYCSL-R450-SUPER-UNRESOLVED`); `super().__init__(..)` stays route #380's.
(#448) a builtin row carries CROSS-CONSTRAINTS `_XC448` -- keyword k accepted only with lo..hi
positionals: `max` / `min` `default` (1), `sum` / `enumerate` `start` (1), `round` `ndigits` (1), `int`
`base` (1), `replace` `count` (2), `split` `sep` (0) / `maxsplit` (0..1); `pow` with a modulus needs
three `int`s -- checked by #441's table under a claim (`PYCSL-R441-BUILTIN-SIGNATURE`) and in every
function together with the builtin's real `inspect.signature` where CPython publishes one (`len(n, n)`
in an unclaimed callee; `PYCSL-R448-BUILTIN-CROSS-CONSTRAINT`). (#455) `property` / accessors /
`cached_property` / `classmethod` only on a `def` of a class body; the last `def` of a name in its scope
never `@overload`-decorated; no builtin decorator on a `class` statement (`PYCSL-R455-DECORATOR-SITE`,
whatever the claims). Witnesses `6950`-`6969`; controls `6980`-`6984`. Measured cost: 0 corpus /
`python-reference` / mirror / `pycsl_lib` files refused that emitted at base (the 2569-file corpus
emission and the 53 mirrors byte-identical). Residual (not judged): calls of a closure's enclosing-scope
def, of a local bound otherwise than by one `def`, through a receiver whose class is not a parameter
annotation or `self`, or with a `*` / `**` argument; a builtin without a published signature (`int`,
`range`, `max` ...) other than through the cross-constraints and #441's rows; what a builtin / stdlib
base method itself raises when reached through `super()`.

### 7.180 An opaque fallback is refused under the claim it would assume: names, attributes, `@`, module functions, class specs and operand classes (routes #444 / #445 / #446 / #453 / #457 / #458, run #3)

Red team 36 (PROVED `#@ no_exception \all` on main, CPython NameError / AttributeError /
TypeError / OSError) found six ways in which a construct the emitter does not recognise is lowered
to an OPAQUE value with nothing owed, so the claim is verified by assumption: an unbound name
becomes `val constant x` (#444: a misspelt local, a comprehension target read after the
comprehension, an undefined global); a missing attribute becomes an opaque `getattr` or an
always-present record field (#445: `self.cout` for `self.count`, a field stored in one `__init__`
branch, a subclass whose `__init__` skips `super().__init__()`, `n.zz` on an `int`, `P.zzz` on a
class); `a @ b` becomes `unknown_op` (#446); a module function is admitted by its tail when the
tail is one of route #161's builtin METHOD names (`shutil.copy`, `os.replace`,
`itertools.count(<str>)`) and a module attribute the module does not have (`sys.maxint`,
`math.PI`, `os.path.lower`) becomes an opaque `get_<attr>` (#453); `isinstance(x, S)` accepts any
imported name as a class (`sqrt`, `json.loads`, `typing.Any`) (#457); and a binary operator is
lowered by ONE operand's class (`str / str` as a path join, `int + str` as a concatenation) (#458).

ONE RULE, allow-list polarity, refuse by default. The claim that speaks for a function is its own
`#@ no_exception` JOINED with the claim of every claiming function that may call it (by name, by
method name on any receiver, by an attribute load of a method's name, by a constructor `C(..)` --
the `__init__` / `__post_init__` / `__new__` of C's file MRO -- and every dunder method of a file
class), transitively; `\trusted` / `\abstract` functions are not entered. Under that claim, when
it covers the exception CPython raises there:

* (#444, NameError) every name read in the body must resolve to a parameter, a binding of the
  function's own scope (assignment / loop / `with` / `except` / match / import / nested def or
  class / walrus target / `global` / `nonlocal`), an enclosing function's binding, a module-scope
  binding (at any depth of module-level statements, not inside a def / class / lambda /
  comprehension; plus names a function declares `global`) or a builtin of the real `builtins`
  module. A comprehension's, generator's or lambda's targets are scoped to it. Annotations are
  not read; a file with a `*` import is not judged. `PYCSL-R444-UNBOUND-NAME`.
* (#445, AttributeError) an attribute read on a receiver whose class is a FILE class X -- `self`
  of a method of X (not rebound), a class object `X` (or a nested class `P.Inner`), or a receiver
  derived (§7.131) only as file classes -- must be a binding of X's class body over its file MRO
  (a method, property, class attribute, nested class; an annotation without a value binds
  nothing except in a `Protocol`), or for an instance a field DEFINITELY assigned by the
  constructor actually run (route #347's sets: a subclass `__init__` without
  `super().__init__()` runs no base store), or an attribute of every object (of `type` for a
  class object), or a name the file stores through another receiver. A class with a non-file
  base (other than `object` / `Generic` / `Protocol` / `ABC`) or a `__getattr__` /
  `__getattribute__`, and a file that adds attributes dynamically (`setattr`, `__dict__`), are
  not judged. On a receiver derived as exactly ONE builtin class (or the classes an
  `isinstance` guard decided, §7.133), the real class must have the attribute.
  `PYCSL-R445-ATTRIBUTE-NOT-DEFINED`.
* (#446) `@` / `@=` is refused under ANY claim: it has no lowering rule.
  `PYCSL-R446-MATMUL-UNMODELLED`.
* (#453) an attribute chain rooted at a name bound once by an import of a standard-library
  module must exist on the REAL module object at verification time (`hasattr`, a submodule the
  file imports, or a dotted store of the chain in the file) -- AttributeError,
  `PYCSL-R453-MODULE-ATTRIBUTE`; and a CALL of such a chain whose tail is one of route #161's
  method names is admitted (under any claim) only by a (module, function) row with its argument
  classes: `os.path.join` over `str` arguments, `copy.copy` of a builtin value or of a file-class
  instance whose MRO binds no copy-protocol hook, `dataclasses.replace(d)` of exactly a file
  `@dataclass` with no `__post_init__` and no `InitVar`.
  `PYCSL-R453-MODULE-FUNCTION-NOT-ADMITTED`. A non-standard-library module is not judged.
* (#457, TypeError) each imported name / dotted attribute in the class spec of
  `isinstance` / `issubclass` (through tuples and `|`) is resolved on the real standard-library
  module and must be accepted by the real `isinstance(0, o)` / `issubclass(int, o)` (functions,
  `typing.Any` and special forms are refused). `PYCSL-R457-CLASS-SPEC-NOT-A-CLASS`.
* (#458, TypeError) a binary or augmented operator whose two operands are each derived as
  exactly ONE builtin class is admitted iff the real operation on a sample value of each class
  raises no TypeError (`operator.<op>` / `operator.i<op>`): the CPython numeric tower, sequence
  concatenation and repetition, set and dict operators pass; `str / str`, `int + str`,
  `bytes + int` are refused. `str` / `bytes` `%` (formatting, value-dependent), `None` operands
  (route #252), several or underivable classes are not judged.
  `PYCSL-R458-OPERAND-CLASSES`.

The same reach applies to §7.141's BUILTIN FUNCTION rows: in a function that claims nothing
itself but is called by a claiming one, a call `f(..)` of an unshadowed builtin is judged by its row
under the caller's claim (measured: `def g(n: int): return len(n)` called by a claimed `f` proved
under `#@ no_exception \all` on main; witness `6868`, control `6875`). Method / receiver rows
(§7.133 / §7.141 / §7.150) are NOT extended: measured, extending the whole claim test refused 10
PASS corpus files (`super()` receivers and `list.pop` in reached constructors). Route #161's callee
whitelist and the Module 6 obligations still read a function's OWN claim (residual:
`math.factorial(n)` in an unclaimed callee proves).

No emission changes; no axiom. Witnesses `6850`-`6868` (expected FAIL, refused); controls
`6870`-`6875` (expected PASS). Census of the fallback sites:
`getting-better/systematic-soundness-r3/r1-opaque/census-fallback-sites.tsv`.

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

