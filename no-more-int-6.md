# Plan: no-more-int Part 6 — the residual after Part 5

Standalone successor to `no-more-int-5.md`. Part 5 cleared almost the entire backlog: the A2b
framing-lemma *demonstration* (Gaps 1–5), the sum-type extensions (A5a-residual, A5b, A5c, A5d), the
tractable half of A1-residual (nested-map dict values), A3 chain-length, the A6(a) coercion
retirement, and the A7 documentation. What is left is **one substantial track** (the A2b ownership
frontend), **one design-blocked item** (A1-residual array values), and a **handful of low-value,
build-on-demand pieces**. Each item below states its **gate/driver**, **risk**, and a **verdict**.

The Gate-A demand-driver discipline still holds: commit a `# pycsl-expected: FAIL` driver first,
implement to flip it, then full-corpus sweep + emission-identical byte-diff as gates.

## Where we are after Part 5 (all committed + pushed)

| Landed in Part 5 | Drivers |
|---|---|
| **A2b** framing-lemma demonstration — `\permutation` operator, imported `permut_refl`/`rev_permutation` axioms (Rocq+Lean cross-validated), reversal-is-a-permutation | 0537–0539 |
| **A1-residual** nested-map dict values (`Dict[str, Dict[int,int]]`, the json `JObj` enabler) | 0532 |
| **A3** bounded `chain` length | 0530 |
| **A5a-residual** mutually-recursive datatypes **and** functions | 0533/0534 |
| **A5b** match captures in contracts (projectors `\is_ctor` / `\payload`) | 0541 |
| **A5c** guarded + or + nested match patterns | 0531/0535/0536 |
| **A5d** parametric datatypes `Option[T]` | 0540 |
| **A6(a)** retire dead `self`/record→int coercion · **A7** document benign collapses | — |

The supporting docs: `docs/handling-aliasing.md` (the position), `docs/framing-lemma-demonstration.md`
(the realized 0537–0539 demo), `a2b-stage4-scaffold.md` (the build log).

---

# PART A — the substantial remaining track: A2b ownership / alias-check frontend

**Status:** the framing-lemma *research demonstration* is done (Part 5); the **memory model that lets
real mutate-through-alias Python verify — or be rejected cleanly — is NOT started.** This is the
multi-week piece, and the only large item left in the whole no-more-int program.

**The decided design (from `docs/handling-aliasing.md`):** restrict aliasing by default (ownership,
the Creusot move), provide region-logic as an explicit escape hatch (not IDF/SL), and route the hard
reachability cases through proof-assistant-imported framing lemmas (the §3 mechanism, now
demonstrated). What remains to *build* is the front half of that — stages 1–2 of the near-term plan:

### A2b-1 — specify the ownership discipline (design, ~1–2 wk)
Decide precisely what "no aliasing across method boundaries" means in Python terms:
- parameter **ownership transfer** vs **stack-scoped borrowing**;
- what `self` ownership means for methods;
- how **immutable values** (which may alias freely and safely — `int`, `str`, frozen/record-by-value)
  are distinguished from mutable ones (`list`, `dict`, `set`, mutable objects).
Reference points: Creusot's borrow model, Dafny's `modifies` discipline.
- **Deliverable:** a written discipline spec (a `docs/` note) + the precise accept/reject rule.
- **Verdict:** prerequisite for A2b-2; no code, but the load-bearing decision.

### A2b-2 — the ownership/alias checker as a frontend pass (~3–4 wk)
Before WhyML emission, run an analysis that **rejects programs violating the discipline** with a
clear diagnostic — the gatekeeper that lets everything downstream stay in Why3's native region
system. (Per-program-point alias-graph computation, à la the Kotlin-on-Viper approach, is one
concrete recipe.) Under the discipline, the existing `assigns` clause gains a precise meaning — the
footprint of an *owned* region — **with no syntax change**.
- **Gate / drivers:** (a) a `# pycsl-expected: FAIL` program that mutates through an alias, **rejected
  with the ownership diagnostic** (a new *semantic-error* negative test, like 0284); (b) a sibling
  owned-transfer program that **verifies**; (c) the existing `assigns`-using corpus continues to
  verify **byte-identically** (this is the regression gate — the checker must not change accepted
  programs' emission).
- **Risk:** high — a sound, precise alias analysis is real engineering, and the diagnostics must be
  crisp (a false reject is worse than a false accept here). Stage it: start with intra-procedural
  aliasing, then parameter passing, then `self`.
- **Verdict:** the genuine remaining work on A2b. **Pull only when arbitrary-mutation Python is in
  scope** (e.g. a self-hosting milestone over pycsl's own mutating passes). Until then, record param
  mutation stays out of scope (the value-semantics boundary, documented).

### A2b — cheap de-risk available NOW (no ownership checker needed)
Before the big build, the framing-lemma mechanism can be exercised further on **immutable** data to
keep proving out `axiom_from` for framing without any aliasing work — e.g. a `permut` **transitivity**
or **`Counter`/multiset** lemma, or the A4 json round-trip (Part C). These need only a registry entry
+ paired proofs, exactly like 0538/0539.

---

# PART B — design-blocked: A1-residual array-valued dicts (the seq-model)

**Status:** `Dict[str, List[int]]` (array-*valued* dicts) is **parked behind Why3's mutable-aliasing
wall** — a mutable `array int` cannot live inside a pure `map` (the spike in no-more-int-5
§A1-residual; "instantiates pure type variable 'v with a mutable type array"). The nested-*map* value
(`Dict[str, Dict]`) is done (0532) because `map` is pure; the *array* value needs an immutable model.

**What it needs — the seq-model:** model the dict's list value as an immutable **`Seq.seq int`**
(`map κ (option (seq int))`), with:
- an **array→seq snapshot** at the store site (`d[k] = xs` stores a *copy* of `xs`'s current content —
  a sound under-approximation, since faithful aliasing is out of scope by the A2b boundary);
- `Seq.length` at the read (`len(d[k])`), `Seq.get` for element reads.
The crux is the array→seq conversion (Why3 has no implicit one; build it from the array's logical
model `a.elts`/`a.length`, or an abstract `val function array_to_seq`).
- **Gate / driver:** `Dict[str, List[int]]` with `d[k] = xs` then `len(d[k]) == len(xs)` over the seq
  model (the FAIL driver 0530-style that the spike reverted).
- **Risk:** medium-high — new `seq` plumbing through the dict path; interacts with the value-semantics
  boundary (snapshot semantics must be documented).
- **Verdict:** **build only if a dict-of-lists driver appears** AND the snapshot semantics is
  acceptable. Composes with the A2b ownership decision (both are the value-semantics question).

---

# PART C — low-value / build-on-demand (each strictly on a concrete driver)

### A6(b) — remove the dead dict key/value→int defensive coercion
The dict key/value→int erasure is now a *guarded call-site pass-through* (dead for typed dicts post
T1.1/T1.2), not a `_coerce_to_int` category. Removing the guarded call is byte-identical but only
*defensive-net* removal. **Parked behind A1-residual** (a typed non-int/non-string value would
exercise it). Low value; sweep-gated when taken.

### A3-residual — the rest of eager itertools
Only `chain` length is modeled (0530). `islice` / `product` / `combinations`, and chain
*membership/content*, are unbuilt. Lazy/infinite (`cycle`/`count`/`repeat`, `yield`) stays **out of
scope** (no SMT-tractable stream model). *Driver each:* the relevant length/membership contract.
**Low value; build only on a driver.**

### A4 — json round-trip (`loads(dumps(x)) == x`)
**Recast (Part 5): not a research wall — an `axiom_from` application.** Prove `decode ∘ encode = id`
(bounded depth) in Rocq/Lean over a recursive `#@ datatype Json = …` (uses A5a recursive datatypes +
A1's nested-map `JObj`, both done), cross-check, import via `#@ proof` — *exactly the 0538/0539
shape*. The verified-serialization canon (**Narcissus**, POPL 2019; **EverParse/3D**) structures the
proof. **Default don't-build absent a json-content driver**; when pulled, it is ordinary bridge usage
(registry entry + paired proofs + a `json.py` over the recursive datatype), the natural *second*
demonstration of the framing-lemma mechanism after permutation.

### Small follow-ons inside already-done items
- **A5b** — `\payload` over a **type-parameter** payload (currently needs the `\is_ctor` guard because
  the fall-through `_` arm is ill-typed for `'a`); and **multi-payload index selection** (`\payload(x,
  Pair, 1)` — today only the first payload). Add when a driver needs them.
- **A5c** — **or-patterns that bind a payload across alternatives** (`case Some(n) | Wrapped(n)`),
  which Why3 requires to bind identically in each alternative. Flat or-patterns and nested patterns
  are done; this binding variant is a follow-on.
- **A5a** — *mutually-recursive datatype over json* (`JObj` ↔ `Json`) falls out of A4 above.

---

## Out of scope (documented, do not build)
- Lazy/infinite iterators (`cycle`/`count`/`repeat`, generators/`yield`) — no SMT-tractable stream model.
- Adopting **IDF/SL as a foundation** — re-implementing Viper inside Why3 (the Cameleer anti-pattern);
  if full IDF expressiveness is ever needed for a Python fragment, target Viper for *that fragment*.
- Faithful **mutate-through-alias** semantics beyond the ownership discipline — the value-semantics
  boundary, documented in `docs/handling-aliasing.md`.

## Suggested order (by leverage)
1. **Cheap A2b de-risk / A4** — another imported framing lemma (transitivity, or the json round-trip)
   if a driver appears: registry + paired proofs only, no new machinery. Highest ratio of
   demonstration value to effort.
2. **A1-residual seq-model** — only if a dict-of-lists driver appears and snapshot semantics is
   acceptable; then **A6(b)** falls out (the typed value exercises the now-removable coercion).
3. **A2b-1 then A2b-2** — the ownership discipline spec, then the alias-check frontend. The large
   item; pull when arbitrary-mutation Python (or the self-hosting milestone) genuinely needs it.
4. **A3-residual** — each itertools member strictly on its own driver; lowest value.

## Critical files (re-derive line numbers by symbol)
- A2b frontend: a NEW pass near `Module4_SemanticAnalyzer.py` (the ownership/alias checker would run
  before WhyML emission); `assigns` handling in `module6_whyml/statements.py`.
- A1-residual seq: `Module4_SemanticAnalyzer.py` (`_get_dict_value_type`), `module6_whyml/statements.py`
  (dict-set), `expressions.py` (dict read / `len`), a new `seq`-snapshot op.
- A4 / framing lemmas: `module6_whyml/preamble.py` (`_AXIOM_REGISTRY` / `_AXIOM_FUNCTIONS` /
  `_emit_preamble_axioms`); `Module2_Parser.py` (`\permutation` and any new spec op); the `#@ proof`
  cross-check (`audit_proof.py`, `bin/proof2why3-*`, `src/formal-semantics/{rocq,lean}/`).
- A5b/A5c/A5d follow-ons: `module6_whyml/expr_ghost_spec_ops.py` (`\payload`/`\is_ctor`),
  `module6_whyml/stmt_control_flow.py` (match lowering), `module6_whyml/preamble.py` (`_fmt_variant`).

## References
- Position: `docs/handling-aliasing.md` (the four-part frame/aliasing design + Creusot proximity).
- Demonstration: `docs/framing-lemma-demonstration.md` (0537–0539, the realized `axiom_from`-for-framing).
- Build log: `a2b-stage4-scaffold.md`. Predecessors: `no-more-int-{3,4,5}.md`.
- Canon: Denis et al. *Creusot* (ICFEM 2022); Banerjee–Naumann–Rosenberg *Regional Logic* (ECOOP
  2008); Delaware et al. *Narcissus* (POPL 2019); Filliâtre–Paskevich *Why3* (ESOP 2013).
