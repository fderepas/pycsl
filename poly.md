# Plan: polymorphic / generic datatypes — implementation plan derived from `poly-spec.md`

Companion to `poly-spec.md`. The spec is the normative **"what must hold"**; this is the **"how we
build it, in what order, behind which gates."** It is the fourth of the companion quartet (with
`#@ datatype`, `#@ lemma`/`lemma.md`, `#@ inductive`/`inductive.md`, and typed quantifiers).

## §0 — Reality check: HALF of this spec already shipped (read this first)

`poly-spec.md` is **partly stale**. Its anchor claim — corpus `0540` "fails today, the `[T]`
type-parameter syntax is not in the grammar" — is **no longer true**. Verified against the live tree:

- **Generic DATATYPES are implemented** (feature **A5d**). `#@ datatype Option[T] = Nothing | Just(T)`
  and recursive `#@ datatype List[T] = LNil | LCons(T, List[T])` **parse and verify today**; corpus
  `0540` carries **no** `# pycsl-expected: FAIL` and **PASSES**. The machinery: `Module2_Parser.py`
  `DatatypeDecl.type_params` (:628) + grammar/transformer (:1081-1083); `Module5_IREmitter.py`
  `type_params` IR (:80-81); `module6_whyml/preamble.py::_fmt_variant` emits `type option 't = …`
  (:637-643). Parametric *instantiation* per use (`Just(7)`→`option int`, `Just(s)`→`option string`)
  works. So spec **P1 datatypes** and **P2 recursive generic datatypes** are essentially DONE.

- **Polymorphic FUNCTIONS are NOT.** `def length[T](xs: List[T]) -> int` fails at the parser:
  `pure_ast parser: PEP 695 type parameters not yet implemented` (`src/pycsl/pure_ast.py:1373`). The
  AST node schema already *reserves* `type_params` slots on `FunctionDef`/`ClassDef`/`TypeAlias`
  (pure_ast.py:159-161,186) — only the **parsing** is stubbed.

**So this plan is scoped to the half that remains: polymorphic functions, predicates, and lemmas**
(`def f[T](…)`), the threading of a function's type variables through its signature into Why3 `'a`,
the parametricity/binding checks for that case, and P4 performance. The datatype half is a *baseline
to verify-and-document*, not to build. **First action is to correct 0540's docstring** (it still says
"fails today") and add the missing doc-coherency for the already-shipped `[T]` datatype surface.

---

## §1 — Reuse / status map

| Spec demand | Status in the tree (file:line) | Work |
|---|---|---|
| `#@ datatype Name[T,…]` generic + recursive; `Name[args]` payload type-application; parametric instantiation | **DONE (A5d)** — M2 `DatatypeDecl.type_params` (:628,1081), M5 (:80-81), preamble `_fmt_variant` `type n 't = …` (:637-643); corpus `0540` PASSES | verify + **document** (the spec/0540 docstring are stale) |
| Why3 polymorphic equality `=` at a type var | from Why3, lowers directly (§6.3) | none |
| `mixin_type: CNAME ("[" … "]")?` type-application syntax already in grammar | exists for mixin sigs (`Module2_Parser.py:959`) | reuse the shape for function param/return type-app parsing |
| **Polymorphic function `def f[T](…)`** | **BLOCKED** — `pure_ast.py:1373` rejects PEP 695 fn type params; node schema reserves `type_params` (:159-161) | **build** — the gating obstacle (S0) |
| Type var in a function signature → Why3 `'a`; emit `let [rec] function/predicate/lemma` polymorphically | the τ-table / function emitter handle concrete types + variant; `_fmt_variant` already maps datatype type-params to `'t` | **build** — extend signature τ to bind a function's own type vars to `'a` |
| Generic recursive function still needs `#@ \variant` | `\variant` machinery exists (`functions.py` variant emission) | reuse unchanged (§8.4) |
| Generic **predicates / lemmas** (prove-once/reuse) | depend on `#@ inductive` (`inductive.md`) and `#@ lemma` (`lemma.md`) — **neither built** | **gated** on those features (P3) |
| Optional per-site monomorphization (perf) | none | P4, gated on a hot-spot driver |

**Net new code:** PEP 695 function-type-param parsing in `pure_ast` (+ weave the scope), signature-τ
binding of a function's type vars to `'a`, polymorphic `let [rec] function/predicate/lemma` emission,
and the Module-4 binding/arity/parametricity checks (§3). Datatypes: verify + document only.

---

## §2 — R0 pre-flight: drivers FIRST (one already half-exists)

Step 0; drivers in `test-suite/corpus/pycsl-reference/` at the next free numbers (**0555+** at time of
writing). Spec §9/§10:

**Baseline-confirm (already PASSING — lock them in / fix docstrings):**
1. `0540` (`Option[T]`) — **correct its docstring** ("fails today" → "PASSES, A5d") so it stops
   mis-claiming. The existing two-instantiation (int+str) test stays.

**Positive (flip to PASS as each phase lands):**
2. **P-fn flagship** — `def length[T](xs: List[T]) -> int` (recursive, `#@ \variant xs`); proves
   `\result >= 0` at `List[int]` and `List[Json]` in one file. (Today: parse error at `[T]`.)
3. **swap** — `def swap[A,B](p: Pair[A,B]) -> Pair[B,A]` with `ensures \result == p`-style involution.
4. **Polymorphic lemma reuse** (the headline) — `length_append[T]` proved once, instantiated at two
   types (gated on `#@ lemma`).

**Negative / soundness twins (commit `# pycsl-expected: FAIL`, STAY failing — spec §9/§10):**
5. **Unbound type variable** — a `T` in a signature/payload not declared in `[…]` → rejected (§8.1).
6. **Wrong type-arity application** — `Pair[int]` (a 2-param ctor applied to 1) → rejected (§8.2).
7. **Parametricity violation** — inspecting a bare `T`-typed value (`if t == 0` with `t: T`) → rejected
   (§8.3). The kinding lynchpin.
8. **Partial type application** in a type position (`xs: List`) → rejected (§8.5).

**Exit:** drivers committed; 0540 reconfirmed PASS; positives FAIL at parse; negatives FAIL and stay.

---

## §3 — Code-ready staged plan (supersedes spec §9)

Each stage: entry = prior exit + driver committed; exit = driver flips/holds + full sweep clean +
**byte-identical corpus that uses no generics** (additive) + `bin/doc-coherency.py --check` green.

### S0 — PEP 695 function type-parameter parsing (the gating obstacle)
- *First file:* `src/pycsl/pure_ast.py` — implement the `type_params` parse for `def f[T](…)` (the
  rejection at :1373); the `FunctionDef.type_params` slot already exists (:159). Decide class `C[T]`
  scope-out for now (datatypes carry their params via `#@ datatype`, not `class`). `Module3_Weaver.py`
  — record the function's type-param scope on the def node (mirror how datatype `type_params` are
  carried). Grammar for `Name[args]` type-applications in param/return positions reuses the
  `mixin_type` shape (`Module2_Parser.py:959`).
- *Exit:* `def length[T](xs: List[T]) -> int` parses to `--no-proof` without the PEP-695 error.

### S1 — signature τ + polymorphic emission
- *First files:* the function emitter (`module6_whyml/functions.py`) + τ (`module6_whyml/types.py`) —
  bind a function's declared type vars to fresh Why3 `'a, 'b, …` (reuse `_fmt_variant`'s datatype
  type-param→`'t` mapping), so a param typed `List[T]` lowers to `list 'a` and the head emits
  `let [rec] function length (xs: list 'a) : int …`. Predicates/lemmas reuse the same head machinery
  with their keyword.
- **Gate-B spike (first):** hand-write the target `.mlw` for the P-fn flagship and run Why3 with
  **poly-encoding** (the default driver transform, spec §6) to confirm it typechecks and discharges at
  two instantiations. The one external unknown.
- *Exit:* P-fn flagship + `swap` PASS at multiple instantiations.

### S2 — Module-4 binding / arity / parametricity checks (the soundness-ish heart, §3 detail below)
- *First file:* `Module4_SemanticAnalyzer.py` — type-var binding/scoping, type-constructor arity,
  no-partial-application, **parametricity** (no inspecting a bare-`T` value). Reuse the existing
  positivity/recursion checks unchanged for generic recursive defs (§8.4).
- *Exit:* negatives 5–8 rejected with distinct errors; positives still pass.

### S3 — generic predicates & lemmas (DEPENDS ON `inductive.md` + `lemma.md`)
- Polymorphic inductive predicates (`forall_list[T]`) and lemmas (`length_append[T]`) — prove-once,
  reuse at every instantiation (the §7 headline). Gate on those two features existing; this stage is
  the *generic* layer over them (their type-var threading reuses S0–S1).
- Driver: the §4 generic-`List[T]` JSON refactor + a `wf`/`forall_list` predicate + `length_append`
  lemma instantiated at `List[int]` and `List[Json]`.
- *Exit:* polymorphic-lemma-reuse driver (4) PASSES at two instantiations.

### S4 — performance & docs (spec §9 P4)
- Optional per-instantiation **monomorphization** escape hatch (emit `list int`, `list json` as
  separate monomorphic types) behind a pragma/flag, gated on a real solver hot-spot driver; an
  encoding-equivalence gate (poly-encoded vs monomorphized give the same corpus results, spec §10).
  Bounded polymorphism (`List[T: Ord]` via Why3 `clone`) is research — out of scope (§11.2).
- 5-surface doc-coherency: document the `[T]` generic surface (datatypes **and** functions) in
  `README.md`, `docs/pycsl-concrete-syntax-reference.md`, `docs/pycsl-static-semantics-reference.md`
  (τ for type vars / applications), `docs/pycsl-translational-reference.md`, `test-suite/annotations.md`
  (extend §2.6), and the `pycsl-annotate` skill. **Note:** the *datatype* generic surface shipped (A5d)
  but may be under-documented across all five surfaces — reconcile it here too.

**YAGNI exit:** stop at any stage no driver needs. P3 starts only once `#@ inductive`/`#@ lemma` exist;
P4 monomorphization only on a measured hot spot.

---

## §3 (detail) — Module-4 checks, with parametricity as the lynchpin

A generic definition is well-formed iff (spec §8), each a distinct `PyCSLSemanticError` (negatives 5–8
are the teeth):

1. **All type variables bound (§8.1).** Every `T` in a payload/signature is declared in the enclosing
   `[…]`; a free type var ⇒ reject (negative 5).
2. **Type-constructor arity (§8.2).** A generic datatype is applied to exactly its declared number of
   type args wherever a *type* is expected (`Pair[int]` ⇒ reject, negative 6).
3. **No partial type application (§8.5).** `List` alone is valid only in type-constructor position,
   never as a complete type (`xs: List` ⇒ reject, negative 8).
4. **Kinding + parametricity (§8.3, the lynchpin).** Type vars appear only in type positions, never as
   values; a polymorphic function may **not** branch on / compare / inspect a bare-`T` value beyond
   its operations (`if t == 0` with `t: T` ⇒ reject, negative 7). This is what makes the polymorphism
   *parametric* (the function behaves uniformly at every instantiation); without it a "polymorphic"
   function could secretly depend on the instantiation, breaking the prove-once-reuse guarantee.
5. **Recursion/positivity unchanged (§8.4).** A generic recursive datatype obeys the monomorphic
   rules; a generic recursive function still needs `#@ \variant`; a generic inductive predicate still
   needs strict positivity. **Reuse the existing checks** — do not fork them.

Open during S2 (resolve against the flagship): whether parametricity is checked on the Module-3 AST
(branch/compare nodes over a `T`-typed binder) or needs the IR — start on the AST.

---

## §4 — Effort sizing

| Stage | Scope | Size |
|---|---|---|
| **R0 + 0540 fix** | drivers (positives + soundness twins) + correct 0540 docstring | ~1 day |
| **S0 PEP-695 fn parsing** | `pure_ast` type-param parse + weave scope + type-app grammar reuse | ~3–5 days |
| **S1 signature-τ + emission + Why3 spike** | bind fn type vars→`'a`; polymorphic `let [rec] function/predicate/lemma`; poly-encoding spike | ~3–5 days |
| **S2 Module-4 checks** (the heart) | binding, arity, no-partial-app, parametricity; reuse positivity/variant | ~1 week |
| **S3 generic predicates/lemmas** | the generic layer — **gated on inductive + lemma** | ~3–5 days (after those) |
| **S4 monomorphization + 5-surface docs** | perf escape hatch (gated) + doc-coherency incl. the shipped datatype surface | ~3–5 days |

**Remaining-scope total (excluding the already-done datatypes, and the inductive/lemma deps): ~3–4
weeks.** S2 owns the parametricity risk; S0 (pure_ast PEP-695) is the gating obstacle and the only
deep-parser change; S1's external unknown is the poly-encoding spike.

---

## §5 — Reference corpus additions (mandatory)

Per the reference-corpus discipline (numbers indicative, next-free at authoring — 0555+):

- **0540** — *fix existing docstring* to "PASSES (A5d)"; keep as the generic-datatype baseline.
- **0555** P-fn `length[T]` over `List[int]` + `List[Json]` — PASS.
- **0556** `swap[A,B]` involution — PASS.
- **0557** `length_append[T]` lemma reused at two instantiations — PASS (after `#@ lemma`).
- **0558** §4 generic-`List[T]` JSON refactor + `forall_list[T]` predicate — PASS (after `#@ inductive`).
- **0559** unbound type variable — FAIL (rejected).
- **0560** wrong type-arity `Pair[int]` — FAIL (rejected).
- **0561** parametricity violation (`if t == 0`, `t: T`) — FAIL (rejected).
- **0562** partial type application `xs: List` — FAIL (rejected).

Plus the spec §10 **encoding gate** (generated WhyML typechecks under Why3 poly-encoding; a
monomorphization toggle gives equivalent results) and the **erasure check**.

---

## §6 — Decided vs still open (maps spec §11)

**Decided by this plan:**
- Generic *datatypes* are already shipped (A5d) — this plan builds the *function/predicate/lemma* half
  and documents the whole `[T]` surface; it does not rebuild datatypes.
- The gating obstacle is `pure_ast` PEP-695 function-type-param parsing (S0); emission relies on Why3's
  default poly-encoding (no front-end monomorphization by default).
- Parametricity (no inspecting a bare-`T` value) is enforced in Module 4 — the prove-once guarantee.

**Still open (resolve in the named phase / gated):**
- **§11.1 monomorphization policy** — never / per-pragma / timeout-heuristic; S4, on a hot-spot driver.
- **§11.2 bounded polymorphism** (`List[T: Ord]` via Why3 `clone`) — research follow-on, out of scope.
- **§11.3 higher-order functions** (one generic `fold`) — a separate larger proposal; out of scope.
- **§11.4 type-argument inference** — must sites spell out `List[Json]` or can PyCSL infer under the
  annotate-everything rule; decide in S1.
- **§11.5 cross-module generic libraries** (`List[T]` theory) — theory-cloning; P4+, gated.

## §7 — Net
The spec's first half (generic datatypes) **already shipped (A5d)** — so the honest, code-ready scope is
the *polymorphic functions/predicates/lemmas* half. The three things that make it buildable: (1) the
gating obstacle is a single deep-parser change (`pure_ast` PEP-695 `def f[T]`, whose AST slot already
exists), (2) emission reuses the datatype type-param→`'a` mapping (`_fmt_variant`) and rides Why3's
poly-encoding, and (3) the risk concentrates in a **Module-4 parametricity check** (§3) that guarantees
prove-once-reuse. P3 (generic predicates/lemmas) is **gated on `inductive.md` + `lemma.md`** — the
quartet is interdependent. First action: **R0** drivers + fix 0540's stale docstring, then the S0
`pure_ast` change, then the S1 poly-encoding spike.
