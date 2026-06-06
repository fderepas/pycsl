# remains.md — ledger of the four-feature implementation run

Autonomous, depth-first-with-stop-and-flag implementation of `quantification.md`, `lemma.md`,
`inductive.md`, `poly.md`. This is the honest record: **what landed**, **what is deferred and why**,
and — most important — **which soundness logic you should review before trusting it**.

All four Why3 feasibility spikes were run against the installed **Why3 1.8.2** first and passed
(`let rec lemma`, `inductive`, polymorphic `let function`, quantified goals). So no feature is blocked
by the backend; the deferrals below are PyCSL-side scope/risk calls, not Why3 limits.

## Commit trail (this run)
- `37d9a37` quantification P1 — typed quantifier binders
- `9896cb7` lemma functions — `let [rec] lemma` (its commit/docs call the variant check a "soundness
  lynchpin"; **that wording is wrong** — see review note 1 / decision A below)
- `6391813` inductive predicates — P1 single least-fixpoint relation

Each landed with: flagship PASS + negative twins XFAIL, **whole-corpus byte-identical** vs its
baseline (the additive-directive gate), and 5-surface doc-coherency green. Combined new drivers
**0555–0563: 9/9** (4 PASS, 5 XFAIL).

---

## ⚠️ Soundness logic — review status (read this first)

These are the parts where a subtle bug would let the verifier prove `False`. They are tested
(anti-soundness drivers stay failing). **Review outcome:** notes 2 (inductive positivity) and 3
(quantification binder use) are **agreed/settled** — Why3 is the accepted enforcer, no PyCSL pre-check
planned. Note 1 (lemma variant check) is **decided** — drop it (decision A), Why3 owns termination.
The remaining open soundness items are the *deferred lemma checks* called out in note 1
(ghost-discipline / body-whitelist / trust-leakage / call-position).

1. **lemma — `Module4_SemanticAnalyzer._validate_lemma`** (`9896cb7`).
   **CORRECTION (was mislabeled a "soundness lynchpin" — it is not).** The variant-on-recursion check
   (reject a recursive `#@ lemma` lacking `#@ \variant`, driver `0560`) was empirically tested against
   Why3 1.8.2 and adds **no soundness**:
   - A structurally-recursive lemma with **no** variant clause **still proves** — Why3 *infers* the
     structural variant.
   - The genuinely unsound case — a non-terminating recursion claiming `false` — is **rejected by Why3**
     ("Cannot prove termination"), so its conclusion is never exported.

   So Why3's termination check is the real enforcer. Worse, the PyCSL check is **over-restrictive**: it
   rejects the structurally-recursive lemmas Why3 would happily prove, so `0560` is not an *unsound*
   lemma but a *provable-but-unannotated* one — mislabeled as a soundness negative.

   **DECISION — go with option A (drop the check; trust Why3).** Pending code change (not yet applied):
   - Remove the variant-on-recursion branch from `_validate_lemma` (keep `\diverges`-forbidden and
     ≥1-`ensures`). Recursive lemmas then behave exactly like Why3 — structural recursion needs no
     variant; ill-founded recursion fails the termination VC.
   - **Retarget driver `0560`** to the *true* boundary: a non-terminating lemma claiming `false`, which
     stays FAIL because Why3 can't prove termination — a genuine "you cannot prove `False` by
     ill-founded recursion" demonstration. Update its docstring + the commit/annotations wording that
     called the variant check a soundness lynchpin.

   *Independent of A:* the `\diverges`-forbidden and ≥1-`ensures` checks remain; the **ghost-discipline
   / body-whitelist / trust-leakage / call-position** checks are still NOT implemented (see deferred
   below) — a lemma can currently `assigns` non-`\nothing` or call a `\trusted` function and be
   accepted, which weakens (but per Why3 does not break) the "no unchecked axiom" guarantee. *These* are
   the real lemma-soundness refinements to weigh, not the variant check.

2. **inductive — strict positivity is enforced by Why3, NOT by PyCSL** (`6391813`). **AGREED (user) —
   settled, no PyCSL pre-check planned.** A non-strictly-positive rule is rejected by Why3 at
   verification ("non strictly positive occurrence", driver `0563`), so an unsound least fixpoint
   **cannot verify**. PyCSL emits the `inductive` decl and relies on Why3's check; that is the accepted
   design (Why3 is the authority), consistent with how the lemma variant check resolves (decision A).
   A Module-4 `_validate_inductive` pre-check (positivity / conclusion-shape / arity / exec-position) is
   therefore **not on the soundness path** — only an optional earlier/cleaner-diagnostic nicety if ever
   wanted, not a gap.

3. **quantification — typed binder resolution** (`37d9a37`). **AGREED (user) — settled.**
   `Module4._validate_quant_binders` rejects an unresolved binder *type* (driver `0556`). It does not
   type-check the binder's *use* in the body — arithmetic on a datatype binder (`\forall c: Color;
   c + 1`) is caught by Why3's typechecker (driver `0557`), which is the accepted enforcer. No PyCSL
   body-type pre-check is planned; the Why3 type error is sufficient.

**Net:** every soundness-critical violation is caught *somewhere* (PyCSL or Why3); the deferred items
are about making the diagnostic earlier/cleaner and adding defense-in-depth, not about closing a hole
that currently lets `False` through. **Termination/well-foundedness for recursive lemmas is owned by
Why3** (it infers structural variants and rejects ill-founded recursion) — including the
mutually-recursive case — so PyCSL's variant check was redundant *and* over-restrictive (decision A
above drops it). The real lemma-soundness items to weigh are the deferred ghost-discipline /
body-whitelist / trust-leakage / call-position checks.

---

## Per-feature status

### quantification — P1 landed; P2–P4 QUEUED for development (Gate-A-driver-first)
**Landed (`37d9a37`):** typed `\forall x: T` / `\exists x: T` binders over a declared `#@ datatype`
or scalar; legacy untyped binders byte-identical (the typed-binder node is inert when
`binder_type=None`). Flagship `0555` (`\forall c: Color; rank(c) in [0,2]`) proves via finite-ADT
case-split. The plan's finite-expansion fast-path was **unnecessary** (the binder discharges directly)
→ not built (YAGNI).

**Decision: develop P2 → P3 → P4, each Gate-A-driver-first** (write the `# pycsl-expected: FAIL`
demand-driver, confirm it fails for the right reason, implement until it flips, byte-diff + sweep +
docs). Not yet done in code — what follows is the plan plus what's been *probed so far*.

- **P2 — induction over recursive datatypes.** A `\forall x: Nat; …` binder already *parses and emits*
  (P1 resolves any datatype binder, recursive or not). The open question was whether the **discharge**
  composes for free from P1 + the landed `#@ lemma` (a recursive lemma proves the universal, whose
  exported fact then closes the contract's quantified goal). **Probed — it does NOT compose for free.**
  A driver with `def all_nonneg() -> int: #@ ensures \forall x: Nat; to_int(x) >= 0` + a recursive
  lemma `to_int_nonneg` emitted `all_nonneg` (whose contract references `to_int`) **before** `to_int`
  and the lemma → Why3 `unbound function or predicate symbol 'to_int'`. **Root cause = the cross-cutting
  SCC contract-ordering issue (below): `all_nonneg`'s body has no calls, so the SCC sort placed it
  first, ahead of the function/lemma its *contract* depends on.** So **P2 is gated on the SCC fix**
  (add contract-reference edges to the call graph) — which is byte-diff-risky and must itself be
  byte-diff-gated. Until then, the only workaround is to force a body edge (the function calling the
  referenced function/lemma), which is unnatural for a pure quantified-fact wrapper. *Conclusion: P2 is
  not "free composition"; its first real task is the SCC ordering fix.* The `#@ by induction on` clause
  (drive Why3's `induction_ty_lex` from the proof harness) remains an optional alternative to the
  lemma route.
- **P3 — sets & bounded quantification** (`set[T]` binder, `x in S` desugar to `Fset.mem`, trigger
  inference). The node already carries an (unused) `domain` field for the `in S` form. Genuinely new
  code: a `needs_fset` preamble import (`use set.Fset`), the `\forall x: T in S; P` ⇒
  `forall x. Fset.mem x S -> P` desugar from `domain`, Module-4 `S: set[T]` check, and trigger
  inference (the brittle part — may itself be split out). Not started.
- **P4 — objects** (value-mode `\forall o: C; inv_C(o) ==> …` with the class invariant
  auto-inserted as the antecedent so the binder ranges only over invariant-satisfying shapes;
  ghost-collection mode via P3's `Fset`). The binder `o: C` already resolves (P1 admits class names);
  the new work is the auto-inserted invariant guard. Not started.
- Multi-binder sugar (`\forall x: T, y: U;`) — single-binder only today; desugar to nested binders.

**Suggested order given the probe:** land the **SCC contract-ordering fix first** (it unblocks P2 and
smooths P3/P4, and is independently the right fix — see cross-cutting findings), each behind its own
byte-diff gate; then P2 driver, then P3, then P4.

### lemma — P1 + P2/S3 landed; soundness refinements deferred
**Landed (`9896cb7`):** `#@ lemma` → `let [rec] lemma name (p): unit … = <proof body>`. Non-recursive
(`0558`, SMT) and **recursive/inductive** (`0559`, `to_int(n)>=0` over a datatype, proved by induction,
879 steps) both work. Module-4 `_validate_lemma`: `\diverges`-forbidden + ≥1-`ensures` + (currently)
variant-on-recursion — **the last is slated for removal under decision A (review note 1):** it adds no
soundness (Why3 owns termination + infers structural variants) and is over-restrictive; driver `0560`
is to be retargeted to a non-terminating lemma (the true boundary).

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

### inductive — P1 landed; positivity owned by Why3 (agreed); P2–P4 deferred
**Landed (`6391813`):** module-level `#@ inductive p(params):` + `#@ rule <name>: <horn-clause>`
(body reuses the contract-expression grammar incl. typed quantifiers). Single predicate emits
`inductive p t = | Rule : clause` (**no `end`** — verified: an `end` closes the module). Predicate
applications `p(args)` → `(p args)`. Flagship `0562` (`even`, introduction proves `even(4)`); `0563`
(non-positive) rejected by Why3.

**Deferred:**
- **Module-4 `_validate_inductive`** — **NOT a soundness item (agreed, review note 2):** Why3 owns
  strict positivity. A PyCSL pre-check (polarity walk, conclusion-shape, arity, binder typing,
  executable-position ban) is only an optional earlier/cleaner-diagnostic nicety, not planned. *Note
  if ever built:* PyCSL's `not` does not parse inside a rule clause the way the spec's Horn syntax
  assumes, so the non-positive negative driver uses a nested-implication form; a polarity walk should
  handle both.
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
- **SCC ordering ignores contracts. → now a HARD BLOCKER for quantification P2.**
  `sort_functions_by_scc` builds the call graph from function *bodies* only, so a function whose
  **contract** references a pure function (e.g. `ensures rank(c)…`, or `ensures \forall x: Nat;
  to_int(x) >= 0`) is not ordered after it → `unbound symbol` unless a body call creates the edge or
  source order happens to work. The landed P1/lemma/inductive drivers sidestep this (their bodies call
  the referenced function). But the **P2 probe hit it head-on**: a pure quantified-fact wrapper has no
  body calls, so it is ordered ahead of the `to_int`/lemma its contract depends on and fails to compile
  — see the P2 entry above. A real fix — add contract-reference edges to the call graph (so a function
  is ordered after every pure symbol its requires/ensures/variant mention) — is **byte-diff-risky**
  (could reorder existing files) and was deliberately not attempted in this run. **It is now on the
  critical path for P2** and should be the first, byte-diff-gated change when P2 development starts; it
  also smooths P3/P4.
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
