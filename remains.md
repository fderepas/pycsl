# remains.md — ledger of the four-feature implementation run

Autonomous, depth-first-with-stop-and-flag implementation of `quantification.md`, `lemma.md`,
`inductive.md`, `poly.md`. This is the honest record: **what landed**, **what is deferred and why**,
and — most important — **which soundness logic you should review before trusting it**.

All four Why3 feasibility spikes were run against the installed **Why3 1.8.2** first and passed
(`let rec lemma`, `inductive`, polymorphic `let function`, quantified goals). So no feature is blocked
by the backend; the deferrals below are PyCSL-side scope/risk calls, not Why3 limits.

## Commit trail (this run)
- `37d9a37` quantification P1 — typed quantifier binders
- `9896cb7` lemma functions — `let [rec] lemma` + variant-on-recursion soundness
- `6391813` inductive predicates — P1 single least-fixpoint relation

Each landed with: flagship PASS + negative twins XFAIL, **whole-corpus byte-identical** vs its
baseline (the additive-directive gate), and 5-surface doc-coherency green. Combined new drivers
**0555–0563: 9/9** (4 PASS, 5 XFAIL).

---

## ⚠️ Soundness logic to review before trusting (read this first)

These are the parts where a subtle bug would let the verifier prove `False`. They are tested
(anti-soundness drivers stay failing), but a formal-methods review is the right final check.

1. **lemma — `Module4_SemanticAnalyzer._validate_lemma`** (`9896cb7`). Enforces the
   **variant-on-recursion lynchpin**: a recursive `#@ lemma` without `#@ \variant` is rejected (driver
   `0560`). It detects self-recursion by an AST walk for a `Call` to the function's own name. *Review
   angle:* is the self-call detection complete? It will miss **indirect/mutual** recursion (lemma A
   calls lemma B calls A) — a mutually-recursive lemma group without variants would NOT be caught by
   this check (Why3's own termination check is the backstop, but PyCSL wouldn't pre-reject it). Single
   self-recursion is covered. Also: the `\diverges`-forbidden and ≥1-`ensures` checks are there; the
   **ghost-discipline / body-whitelist / trust-leakage / call-position** checks are NOT (see deferred
   below) — a lemma can currently `assigns` non-`\nothing` or call a `\trusted` function and still be
   accepted, which weakens (but per Why3 does not break) the "no unchecked axiom" guarantee.

2. **inductive — strict positivity is enforced by Why3, NOT by PyCSL** (`6391813`). A
   non-strictly-positive rule is rejected by Why3 at verification ("non strictly positive occurrence",
   driver `0563`), so an unsound least fixpoint **cannot verify**. PyCSL emits the `inductive` decl
   and relies on Why3's check. *Review angle:* this is sound (Why3 is the authority), but there is **no
   PyCSL pre-check** — the diagnostic comes from Why3, not a clean Module-4 error, and PyCSL does not
   independently verify conclusion-shape/arity/exec-position. If you want defense-in-depth, the Module-4
   `_validate_inductive` pass is the deferred item.

3. **quantification — typed binder resolution** (`37d9a37`).
   `Module4._validate_quant_binders` rejects an unresolved binder type (driver `0556`). *Review angle:*
   it does **not** type-check the binder's *use* in the body — e.g. arithmetic on a datatype binder
   (`\forall c: Color; c + 1`) is caught only by Why3's typechecker (driver `0557`), not by Module 4.
   Sound (Why3 catches it) but the diagnostic is a Why3 type error, not a PyCSL one.

**Net:** every soundness-critical violation is caught *somewhere* (PyCSL or Why3); the deferred items
are about making the diagnostic earlier/cleaner and adding defense-in-depth, not about closing a hole
that currently lets `False` through. The one genuine gap to weigh: **mutually-recursive lemmas without
variants** rely solely on Why3's termination check, not PyCSL's.

---

## Per-feature status

### quantification — P1 landed; P2–P4 deferred
**Landed (`37d9a37`):** typed `\forall x: T` / `\exists x: T` binders over a declared `#@ datatype`
or scalar; legacy untyped binders byte-identical (the typed-binder node is inert when
`binder_type=None`). Flagship `0555` (`\forall c: Color; rank(c) in [0,2]`) proves via finite-ADT
case-split. The plan's finite-expansion fast-path was **unnecessary** (the binder discharges directly)
→ not built (YAGNI).

**Deferred (each gated on its own driver, per the plan's YAGNI exit):**
- **P2 — induction over recursive datatypes** + the `#@ by induction on` clause. *Now easier:* the
  `#@ lemma` feature (landed) supplies the induction principle, so a `\forall x: Tree; …` consequence
  can be discharged by a recursive lemma rather than the planned `#@ proof` import.
- **P3 — sets & bounded quantification** (`set[T]` binder, `x in S` desugar to `Fset.mem`, trigger
  inference). The node already carries a `domain` field (unused) for the `in S` form.
- **P4 — objects** (value-mode `\forall o: C; inv_C(o) ==> …` with auto-inserted class invariant;
  ghost-collection mode).
- Multi-binder sugar (`\forall x: T, y: U;`) — single-binder only today.

### lemma — P1 + P2/S3 landed; soundness refinements deferred
**Landed (`9896cb7`):** `#@ lemma` → `let [rec] lemma name (p): unit … = <proof body>`. Non-recursive
(`0558`, SMT) and **recursive/inductive** (`0559`, `to_int(n)>=0` over a datatype, proved by induction,
879 steps) both work. Module-4 `_validate_lemma`: variant-on-recursion + `\diverges`-forbidden +
≥1-`ensures`.

**Deferred — the rest of the §3 soundness pass** (refinements; see review note 1):
- assigns-`\nothing` / return-`None` **ghost discipline** (a lemma may currently declare a non-empty
  `assigns`).
- **proof-body statement whitelist** (§5) — restrict bodies to {self-call, lemma call, `match`,
  `#@ assert`/`#@ check`, `#@ ghost`, `if/else`, `pass`}.
- **no-trust-leakage** — a plain `#@ lemma` body calling a `\trusted` function should require
  `#@ lemma \trusted`.
- **contract-call-position ban** — a lemma name used inside a `#@ requires`/`#@ ensures` *expression*.
- **mutual lemma groups** without per-member variants (the indirect-recursion gap, review note 1).
- `#@ lemma \trusted` shim; `#@ by induction on` empty-body form; cross-module lemma reuse.

### inductive — P1 landed; positivity pre-check + P2–P4 deferred
**Landed (`6391813`):** module-level `#@ inductive p(params):` + `#@ rule <name>: <horn-clause>`
(body reuses the contract-expression grammar incl. typed quantifiers). Single predicate emits
`inductive p t = | Rule : clause` (**no `end`** — verified: an `end` closes the module). Predicate
applications `p(args)` → `(p args)`. Flagship `0562` (`even`, introduction proves `even(4)`); `0563`
(non-positive) rejected by Why3.

**Deferred:**
- **Module-4 `_validate_inductive`** — a clean PyCSL pre-check for strict positivity (polarity walk),
  conclusion-shape, arity, binder typing, and executable-position ban. *Note:* PyCSL's `not` does not
  parse inside a rule clause the way the spec's Horn syntax assumes, so the non-positive negative
  driver uses a nested-implication form; a polarity walk should handle both. Why3 enforces soundness
  meanwhile (review note 2).
- **P2 — mutually-inductive `with` groups** (`inductive wf … with wf_spine …`). The single-predicate
  emitter would extend to a group; needs the `with` keyword and group-wide positivity.
- **P3 — relational form** (reachability) + universally-quantified consequences via `#@ lemma`
  (now feasible — lemma exists).
- **P4 — reflection** (decision function + agreement lemma); coinductive predicates (out of scope).

### poly — STOP-AND-FLAGGED (function half not implemented)
Generic **datatypes already shipped** (feature A5d): `Option[T]`, parametric instantiation; corpus
`0540` passes. The plan's stale "0540 fails today" premise was corrected in `poly.md` §0. The
remaining **function/predicate/lemma** half was not implemented. Concrete obstacles discovered (these
sharpen `poly.md` — they are findings, not guesses):

1. **`pure_ast` PEP-695 parse (S0)** — prototyped (`def f[T](…)` parsing a `[names]` list into
   `type_params`) and then **reverted** to keep the tree clean (a parse-without-emission would be a
   silent footgun). The change is ~20 lines at `pure_ast.py::funcdef` (replace the
   `unsupported("PEP 695 type parameters")` at the `[` check). Bounds/defaults/variadics should stay
   rejected.
2. **Recursive generic datatype payloads don't parse** — `#@ datatype List[T] = LCons(T, List[T])`
   fails: `variant_def` (`Module2_Parser.py`) accepts only bare-CNAME payloads, so the
   type-application `List[T]` in a payload is rejected. (Non-recursive generics like
   `Option[T] = Just(T)` work because `T` is a bare name.) The variant-payload grammar must accept
   `Name[args]` for recursive generics (poly P2). *This was only reachable after the S0 parse — the
   pure_ast error previously masked it.*
3. **Function τ-threading (S1)** — a param typed `xs: List[T]` (T the function's type var) must lower
   to `list 'a`, and the head to `let [rec] function f (xs: list 'a)`. The datatype `_fmt_variant`
   already maps a datatype's own type-params to `'t`; the function path needs the analogous binding in
   `module6_whyml/types.py` / `functions.py`. Not started.
4. **Parametricity check (S2)** — reject inspecting a bare-`T` value (`if t == 0`, `t: T`) — the
   prove-once-reuse guarantee. Not started.

**Recommendation:** poly's function half is a genuine ~3-week multi-stage feature (grammar + τ +
parametricity); its highest-value part (generic datatypes) already exists. Land it as a dedicated
follow-on, starting with obstacles (1)+(2) which together unblock recursive generic *datatypes*, then
(3)+(4) for functions.

---

## Cross-cutting findings (affect future work on these features)
- **SCC ordering ignores contracts.** `sort_functions_by_scc` builds the call graph from function
  *bodies* only, so a function whose **contract** references a pure function (e.g. `ensures rank(c)…`,
  or a lemma whose `ensures` mentions `to_int`) is not ordered after it → `unbound symbol` unless a
  body call creates the edge or source order happens to work. The new drivers sidestep this (the body
  calls the referenced function). A real fix — add contract-reference edges to the call graph — is
  **byte-diff-risky** (could reorder existing files) and was deliberately not attempted. Worth a
  scoped, byte-diff-gated change later; it would make P2/P3 of every feature smoother.
- **`#@ rule` / `#@ inductive` are now reserved-ish words** at contract-start (added to the grammar +
  `_MODULE_PREFIXES`). The contextual LALR lexer keeps them contextual, and the full byte-diff
  confirmed no existing file regressed — but keep it in mind if a future contract wants `rule` as an
  identifier.

## How to verify this run
```
bin/run-reference-tests.sh --pycsl --start-at 555 --stop-at 563     # 9/9 (4 PASS, 5 XFAIL)
bin/doc-coherency.py --check                                         # exit 0 (incl. lemma/inductive/rule)
```
Each feature commit was gated on a whole-corpus emission byte-diff vs its parent (the additive-directive
safety property); those temporary worktrees/dirs were cleaned up after confirming identical.
