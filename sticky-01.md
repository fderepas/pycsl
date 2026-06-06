# Plan — Mechanically cross-check `#@ proof` registry + re-run proofs at audit time

> Eliminates three current trust assumptions in 0342's chain:
> 1. The registry body faithfully encodes the Rocq theorem.
> 2. The registry body faithfully encodes the Lean theorem.
> 3. The Rocq and Lean theorems are statements of the same
>    mathematical claim.
>
> AND replaces today's syntactic audit (namespace-aware presence
> check only) with an actual re-verification: `coqc` + `lake build`
> run on the cited proof files; failure of either fails the
> audit.
>
> Operates against `0342_explanation.md` §9.3-§9.5 weaknesses and
> `docs/cross-validated-spec-sources.md` §1-§7 architecture sketch.
> Working directory: `/home/fabrice.derepas@canonical.com/git/pycsl/`.

## Context

Today (2026-05-29 v3 state):

- The seven `#@ proof rocq` / `#@ proof lean` directives in
  `test-suite/corpus/pycsl-reference/0342.py` resolve via
  `src/pycsl/audit_proof.py`, which only parses the proof file
  for a matching `Module X. ... Theorem foo` (Rocq) or
  `namespace X` ... `theorem foo` (Lean) declaration. It does NOT
  invoke `coqc` or `lake build`.

- The WhyML axiom body for each cited qualname comes from the
  hand-curated `_AXIOM_REGISTRY` dict in
  `src/pycsl/module6_whyml/preamble.py:18-36`. There is NO
  mechanical link between the registry body, the Rocq theorem
  statement, and the Lean theorem statement.

- Result: a registry entry whose body differs from what
  Rocq+Lean actually prove would still pass `pycsl
  --audit-proof` and would produce a "verified" `.mlw` whose
  axioms are unsound — verification would succeed vacuously.

This plan delivers both pieces of the closure in one sequenced
work program, staged so each phase is independently
deployable:

- **Phase 0**: `--reverify-proofs` flag invoking `coqc` and
  `lake build` on the cited proof files. Quick win,
  closes Goal B alone. ~3-5 days.
- **Phases 1-4**: `proof2why3` package extracting theorem
  statements from Rocq + Lean, normalizing to a shared IR, and
  diffing against each other and the registry. Closes Goal A.
  ~2-3 weeks.
- **Phase 5**: integrate into `make self-annotate-verify` and
  `bin/run-reference-tests.sh`; make the registry auto-generated
  rather than hand-curated. ~2-3 days.

Total: **~4 weeks** focused work for a complete closure.

The architecture mirrors what
`docs/cross-validated-spec-sources.md` §5-§7 already sketched —
this plan makes that sketch concrete and executable.

---

## Phase 0 — `--reverify-proofs`: actually invoke coqc + lake (Goal B)

### Problem

The audit's PASS verdict today guarantees only that "some file in
`<test>.proofs/{rocq,lean}/` contains a theorem named X under
namespace Y". It does NOT guarantee:
- the theorem compiles under Coq/Lean's kernel,
- the theorem has zero `Admitted` / `sorry` / unsupported `axiom`,
- the proof file's `Require Import` / `import` lines resolve,
- the file's dependencies are present in the local environment.

A `True. Proof. trivial. Qed.` audit stub (like the ones added in
item 49 of `closer-to-code-execution-status.md` for the
self-annotate citations) would pass audit even though it isn't a
real proof.

### Approach

Add a `--reverify-proofs` flag to `pycsl` and an internal mode in
`audit_proof.py`. When set:

1. **For Rocq**: invoke `coqc -R <proofs_dir> <Namespace> <file>.v`
   for each `.v` file under `<test>.proofs/rocq/`. Cwd inside the
   proof dir; capture stdout+stderr; require exit 0.
2. **For Lean**: invoke `lake env lean <file>.lean` for each
   `.lean` file under `<test>.proofs/lean/` if no `lakefile.lean`
   is present; otherwise invoke `lake build` in the directory.
   Capture; require exit 0.
3. **Axiom inventory** for Rocq: after successful compile, run a
   small companion `.v` script that does
   `Print Assumptions <qualname>.` for each cited qualname.
   Fail if the assumption set contains anything outside an
   allow-list (`Coq.Logic.PropExtensionality.propositional_extensionality`,
   `Coq.Logic.FunctionalExtensionality.functional_extensionality_dep`).
4. **Axiom inventory** for Lean: after successful compile, run
   `#print axioms <qualname>` and require the assumption set is
   subset of `{propext, Classical.choice, Quot.sound}`.
5. **Cache by content hash**: store the result keyed on
   SHA-256 of the proof file + Coq/Lean version. Skip re-verify
   on cache hit. Cache directory:
   `.audit-cache/{rocq,lean}/<sha>.json` containing
   `{exit_code, axioms, mtime}`. Invalidated automatically when
   the file changes.

### Implementation surface

- **New file** `src/pycsl/audit_proof_reverify.py` — orchestrates
  `coqc` / `lake` subprocess invocations. Reuses the path-resolution
  logic from `src/pycsl/pycsl.py:469` (existing `coqc -R why3_coq
  Why3 vpath` pattern for Why3-extracted Coq proofs).
- **Modified** `src/pycsl/audit_proof.py:328-340`
  (`_audit_one_prover`). Adds an optional `reverify: bool`
  parameter that, when true, invokes
  `audit_proof_reverify.verify_rocq_file` /
  `verify_lean_file` after the namespace-presence check passes.
- **Modified** `src/pycsl/pycsl.py:554-568`. Adds
  `--reverify-proofs` flag (default false on `--audit-proof`,
  default **true** on `make self-annotate-verify` after Phase 5
  integration). Adds `--axiom-allowlist` for the inventory check
  (with sensible defaults baked in).
- **New file** `src/pycsl/proof_axiom_allowlist.py` — declares the
  hard-coded Coq/Lean kernel axiom allow-list with a short
  rationale per entry. Used by the inventory check.

### Critical functions to reuse

- `src/pycsl/pycsl.py:_run_coqc_with_why3lib` (line ~469) — the
  existing subprocess wrapper. Generalize so it accepts an
  explicit `-R` argument plus arbitrary `coqc` flags.
- `src/pycsl/audit_proof.py:_extract_directives` — already
  collects the cited qualnames per file; output drives the
  per-qualname `Print Assumptions` invocation.

### Verification

After Phase 0:

```bash
# Audit-only (today's behavior, retained)
pycsl --audit-proof test-suite/corpus/pycsl-reference/0342.py
# Expect: 14/14 PASS via namespace presence.

# Audit + re-verify (NEW)
pycsl --audit-proof --reverify-proofs \
      test-suite/corpus/pycsl-reference/0342.py
# Expect:
# 14/14 PASS via namespace presence,
# 0342.proofs/rocq/gcd.v compiled by coqc (≤ 5 s),
# 0342.proofs/lean/Gcd.lean compiled by lake env lean,
# all 14 qualnames' Print Assumptions inside allow-list.

# Negative test: inject a `Admitted.` somewhere — must FAIL
git stash; sed -i 's/Qed\./Admitted./' 0342.proofs/rocq/gcd.v
pycsl --audit-proof --reverify-proofs <file>.py
# Expect: FAIL with non-empty Print Assumptions.
git stash pop

# Self-annotate end-to-end (audit-only behaviour for self-annot
# stubs, which intentionally use True statements):
make self-annotate-verify
# Expect: 34/34 PASS (unchanged from current state).
```

### Risk + fallback

- Coq version mismatch (project locked to 8.20.1; user environment
  may have 8.18 from a different opam switch). Mitigation: the
  reverify subprocess explicitly activates the project's pinned
  switch via `opam env --switch=coq-4.14`.
- `lake build` cost (~30 s cold, ~3 s warm) makes
  `make self-annotate-verify` slow on a clean tree. Mitigation:
  hash cache + parallelism (4 worker subprocesses by default).
  Total cost target: ≤ 15 s for the full self-annotate corpus
  cached, ≤ 60 s cold.
- Lean's `#print axioms` output format isn't perfectly stable.
  Mitigation: parse with a tolerant line-based extractor, not
  brittle regex; pin to Lean 4.29.

---

## Phase 1 — Rocq statement extractor (`proof2why3 extract --rocq`)

### Problem

To compare a Rocq theorem's *statement* against the registry body,
we need a stable machine-readable rendering of the theorem's type
as Coq sees it post-elaboration (with implicit args resolved,
notations expanded enough to be unambiguous, but not so far that
the term becomes unrecognizable).

### Approach — `coq-serapi` (sertop) as the front-end

Use [`coq-serapi`](https://github.com/ejgallego/coq-serapi)
(`sertop`), the canonical Coq AST-as-s-expression serializer. It
is the recommended way to consume Coq's elaborated terms outside
the kernel proper. Single opam install.

Pipeline:

1. **Compile the file once** under the project's local Coq
   switch via Phase 0's reverify path. Produces `.vo`.
2. **Spawn `sertop`** as a subprocess. Send commands:
   ```
   (Add () "Require Import Pycsl.Reference.Gcd.")
   (Exec 1)
   (Query () (Definition Pycsl.Reference.Gcd.gcd_step))
   ```
3. **Parse the s-expression response**. sertop returns the term
   AST with constructor tags `Prod`, `Forall`, `App`, `Const`,
   `Ind`, `Var`, `Sort`, etc. Project into the shared IR
   (Phase 3).
4. **Repeat per cited qualname** in the directive list.

### Implementation surface

- **New package** `src/pycsl/proof2why3/`:
  - `__init__.py`
  - `sertop.py` — sertop subprocess driver + s-expression parser.
    Robust against partial reads, ack/feedback chatter, and
    exit-code propagation.
  - `extract_rocq.py` — given a `.v` file + cited qualname,
    returns the elaborated theorem statement as a parsed
    s-expression. Calls into `sertop.py`.
- **New script** `bin/proof2why3` — CLI dispatcher with
  subcommands `extract`, `cross-check`, `emit`, `verify`.
  Mirrors the design in
  `docs/cross-validated-spec-sources.md` §2.

### Reused infrastructure

- The Rocq build switch resolution in `src/pycsl/pycsl.py:_run_coqc_with_why3lib`
  generalizes to find `sertop` in the same `opam env --switch=coq-4.14`.
- `audit_proof._extract_directives` already parses
  `#@ proof rocq <qualname>` from Python files.

### Verification

```bash
# Phase 1 unit test
.venv/bin/python -m pytest src/pycsl/proof2why3/tests/test_extract_rocq.py
# Expect: extraction for all seven 0342 qualnames returns
# a non-trivial parsed IR; each contains a `Forall` over `nat`
# binders, a `Prod` chain for `->` arrows, and an `App` rooted
# at the `Nat.gcd` constant.

# CLI smoke test
proof2why3 extract --rocq \
    test-suite/corpus/pycsl-reference/0342.proofs/rocq/gcd.v \
    --qualname Pycsl.Reference.Gcd.gcd_step
# Expect: stdout = canonical-form rendering of the theorem.
```

### Risk + fallback

- sertop is an external opam dependency. If the environment
  doesn't have it, the build fails loudly with an install hint.
  Mitigation: document in `docs/setup.md` + add `opam install
  coq-serapi.8.20.0` to the bootstrap script.
- sertop's s-expression schema changes between versions.
  Mitigation: pin `coq-serapi` to a known-good version per the
  project's Coq pin; bake the schema version into the IR header.

---

## Phase 2 — Lean statement extractor (`proof2why3 extract --lean`)

### Problem

Lean 4 has no exact analogue of sertop, but its metaprogramming
API lets us write a small Lean script that elaborates the proof
file, queries the cited theorem's type as `Lean.Expr`, and dumps
it to JSON via `Lean.Json`.

### Approach — Lean meta-script

1. **Compile the proof file** via Phase 0's reverify path
   (`lake build` or `lake env lean`).
2. **Write a generic extractor script** at
   `bin/proof2why3-lean-extract.lean` that:
   ```lean
   import Lean
   open Lean Elab Meta

   def extractStatement (qn : Name) : MetaM Json := do
     let env ← getEnv
     let info := env.find? qn |>.getD (panic! s!"not found: {qn}")
     let type ← Lean.Meta.ppExpr info.type
     return Json.mkObj [
       ("name",  Json.str qn.toString),
       ("type",  Json.str (toString type)),
       ("ast",   reflectExpr info.type)
     ]
   ```
   (See [Lean.MetaM` docs](https://leanprover.github.io/) for
   `ppExpr` and `Expr` introspection. The `reflectExpr` helper
   walks the expression and dumps a structured AST.)
3. **Invoke** via `lake env lean --run
   bin/proof2why3-lean-extract.lean --target
   Pycsl.Reference.Gcd.gcd_step`. Capture JSON from stdout.
4. **Parse** in Python (`extract_lean.py`) and project into the
   shared IR (Phase 3).

### Implementation surface

- **New file** `bin/proof2why3-lean-extract.lean` — the Lean
  meta-script. Takes `--target <Name>` and an optional
  `--proofs-dir`; emits JSON to stdout.
- **New file** `src/pycsl/proof2why3/extract_lean.py` — Python
  wrapper invoking `lake env lean --run` and parsing the JSON
  response.
- **New** `0342.proofs/lean/lakefile.lean` (if absent) — minimal
  Lake project descriptor that includes the proof file in the
  default target. Required so `lake build` and `lake env lean`
  can find the file. If a parent lakefile already exists for
  cross-prover tests, reuse it.

### Reused infrastructure

- `src/formal-semantics/lean/lakefile.lean` shows the existing
  Lean package pattern (`package PyCSL; lean_lib PyCSL`); the
  per-test lakefiles follow the same shape with a `lean_lib
  PycslReferenceGcd` target.

### Verification

```bash
# Phase 2 smoke
lake env lean --run bin/proof2why3-lean-extract.lean \
   --target Pycsl.Reference.Gcd.gcd_step \
   --proofs-dir test-suite/corpus/pycsl-reference/0342.proofs/lean
# Expect: JSON {name: "Pycsl.Reference.Gcd.gcd_step", type: "...",
#               ast: { forall: "a", ty: "Nat", body: {...} }}
```

### Risk + fallback

- Lean meta-script depends on Lean 4 elaboration internals which
  evolve fast. Mitigation: pin Lean version (already done — 4.29);
  isolate the meta-script under the pinned lakefile.
- `lake env lean --run` startup cost is ~2-3 s per invocation.
  Mitigation: extract all qualnames for a file in a single
  invocation (`--targets q1,q2,…`).

---

## Phase 3 — Shared IR + canonicalization (`proof2why3.ir`, `.canonical`)

### Problem

Rocq's elaborated AST and Lean's `Expr` use different constructors,
different name resolution rules, and different conventions for
implicit arguments. Comparing them directly is hopeless. Project
both into a *shared first-order IR* whose terms can be syntactically
diffed.

### Approach — first-order IR with explicit nat-as-int normalization

The IR shape was already sketched in
`docs/cross-validated-spec-sources.md` §5:

```python
@dataclass class Var:       name: str
@dataclass class Lit:       value: int | bool
@dataclass class App:       fn: str; args: list[Node]
@dataclass class BinOp:     op: str; lhs: Node; rhs: Node
@dataclass class UnaryOp:   op: str; arg: Node
@dataclass class Forall:    var: str; ty: str; body: Node
@dataclass class Exists:    var: str; ty: str; body: Node
@dataclass class Divides:   d: Node; n: Node
@dataclass class Unsupported: reason: str; raw: str
```

Canonicalization (mirror §6) does:

1. **Strip implicit / instance binders.** Rocq's elaborated form
   may carry `{a : Type} (HEq : Eq a)` style binders that Lean
   omits. Drop both sides.
2. **Alpha-normalize** bound variables to `v0`, `v1`, ….
3. **AC-flatten** `and`, `or`, `+`, `*` into n-ary sorted nodes.
4. **Confluent rewrites**: `a + 0 → a`, `a * 1 → a`, `not (not a)
   → a`, `a == a → True`, etc.
5. **Normalize divides** to one canonical form (operational `a %
   d == 0` by default).
6. **`nat` quantifier expansion**: `forall x : nat, P(x)` →
   `forall x : int, x >= 0 ==> P(x)`. This is the explicit
   handler for the int↔nat coercion mentioned in
   `0342_explanation.md` §9.4.
7. **Sort multiset of top-level conjuncts** (so `A ∧ B` and `B ∧
   A` are canonically equal).

The output is a fully canonicalized first-order term ready for
structural equality.

### Implementation surface

- **New file** `src/pycsl/proof2why3/ir.py` — dataclasses.
- **New file** `src/pycsl/proof2why3/canonical.py` — the
  normalization pipeline. Each transformation is a separate
  function; the pipeline composes them with explicit fixpoint
  iteration where needed (e.g., AC-flatten until stable).
- **New file** `src/pycsl/proof2why3/from_rocq.py` — projects
  parsed sertop output into the IR. Knows about Coq stdlib
  constants: `Nat.gcd → "gcd"`, `Nat.modulo → "mod"`,
  `Nat.lt → "<"`, etc. Mapping table at the top of the file.
- **New file** `src/pycsl/proof2why3/from_lean.py` — projects
  parsed Lean meta-script output into the IR. Mapping table for
  Mathlib constants: `Nat.gcd → "gcd"`, `HMod.hMod → "mod"`,
  `Nat.lt → "<"`, etc.

### Reused infrastructure

- Existing canonicalization sketch in `pycsl-bridge-plan.md` (per
  cross-validated-spec-sources.md §6) is the design baseline.
- The `Module2_Parser` Lark grammar already handles Why3-style
  binders for the registry parser case (Phase 4) — we can reuse
  its token names.

### Verification

```bash
# Phase 3 unit tests
pytest src/pycsl/proof2why3/tests/test_canonical.py
# Expect: representative round-trips. For example, the seven
# gcd theorems each canonicalize to a stable IR; small surface
# perturbations (variable renaming, conjunct reordering,
# nat→int coercion) all collapse to the same canonical form.
```

### Risk + fallback

- The constant mapping table is open-ended. Mitigation: start
  with the Mathlib + Coq.Init.Nat slice that 0342 needs (~12
  constants); add new entries as future tests require them.
- An unsupported construct triggers `Unsupported(reason, raw)`.
  Mitigation: every IR diff that involves `Unsupported` is a
  hard FAIL; the user is told exactly which construct needs a
  mapping entry.

---

## Phase 4 — 3-way cross-check (`proof2why3 cross-check`)

### Problem

Once Rocq, Lean, and registry are all expressible in the same IR,
the cross-check is a structural diff. But we want a *3-way* check:

- Rocq IR ↔ Lean IR (catches divergent theorem statements
  between the two prover ecosystems).
- Rocq IR ↔ Registry IR (catches a registry body that diverges
  from the Rocq theorem).
- Lean IR ↔ Registry IR (catches the symmetric case for Lean).

A 3-way agreement gives strong confidence. A 2-way agreement +
1-way disagreement points at the dissenting source.

### Approach

1. **Parse the registry body**: the registry string
   `"forall a b : int. b > 0 -> gcd a b = gcd b (mod a b)"` is
   valid WhyML syntax. Parse with a small Lark grammar (new
   file `src/pycsl/proof2why3/whyml_axiom_parser.py`) into the
   shared IR directly — WhyML's `forall`, `->`, `mod`, etc., are
   all already operators in the IR. This is the simplest of the
   three projections.
2. **Run canonicalization** on all three IRs.
3. **Multiset diff** of top-level conjuncts. For each pair, report:
   - structural equality (PASS);
   - "shape-equal but constants differ" (a less-severe FAIL —
     e.g., bound names match but a constant is wrong);
   - "shape diverges" (severe FAIL).
4. **Aggregate per qualname**: a qualname is FULLY CROSS-VALIDATED
   iff all three pairwise diffs are equality. Anything else is a
   build-time error.

### Implementation surface

- **New file** `src/pycsl/proof2why3/crosscheck.py` — 3-way diff
  driver. Top-level `cross_check_qualname(qn) -> CheckReport`.
- **New file** `src/pycsl/proof2why3/whyml_axiom_parser.py` — the
  tiny Lark grammar for the registry body slice.
- **New file** `bin/check-proof-crosscheck.sh` — CI wrapper that
  invokes `proof2why3 cross-check` on every Python file with
  `#@ proof` directives. Listed as new file in
  `docs/cross-validated-spec-sources.md` §2.

### Reused infrastructure

- `_AXIOM_REGISTRY` in
  `src/pycsl/module6_whyml/preamble.py:18` provides the registry
  bodies indexed by qualname.
- Module2_Parser's expression grammar already knows WhyML-like
  syntax — the registry parser can borrow most of it.

### Verification

```bash
# Phase 4: cross-check 0342
proof2why3 cross-check test-suite/corpus/pycsl-reference/0342.py
# Expect:
# Pycsl.Reference.Gcd.gcd_result_nonneg  : PASS (Rocq == Lean == Registry)
# Pycsl.Reference.Gcd.gcd_result_positive: PASS
# Pycsl.Reference.Gcd.gcd_divides_a      : PASS
# Pycsl.Reference.Gcd.gcd_divides_b      : PASS
# Pycsl.Reference.Gcd.gcd_0              : PASS
# Pycsl.Reference.Gcd.gcd_step           : PASS
# Pycsl.Reference.Gcd.gcd_greatest       : PASS

# Negative test: corrupt the registry
sed -i 's/gcd a 0 = a/gcd a 0 = 0/' src/pycsl/module6_whyml/preamble.py
proof2why3 cross-check test-suite/corpus/pycsl-reference/0342.py
# Expect: gcd_0 FAIL (Rocq == Lean, Registry differs at RHS).
git checkout src/pycsl/module6_whyml/preamble.py
```

### Risk + fallback

- Registry strings sometimes embed Why3-specific operator quirks
  (e.g., `\\/` for logical or) that the simple grammar must
  handle. Mitigation: the grammar is purpose-built for the
  axiom-body subset (no full WhyML expression support), so the
  operator set is finite and enumerable.

---

## Phase 5 — Integration (registry auto-generation; `make` gate)

### Problem

Once the cross-check works, the manual registry can become a
*generated artifact*. The registry's source of truth shifts from
the Python dict to "the canonical IR derived from the Rocq+Lean
proofs that agree".

### Approach

Two integration points:

1. **Registry generation**: add `proof2why3 emit` that, given a
   qualname:
   - extracts from Rocq and Lean,
   - canonicalizes both,
   - checks they agree,
   - serializes the canonical IR back to WhyML axiom body
     syntax,
   - writes/updates the registry entry.

   Run as part of `make sync-annotate-src` (or a new
   `make sync-axiom-registry`). The committed registry remains
   in `preamble.py` for fast Module 6 emission; the generation
   step ensures it stays in sync with the proof sources.

2. **Build-time gate**: extend `make self-annotate-verify` to
   invoke `bin/check-proof-crosscheck.sh` after the existing
   `check-proof-attributions`. Failure cascade: cross-check
   failure aborts the verify.

3. **Trust-class downgrade**: the seven `pycsl_axiom_*` axioms in
   the generated `.mlw` move from Tier-1 (named external axiom,
   manually justified) to Tier-3+ (machine-derived from
   Tier-0a-verified Rocq + Lean proofs). The trust assumption
   becomes "the cross-check passes" — a single mechanically
   enforced predicate replacing three manual ones.

### Implementation surface

- **New file** `src/pycsl/proof2why3/emit_why3.py` —
  IR → WhyML axiom body serializer.
- **Modified** `Makefile:48-70` — add `check-proof-crosscheck`
  target invoked by `check-proof-attributions`.
- **Modified** `src/pycsl/module6_whyml/preamble.py:18-36` — the
  `_AXIOM_REGISTRY` dict gains a stub header `# AUTO-GENERATED by
  proof2why3 emit; do not edit by hand. See sticky-01.md Phase 5.`
- **New file** `bin/check-proof-crosscheck.sh` — `make`-callable
  wrapper invoking `proof2why3 cross-check` over the annotated
  corpus.
- **Modified** `0342_explanation.md` §9.3, §9.5, §9.7 — update
  the confidence analysis to reflect the new state. The three
  manual trust assumptions in §4.3 are reduced to one machine
  check.

### Verification

```bash
# End-to-end verification after all five phases
make self-annotate-verify
# Expect:
#   ✓ Audit (namespace presence): 34/34 PASS
#   ✓ Reverify (coqc + lake build): 14/14 PASS for 0342
#   ✓ Cross-check (Rocq == Lean == Registry): 7/7 PASS for 0342
#   ✓ Print Assumptions allow-list: 14/14 PASS

bash bin/run-reference-tests.sh --pycsl --start-at 342 --stop-at 342
# Expect: 0342 full proof PASS, unchanged.

# Regression: corrupt one Rocq theorem statement
sed -i 's/a mod b/b mod a/' \
    test-suite/corpus/pycsl-reference/0342.proofs/rocq/gcd.v
make self-annotate-verify
# Expect: gcd_step cross-check FAIL with detailed diff —
# "Rocq says: gcd a b = gcd b (b mod a); Lean says: gcd a b
# = gcd b (a mod b); Registry says: same as Lean".
git checkout test-suite/corpus/pycsl-reference/0342.proofs/rocq/gcd.v
```

---

## Critical files (consolidated)

**New files**:

- `src/pycsl/audit_proof_reverify.py` (Phase 0)
- `src/pycsl/proof_axiom_allowlist.py` (Phase 0)
- `src/pycsl/proof2why3/__init__.py` (Phases 1-5)
- `src/pycsl/proof2why3/sertop.py` (Phase 1)
- `src/pycsl/proof2why3/extract_rocq.py` (Phase 1)
- `bin/proof2why3-lean-extract.lean` (Phase 2)
- `src/pycsl/proof2why3/extract_lean.py` (Phase 2)
- `src/pycsl/proof2why3/ir.py` (Phase 3)
- `src/pycsl/proof2why3/canonical.py` (Phase 3)
- `src/pycsl/proof2why3/from_rocq.py` (Phase 3)
- `src/pycsl/proof2why3/from_lean.py` (Phase 3)
- `src/pycsl/proof2why3/crosscheck.py` (Phase 4)
- `src/pycsl/proof2why3/whyml_axiom_parser.py` (Phase 4)
- `src/pycsl/proof2why3/emit_why3.py` (Phase 5)
- `bin/proof2why3` (CLI dispatcher; Phases 1-5)
- `bin/check-proof-crosscheck.sh` (Phase 4/5)
- `0342.proofs/lean/lakefile.lean` (Phase 2; if absent)

**Modified files**:

- `src/pycsl/audit_proof.py` — add `reverify: bool` parameter
- `src/pycsl/pycsl.py:554-568` — `--reverify-proofs` flag
- `src/pycsl/module6_whyml/preamble.py:18-36` — auto-generated
  marker on `_AXIOM_REGISTRY`
- `Makefile:48-70` — `check-proof-crosscheck` target
- `0342_explanation.md` §9.3-§9.7 — confidence-analysis refresh
- `docs/cross-validated-spec-sources.md` — close out the "future
  work" status; pipeline is now live

**Documentation**:

- This file (`sticky-01.md`) tracks the plan.
- `closer-to-code-execution-status.md` — add items 53-57
  (one per phase).
- `self-annot-2.md` — note that the Tier-1 axiom assumptions
  shrink from three manual to one mechanical.

---

## Sequencing rationale

- **Phase 0 first** because re-verification is a clean win on its
  own — it closes Goal B with no dependency on the harder Goal A
  work. Even if Phases 1-5 slip, the audit becomes meaningfully
  stronger after Phase 0.
- **Phase 1 before Phase 2** because Coq's sertop is more mature
  than Lean's metaprogramming; getting Rocq extraction right
  first informs the Lean projection design.
- **Phase 3 in parallel with Phase 2** is possible — the IR
  design doesn't depend on Lean specifically. Defer the
  parallelism decision until Phase 2's actual cost is known.
- **Phase 4 requires all of 1-3** by definition.
- **Phase 5 is the integration crunch** — schedule for a focused
  week after the four upstream phases settle.

## Effort summary

| Phase | Days | Deliverable |
|---|---|---|
| 0 | 3-5 | `--reverify-proofs` flag; Goal B closed |
| 1 | 5-7 | Rocq statement extractor |
| 2 | 3-5 | Lean statement extractor |
| 3 | 5-7 | Shared IR + canonicalization |
| 4 | 3-5 | 3-way cross-check; Goal A closed |
| 5 | 2-3 | Make-gate integration |

**Total: 21-32 days** (~4 weeks at typical sustained pace).

## Risk register (cross-phase)

- **opam / lake version drift** — pin Coq 8.20.1, Lean 4.29.1,
  `coq-serapi` 8.20.0. Bake versions into the audit cache key so
  a version bump invalidates the cache.
- **CI runtime cost** — cold `lake build` on 26 self-annotate
  files plus 12 cross-validated reference tests is ~30 minutes.
  Mitigate via aggressive content-hash caching and parallel
  worker pools.
- **Lean meta-script churn** — Lean 4 internals change. Mitigate
  by pinning Lean version and writing the meta-script against
  stable public API only (`Lean.Environment`, `Lean.Elab.Meta`).
- **Single-statement scope** — this plan covers PyCSL's
  `#@ proof <prover> <qualname>` directive at the *statement*
  level. It does NOT extend to verifying the *axiom-using
  contexts* — i.e., that the cited theorem is actually applied
  correctly inside the WhyML preamble's axiom block. That's a
  Why3-side soundness check (Tier-2 trust) and out of scope.

---

_Cross-references:_
- `docs/cross-validated-spec-sources.md` — original architecture
  sketch this plan operationalizes.
- `0342_explanation.md` §4.3 and §9 — what this plan removes from
  the trust base.
- `closer-to-code-execution-status.md` item 49 — the audit-anchor
  stubs from prior work; the reverify path needs to handle them
  separately (they intentionally compile to `True` statements,
  so reverify accepts them but cross-check is N/A for stubs).
- `closer-to-code.md` Q4 trust-seam — this plan tightens the
  Tier-1 corner of that diagram.
