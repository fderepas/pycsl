# remains-2.md — consolidated status & plan for the companion-feature run

Single source of truth, merging the four-feature ledger (`remains.md`) and the quantifier-discharge
plan (`scc3.md`). Covers the autonomous, depth-first-with-stop-and-flag implementation of
`quantification.md`, `lemma.md`, `inductive.md`, `poly.md` and the supporting ordering/discharge fixes
(`scc.md` contract-reference edges, `scc2.md` `#@ uses`, `scc3.md` binder/domain type propagation).

**What landed** (all four Why3 1.8.2 feasibility spikes passed first — `let rec lemma`, `inductive`,
polymorphic `let function`, quantified goals — so no deferral is a backend limit):

- **quantification — P1, P2, P3 (sets), P4 (value mode): all landed and discharging.**
- **lemma — P1 + P2/S3 (inductive) landed.**
- **inductive — P1 (single predicate) landed.**
- **poly — datatypes already shipped (A5d); the function/predicate/lemma half is stop-and-flagged.**

Every landed feature was gated on: flagship PASS + negative twins XFAIL, **whole-corpus byte-identical
emission** vs its parent (the additive-directive safety property), and 5-surface doc-coherency green.

## Commit trail
- `37d9a37` quantification P1 — typed quantifier binders (`\forall x: T`)
- `9896cb7` lemma functions — `let [rec] lemma` (+ Module-4 `_validate_lemma`; see Soundness note 1)
- `6391813` inductive predicates — P1 single least-fixpoint relation
- `ff11f18` scc.md — contract-reference edges in the SCC call graph
- `b68373b` scc2.md — `#@ uses` lemma-citation ordering → quantification P2
- `77fe1bd` scc3.md Phases A+B — quantification P3 (sets) + P4 (value mode)

Corpus drivers added: **0555–0569** (quantification 0555-0557, lemma 0558-0561, inductive 0562-0563,
scc 0564-0565, P4/P3 0566-0569).

---

## ⚠️ Soundness review status (read first)

Parts where a subtle bug would let the verifier prove `False`. **Outcome: all three reviewed and
settled.** The only *open* soundness work is the deferred lemma checks in note 1.

1. **lemma `_validate_lemma` variant-on-recursion check — mislabeled; DECISION A (drop it).**
   Empirically (Why3 1.8.2): a structurally-recursive lemma with **no** `#@ \variant` still proves
   (Why3 infers the structural variant), and a non-terminating recursion claiming `false` is **rejected
   by Why3** ("Cannot prove termination"). So Why3 owns termination/well-foundedness; the PyCSL check
   adds **no soundness** and is **over-restrictive** (it rejects provable lemmas) — driver `0560` is a
   *provable-but-unannotated* lemma mislabeled as a soundness negative.
   - **Pending code:** remove the variant-on-recursion branch from `_validate_lemma` (keep
     `\diverges`-forbidden + ≥1-`ensures`); **retarget `0560`** to a non-terminating lemma claiming
     `false` (stays FAIL via Why3's termination VC — the *true* boundary); fix the commit/annotations
     wording that called it a "soundness lynchpin".
   - Dropping it also closes the *mutual-recursion* gap (the check only caught direct self-recursion;
     Why3 covers all cases).
2. **inductive strict positivity — Why3 is the enforcer (AGREED, settled).** A non-strictly-positive
   rule is rejected by Why3 ("non strictly positive occurrence", `0563`); PyCSL emits the `inductive`
   decl and relies on that. A Module-4 `_validate_inductive` pre-check is **not on the soundness path**
   — only an optional cleaner-diagnostic nicety, not planned.
3. **quantification typed-binder use — Why3 is the enforcer (AGREED, settled).**
   `_validate_quant_binders` rejects an unresolved binder *type* (`0556`); misuse of a datatype binder
   (e.g. arithmetic, `0557`) is caught by Why3's typechecker. No PyCSL body-type pre-check planned.

**Net:** every soundness-critical violation is caught somewhere (PyCSL or Why3). The genuine remaining
lemma-soundness refinements are the deferred ghost-discipline / body-whitelist / trust-leakage /
call-position checks (note 1, "Open work" below) — defense-in-depth, not open holes.

---

## Per-feature status

### quantification — P1–P4 landed
- **P1 typed binders** (`37d9a37`): `\forall x: T` / `\exists x: T` over a scalar or declared
  `#@ datatype` / class → `forall x : t.`. Legacy untyped binders byte-identical (inert when
  `binder_type=None`). `0555` PASS; `0556` (unresolved type) / `0557` (arithmetic on datatype binder)
  XFAIL. The finite-expansion fast-path was unnecessary (binder discharges directly).
- **P2 recursive-datatype wrapper** (`ff11f18` + `b68373b`): `\forall x: Nat; to_int(x) >= 0` +
  `#@ uses to_int_nonneg` discharges. Needed **two** orderings, both via the SCC machinery: (A) the
  named function `to_int` before the wrapper (scc.md contract-reference edge), (B) the proving lemma
  before the wrapper (scc2.md `#@ uses` citation edge — the wrapper doesn't *name* the lemma).
  `0564` (reference) / `0565` (citation).
- **P3 set bounded quantification** (`77fe1bd`, scc3.md Phase B): `\forall x: int in s; x >= 0`
  desugars to `\forall x; (x in s) ==> …`; `Module5._csl_in` dispatches a *set* domain to clean key
  membership `Map.get s x` (lists keep the positional `exists`). Discharges by **e-matching on
  `Map.get s k`** — no trigger needed. `0568` PASS / `0569` (no membership hypothesis) XFAIL.
- **P4 object quantification, value mode** (`77fe1bd`, scc3.md Phase A): `\forall o: C; o.x >= 0`.
  A quantifier-bound record var is registered during body emission so `o.field` lowers to the record
  field (not an abstract `get_field`); the class invariant is supplied **free** by the Why3 type
  invariant on the record — no explicit `inv(o) ==>` guard. `0566` PASS / `0567` (no class invariant →
  ranges over invariant-free records) XFAIL.

### lemma — P1 + P2/S3 landed
`#@ lemma` → `let [rec] lemma name (p): unit … = <proof body>`. Non-recursive (`0558`, SMT) and
recursive/inductive (`0559`, `to_int(n)>=0` by induction, 879 steps) both prove. Module-4
`_validate_lemma`: `\diverges`-forbidden + ≥1-`ensures` + (currently) variant-on-recursion — the last
**slated for removal** (Soundness note 1).

### inductive — P1 (single predicate) landed
Module-level `#@ inductive p(params):` + `#@ rule <name>: <horn-clause>` (rule body reuses the
contract-expression grammar incl. typed quantifiers). Emits `inductive p t = | Rule : clause`
(**no `end`** — an `end` would close the module). Predicate applications `p(args)` → `(p args)`.
`0562` (`even`, introduction proves `even(4)`) PASS / `0563` (non-positive, Why3-rejected) XFAIL.

### poly — datatypes shipped (A5d); function half stop-and-flagged
Generic *datatypes* (`Option[T]`, parametric instantiation) already work; `0540` passes (the spec's
stale "0540 fails today" was corrected in `poly.md` §0). The function/predicate/lemma half is not
implemented — see "Open work / poly" for the four concrete obstacles.

---

## Cross-cutting findings
- **SCC ordering ignored contracts — ✅ FIXED** (`ff11f18` + `b68373b`). The call graph was body-only,
  so a function whose *contract* referenced a pure symbol could be emitted before it (`unbound
  symbol`). Fixed by unioning contract-reference edges (scc.md) and `#@ uses` citation edges (scc2.md)
  into the existing Tarjan/SCC, via a single shared `emits_as_logic_symbol` classifier consumed by both
  the edge collector and the emitter (so the graph and emission agree on "depends on"). Byte-identical
  490/490 — the edges are redundant for every currently-compiling file.
- **Binder/domain type propagation — ✅ FIXED** (`77fe1bd`, scc3.md A+B). A quantifier's binder type
  (P4) and a domain's set type (P3) were not carried into the body's member-access / membership
  lowering, so `o.x` → abstract `get_x o` and `x in s` → mis-typed positional membership. Fixed by
  registering bound record vars during body emission and dispatching `_csl_in` on the domain type.
  Byte-identical 492/492.
- **`inductive` is a reserved-ish word** at contract-start (the block-folder `_INDUCTIVE_HDR` +
  grammar); the contextual LALR lexer keeps it contextual and the byte-diff confirmed no regression.
  **`rule` is no longer reserved** — the keyword was retired (`5516569`); rules now fold in by
  indentation, leaving only `inductive` (which mirrors Why3/Rocq/Lean).

---

## Open work (the remaining plan, prioritized)

**Implementation pass status.** ✅ Landed: **A** (lemma decision-A + ghost discipline + trust-leakage,
`ca260ff`), **B-relational** inductive (free, `4b37f18`), **C-multi-binder** (`4b37f18`), **B `#@ rule`
→indentation** (keyword retired, `5516569`). ⏳ Remaining (each genuinely substantial or brittle — *not*
quick wins; stop-and-flagged with scope below): inductive reflection and the
relational-consequence-via-lemma; quantification `#@ by induction on`, Phase-C triggers (brittle), and
ghost-collection mode; and all four poly obstacles (the ~3-week function half). Drivers to date:
**0555–0575** (21 total: 13 PASS, 8 XFAIL). Also done: B `#@ rule`→indentation (`5516569`) and B-mutual
`with` groups (`0574`/`0575`).

### A. lemma soundness — ✅ DONE (decision A + ghost discipline + trust-leakage)
- **Decision A applied:** the variant-on-recursion check is removed; `0560` retargeted to a
  non-terminating lemma (Why3 termination VC rejects it); `0570` added (recursive lemma with NO
  `#@ \variant` proves — Why3 infers the structural variant); docs ("lynchpin" wording) fixed.
- **Ghost discipline + trust-leakage enforced** in `_validate_lemma`: return `None`, `assigns \nothing`,
  no `return <value>`, and no body call to a `\trusted` function (the last is the one Why3 can't catch;
  driver `0571`).
- **Still deferred:** the proof-body statement *whitelist* (broad; low value — Why3 type-checks the
  body anyway); the `#@ lemma \trusted` shim; cross-module lemma reuse. The **contract-call-position
  ban** is *not* a PyCSL check — Why3 rejects a lemma used as a term (same posture as inductive
  positivity / quantifier binder-use).

### B. inductive — surface simplification + the deferred phases
- **`#@ rule`→indentation — ✅ DONE.** The `rule` keyword is retired; rules are bare `name: clause`
  lines indented 4 spaces under the `#@ inductive …:` header (like `#@ act:` / `#@ happy:`):
  ```python
  #@ inductive even(n: int):
  #@     even_zero: even(0)
  #@     even_step: \forall m: int; even(m) ==> even(m + 2)
  ```
  **The LALR delimiter is clean** — `inductive_decl: "inductive" CNAME "(" mixin_params? ")" ":"
  inductive_rule+` with `inductive_rule: CNAME ":" expr` builds with no conflict (an `expr` can't be
  followed by a bare `CNAME`, so the next rule's name is unambiguous). Implemented: Module 1
  `_INDUCTIVE_HDR` block-folder + dropped `inductive`/`rule` from `_MODULE_PREFIXES`; Module 2 inline
  `inductive_rule+` grammar + transformer (rules parsed into `InductiveDecl.rules`); Module 3 hoists
  (no grouping); dead `RuleDecl` removed. Drivers 0562/0563/0572 rewritten. **Emission byte-identical**
  (the 3 inductive files emit identically old-syntax+old-code vs new-syntax+new-code; 482 other files
  unchanged). `rule` removed from all 5 doc surfaces (doc-coherency green; no longer a tracked
  directive).
- **P2 mutually-inductive `with` groups** — ✅ **DONE (drivers `0574`/`0575`).** A `#@ with q(sig):`
  continuation block (folded into the inductive contract by Module 1; parsed into `InductiveDecl.members`
  by Module 2; all members registered in `_inductive_preds`) emits one Why3 group
  `inductive p … = | … with q … = | …` (no `end`). `even`/`odd` discharges `even(4)`; group-wide
  strict positivity is enforced by Why3 (`0575` — a non-positive occurrence in a `with`-member is
  rejected).
- **P3 relational form** (reachability) — ✅ **DONE (free; driver `0572`)**. The existing
  single-predicate machinery already handles a multi-arg, *non-structural* predicate
  (`reach(x+1,z) ==> reach(x,z)` — recurses on `x+1`, which a terminating function can't express) with
  nested typed quantifiers in rule bodies; `reach(0,2)` discharges by introduction. The
  *universally-quantified-consequence-via-`#@ lemma`* extension (proving `\forall a,b; reach(a,b) -> Q`
  by the inductive's induction principle) is the remaining, harder piece — still open.
- **P4 reflection** (decision function + agreement lemma); coinductive predicates out of scope. *(Open.)*
- *(Not soundness — note 2)* an optional Module-4 `_validate_inductive` pre-check (positivity /
  conclusion-shape / arity / exec-position); Why3 already enforces positivity. If ever built, note that
  PyCSL's `not` doesn't parse inside a rule clause the way the spec's Horn syntax assumes (the
  non-positive negative driver uses a nested-implication form; a polarity walk should handle both).

### C. quantification — the brittle/edge tail
- **Phase C — triggers (DEFERRED; list-bounded only).** Set-bounded quantification e-matches via
  `Map.get S x` with no trigger; only *list*-bounded (positional `exists`) needs one. *Mechanism when
  built:* select a trigger from the body's membership / pure-function / field terms mentioning every
  bound var; refuse interpreted-only patterns (`+`,`*`,`and`, nested quantifiers — matching-loop risk);
  emit Why3 `[pattern]`; `#@ trigger f(x), g(x)` overrides; Module-4 warns when no admissible trigger
  exists. **MEDIUM-risk, brittle** — keep behind its own drivers (missing-trigger FAIL twin;
  trigger-override loop-free regression).
- **P4 ghost-collection mode** (`\forall o: C in registry; …`) — composes P4 (class binder) + P3 (set
  membership over a ghost `set[C]`); needs a decidable-equality story for class-instance set elements.
  Land after a driver.
- **Multi-binder** sugar — ✅ **DONE (driver `0573`)**. `\forall x, y, …; P` desugars in the
  transformer to nested single binders (all `int`); `\exists` likewise. *Per-binder types in a
  multi-binder (`\forall x: T, y: U;`) remain unsupported — nest explicitly.*
- **`#@ by induction on x`** — the lemma-free P2 alternative (drive Why3's `induction_ty_lex` from the
  proof harness); orthogonal, still open.
- *Explicitly NOT needed:* an `Fset` theory import — the `map int (option int)` set model with
  `Map.get` key membership suffices for bounded quantification; `Fset` would only matter for
  cardinality/union lemmas (a separate, later concern).

### D. poly — the function/predicate/lemma half
Generic *datatypes* shipped; the function half is a ~3-week multi-stage feature. Ordered obstacles:
1. **`pure_ast` PEP-695 parse** — `def f[T](…)` (parse `[names]` into `type_params`); ~20 lines at
   `pure_ast.py::funcdef` (replace the `unsupported(...)` at the `[` check); bounds/defaults/variadics
   stay rejected. (Prototyped + reverted to keep the tree clean.)
2. **Recursive generic datatype payloads** — `variant_def: CNAME "(" CNAME ("," CNAME)* ")"` accepts
   only bare-CNAME payloads, so the type-application `List[T]` in `LCons(T, List[T])` is not a payload
   type. (Re-probed this pass: the bare decl appears to parse, but the moment a driver *uses* the type
   — `def f(x: List)` or a `\is_ctor` contract — it parse-errors at the `List` token. So both the
   payload grammar AND the use-site/annotation path need the `Name[args]` form.) After the grammar,
   the *emitter* must thread the datatype's type param through the recursive payload
   (`List[T]` → `list 'a`), i.e. the same τ-threading as (3). Not a grammar-only fix.
3. **Function τ-threading** — a param `xs: List[T]` (T the function's type var) must lower to
   `list 'a`, head to `let [rec] function f (xs: list 'a)`; reuse `_fmt_variant`'s datatype
   type-param→`'t` mapping in `module6_whyml/types.py` / `functions.py`.
4. **Parametricity check** — reject inspecting a bare-`T` value (`if t == 0`, `t: T`) — the
   prove-once-reuse guarantee.

---

## How to verify
```
bin/run-reference-tests.sh --pycsl --start-at 555 --stop-at 573   # 19/19 (11 PASS + 8 XFAIL twins)
bin/doc-coherency.py --check                                       # exit 0
```
Each feature/phase commit was gated on a whole-corpus emission byte-diff vs its parent
(`PYTHONHASHSEED=0 --no-proof --keep-mlw`, honoring per-file flags) confirming the additive-directive
property — temporary worktrees cleaned up after confirming identical.

---
*Supersedes `remains.md` and `scc3.md`. The historical ordering plans `scc.md` (contract-reference
edges) and `scc2.md` (`#@ uses`) remain as the per-feature plan records.*
