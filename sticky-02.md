# Plan — Close the remaining gaps from `sticky-01.md` Phases 1-4

> Continuation of `sticky-01.md`. The first iteration (items 53-55 in
> `closer-to-code-execution-status.md`) landed:
>
> - Phase 0 (`--reverify-proofs`): coqc + lake env lean +
>   Print Assumptions / #print axioms allow-list check, content-hash
>   cached.
> - Phases 1+2+3 v0: regex-based 3-way cross-check, 7/7 PASS on 0342,
>   identified two real registry gaps.
> - Phases 1-4 v1: first-order IR (Forall/App/BinOp/etc.) + recursive
>   descent + canonicalization, 7/7 PASS on 0342, negative test
>   fingers dissenting source.
>
> This plan closes the four gaps explicitly called out in item 55's
> "Production gap remaining" section:
>
> - **Gap A**: sertop (Coq elaborated AST instead of pretty-print
>   scraping).
> - **Gap B**: Lean meta-script using `Lean.Environment` + `Expr` API
>   instead of `#check` text scraping.
> - **Gap C**: IR expansion for non-gcd-family theorem shapes
>   (predicates, higher-order quants, records, classes).
> - **Gap D**: Phase 5 — wire cross-check into `make self-annotate-verify`.
>
> Working directory: `/home/fabrice.derepas@canonical.com/git/pycsl/`.
> Switches: `coq-4.14` (OCaml 4.14.2) for Coq work, Lean 4.30.0
> (via `~/.elan/`) for Lean.

## Context

The v1 cross-check from sticky-01 works on 0342 but has three known
fragilities:

1. The Coq extractor scrapes `coqc … Check qn.` stdout. The Coq
   pretty-printer's output format is stable enough for the
   gcd-family but is documented as non-versioned: notation handling,
   `Set Printing All` toggles, and Coq stdlib version-drifts will
   surface here. The proper fix is `coq-serapi` (sertop), which
   exposes Coq's elaborated AST as s-expressions over a pipe.

2. The Lean extractor scrapes `lake env lean … #check @qn` stdout.
   Lean 4's pretty-printer has the same fragility class. The proper
   fix is a small Lean meta-script using `Lean.Environment.find?`
   and `Lean.Expr` to emit structured JSON.

3. The IR (`src/pycsl/proof2why3/ir.py`) only models the
   gcd-family-needed subset: Forall, Exists, App, BinOp, UnaryOp,
   IntLit, BoolLit, Var, Unsupported. Real-world proofs hit:
   - predicate applications (`wp s Q es`, `P args…`),
   - quantification over predicates (`forall P : ExecState → Prop, …`),
   - record / structure result types,
   - type-class dispatch (Lean's `HEq`, `Decidable`),
   - mutual recursion.

   Each of these falls through to `Unsupported` today, which the
   diff reports correctly but does NOT cross-check.

4. The cross-check is currently manual:
   `python -m pycsl.proof2why3.crosscheck_ir <file>`. Wiring it
   into `make self-annotate-verify` (alongside the existing
   namespace audit + `--reverify-proofs`) makes the trust chain
   gate enforce structural agreement on every CI run.

Sequencing decision: D first (easiest, highest immediate value),
then A and B in parallel (independent extraction backends), then C
driven by what A+B actually surface from real-world theorems.

DEFERRED to future sessions:
- Coq universe-polymorphism diff (universe-polymorphic statements
  produce `Var` referencing unified universes that won't compare
  across rocq/lean — needs an explicit Universe layer in IR).
- Mathlib-only theorems (Lean side may need Mathlib in lakefile).
- `proof2why3 emit` direction (regenerate `_AXIOM_REGISTRY` from
  the cross-checked IR).

Total estimate across A+B+C+D: **~12-19 days**.

---

## Phase D — `make` integration (~1-2 days, do first)

### Problem

`python -m pycsl.proof2why3.crosscheck_ir <file>` is currently
manual. The current `make self-annotate-verify` runs
`check-proof-attributions` (namespace audit) only. A
build-time-enforced cross-check is the gating that closes the
"manual curation" trust assumption from `0342_explanation.md` §4.3.

### Approach

1. **New shell wrapper** `bin/check-proof-crosscheck.sh`:
   ```bash
   #!/usr/bin/env bash
   set -u
   total_pass=0
   total_fail=0
   for f in test-suite/corpus/pycsl-reference/*.py \
            src/self-annotate/src/*.py \
            src/self-annotate/src/module6_whyml/*.py; do
       [ -f "$f" ] || continue
       # Skip files with no `#@ proof` directives — nothing to check.
       grep -q "^#@ proof " "$f" || continue
       out=$(./.venv/bin/python -m pycsl.proof2why3.crosscheck_ir "$f" 2>&1)
       pass=$(echo "$out" | sed -n 's/.*\([0-9][0-9]*\) PASS.*/\1/p' | tail -1)
       fail=$(echo "$out" | sed -n 's/.*\([0-9][0-9]*\) FAIL.*/\1/p' | tail -1)
       [ -z "$pass" ] && pass=0
       [ -z "$fail" ] && fail=0
       total_pass=$((total_pass + pass))
       total_fail=$((total_fail + fail))
       if [ "$fail" -ne 0 ]; then
           echo "$out"
       fi
   done
   echo "=== Cross-check summary: $total_pass PASS, $total_fail FAIL ==="
   [ "$total_fail" -eq 0 ] || exit 1
   ```
2. **Makefile target** added near `check-proof-attributions`:
   ```makefile
   .PHONY: check-proof-crosscheck
   check-proof-crosscheck: .venv
       @bash bin/check-proof-crosscheck.sh
   ```
   Wire it into `self-annotate-verify`:
   ```makefile
   self-annotate-verify: .venv
       @echo "=== Self-annotation verification (canonical src/) ==="
       …existing per-file --no-proof loop…
       @$(MAKE) check-proof-attributions
       @$(MAKE) check-proof-crosscheck   # NEW
   ```
3. **Audit-anchor stubs** under `src/self-annotate/src/*.proofs/`
   don't have `_AXIOM_REGISTRY` entries — their `True` theorem bodies
   would canonicalize to `Forall(…, body=Var(true))` but the
   registry side would be missing. Decision: the wrapper SKIPs
   any qualname missing from `_AXIOM_REGISTRY` rather than
   FAILing. Audit-anchor stubs are documented as "namespace
   presence only, NOT cross-validated"; the cross-check only
   applies to entries with registry bodies.

   Implementation: `crosscheck_ir.py:crosscheck_file_ir` already
   handles the missing-registry case (`r.registry_canon = None`,
   `pairwise["rocq==registry"] = None`, `all_agree = False`
   because the registry side is missing). We need to add an
   explicit "SKIP registry-not-cited" classification so these
   don't count as FAIL.

4. **Cache friendliness**: cross-check today re-extracts on
   every run. Add a SHA-256-keyed cache (mirroring
   `audit_proof_reverify.py`'s pattern) under
   `.audit-cache/crosscheck/` so warm runs are sub-second.

### Implementation surface

- **New file** `bin/check-proof-crosscheck.sh` (~30 lines).
- **Modified** `Makefile:33-40` (`self-annotate-verify`) + add
  `check-proof-crosscheck` rule.
- **Modified** `src/pycsl/proof2why3/crosscheck_ir.py`:
  - Add explicit "registry not cited" SKIP classification.
  - Add cache reading/writing via the same scheme as
    `audit_proof_reverify.py`.
- **New file** `src/pycsl/proof2why3/crosscheck_cache.py` —
  factor the cache logic out so reverify + crosscheck share it.

### Verification

```bash
# Phase D end-to-end:
make self-annotate-verify
# Expect:
#   ✓ Self-annotation verification: 14 files PASS  (existing)
#   ✓ Proof-attribution audit: 34/34 PASS         (existing)
#   ✓ Cross-check summary: 7 PASS, 0 FAIL         (NEW)

# Cache warm-run:
time make self-annotate-verify
# Expect: ≤ 2 s warm vs ≤ 60 s cold.

# Negative test:
sed -i 's|gcd a 0 = a|gcd a 0 = a + 1|' src/pycsl/module6_whyml/preamble.py
make self-annotate-verify
# Expect: cross-check FAIL on Pycsl.Reference.Gcd.gcd_0 with
# detailed IR diff. Make exits non-zero.
git checkout src/pycsl/module6_whyml/preamble.py
```

### Risk + fallback

- The `grep -q "^#@ proof "` skip avoids extracting on files
  that don't cite anything (most files). If a file is missed
  because the `#@` is indented, skip it — extraction overhead
  is acceptable in the worst case.
- Cache invalidation must include both the proof file's SHA
  AND the registry body string — a registry edit without a proof
  file edit must invalidate.

---

## Phase A — sertop for Coq elaborated-AST extraction (~3-5 days)

### Problem

The current extractor (`src/pycsl/proof2why3/extract.py:extract_rocq_statements`)
scrapes `coqc` stdout from a companion file containing
`Check <qualname>.` lines. The output is Coq's pretty-printer
output — stable on the gcd-family but not version-pinned. Known
fragilities:

- `Set Printing Notations` (default) vs `Unset Printing Notations`
  alters operator rendering.
- Coq 8.18→8.20 changed how `forall (x : T)` vs `forall x : T,`
  is rendered.
- Implicit args (`@gcd Nat`, `gcd ?a`) leak in some
  configurations.
- Universe annotations (`@gcd_step Type@{u}`) appear in
  universe-polymorphic statements.

The proper fix is `coq-serapi` ([sertop](https://github.com/ejgallego/coq-serapi))
— Coq's official AST-as-s-expression serializer.

### Approach

1. **Install dependency**:
   ```bash
   opam install coq-serapi=8.20.0+0.20.0
   ```
   Verified to install 9 packages (sexplib + ppx + parsexp +
   yojson_ppx + sertop). Adds ~few minutes to a clean opam build.

2. **New file** `src/pycsl/proof2why3/sertop.py`:
   - Spawns `sertop --printer=sertop -Q . ""` as a long-lived
     subprocess (one process per file, not one per qualname,
     amortizing startup).
   - Writes `(Add () "Require Import <module>.")` then
     `(Exec 1)` then `(Query () (Definition Pycsl.Reference.Gcd.gcd_step))`.
   - Reads s-expression responses via a small reader: `(`/`)`
     stack with token accumulation.
   - Returns the *type term* AST as a Python tuple-of-tuples
     (Lisp-style sexp).

3. **Modify** `src/pycsl/proof2why3/extract.py`:
   - Add `extract_rocq_statements_sertop()` alongside the
     existing `extract_rocq_statements()` (`Check`-based).
   - Default `extract_rocq_statements` to dispatch by env var:
     `PROOF2WHY3_USE_SERTOP=1` selects sertop, otherwise fall
     back to the `Check` extractor (preserves current CI behavior
     until the sertop path is fully tested).

4. **New file** `src/pycsl/proof2why3/from_sexp.py`:
   - Projects a sertop s-expression AST into the shared IR
     (`ir.py`).
   - Mapping rules:
     - `(Prod (Name a) Nat (Prod (Name b) Nat (App (Const PeanoNat.Nat.gcd) [Var a; Var b] = …)))` →
       `Forall(("a", "b"), "nat", App("gcd", (Var("a"), Var("b"))) ...)`.
     - `Const` references: short-name strip per the existing
       `_LIBRARY_PREFIX_STRIPS` table.
     - `Universe` / `Sort` annotations: stripped silently
       (Tier-3 — universe checking is trusted to Coq's kernel).
     - `Lambda`, `LetIn`: emitted as `Unsupported(reason="lambda")`
       — predicates as values are out of scope for Phase A; Phase
       C may add them.

5. **Wire into `crosscheck_ir.py`**:
   - When sertop is available, use `extract_rocq_statements_sertop`
     and `from_sexp.project_to_ir` instead of
     `extract_rocq_statements` + `parse_type_expr`.
   - The downstream canonicalization (`canonical.canonicalize`) is
     unchanged — the IR shape is the same regardless of extraction
     backend.

### Implementation surface

- **opam dep** `coq-serapi=8.20.0+0.20.0`.
- **New** `src/pycsl/proof2why3/sertop.py` (~150 lines):
  - subprocess driver + s-expression reader/writer.
- **New** `src/pycsl/proof2why3/from_sexp.py` (~200 lines):
  - sexp → IR projection.
- **Modified** `src/pycsl/proof2why3/extract.py`:
  - Environment-driven dispatch between sertop and Check.
- **New** `tests/proof2why3/test_sertop.py` (~80 lines):
  - Round-trip tests: each gcd theorem extracts via both backends
    and the resulting IR canonicalizes to the same Term.
- **Updated docs**:
  - `docs/setup.md` — note `coq-serapi` in the bootstrap list.
  - `closer-to-code-execution-status.md` — item 56 for Phase A.

### Reused infrastructure

- `audit_proof_reverify._coqc_version` — generalize to also
  return sertop version when available; used in the cache key
  so a sertop upgrade invalidates cached IRs.

### Verification

```bash
# Phase A unit tests:
.venv/bin/pytest tests/proof2why3/test_sertop.py -v
# Expect: all 7 gcd theorems produce a non-Unsupported IR via
# sertop, AND the canonicalized form matches the Check-extractor
# canonicalized form.

# Phase A end-to-end:
PROOF2WHY3_USE_SERTOP=1 python -m pycsl.proof2why3.crosscheck_ir \
    test-suite/corpus/pycsl-reference/0342.py
# Expect: 7/7 PASS, same hashes as the default extractor.

# Regression: disable sertop, ensure Check path still works.
unset PROOF2WHY3_USE_SERTOP
python -m pycsl.proof2why3.crosscheck_ir \
    test-suite/corpus/pycsl-reference/0342.py
# Expect: 7/7 PASS, same hashes.
```

### Risk + fallback

- **opam install slow / fails**: if sertop isn't available in the
  user's environment, the `PROOF2WHY3_USE_SERTOP` env var stays
  unset and the existing Check extractor runs. No CI break.
- **sertop schema drift**: pin `coq-serapi=8.20.0+0.20.0`. Bake
  the version into the cache key.
- **Lambda / dependent types in elaborated AST**: produce
  `Unsupported(reason="lambda-in-coq-ast")` and surface as
  parser-gap in the diff. Don't silently misinterpret.

---

## Phase B — Lean meta-script for `Lean.Expr` extraction (~3-5 days)

### Problem

Symmetric to Phase A on the Lean side. The current Lean extractor
(`extract_lean_statements`) scrapes `lake env lean … #check @qn`
stdout. Lean's `#check` pretty-printer is unstable: dot notation
(`a.gcd b`) vs explicit (`Nat.gcd a b`), implicit-arg `@`
insertion, universe annotations, custom notation extensions.

### Approach

1. **New file** `bin/proof2why3-lean-extract.lean` — Lean
   meta-script:
   ```lean
   import Lean
   open Lean Elab Meta

   /-- Extract a JSON-serializable representation of a theorem
       statement, given its qualified name. -/
   def extractTheoremIR (qn : Name) : MetaM Json := do
     let env ← getEnv
     match env.find? qn with
     | none => throwError s!"not found: {qn}"
     | some info => exprToJson info.type

   /-- Project a Lean.Expr into our shared IR JSON shape. -/
   partial def exprToJson : Expr → MetaM Json
     | .forallE n t b _ => do
         let tStr ← ppExpr t
         let bJson ← exprToJson b
         return Json.mkObj [
           ("kind", Json.str "forall"),
           ("binder", Json.str n.toString),
           ("ty", Json.str (toString tStr)),
           ("body", bJson)
         ]
     | .app f a => do
         let fJson ← exprToJson f
         let aJson ← exprToJson a
         return Json.mkObj [
           ("kind", Json.str "app"),
           ("fn", fJson),
           ("arg", aJson)
         ]
     | .const n _ => return Json.mkObj [
           ("kind", Json.str "const"),
           ("name", Json.str n.toString)
         ]
     | .fvar id    => return Json.mkObj [("kind", Json.str "fvar"), ("id", Json.str id.name.toString)]
     | .bvar i     => return Json.mkObj [("kind", Json.str "bvar"), ("idx", Json.num i)]
     | .lit lit    => return Json.mkObj [("kind", Json.str "lit"), ("value", Json.str (toString lit))]
     | other       => return Json.mkObj [("kind", Json.str "unsupported"), ("raw", Json.str (toString other))]

   def main (args : List String) : IO Unit := do
     -- args: ["--proofs-dir", "<dir>", "--targets", "q1,q2,…"]
     -- Parses, imports the proof module, calls extractTheoremIR per target,
     -- writes JSON array to stdout.
     …
   ```

2. **Per-test lakefile**: 0342.proofs/lean/ doesn't have one yet.
   Add a minimal `lakefile.lean`:
   ```lean
   import Lake
   open Lake DSL

   package PycslReferenceGcd0342 where

   lean_lib PycslReferenceGcd0342 where
     srcDir := "."
     roots := #[`Gcd]
   ```
   This lets `lake build` resolve the proof file. The meta-script
   imports `Gcd` from this package.

3. **New file** `src/pycsl/proof2why3/extract_lean_meta.py`:
   ```python
   def extract_lean_statements_meta(proof_file: Path, qualnames: list[str]) -> dict[str, dict]:
       """Run the Lean meta-script and parse its JSON output."""
       res = subprocess.run([
           "lake", "env", "lean", "--run",
           str(_REPO_ROOT / "bin" / "proof2why3-lean-extract.lean"),
           "--proofs-dir", str(proof_file.parent),
           "--targets", ",".join(qualnames),
       ], cwd=str(proof_file.parent), capture_output=True, text=True, timeout=300)
       return json.loads(res.stdout)
   ```

4. **New file** `src/pycsl/proof2why3/from_lean_json.py`:
   - Projects the JSON IR from the meta-script into the shared IR.
   - Mapping:
     - `{"kind":"forall", "binder":"a", "ty":"Nat", "body":…}` →
       `Forall(("a",), "nat", …body…)`.
     - `{"kind":"app", "fn":…, "arg":…}` → linearize curried
       applications into `App(head, args)` form.
     - `{"kind":"const", "name":"Nat.gcd"}` → `Var("gcd")` after
       library-prefix strip.
     - `bvar i` → `Var("v"+str(de Bruijn → name lookup))`. The
       conversion requires a context stack tracking the binders.

5. **Wire into `crosscheck_ir.py`**: parallel `PROOF2WHY3_USE_LEAN_META=1`
   env var dispatches to `extract_lean_statements_meta` +
   `from_lean_json.project_to_ir`.

### Implementation surface

- **New** `bin/proof2why3-lean-extract.lean` (~120 lines).
- **New** `test-suite/corpus/pycsl-reference/0342.proofs/lean/lakefile.lean`
  (~10 lines).
- **New** `src/pycsl/proof2why3/extract_lean_meta.py` (~80 lines).
- **New** `src/pycsl/proof2why3/from_lean_json.py` (~150 lines).
- **Modified** `src/pycsl/proof2why3/extract.py` — env-driven
  dispatch.
- **New** `tests/proof2why3/test_lean_meta.py` — round-trip tests.

### Verification

```bash
# Phase B unit tests:
.venv/bin/pytest tests/proof2why3/test_lean_meta.py -v
# Expect: 7/7 gcd theorems produce non-unsupported IR; canonicalized
# Term matches the #check-extractor canonicalized Term.

PROOF2WHY3_USE_LEAN_META=1 python -m pycsl.proof2why3.crosscheck_ir \
    test-suite/corpus/pycsl-reference/0342.py
# Expect: 7/7 PASS, identical hashes as default Lean path.
```

### Risk + fallback

- **Lean 4.30 internals churn**: pin Lean version (already done via
  `~/.elan/toolchains/`); bake into cache key.
- **De Bruijn lookup bugs**: lambda/forall binder tracking is
  the main source of bugs in this kind of script. Unit tests
  cover binder shadowing.
- **Mathlib dependency**: 0342's Lean proofs use `Nat.gcd_*`
  helpers that are partly stdlib, partly Mathlib. If the lake
  build needs Mathlib, lakefile.lean must `require mathlib from
  git "https://github.com/leanprover-community/mathlib4"`. Heavy
  install but a one-time cost. Mitigation: try without Mathlib
  first (some `Nat.gcd_*` are core), add only if needed.

---

## Phase C — IR expansion for non-gcd-family theorems (~5-7 days)

### Problem

The current IR (`ir.py`) handles the gcd-family surface but not
real-world theorem shapes. After Phases A+B, the extractors will
surface terms that fall through to `Unsupported`. The IR needs
extension to model the cases that matter for the audit.

### Approach

Add the following IR nodes (in priority order — drive by what
extraction actually surfaces):

1. **`Predicate(name, args)`** — distinguishes a logical predicate
   call from a numeric function call. Today's `App` covers both;
   splitting helps with canonicalization rules (predicates can be
   negated; functions can't).

2. **`HigherOrderForall(predicate_var, arg_types, body)`** — for
   quantification over predicates as in `forall (P : ExecState →
   Prop), wp s P es → …`. The gcd family doesn't use these;
   `wp_gen_correct` (cited from Module 5) does.

3. **`Record(fields)`** / **`RecordType(name, fields)`** — for
   result types like Why3's `Map.map int int`. Today's `App` works
   for parametric type calls but record-as-value (e.g., `(a, b)
   : tuple int int`) needs a separate node.

4. **`InstanceArg(class_name, args)`** — Lean type-class arguments.
   Today these are stripped silently; for theorems like
   `Decidable (gcd a b = c)` they're load-bearing.

5. **`MutualGroup([theorems])`** — for the SCC of mutually
   recursive theorems Module 5's `wp_gen` family relies on. Out of
   scope for cross-check (a mutual group is one logical statement,
   diffed as a whole) — but the IR needs to represent it.

### Phasing

- **C.1** (2 d): Predicate + HigherOrderForall. Unblocks
  `wp_gen_correct` and `pycsl_soundness` citations.
- **C.2** (1-2 d): Record / RecordType. Unblocks tuple-returning
  function specs.
- **C.3** (1-2 d): InstanceArg. Lean-only; needed for any
  Mathlib-tagged theorem.
- **C.4** (1-2 d): MutualGroup + cross-check semantics.

Each sub-phase adds a node + the canonicalization rules + a stress
test pulling a theorem outside the gcd family. The proper test set
needs theorems that aren't all `True. Proof. trivial.` audit stubs —
candidates: Module 5's `wp_gen_assign` once it gets a real proof
upstream, or a new cross-validated reference test
(0353.py — pick a non-gcd worked example).

### Implementation surface

- **Modified** `src/pycsl/proof2why3/ir.py`: add 5 new dataclasses.
- **Modified** `src/pycsl/proof2why3/canonical.py`: extend the
  pipeline to handle each new node. Mainly: predicates need to be
  sorted at the conjunct level; records need field-name
  canonicalization.
- **Modified** `src/pycsl/proof2why3/from_sexp.py` (Phase A) +
  `from_lean_json.py` (Phase B): project the new shapes from each
  extraction backend.
- **New test corpus** under `tests/proof2why3/fixtures/`: small
  synthetic theorems (one per IR node type) so the pipeline can be
  unit-tested without a full proof toolchain.

### Verification

```bash
# Phase C smoke
.venv/bin/pytest tests/proof2why3/ -v
# Expect: all unit tests pass. Each new IR node round-trips
# extraction-canonicalization-equality for a synthetic theorem.

# Integration: pick a non-gcd cross-validated test (e.g., 0352
# already exists with Gcd.v — verify it still works).
python -m pycsl.proof2why3.crosscheck_ir \
    test-suite/corpus/pycsl-reference/0352.py
# Expect: PASS (or graceful diff showing exactly which IR node
# is novel vs gcd-family).
```

### Risk + fallback

- The IR can grow without bound. Each new node adds canonical-form
  rules. Keep a hard rule: every node has a documented
  canonicalization step OR is flagged `Unsupported`. No silent
  approximation.
- Lean's universe handling is genuinely complex. For Phase C
  punt: strip universe annotations entirely. A future phase can
  add a Universe layer if PyCSL ever needs it.

---

## Critical files (consolidated)

**New (Phase D)**:
- `bin/check-proof-crosscheck.sh`
- `src/pycsl/proof2why3/crosscheck_cache.py`

**New (Phase A)**:
- `src/pycsl/proof2why3/sertop.py`
- `src/pycsl/proof2why3/from_sexp.py`
- `tests/proof2why3/test_sertop.py`

**New (Phase B)**:
- `bin/proof2why3-lean-extract.lean`
- `test-suite/corpus/pycsl-reference/0342.proofs/lean/lakefile.lean`
- `src/pycsl/proof2why3/extract_lean_meta.py`
- `src/pycsl/proof2why3/from_lean_json.py`
- `tests/proof2why3/test_lean_meta.py`

**New (Phase C)**:
- `tests/proof2why3/fixtures/` (small synthetic test theorems)
- `tests/proof2why3/test_ir_expansion.py`

**Modified across phases**:
- `Makefile` — `check-proof-crosscheck` target (Phase D)
- `src/pycsl/proof2why3/ir.py` — 5 new node types (Phase C)
- `src/pycsl/proof2why3/canonical.py` — rules per new node (Phase C)
- `src/pycsl/proof2why3/extract.py` — env dispatch between sertop
  and Check (Phase A), meta-script and #check (Phase B)
- `src/pycsl/proof2why3/crosscheck_ir.py` — SKIP for missing
  registry entry; cache wire-up (Phase D)

**Documentation**:
- `closer-to-code-execution-status.md` — items 56-59 (one per phase)
- `0342_explanation.md` §9 — confidence-analysis refresh once
  Phase A+B land (the registry assumption shrinks to
  "extraction backend is correct")
- `docs/cross-validated-spec-sources.md` — mark Phases 1-4 as
  CLOSED once C finishes

---

## Verification (end of plan)

After all four phases land:

```bash
# Full Layer 1 verify, now with cross-check gating.
make self-annotate-verify
# Expect:
#   ✓ Self-annotation verification: 14/14 PASS         (Layer 1 no-proof)
#   ✓ Proof-attribution audit:      34/34 PASS         (namespace)
#   ✓ Cross-check summary:           7 PASS, 0 FAIL    (3-way IR)

# Reverify on the canonical example, sertop + lean-meta enabled.
PROOF2WHY3_USE_SERTOP=1 PROOF2WHY3_USE_LEAN_META=1 \
    pycsl --audit-proof --reverify-proofs \
    test-suite/corpus/pycsl-reference/0342.py
# Expect: 14 namespace + 14 reverify + 7 IR cross-check = 35 PASS.

# Negative test (still works at the make level).
sed -i 's|gcd a 0 = a|gcd a 0 = a + 1|' src/pycsl/module6_whyml/preamble.py
make self-annotate-verify
# Expect: cross-check FAIL at Pycsl.Reference.Gcd.gcd_0, exit 1.
git checkout src/pycsl/module6_whyml/preamble.py

# Reference tests + suite stay green.
bash bin/run-reference-tests.sh --pycsl --start-at 342 --stop-at 351
# Expect: 10/10 PASS.
bash bin/run-self-annotation-suite.sh
# Expect: 26/26 PROVED.
```

End-state metrics expected:

- **Tier-1 axiom count**: 0342's spec-import axioms are now
  *mechanically* derived from the cross-checked IR, not from the
  hand-curated `_AXIOM_REGISTRY`. The registry remains as a cache;
  divergence between registry and extracted IR is a build error.
- **CI runtime**: cold ~ 60-90 s (sertop startup + lake build);
  warm with caches: ≤ 3 s.
- **Per-theorem confidence**: 0342_explanation.md §9.4's "manual
  curation" assumption is gone for any cited theorem; the trust
  chain is `theorem statement ← prover kernel ← extraction
  backend ← canonicalization ← structural equality`.

---

## Sequencing rationale

- **Phase D first** — `make` integration is the highest-leverage
  cheap win. Once landed, the current v1 cross-check gates every
  build automatically, even before A/B/C add robustness.
- **Phase A and B independent** — sertop has an opam dependency;
  the Lean meta-script doesn't. Can run them in parallel by two
  contributors, or A→B sequentially by one.
- **Phase C last** — the IR expansion is driven by what
  extraction actually surfaces. Doing it before A+B means
  guessing at what shapes Lean/Coq elaboration will produce;
  doing it after A+B means writing IR exactly for the cases
  that matter.

## Effort summary

| Phase | Days | Closes which Gap |
|---|---|---|
| D | 1-2 | Gap D: make integration |
| A | 3-5 | Gap A: sertop |
| B | 3-5 | Gap B: Lean meta-script |
| C | 5-7 | Gap C: IR expansion |

**Total: ~12-19 days** focused work.

## Risk register

- **sertop / coq-serapi unavailable in some envs.** Mitigation:
  feature flag (`PROOF2WHY3_USE_SERTOP=1`) preserves fallback.
- **Lean meta-script depends on Mathlib in some cases.** Mitigation:
  try stdlib-only first; only add Mathlib if a target theorem
  needs it.
- **IR expansion induces a canonicalization regression.** Mitigation:
  golden test suite — the 7 gcd theorems' canonical hashes are
  recorded; any change to `canonical.py` that perturbs them is
  flagged in CI.
- **`make self-annotate-verify` runtime growth.** Mitigation:
  aggressive content-hash caching at every layer (reverify,
  cross-check, sertop).

---

_Cross-references:_
- `sticky-01.md` — prior plan; this is the explicit continuation.
- `closer-to-code-execution-status.md` items 53-55 — what landed.
- `0342_explanation.md` §4.3, §9.3-§9.7 — trust assumptions this
  plan reduces.
- `docs/cross-validated-spec-sources.md` — original architecture
  sketch, now ~80% materialized after Phases 1-5.

_Naming convention reminder (from saved feedback):_ `/plan` output
is saved to a named repo-root file (this one is `sticky-02.md`,
continuing the series). The harness plan file at
`~/.claude/plans/parsed-booping-ember.md` is not the source of
truth.
