# Working with two sources of truth — the dual Rocq + Lean mechanism in PyCSL

Technical reference for engineers maintaining, extending, or
evaluating the `proof2why3` pipeline. Describes the dual-prover
architecture, the per-prover extraction backends, the shared IR,
the canonicalization rules that reconcile cross-prover encoding
differences, and the 3-way structural diff.

The companion narrative document is `0342_explanation.md` (the
GCD worked example). This file is the architectural reference;
read it alongside the source code in `src/pycsl/proof2why3/` and
the architecture sketch at `docs/cross-validated-spec-sources.md`.

---

## 1. Why two sources of truth

PyCSL's spec-import directive `#@ proof <prover> <qualname>`
binds a Why3 axiom to a kernel-checked theorem in a proof
assistant. The axiom is what Module 6 splices into the generated
`.mlw`; the theorem is what discharges the *trust* of that axiom.
Two questions follow:

1. **Trust:** does the Why3 axiom body faithfully encode the
   theorem the prover actually proves?
2. **Faithfulness across provers:** if both Rocq and Lean cite
   "the same" theorem, do they actually agree on its statement?

A single-prover binding answers (1) only at the level of "human
review of the registry". Two independent provers, both required
to agree, answer (1) and (2) jointly: each prover's kernel is
independently developed (different OCaml/Lean codebases,
different stdlib lineages, different communities), so their
agreement on a statement is strong evidence the statement is
well-formed and means what the human author intended. Their
disagreement, conversely, fingers a curator error.

The dual mechanism trades one machine-uncheckable trust
assumption ("the registry is correctly hand-written") for two
machine-checkable ones ("Rocq and Lean see the same statement"
and "both match the registry"). When `make self-annotate-verify`
runs the 3-way structural diff (see §6) on every build, both
machine-checkable predicates become hard build gates.

---

## 2. The end-to-end pipeline

For a single cited qualname, e.g. `Pycsl.Reference.Gcd.gcd_step`:

```
       0342.py
        │ contains
        │   #@ proof rocq Pycsl.Reference.Gcd.gcd_step
        │   #@ proof lean Pycsl.Reference.Gcd.gcd_step
        ▼
src/pycsl/audit_proof.py                    ← namespace audit
        │ confirms the qualname is *declared* in the
        │ matching .v / .lean file (line-oriented parser)
        ▼
src/pycsl/audit_proof_reverify.py           ← optional reverify
        │ if --reverify-proofs: coqc + lake env lean compile
        │ the proof files; assumption sets matched against
        │ src/pycsl/proof_axiom_allowlist.py
        ▼
src/pycsl/proof2why3/{sertop,extract_lean_meta}.py
        │ extract each cited theorem's elaborated AST
        │ Rocq via sertop; Lean via lake env lean --run
        ▼
src/pycsl/proof2why3/{from_sexp,from_lean_json}.py
        │ project each prover's AST into the shared IR
        ▼
                  proof2why3.ir.Term
                       │ (frozen dataclasses; hashable)
                       ▼
              proof2why3.canonical.canonicalize
                       │ 8-step pipeline; fixed point
                       ▼
               canonical Term (Rocq side)
               canonical Term (Lean side)
               canonical Term (Registry side, via parser.py
                               on the WhyML axiom body)
                       │
                       ▼
       proof2why3.crosscheck_ir.crosscheck_file_ir
                       │ structural equality (Python `==`)
                       │ on frozen dataclasses
                       ▼
        rocq_canon == lean_canon == registry_canon ?
                       │
            yes ──→ PASS    no ──→ FAIL with per-Term
                                   pinpoint diff fingering
                                   the dissenting source
```

The whole chain runs on `make self-annotate-verify`. The
`make` target invokes `bin/check-proof-crosscheck.sh`, which
iterates annotated files and aggregates PASS/SKIP/FAIL counts;
any FAIL fails the build.

---

## 3. Statement extraction — per-prover backends

The hardest engineering problem is getting the theorem
statements *out* of each prover in a form we can compare. Each
prover has two extraction paths in the codebase: a robust
default (textual pretty-printer scraping) and an
elaborated-AST path (recommended). Both produce the same
canonical IR; the elaborated-AST paths are preferred because
they bypass the pretty-printer's notation/version fragility.

### 3.1 Rocq extraction

**Text path** (`extract.py:extract_rocq_statements`):

- Companion `.v` file with `Check <qualname>.` lines.
- `coqc` runs the companion; stdout has `<qualname>\n     :
  <pretty-printed type>`.
- Parsed by `parser.parse_type_expr` (a recursive-descent
  parser, ~430 lines, see `src/pycsl/proof2why3/parser.py`).
- Pre-parse `normalize_surface()` strips library prefixes
  (`PeanoNat.Nat.gcd` → `gcd`), Unicode operators
  (`∀` → `forall`, `→` → `->`, `≥` → `>=`, `∨` → `\/`,
  `∧` → `/\`), and Lean dot notation (`a.gcd b` → `gcd a b`)
  for parity with the Lean side.

**Elaborated-AST path** (`extract_via_sertop` in `sertop.py`,
`PROOF2WHY3_USE_SERTOP=1`):

- Spawns `sertop --printer=sertop -Q <path>,<logical>` as a
  subprocess. See `run_sertop_batch` in
  `src/pycsl/proof2why3/sertop.py:191`.
- Sends pipelined commands:
  ```
  (Add () "Require Import <module>.")
  (Exec 2)                  ← STMID 2 = first user Add
  (Query () (TypeOf "<qualname>"))
  ...
  (Quit)                    ← invalid command; flushes buffer
  ```
- Trailing `(Quit)` is load-bearing: sertop's stdout buffer
  holds the last command's `Completed` until something flushes
  it. `(Quit)` triggers an `Of_sexp_error` and exits, which
  flushes everything.
- Response shape (one line per Answer): `(Answer N (ObjList
  ((CoqConstr <constr_sexp>))))`.
- `parse_sexp` (in `sertop.py:127`) tokenizes and builds nested
  Python tuples.
- `from_sexp.project_constr` (442 lines,
  `src/pycsl/proof2why3/from_sexp.py:336`) walks the parsed
  s-expression and emits IR. The Constr.t cases handled:
  `Prod`, `Rel`, `Var`, `Sort`, `Cast`, `App`, `Const`, `Ind`,
  `Construct`, `Int`. Lambda / LetIn / Case / Fix / CoFix /
  Proj / Float / Array fall through to `Unsupported`.

The sertop schema is documented inline at the top of
`from_sexp.py`. Reference: `~/.opam/coq-4.14/.opam-switch/
sources/coq-serapi.8.20.0+0.20.0/serlib_8_20/ser_constr.ml`.

### 3.2 Lean extraction

**Text path** (`extract.py:extract_lean_statements`):

- Appends `#check @<qualname>` lines to a copy of the proof
  file; runs `lake env lean <copy>`; parses the
  `<qualname> : <pretty-printed type>` lines from stdout.
- Same surface normalization as the Rocq text path.

**Elaborated-AST path** (`extract_lean_meta.py`,
`PROOF2WHY3_USE_LEAN_META=1`):

- The companion meta-script
  `bin/proof2why3-lean-extract.lean` runs under
  `lake env lean --run`. It:
  1. Calls `enableInitializersExecution`.
  2. `importModules` for `Init` + the cited module.
  3. For each qualname, `env.find? <name>` returns
     `ConstantInfo`; takes `info.type` (a `Lean.Expr`).
  4. Recursively walks the `Expr` and emits compact JSON via
     `Json.compress`. The recursion (`exprToJson`) handles
     `forallE`, `lam`, `app`, `const`, `fvar`, `bvar`, `lit`,
     `sort`, `mvar`, `letE`; anything else maps to
     `{"kind":"unsupported", "raw":<toString>}`.
- One JSON object per qualname is written to stdout, terminated
  by `{"end": true}`.
- `extract_lean_statements_meta` in
  `src/pycsl/proof2why3/extract_lean_meta.py` runs the
  subprocess and parses the JSON.
- `from_lean_json.project_to_ir` (262 lines,
  `src/pycsl/proof2why3/from_lean_json.py:167`) projects the
  JSON tree to IR.

Lean's Expr is unary-binder (one binder per `forallE`); the
canonicalizer's `_flatten_foralls` step (§5.2) folds adjacent
same-type binders back into the n-ary `Forall(binders=…)` form
the IR uses.

### 3.3 Both paths produce the same IR

This is by construction. The text paths use `parser.py` with
`normalize_surface()` to strip the surface artifacts; the
elaborated-AST paths bypass the pretty-printer entirely.
Negative tests confirm canonical-form equality across all four
extraction-path combinations (text/AST × Rocq/Lean) on the
0342 gcd-family and on `wp_gen_correct` (a non-gcd predicate
theorem).

---

## 4. The shared first-order IR

Frozen dataclasses in `src/pycsl/proof2why3/ir.py:1-180`:

```python
@dataclass(frozen=True) class Var:       name: str
@dataclass(frozen=True) class IntLit:    value: int
@dataclass(frozen=True) class BoolLit:   value: bool
@dataclass(frozen=True) class App:       head: str; args: Tuple[Term, ...]
@dataclass(frozen=True) class BinOp:     op: str; lhs: Term; rhs: Term
@dataclass(frozen=True) class UnaryOp:   op: str; arg: Term
@dataclass(frozen=True) class Forall:    binders: Tuple[str, ...]; ty: str; body: Term
@dataclass(frozen=True) class Exists:    binders: Tuple[str, ...]; ty: str; body: Term
@dataclass(frozen=True) class Unsupported: reason: str; raw: str
```

Key design choices:

- **Frozen** → automatic `__hash__` and `__eq__` from the field
  tuple. Structural equality is just `==`.
- **n-ary binders** in `Forall`/`Exists` — adjacent same-type
  binders fold into one node (e.g. `Forall(("a", "b"), "int",
  ...)`), not nested.
- **String type field** on `Forall.ty` — keeps the IR
  first-order while allowing predicate types like
  `"(exec_state -> prop)"` to be carried through unchanged.
  See §5.3.
- **`Unsupported`** is the explicit failure node. Any
  cross-check involving Unsupported is a hard FAIL (not a
  silent PASS); the parser-gap is visible.

The IR is intentionally first-order. Dependent types, type
classes, universe polymorphism, and lambda values are not
representable — they appear as Unsupported when extraction
hits them. For the gcd-family + wp_gen_correct + the
self-annotate audit-anchor stubs (the current corpus), this
is sufficient.

Reference: `src/pycsl/proof2why3/ir.py`.

---

## 5. Canonicalization — the eight-step pipeline

`canonical.canonicalize` (`src/pycsl/proof2why3/canonical.py`)
applies eight transformations in fixed order. Each step exists
to reconcile a *specific* class of cross-prover encoding
difference. Reading the steps in order is the most direct way
to understand what differences the cross-check actually
flattens.

### 5.1 `_expand_nat_to_int` (lines ~92-135)

**What it does**: `forall x : nat, P(x)` becomes
`forall x : int, x >= 0 -> P(x)`. Applied to both `nat` (Coq)
and `Nat` (Lean).

**Why**: Rocq's `Nat.gcd` and Lean's `Nat.gcd` are typed over
`nat`/`Nat`; PyCSL's WhyML registry bodies are stated over
`int` with `a >= 0` side conditions. Without expansion the
canonical forms would differ in binder type. With expansion,
both sides become `int`-with-side-condition; the registry side
is already in that form.

**Soundness note**: the conversion is only sound for the
non-negative subset. The function's `#@ requires a >= 0` clause
is what restricts the domain. Conceptually the canonicalization
is `forall x : nat, P(x) ⇔ forall x : int, x >= 0 -> P(x)` in
the model where `int.Int` extends `nat`; both directions hold.

### 5.2 `_flatten_foralls` (lines ~250-310)

**What it does**: `Forall("x", T, Forall("y", T, P))` folds to
`Forall(("x", "y"), T, P)` (recursively, until no adjacent
same-type Foralls remain).

**Why**: Lean's `Expr.forallE` is unary — `∀ (a b : Nat), P`
encodes as `forallE "a" Nat (forallE "b" Nat P)`. Rocq's `Prod`
is also unary at the AST level. Both produce the same flat
form after the step; the IR represents only the flat form.

The step also gathers leading arrow hypotheses that sit
*between* same-type binders (preserving their position via the
body's de Bruijn refs), so `forall x, h(x) -> forall y, P(x, y)`
correctly stays as `forall x y, h(x) -> P(x, y)`.

### 5.3 Predicate-typed Foralls

The Forall binder type is a string. For base types (`nat`,
`int`, `Bool`, custom inductives like `stmt`, `exec_state`),
the string is the type name. For predicate types like
`ExecState → Prop`, both projectors serialize the type as
`(exec_state -> prop)` via the Term `pp()` method.

This is what lets `wp_gen_correct` cross-validate:

```
forall v0 : stmt,
  forall v1 v2 v3 v4 : (exec_state -> prop),
  forall v5 : (ident -> (exec_state -> prop)),
  forall v6 v7 : exec_state,
  iff (wp v0 v1 v2 v3 v4 v5 v6 v7)
      (wp_w (gen v0) (enc v1 v2 v3 v4 v5) v6 v7)
```

Both prover sides produce this identical canonical form despite
encoding the continuation types differently at the AST level
(Coq's `Prod(Anonymous, ExecState, Prop)`; Lean's
`forallE "a._@._internal._hyg.N" (const ExecState) (sort Prop)`).

### 5.4 `_flip_comparisons` (lines ~333-365)

**What it does**: `a <= b` → `b >= a`, `a < b` → `b > a`.
Direction-flip; equivalent under standard order axioms.

**Why**: Rocq's `Peano.le` (`a ≤ b`) and Lean's `LE.le` both
encode the operator in argument order `(left, right)` but the
text path's parser would emit them as-is, while the registry
might be authored either way. Normalizing direction collapses
the trivial difference.

### 5.5 `_dedup_arrow_chain` (lines ~371-395)

**What it does**: in an arrow chain `H1 -> H2 -> H1 -> C`,
duplicates collapse → `H1 -> H2 -> C`.

**Why**: defensive — when nat-lifting (5.1) introduces `v >= 0`
side conditions, a hypothesis already present (e.g. `b > 0` in
gcd_step) might cause logically-implied side conditions. We
don't remove implied ones, only literal duplicates.

### 5.6 `_ac_normalize` (lines ~404-435)

**What it does**: associative-commutative flatten + sort for
`\/` and `/\`. `A \/ B \/ C` and `C \/ B \/ A` canonicalize to
the same form via stable sort on `pp()`.

**Why**: the order of `A \/ B` vs `B \/ A` depends on which
side the prover happens to put a disjunct on — operator-symbol
canonicalization eliminates this as a difference.

### 5.7 `_iff_app_to_binop` (lines ~163-200)

**What it does**: `App("iff", [a, b])` → `BinOp("iff", a, b)`.

**Why**: both Coq's `iff` (defined via App over a `Const`) and
Lean's `Iff` (defined via App over a `Const`) extract as App
nodes. The canonical form for binary logical connectives is
BinOp; the rewrite makes the two backends produce identical
shape.

### 5.8 `_normalize_names` (lines ~119-178)

**What it does**: `_camel_to_snake` on Var names, App heads,
Forall binder names, and tokens in Forall type strings.
`wpGenCorrect` → `wp_gen_correct`, `ExecState` →
`exec_state`, `preEs` → `pre_es`, etc. Capture-avoiding
substitution propagates the binder renaming into the body's
Var references.

**Why**: Rocq uses snake_case by community convention; Lean
uses camelCase / PascalCase. Without normalization,
`wpW` (Lean) and `wp_w` (Rocq) compare unequal despite naming
the same function. The rule is conservative: only ASCII
identifier-token boundaries are split; operators and base type
names (`int`, `nat`, `Prop`, `Type`) are passed through.

A residual risk class: two distinct identifiers that happen to
collide under snake_case (e.g. `FooBar` and `Foo_bar` both
mapping to `foo_bar`) would compare equal. No known instance;
mitigated by the alpha-rename step (5.9) operating *after*
name normalization so bound-variable identity stays distinct.

### 5.9 `alpha_normalize` (lines ~440-475)

**What it does**: bound variables renamed to `v0`, `v1`, … left
to right.

**Why**: bound-variable names are syntactic — the canonical
form should be independent of authoring choice. After (5.8) and
(5.9), bound-variable identity is positional, not nominal.

### 5.10 Lean-side anonymous binder detection

This is in the Lean projector (`from_lean_json._body_references_bvar_0`,
lines ~140-165) not the canonical pipeline, but conceptually
part of canonicalization.

**What it does**: in Lean, `H → body` and `∀ (h : H), body` are
the same `forallE` node; the difference is whether the body
references the bound variable. The projector classifies a
binder as "arrow hypothesis" iff: (a) name pattern matches an
auto-generated form (`_h`, `a._@._internal._hyg.N`, etc.), OR
(b) body doesn't reference `bvar(0)`. The latter handles the
common case where Lean elaborates `H → body` and gives the
hypothesis a short auto-name like `a` or `h` (looks like a
real binder by name) but which body never uses.

**Why**: without this, `forall a b : int, a > 0 \/ b > 0 → P`
emits as `forall a b : int, forall h : (a > 0 \/ b > 0), P`
on the Lean side and `forall a b : int, (a > 0 \/ b > 0) -> P`
on the Rocq side — same meaning, different shape.

Rocq's analogous case is built into the AST: `Prod` with
`(binder_name Anonymous)` is the explicit arrow marker. The
Rocq projector keys off this directly (see `_binder_name` in
`from_sexp.py`).

---

## 6. Reconciliation — the 3-way structural diff

After canonicalization, three Term values exist:

- `rocq_canon` — from the Rocq theorem's elaborated AST
- `lean_canon` — from the Lean theorem's elaborated AST
- `registry_canon` — from the WhyML axiom body in
  `_AXIOM_REGISTRY` (parsed by `parser.py` and run through the
  same canonicalize pipeline)

`crosscheck_ir.IRCrossCheckResult` (`src/pycsl/proof2why3/
crosscheck_ir.py:64-130`) computes:

```python
all_agree         = rocq_canon == lean_canon == registry_canon
pairwise          = {
    "rocq==lean":     rocq_canon == lean_canon,
    "rocq==registry": rocq_canon == registry_canon,
    "lean==registry": rocq_canon == registry_canon,
}
```

Five PASS/FAIL configurations are possible (excluding cases
where one side is missing):

| Rocq=Lean | Rocq=Registry | Lean=Registry | Verdict |
|---|---|---|---|
| PASS | PASS | PASS | full triple agreement → PASS |
| PASS | FAIL | FAIL | provers agree, registry drifted |
| FAIL | PASS | FAIL | Lean drifted (or Rocq matches registry-as-Lean does not) |
| FAIL | FAIL | PASS | Rocq drifted |
| FAIL | FAIL | FAIL | both provers AND registry inconsistent |

The diff printout (`IRCrossCheckResult.diagnostic`) shows all
three canonical pretty-prints, with the pairwise verdicts
listed; whichever side is the outlier is mechanically
identified.

### 6.1 Missing-citation SKIP

A qualname with only Rocq citation (e.g. Module 4's
`Phase1_AST.expr_eq_dec`, where the Lean side was dropped due
to the nested-list DecidableEq synthesis issue) classifies as
SKIP iff the absent prover side has no Term to compare and the
present prover sides agree with the registry. See
`IRCrossCheckResult.registry_skipped` /
`provers_agree`. Audit-anchor stubs
(Module4/5/6 + preamble.proofs/) similarly produce SKIP when
no registry entry exists.

### 6.2 What the diff catches and what it doesn't

**Catches** (each verified by an explicit negative test):

1. *Registry diverges from both provers*. Inject `+ 1` into the
   registry's `gcd_0` RHS → diff shows
   `rocq==lean: PASS`, `rocq==registry: FAIL`,
   `lean==registry: FAIL`. Registry correctly fingered.
2. *One prover diverges*. Patch the *statement* (not body) of
   one Rocq theorem → diff shows `rocq==lean: FAIL`,
   `rocq==registry: FAIL`, `lean==registry: PASS`. Rocq
   correctly fingered.
3. *Proof file stops compiling* (with `--reverify-proofs`).
   `coqc` non-zero exit → reverify FAIL.
4. *Proof introduces a non-allow-listed axiom* (e.g.
   `Admitted.`). `Print Assumptions` reports unexpected name →
   reverify FAIL with offending axiom listed.

**Does not catch**:

1. Both provers AND the registry simultaneously wrong in
   exactly the same way (e.g., `Nat.gcd` redefined unsoundly
   in both stdlibs). Mitigation: stdlib soundness is part of
   the Tier-0b kernel-axiom trust base; redefinition would be
   detectable by the stdlib's own tests.
2. Theorem shape outside the IR's first-order subset
   (dependent quantification, universe polymorphism beyond
   Prop/Type, type classes as values). These propagate as
   Unsupported and surface as parser-gap, not silent PASS.
3. `_normalize_names` collisions (§5.8 residual risk).
4. SMT solver returning Valid on an unsound VC. Separate from
   the cross-check; mitigation is the parallel
   Alt-Ergo→Z3 prover dispatch in Why3.

### 6.3 Where the gate runs

`bin/check-proof-crosscheck.sh` is invoked by the `Makefile`
target `check-proof-crosscheck`, which is in turn called by
`self-annotate-verify`:

```makefile
self-annotate-verify: .venv
    …existing per-file --no-proof loop…
    @$(MAKE) check-proof-attributions     # namespace audit
    @$(MAKE) check-proof-crosscheck       # IR cross-check
```

The shell wrapper skips files without `#@ proof ` lines (most
files), iterates the rest, aggregates PASS/SKIP/FAIL, and exits
non-zero if any FAIL. Output schema:

```
=== Cross-check aggregate over <N> annotated files ===
  PASS:  <m>
  SKIP:  <k>
  FAIL:  <j>
```

Standalone invocation per file:
`python -m pycsl.proof2why3.crosscheck_ir <py_file>`.

---

## 7. Trust analysis of the dual mechanism

Before the cross-check existed, the registry was the single
manual trust seam: three assumptions (registry-encodes-Rocq,
registry-encodes-Lean, Rocq-and-Lean-agree) were verified by
human review. The mechanical cross-check replaces all three
with one mechanically enforced predicate per `make` run.

The new trust base for the cross-check itself:

| Component | Trust class | Notes |
|---|---|---|
| Coq 8.20.1 kernel | Tier-0a/0b | Standard; propext + funext at most. |
| Lean 4.30.0 kernel | Tier-0b | propext, Classical.choice, Quot.sound. |
| `coq-serapi 8.20.0+0.20.0` (sertop) | Tier-2 | Serializes kernel-elaborated Constr.t. A bug would be visible at schema level. |
| `Lean.Meta.ppExpr` / `Lean.Environment.find?` | Tier-2 | Same — produces ASTs as Lean sees them. |
| `proof2why3.parser` (registry-side) | Tier-2 | ~430-line recursive-descent for the WhyML axiom-body subset. |
| `proof2why3.from_sexp` | Tier-2 | sertop sexp → IR projector. |
| `proof2why3.from_lean_json` | Tier-2 | Lean meta-script JSON → IR projector. |
| `proof2why3.canonical` | Tier-2 | Eight-step pipeline; each step's semantic justification is in §5. |
| `proof2why3.crosscheck_ir` | Tier-2 | Glue + diff. |

The Tier-2 entries are *traded against* the previous "human
curator" Tier-3 assumption. The dual mechanism replaces a
manually-reviewable axiom with mechanically-enforced
proof-vs-registry equivalence at the cost of trusting the
extraction/canonicalization pipeline. Mitigations:

- Negative tests confirm pinpoint-correct diff fingering. See
  the worked tests in §6.2.
- `wp_gen_correct` (a non-gcd theorem with predicate
  quantification) cross-validates rocq==lean, exercising the
  IR / canonicalizer on a structurally different shape from the
  gcd family.
- Both extraction backends share the same final IR; cross-prover
  shape divergences would be visible in the diff before
  affecting any verdict.

---

## 8. Worked example — `gcd_step`

Annotation in `test-suite/corpus/pycsl-reference/0342.py:25`:

```
#@ proof rocq Pycsl.Reference.Gcd.gcd_step
#@ proof lean Pycsl.Reference.Gcd.gcd_step
```

**Rocq theorem statement**
(`test-suite/corpus/pycsl-reference/0342.proofs/rocq/gcd.v:38-46`):

```rocq
Theorem gcd_step : forall a b : nat,
  b > 0 -> Nat.gcd a b = Nat.gcd b (a mod b).
```

**Lean theorem statement**
(`test-suite/corpus/pycsl-reference/0342.proofs/lean/Gcd.lean:38-43`):

```lean
theorem gcd_step (a b : Nat) (_h : b > 0) :
    Nat.gcd a b = Nat.gcd b (a % b) := by
  rw [Nat.gcd_comm a b, Nat.gcd_rec b a, Nat.gcd_comm]
```

**Registry body**
(`src/pycsl/module6_whyml/preamble.py`, `_AXIOM_REGISTRY`):

```
"Pycsl.Reference.Gcd.gcd_step":
    "forall a b : int. a >= 0 -> b >= 0 -> b > 0 -> "
    "gcd a b = gcd b (mod a b)",
```

**Common canonical form** (computed by all three pipelines):

```
(forall v0 v1 : int, ((v0 >= 0) -> ((v1 >= 0) ->
   ((v1 > 0) -> ((gcd v0 v1) = (gcd v1 (mod v0 v1)))))))
```

What each canonicalization step contributes:

| Step | Rocq side | Lean side | Registry side |
|---|---|---|---|
| 5.1 nat→int | `nat` → `int` + `a >= 0 -> b >= 0 ->` prepended | Same | No change (already `int`) |
| 5.2 flatten foralls | n-ary already (text); fold on AST | Fold unary binders | n-ary already |
| 5.7 iff→BinOp | n/a (no iff in gcd_step) | n/a | n/a |
| 5.8 normalize_names | `PeanoNat.Nat.gcd` → `gcd` (via library strip), `Nat.modulo` → `mod` | `Nat.gcd` → `gcd`, `HMod.hMod` → `App("mod", …)` via projector mapping | No change |
| 5.9 alpha | `a, b` → `v0, v1` | `a, b` → `v0, v1` | `a, b` → `v0, v1` |

The byte-equal hash confirms agreement. Spot-check from the
session:

```
✓ Pycsl.Reference.Gcd.gcd_step  (rocq ≡ lean ≡ registry,
                                  hash=898716292)
```

---

## 9. References

### Source code

- `src/pycsl/proof2why3/__init__.py` — package marker.
- `src/pycsl/proof2why3/ir.py` (180 lines) — shared IR
  dataclasses, `mk_arrow_chain`, `flatten_arrow_chain`,
  `free_vars`.
- `src/pycsl/proof2why3/parser.py` (434 lines) — Why3 axiom-body
  recursive-descent parser with surface normalization. Used by
  the registry-side projection.
- `src/pycsl/proof2why3/sertop.py` (359 lines) — sertop
  subprocess driver, `run_sertop_batch`, `parse_sexp`,
  `extract_via_sertop`.
- `src/pycsl/proof2why3/from_sexp.py` (442 lines) — Coq Constr.t
  s-expr → IR projector, `project_constr`,
  `_OP_TABLE_BINOP` for HAdd/HSub/... folding, library prefix
  table.
- `src/pycsl/proof2why3/extract.py` (159 lines) — coqc-Check /
  lake-#check text-path extractors.
- `src/pycsl/proof2why3/extract_lean_meta.py` (75 lines) —
  Python wrapper for the Lean meta-extractor.
- `bin/proof2why3-lean-extract.lean` — Lean meta-script
  (`Lean.Environment.find?` + recursive `Expr → Json`).
- `src/pycsl/proof2why3/from_lean_json.py` (262 lines) — Lean
  JSON → IR projector, type-class plumbing strip,
  `_body_references_bvar_0`.
- `src/pycsl/proof2why3/canonical.py` (476 lines) — eight-step
  pipeline + helpers (substitute, free_vars over IR).
- `src/pycsl/proof2why3/crosscheck_ir.py` (291 lines) —
  3-way diff driver, `IRCrossCheckResult`, CLI entry point.
- `src/pycsl/proof2why3/crosscheck.py` (194 lines) — legacy v0
  regex-based cross-check, kept as parity reference. Not
  invoked by `make`.
- `src/pycsl/proof2why3/normalize.py` (253 lines) — legacy v0
  string normalizer, kept for parity reference.

### Audit infrastructure

- `src/pycsl/audit_proof.py` — namespace-aware Rocq/Lean parser
  (`_parse_rocq_file`, `_parse_lean_file`, allow-list-aware
  state machines).
- `src/pycsl/audit_proof_reverify.py` — reverify orchestrator
  (`verify_rocq_file`, `verify_lean_file`, SHA-256 cache at
  `.audit-cache/{rocq,lean}/`).
- `src/pycsl/proof_axiom_allowlist.py` — kernel-axiom allow-list
  (`ROCQ_KERNEL_AXIOM_ALLOWLIST`, `LEAN_KERNEL_AXIOM_ALLOWLIST`)
  and `Print Assumptions` / `#print axioms` parsers.

### Build integration

- `bin/check-proof-crosscheck.sh` — make-callable wrapper.
- `Makefile` — `check-proof-crosscheck` target invoked by
  `self-annotate-verify`.

### Module 6 registry surface

- `src/pycsl/module6_whyml/preamble.py:18+` —
  `_AXIOM_REGISTRY` (qualname → axiom body) and
  `_AXIOM_FUNCTIONS` (qualname prefix → backing function
  declaration spliced into the WhyML preamble).
- `_emit_preamble_axioms` (same file, ~line 303) — emission
  logic; raises `PyCSLIRError` on a citation missing from the
  registry.

### CLI flags

- `pycsl --audit-proof <file>` — namespace audit (default).
- `pycsl --audit-proof --reverify-proofs <file>` —
  namespace + reverify.
- `pycsl --audit-proof-rocq <file>` — Rocq directives only.
- `pycsl --audit-proof-lean <file>` — Lean directives only.
- `PROOF2WHY3_USE_SERTOP=1` — env flag; switches the Rocq
  extractor in `crosscheck_ir.py` from coqc-Check to sertop.
- `PROOF2WHY3_USE_LEAN_META=1` — env flag; switches the Lean
  extractor from lake-#check to the meta-script.

### Companion documents

- `0342_explanation.md` — GCD worked example end-to-end.
- `docs/cross-validated-spec-sources.md` — original
  architecture sketch the proof2why3 pipeline materializes.
- `closer-to-code-execution-status.md` — execution log
  documenting the build-up of the pipeline.

### External dependencies and schemas

- Coq 8.20.1 kernel + Coq stdlib `Nat.gcd_*` lemmas.
- Lean 4.30.0 kernel + Lean core `Nat.gcd_*` lemmas (no Mathlib
  needed for the gcd family).
- `coq-serapi 8.20.0+0.20.0` — install via
  `opam install coq-serapi=8.20.0+0.20.0`. SerAPI schema source:
  `~/.opam/coq-4.14/.opam-switch/sources/
  coq-serapi.8.20.0+0.20.0/serlib_8_20/ser_constr.ml`
  (Constr.t serialization) and `…/serapi/serapi_protocol.ml`
  (query_cmd enum).

### Per-test layout

- `test-suite/corpus/pycsl-reference/0342.py` — Python source
  with cited directives.
- `test-suite/corpus/pycsl-reference/0342.proofs/README.md` —
  conventions doc.
- `test-suite/corpus/pycsl-reference/0342.proofs/rocq/gcd.v` —
  seven theorems under `Module Pycsl. Module Reference.
  Module Gcd.` nesting.
- `test-suite/corpus/pycsl-reference/0342.proofs/lean/Gcd.lean` —
  seven theorems under `namespace Pycsl.Reference.Gcd`.
- `test-suite/corpus/pycsl-reference/0342.proofs/lean/lakefile.lean` —
  per-test Lake package (no Mathlib dep).
