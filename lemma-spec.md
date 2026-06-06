# PyCSL Enhancement Proposal: Lemma Functions

**Status:** Draft / high-level design
**Scope:** Contract-expression language, function-level annotations, static semantics, WhyML lowering, soundness
**Audience:** PyCSL maintainers, contract authors
**Depends on:** `#@ datatype` (sum types), `#@ \variant` (termination), `#@ ghost`
**Non-goal:** implementation patches — this specifies *what* must hold, not the diff.

---

## 1. Motivation

Every inductive property over a recursive `#@ datatype` in PyCSL today must be proved **outside**
the toolchain and imported through `#@ proof rocq|lean`, which carries the full weight of the
proof2why3 cross-check, a namespace audit, and a reconciliation manifest. Concretely, all of
these required a Rocq/Lean round-trip:

- `json_mirror(json_mirror(x)) == x` (the `0542.py` involution),
- `sum_numbers(x) == json_sum(x)` (implementation agrees with a declarative spec),
- `all_nonneg(x) ==> sum_numbers(x) >= 0` (a property guarded by a recursive predicate).

Yet Why3 can prove most such facts **without a proof assistant**, using the standard
*lemma-function* technique: a (ghost) function whose contract is the lemma and whose body is the
proof, where recursive self-calls on structurally-smaller arguments supply the induction
hypothesis and termination makes the induction well-founded. Why3 also offers an `induction`
transformation, and SMT backends consume user lemmas directly (Alt-Ergo instantiates
user-defined lemmas via triggers). This is the same mechanism behind Dafny lemmas and the
Frama-C "lemma functions" line of work.

This proposal surfaces lemma functions in PyCSL, giving authors an **in-toolchain** way to
discharge inductive obligations and reducing the dependency on the external `#@ proof` path to
the genuinely hard cases.

## 2. The assume-vs-prove spectrum

Lemma functions fill the gap between PyCSL's two existing mechanisms for establishing a fact:

| Mechanism | Meaning | How established | Emission | Trust |
|---|---|---|---|---|
| `#@ \trusted` | assumed | nothing — taken on faith | `val` (spec only) | full trust |
| **`#@ lemma`** (new) | **proved here** | **Why3 verifies the body (by induction via recursion)** | **`let [rec] lemma`** | **none — checked** |
| `#@ proof rocq\|lean` | proved elsewhere | Rocq/Lean proof, audited + reconciled | `axiom` in preamble | trust the audit |

The key property: a lemma function introduces **no new axiom that isn't itself verified**. Its
conclusion becomes usable only after Why3 has checked the proof body.

## 3. Surface syntax

A lemma function is an ordinary `def` marked with `#@ lemma`, placed immediately before `def`
(like the other function-level annotations, no blank line):

```
lemma_def ::= "#@ lemma"
              ["#@ requires" pred]*          # hypotheses (optional)
              "#@ ensures" pred              # the conclusion (>= 1 required)
              ["#@ \variant" expr]           # induction measure (required if recursive)
              "#@ assigns \nothing"          # mandatory for lemmas
              "def" NAME "(" params ")" "->" "None" ":"
                  proof_body
```

- The function's **parameters are the universally-quantified variables** of the lemma.
- `#@ requires` clauses are the lemma's hypotheses; `#@ ensures` is what it proves.
- The **return type is `None`** (a lemma computes nothing; it returns unit).
- The **body is the proof**: a sequence of ghost-level statements (see §5).
- A lemma that calls itself is **recursive** and MUST carry `#@ \variant` (§7, soundness).

Invocation has two modes:

- **Implicit (axiom + triggers):** once verified, the lemma's contract is available globally as
  `\forall params. requires ==> ensures`, instantiated by e-matching (optionally steered with
  `#@ trigger`, per the quantification proposal).
- **Explicit (call):** writing `lemma_name(args)` as a statement inside another function's body
  forces the instantiation at that program point — the instantiated `ensures` is assumed for the
  rest of the block. Use this when triggers do not fire.

## 4. Worked examples (target state)

**Recursive (inductive) lemma — implementation agrees with spec.** Replaces the
`#@ proof rocq Pycsl.Reference.Json.sum_matches_spec` import we previously needed:

```python
#@ lemma
#@ ensures sum_numbers(x) == json_sum(x)
#@ \variant x
#@ assigns \nothing
def sum_matches_spec(x: Json) -> None:
    match x:
        case JArr(head, tail):
            sum_matches_spec(head)      # IH: sum_numbers(head) == json_sum(head)
            sum_matches_spec(tail)      # IH: sum_numbers(tail) == json_sum(tail)
        case JObj(key, value, rest):
            sum_matches_spec(value)
            sum_matches_spec(rest)
        case JNull():  pass             # base cases: nothing to prove
        case JBool(b): pass
        case JInt(n):  pass
        case JStr(s):  pass
        case JNil():   pass
```

The recursive calls on `head`/`tail` give Why3 the induction hypotheses; `\variant x` makes the
recursion well-founded; Why3 unfolds both `sum_numbers` and `json_sum` one step on each arm and
closes with the IHs. No proof assistant involved.

**Recursive lemma — predicate-guarded property:**

```python
#@ lemma
#@ requires all_nonneg(x) == 1
#@ ensures sum_numbers(x) >= 0
#@ \variant x
#@ assigns \nothing
def sum_nonneg(x: Json) -> None:
    match x:
        case JArr(head, tail):
            sum_nonneg(head)
            sum_nonneg(tail)
        case JObj(key, value, rest):
            sum_nonneg(value)
            sum_nonneg(rest)
        case _: pass
```

**Non-recursive lemma (no induction) — a one-shot algebraic fact:**

```python
#@ lemma
#@ requires a >= 0 and b >= 0
#@ ensures abs_val(a) + abs_val(b) == a + b
#@ assigns \nothing
def abs_sum_nonneg(a: int, b: int) -> None:
    pass            # SMT discharges directly; body is empty
```

**Using a lemma at a call site:**

```python
#@ ensures \result == json_sum(x)
#@ \variant x
#@ assigns \nothing
def sum_numbers_checked(x: Json) -> int:
    sum_matches_spec(x)             # instantiate the bridge here
    return sum_numbers(x)
```

## 5. The proof body (what statements are allowed)

A lemma body is a **ghost proof term**, not a computation. The admissible statements are:

- **Recursive calls** to the same lemma on structurally-smaller arguments (the induction
  hypotheses) — must respect `#@ \variant`.
- **Calls to other (already-verified) lemma functions.**
- **`match` over a `#@ datatype`** to perform case analysis (the proof's case split).
- **`#@ assert P` / `#@ check P`** intermediate proof obligations (existing PyCSL feature).
- **`#@ ghost` declarations/assignments** for proof-local witnesses.
- **`if`/`else`** to case-split on a boolean hypothesis (each branch needs a statement; use
  `pass`).
- **`pass`** for arms/branches where the conclusion is immediate.

A lemma body MUST NOT: return a value, mutate any non-ghost state, call a non-pure function,
perform I/O, or call a `\trusted`/`\diverges` function in a way the conclusion depends on.

## 6. Lowering to WhyML (Module 6 — WhyML Transpiler)

A lemma function lowers to a Why3 **`let lemma`** (or **`let rec lemma`** when recursive):

```
#@ lemma  (non-recursive)        ->  let lemma name (params) : unit
                                       requires { H } ensures { C }
                                     = <proof body>

#@ lemma  (recursive)            ->  let rec lemma name (params) : unit
                                       requires { H } ensures { C } variant { m }
                                     = <proof body>
```

The `lemma` keyword instructs Why3 to (a) require the body to verify against the contract and
(b) make the contract available as a logical fact `forall params. H -> C` to subsequent goals.
Recursive calls lower to recursive calls, so Why3 derives the induction hypothesis from the
function's own (verified, terminating) contract. Mutually-recursive lemma groups lower to a
`let rec lemma … with lemma …` group (the same SCC machinery already used for mutually-recursive
functions in corpus 0534).

Explicit call sites lower to ordinary calls, which Why3 treats as instantiations that assume the
postcondition at that point.

## 7. Soundness (mandatory rules)

Lemma functions are powerful enough to prove `False` if misused, so the following are
**soundness requirements**, enforced by Module 4, not style preferences:

1. **The body must verify.** A lemma whose proof body fails to discharge is a hard error. There
   is no `--no-proof` shortcut for *claiming* a lemma holds; `--no-proof` may generate the WhyML
   but the lemma's conclusion is not usable until a proving run succeeds.
2. **Recursive lemmas require a strictly-decreasing `#@ \variant`.** This is the lynchpin: an
   ill-founded recursion is an unsound "proof by assuming the goal." Every recursive (IH) call
   must be on an argument strictly smaller under the variant's well-founded order. Missing or
   non-decreasing variant ⇒ rejected.
3. **`#@ \diverges` is forbidden on a lemma.** A non-terminating lemma proves nothing and would
   be unsound as an axiom. `lemma` + `\diverges` ⇒ error.
4. **Ghost discipline.** A lemma is `assigns \nothing`, has return type `None`, is erased at
   extraction, and may not affect any runtime value. It cannot be called from non-ghost code in a
   way that changes observable behaviour.
5. **No silent trust leakage.** A lemma body may call a `\trusted` function only if the lemma is
   itself marked `#@ lemma \trusted` (assumed, warned) — otherwise the trusted dependency would
   smuggle an unverified axiom into a "proved" lemma. A plain `#@ lemma` body must rest only on
   verified facts.
6. **Vacuity warning (advisory).** A lemma with unsatisfiable `requires` is vacuously provable
   and useless; Module 4 SHOULD warn (analogous to the non-vacuity witness for type invariants).

## 8. Static semantics (Module 4 — Semantic Analyzer)

A lemma function is well-formed iff: it carries `#@ lemma`, exactly one or more `#@ ensures` and
`assigns \nothing`; its return type is `None`; its body contains only admissible statements
(§5); if it is recursive it carries a strictly-decreasing `#@ \variant` (§7.2); it is not
`\diverges`; and every function it calls is pure or an already-declared lemma. Explicit lemma
calls are permitted only in ghost/proof position, never inside a `#@ requires`/`#@ ensures`
expression (lemmas are invoked, not referenced as terms; their *conclusions* enter contracts via
the pure functions they mention).

## 9. Module impact

| Module | Change |
|---|---|
| **Module 2 — Parser** | recognize the `#@ lemma` marker and `#@ lemma \trusted` variant |
| **Module 3 — Weaver** | attach the lemma marker to the `def` node (line-number matching as today) |
| **Module 4 — Semantic Analyzer** | enforce §7–§8: return type, ghost discipline, variant-on-recursion, body-statement whitelist, call-position rules |
| **Module 5 — IR Emitter** (`ir_schema`) | a lemma node flag + proof-body representation distinct from a value-returning body |
| **Module 6 — WhyML Transpiler** | emit `let [rec] lemma … : unit … = body`; SCC grouping for mutual lemma sets; map explicit calls to instantiations |
| **proof2why3 / audit_proof** | unchanged; lemma functions deliberately *bypass* the external-proof audit path |

## 10. Relationship to `#@ proof` (external proofs)

Lemma functions and `#@ proof` are complementary, with a clear preference order:

1. **Prefer `#@ lemma`** when Why3 + SMT (with induction via recursion) can discharge the body.
   This keeps the proof in-repo, machine-checked on every run, and free of the Rocq/Lean
   toolchain and reconciliation manifest.
2. **Fall back to `#@ proof rocq|lean`** only when the proof genuinely exceeds Why3's automation
   — e.g. it needs higher-order reasoning, heavy nested induction, or a result that no SMT
   backend will close even with the lemma in hand.
3. A migration path: a fact first imported via `#@ proof` can later be **re-internalised** as a
   `#@ lemma` once a Why3-dischargeable proof body is found, removing the external dependency.

## 11. Phasing

| Phase | Delivers | Risk |
|---|---|---|
| **P1 — Non-recursive lemmas** | `let lemma`, straight SMT proof of the body (often empty); call-site instantiation | low; no induction |
| **P2 — Recursive (inductive) lemmas** | `let rec lemma` + mandatory variant; recursion-as-IH over `#@ datatype` | medium; soundness hinges on the variant check |
| **P3 — Mutual lemma groups + triggers** | `let rec lemma … with …` for mutually-recursive datatypes; `#@ trigger` control of implicit instantiation | medium; trigger brittleness |
| **P4 — Integration & ergonomics** | `#@ lemma \trusted` shim, `#@ by induction` (Why3 transformation as an alternative to explicit recursion), cross-module lemma reuse | medium |

Each phase ships corpus drivers in the existing numbering style: a PASS (the lemma discharges and
is used) and FAIL twins — a recursive lemma **without** a variant (must be rejected as unsound),
a lemma with a false `ensures` (body fails), and a vacuous-`requires` lemma (warned).

## 12. Validation

- **Soundness gate (critical):** a dedicated anti-soundness suite proves the enforcement works —
  e.g. a recursive "lemma" missing its variant, or recursing on a non-smaller argument, must be
  **rejected**, demonstrating that lemma functions cannot be used to derive `False`.
- **Discharge corpus:** the three motivating examples (involution, sum-vs-spec, predicate-guarded
  bound) each pass *without* a `#@ proof` import, confirming the external dependency is removed.
- **Erasure check:** lemma calls and bodies disappear under extraction; no lemma influences a
  computed result.
- **Regression vs `#@ proof`:** files previously relying on imported lemmas continue to verify
  when those lemmas are re-expressed as `#@ lemma` functions.

## 13. Open questions

1. **`induction` transformation vs explicit recursion.** Why3 can sometimes discharge an
   inductive goal with its `induction` tactic and an *empty* body. When should PyCSL prefer
   `#@ by induction on x` over an explicit recursive proof body, and can both be offered?
2. **Custom well-founded orders.** Lemmas whose induction is not structural need
   `#@ \variant (expr, ordering)` with a named order — what is the vocabulary of built-in orders,
   and how are user orders justified?
3. **Cross-module lemma libraries.** Reusing a proven lemma across files points at the
   theory-cloning feature; should a `#@ lemma` be exportable/importable as a verified theory?
4. **Lemmas over machine arithmetic.** How do lemma bodies interact with `#@ assumes
   bounded_int(N)` — are IHs available under overflow-guarded arithmetic?
5. **Quantified lemma conclusions.** Once typed quantifiers land (companion proposal), a lemma
   may `ensures \forall y: T; …`; the instantiation/trigger story for such conclusions needs to
   be unified with that proposal.
