# Remove `--no-proof` and `\trusted` from Test 0342 — Rocq + Lean as Cross-Validated Spec Sources

**Status:** ⚠️ **Historical document.** This plan was the original
proposal for cross-validated spec sources. The work shipped 2026-05-26
→ 2026-05-27 under the directive name `axiom_from`, later renamed
back to `proof` on 2026-05-27. The current syntax is
`#@ proof <prover> <qualname>` (space-separated, load-bearing). The
text below is preserved as historical context; do not re-execute its
steps.

Status (original): Plan (revised)
Date: 2026-05-26
Supersedes: the `#@ uses number.Gcd` plan (`simple2.md`), which solved
the discharge problem but bypassed Rocq/Lean as trust anchors.

## 0. Framing — what this plan is, and what it isn't

The previous plan made Why3's `number.Gcd` stdlib axioms the trust
anchor for 0342's GCD postconditions, and demoted the Rocq and Lean
proofs in `0342.proofs/` to "cross-prover provenance" — documentation
that the audit script resolves but Why3 never reads.

That works for 0342 in isolation, but it is the wrong architecture for
the broader goal: **annotating `pycsl`'s own source with PyCSL
contracts derived from Rocq + Lean theorems, cross-validated against
each other before being shipped to Why3**. Under that architecture,
Why3's stdlib axioms are a *discharger of last resort* (used when no
proof-assistant statement is available), not the source of spec
content.

This plan rebuilds 0342 the right way. The Rocq and Lean theorems in
`0342.proofs/` become the actual statements Why3 uses to discharge.
A new `#@ axiom_from` directive imports those statements into the
WhyML preamble as Why3 axioms, with the statements themselves
extracted by a small `proof2why3` pass that is the precursor of
`rocq2pycsl` / `lean2pycsl`.

The `#@ uses number.Gcd` directive from the previous plan is still
built — it's a useful primitive for proofs that already exist in
Why3's stdlib — but it is no longer the mechanism this test depends
on. 0342 specifically exercises proof-assistant import because that's
what we ultimately need for self-hosting.

## 1. Architecture

```
0342.proofs/rocq/Gcd.v   0342.proofs/lean/Gcd.lean
  @[pycsl_target=...]      @[pycsl_target "..."]
        │                          │
        ▼                          ▼
   rocq-extract               lean-extract
   (sertop)                   (lake env lean --run)
        │                          │
        ▼                          ▼
   Rocq IR ──────┐         ┌────── Lean IR
                 │         │
                 ▼         ▼
              canonical-form
                 │         │
                 └────┬────┘
                      ▼
                cross-check
                      │
       ┌──────────────┼─────────────┐
       │              │             │
       ▼              ▼             ▼
   manifest       Why3 axioms   #@ proof
   (TOML)         in preamble   reverse-ptrs
                      │
                      ▼
                  Module6
                      │
                      ▼
              0342.py annotated
                      │
                      ▼
                    pycsl
                      │
                      ▼
                Alt-Ergo / Z3
```

The pipeline has four logical stages:

1. **Extract** statements from Rocq and Lean (`proof2why3 extract`).
2. **Canonicalize** both to a shared IR and verify they agree
   (`proof2why3 cross-check`).
3. **Emit** the canonical IR as Why3 axioms into the preamble alongside
   the existing `#@ uses` imports (`proof2why3 emit`).
4. **Discharge** the Python contracts against those axioms via the
   normal pycsl → Why3 → SMT pipeline.

The Rocq/Lean theorems remain the trust anchors. Why3 axioms are a
*transport medium* for those statements — not an independent source of
content. If a Rocq/Lean statement is wrong, the emitted Why3 axiom is
wrong, and the verification is vacuous. The cross-check between Rocq
and Lean is the defence against unilateral statement error.

## 2. Where this plan touches the codebase

**New tool: `src/pycsl/proof2why3/`** (new package)
- `extract_rocq.py` — sertop subprocess + s-expr → IR
- `extract_lean.py` — lake env lean subprocess + JSON → IR
- `ir.py` — shared first-order IR (see §5)
- `canonical.py` — normalizer (alpha-rename, AC-flatten, sort, …)
- `crosscheck.py` — multiset diff between Rocq IR and Lean IR
- `emit_why3.py` — IR → Why3 `axiom` declarations
- `cli.py` — subcommands: `extract`, `cross-check`, `emit`

**Modified: PyCSL toolchain**
- `src/pycsl/Module2_Parser.py` — `axiom_from_decl` grammar production
  + `AxiomFromDecl` dataclass alongside `ProofAttribution`
- `src/pycsl/Module3_Weaver.py` — attach `csl_axiom_from: list[AxiomFromDecl]`
  to `ast.Module`
- `src/pycsl/Module5_IREmitter.py` — propagate `axiom_from` into the
  program IR
- `src/pycsl/Module6_WhyMLTranspiler.py` — extend `_emit_preamble_uses`
  (line 2820) to invoke `proof2why3 emit` for each `#@ axiom_from`
  entry and splice the resulting axiom block into the preamble

**Modified: test fixture**
- `test-suite/corpus/pycsl-reference/0342.py` — remove `#@ \trusted`,
  add `#@ axiom_from` directives, add loop invariant
- `test-suite/corpus/pycsl-reference/0342.proofs/rocq/Gcd.v` —
  add `#[pycsl_target=...]` attributes
- `test-suite/corpus/pycsl-reference/0342.proofs/lean/Gcd.lean` —
  add `@[pycsl_target "..."]` attributes

**Modified: docs**
- `docs/pycsl-concrete-syntax-reference.md` — new §2.1.12 "Proof
  assistant axiom import"
- `docs/pycsl-static-semantics-reference.md` — well-formedness rule
  for `axiom_from`
- `docs/pycsl-translational-reference.md` —
  `T[[axiom_from prover qualname]] = axiom <name> : <statement>`
- `config/skills/pycsl-annotate/SKILL.md` — list the new directive

**New: CI hook**
- `bin/check-proof-crosscheck.sh` — invokes `proof2why3 cross-check`
  on all `*.proofs/` directories in the corpus; CI gate

## 3. PyCSL directive surface

Three new module-level directives. They form a hierarchy of trust:

```
#@ uses <theory>
```
Imports a Why3 stdlib theory. Trust anchor: the Why3 team's audit.
Use when the property is covered by Why3's stdlib (`number.Gcd`,
`int.Power`, `real.RealInfix`, `set.Fset`, …). This is the directive
from the previous plan — kept, not removed.

```
#@ axiom_from rocq <qualname>
#@ axiom_from lean <qualname>
```
Imports a proof-assistant theorem as a Why3 axiom in the preamble.
Trust anchor: the named Rocq/Lean proof. Each directive references
exactly one theorem. To use a theorem on both sides, pair the
directives (recommended — enables cross-check).

```
#@ proof rocq <qualname>
#@ proof lean <qualname>
```
Informational reverse pointer (from the bridge plan). The `#@ proof`
directive *does not* add anything to the WhyML preamble; it's purely
documentation. When paired with `#@ axiom_from`, it's redundant —
keep `#@ axiom_from` and drop `#@ proof`, since `#@ axiom_from`
implies the proof exists.

**When to use which:**

| Situation | Directive |
|---|---|
| Property is in Why3 stdlib | `#@ uses <theory>` |
| Property has a Rocq+Lean proof; both checked | `#@ axiom_from rocq` and `#@ axiom_from lean` (paired) |
| Property has a Rocq proof only | `#@ axiom_from rocq` (with warning) |
| Property has a proof but you don't want it as an axiom | `#@ proof rocq/lean` (documentation only) |

## 4. The proof-side attributes

Rocq:

```coq
#[pycsl_target="Pycsl.Reference.Gcd.gcd_divides_a"]
Theorem gcd_divides_a :
  forall a b : nat, a >= 0 -> b >= 0 -> (a > 0 \/ b > 0) ->
    a mod (gcd a b) = 0.
Proof. (* ... *) Qed.
```

Lean:

```lean
@[pycsl_target "Pycsl.Reference.Gcd.gcd_divides_a"]
theorem gcd_divides_a :
    ∀ (a b : Nat), a ≥ 0 → b ≥ 0 → (a > 0 ∨ b > 0) →
      a % Nat.gcd a b = 0 := by sorry
```

The `pycsl_target` string is the *canonical name* of the spec — the
key under which the Rocq and Lean theorems are paired. It need not
match either the Rocq theorem name or the Lean theorem name; it's a
separate namespace dedicated to PyCSL. Convention: use Python-style
dotted paths.

Register the attribute on each side via a small companion library:

```coq
(* 0342.proofs/rocq/PycslAttr.v *)
From Coq Require Import Strings.String.
Declare Attribute pycsl_target : string.
```

```lean
-- 0342.proofs/lean/PycslAttr.lean
import Lean
syntax (name := pycslTarget) "pycsl_target" str : attr
-- (full implementation in lean2pycsl-plan.md §3 Phase 1)
```

## 5. The shared IR

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

@dataclass class TheoremIR:
    target: str            # the pycsl_target name
    source: str            # "rocq" | "lean"
    name: str              # the original theorem name
    binders: list[tuple[str, str]]
    statement: Node
    file: str
    line: int
```

This is the IR from the previous plans, with the `target` field added
for pairing.

## 6. Canonical form

Same as `pycsl-bridge-plan.md` §3.2:

1. Strip implicit/instance binders.
2. Alpha-normalize bound variables to `v0`, `v1`, ….
3. AC-flatten `and`, `or`, `+`, `*` to n-ary sorted nodes.
4. Apply a small confluent rewrite set:
   `a + 0 → a`, `a * 1 → a`, `not (not a) → a`, `a == a → True`, etc.
5. Normalize divides to one representation per config
   (operational `n % d == 0` by default; existential opt-in).
6. Normalize `nat` quantifiers: `forall x : nat, P(x)` →
   `forall x : int, x >= 0 ==> P(x)`. This is what makes
   Rocq `nat` and Lean `Nat` interconvertible at the IR level.
7. Sort multiset of top-level conjuncts.

The output of canonicalization is a hashable representation. Two
theorems agree if and only if their canonical forms are equal.

## 7. The cross-check

For each `pycsl_target` name found in either source:

| State | Action |
|---|---|
| Found in Rocq only | Emit warning; emit Rocq IR as axiom; status `rocq-only` |
| Found in Lean only | Emit warning; emit Lean IR as axiom; status `lean-only` |
| Found in both, canonical forms agree | Emit either IR as axiom (Rocq by default); status `reconciled` |
| Found in both, canonical forms disagree | Halt with structured diff; status `disagreement` |

The structured diff is the one from `pycsl-bridge-plan.md` §3.4 — for
each disagreeing target, print both canonical forms side by side and
the multiset diff of top-level conjuncts. Halt is the default; the
user can override with `--allow-disagreement` (and accept that the
emitted axiom is taken from whichever source was specified, with both
prover names attached as `#@ proof` documentation).

Status is recorded in the manifest.

## 8. Why3 emission

For each cross-checked `pycsl_target`, emit a Why3 `axiom` declaration
in the WhyML preamble. The axiom body is the IR rendered to WhyML
syntax (a small dialect-specific printer, parallel to PyCSL emission).

Example: for `Pycsl.Reference.Gcd.gcd_divides_a`, the emitted preamble
fragment is:

```why3
(* axiom from rocq:Pycsl.Reference.Gcd.gcd_divides_a
   = lean:Pycsl.Reference.Gcd.gcd_divides_a
   (canonical forms verified equal) *)
axiom pycsl_axiom_gcd_divides_a :
  forall a b : int.
    a >= 0 -> b >= 0 -> (a > 0 \/ b > 0) ->
    mod a (gcd a b) = 0
```

Two important details:

- The axiom name is mangled from the `pycsl_target` (replace `.` with
  `_`, prefix `pycsl_axiom_`) to avoid collision with Why3 stdlib.
- The body uses Why3 stdlib symbols (`mod`, `gcd` if `use number.Gcd`
  is also present, etc.). The emitter knows the existing
  `#@ uses` set and emits compatible WhyML.

If the IR mentions a function `gcd` that is not imported via `#@ uses
number.Gcd`, the emitter falls back to declaring it as an abstract
function:

```why3
function gcd (a b : int) : int
axiom pycsl_axiom_gcd_divides_a : ...
```

This keeps `axiom_from` self-contained when no Why3 stdlib counterpart
exists — important for self-hosting properties about pycsl internals.

## 9. The manifest

`test-suite/corpus/pycsl-reference/0342.crosscheck.toml`, generated
during `proof2why3 cross-check` and version-controlled:

```toml
# Auto-generated. Do not edit.
schema_version = 1
generator = "proof2why3 0.1"

[[entry]]
target = "Pycsl.Reference.Gcd.gcd_result_nonneg"
rocq   = { name = "gcd_result_nonneg", file = "Gcd.v",    line = 12 }
lean   = { name = "gcd_result_nonneg", file = "Gcd.lean", line = 8  }
status = "reconciled"
canonical_hash = "sha256:7a3f..."

[[entry]]
target = "Pycsl.Reference.Gcd.gcd_divides_a"
rocq   = { name = "gcd_divides_a", file = "Gcd.v",    line = 24 }
lean   = { name = "gcd_divides_a", file = "Gcd.lean", line = 18 }
status = "reconciled"
canonical_hash = "sha256:b1e2..."

# ... etc.
```

CI runs `proof2why3 cross-check --check-only`. The command exits
non-zero if the manifest is stale or any status is `disagreement` or
`*-only` without an explicit allowlist.

## 10. The rewritten 0342.py

```python
"""GCD via Euclidean algorithm.

Spec axioms imported from Rocq and Lean (cross-checked).
"""

#@ axiom_from rocq Pycsl.Reference.Gcd.gcd_result_nonneg
#@ axiom_from rocq Pycsl.Reference.Gcd.gcd_result_positive
#@ axiom_from rocq Pycsl.Reference.Gcd.gcd_divides_a
#@ axiom_from rocq Pycsl.Reference.Gcd.gcd_divides_b
#@ axiom_from rocq Pycsl.Reference.Gcd.gcd_0
#@ axiom_from rocq Pycsl.Reference.Gcd.gcd_step
#@ axiom_from lean Pycsl.Reference.Gcd.gcd_result_nonneg
#@ axiom_from lean Pycsl.Reference.Gcd.gcd_result_positive
#@ axiom_from lean Pycsl.Reference.Gcd.gcd_divides_a
#@ axiom_from lean Pycsl.Reference.Gcd.gcd_divides_b
#@ axiom_from lean Pycsl.Reference.Gcd.gcd_0
#@ axiom_from lean Pycsl.Reference.Gcd.gcd_step

#@ requires a >= 0
#@ requires b >= 0
#@ ensures \result >= 0
#@ ensures (a > 0 or b > 0) ==> \result > 0
#@ ensures (a > 0 or b > 0) ==> a % \result == 0
#@ ensures (a > 0 or b > 0) ==> b % \result == 0
#@ assigns \nothing
def gcd(a: int, b: int) -> int:
    x = a
    y = b
    #@ loop invariant x >= 0
    #@ loop invariant y >= 0
    #@ loop invariant gcd(x, y) == gcd(a, b)
    #@ loop invariant (a > 0 or b > 0) ==> (x > 0 or y > 0)
    #@ loop variant y
    while y != 0:
        r = x % y
        x = y
        y = r
    return x
```

Why Alt-Ergo discharges:

- **At loop exit** (`y = 0`): invariant gives `gcd(x, 0) == gcd(a, b)`.
- **`gcd_0` axiom** (from Rocq+Lean): `forall a, a >= 0 -> gcd a 0 = a`.
- Therefore `x == gcd(a, b)` at exit.
- **`gcd_divides_a` axiom**: `a % gcd(a, b) == 0` directly gives the
  third ensures.
- **`gcd_divides_b` axiom**: same for `b`.
- **`gcd_result_nonneg` / `gcd_result_positive`**: first two ensures.
- **Loop invariant preservation** (`gcd(x, y) == gcd(x, x % y)` after
  `r = x % y; x, y = y, r`): from `gcd_step` axiom.

The `gcd` symbol in the contract is bound to whatever the Why3
preamble declares. Since `#@ axiom_from` emits the axioms about a
function called `gcd`, and the cross-check ensures Rocq's `gcd` and
Lean's `gcd` are about the same operation (`nat → nat → nat` with the
standard recursive definition), the contract's `gcd(x, y)` resolves
consistently. No `#@ uses number.Gcd` needed — the trust comes from
Rocq+Lean, not Why3.

(If you wanted to add `#@ uses number.Gcd` as well, it would be
redundant but would let Why3 sanity-check the axioms against its
stdlib — a useful "third opinion" if you're paranoid.)

## 11. Phased implementation

### Phase A — proof2why3 extract (week 1)

Build the two extractors. This is `rocq2pycsl` Phase 1 and `lean2pycsl`
Phase 1 from the existing plans, restricted to *statement* extraction
(no Python rewriting, no theorem selection logic beyond
`pycsl_target`).

Deliverable: `proof2why3 extract rocq 0342.proofs/rocq/` and
`proof2why3 extract lean 0342.proofs/lean/` each produce a JSON IR
dump of the tagged theorems.

### Phase B — proof2why3 cross-check (3 days)

Implement canonical form + diff + manifest generation. This is the
core of `pycsl-bridge`.

Deliverable: `proof2why3 cross-check 0342.proofs/` produces
`0342.crosscheck.toml` and exits 0 if all statuses are `reconciled`.

### Phase C — proof2why3 emit (2 days)

WhyML axiom printer. Straightforward IR walk.

Deliverable: `proof2why3 emit 0342.proofs/ --target gcd_divides_a`
prints a Why3 axiom block.

### Phase D — PyCSL grammar (1 day)

Add `axiom_from_decl` to Module2's Lark grammar. Add the IR field
through Modules 3 and 5. Wire Module6's `_emit_preamble_uses` (line
2820) to call `proof2why3 emit` for each declared axiom.

Caveat from the previous plan: check the Lark grammar for keyword
collisions. `axiom_from` is two tokens — `axiom` may already be
reserved in some parser contexts.

### Phase E — Rewrite 0342 (1 day)

Add `pycsl_target` attributes to the Rocq and Lean proofs. Rewrite
`0342.py` per §10. Run `proof2why3 cross-check`, confirm manifest is
clean, run `pycsl 0342.py`, confirm Alt-Ergo discharges.

### Phase F — CI integration (1 day)

Add `bin/check-proof-crosscheck.sh` to the corpus runner. Treat
manifest staleness or any non-reconciled status as a test failure.

**Total: ~2 weeks.** This is significantly more than the previous
plan's 4.5 hours, because we're building the actual cross-validated
spec-source pipeline rather than the Why3-stdlib shortcut. The
durable value is the entire `proof2why3` tool, which is the
self-hosting infrastructure for the whole `pycsl` codebase.

## 12. Verification commands

```bash
# 1. Extract statements from both sides.
proof2why3 extract rocq  test-suite/corpus/pycsl-reference/0342.proofs/rocq/ \
                   --out 0342.rocq.json
proof2why3 extract lean  test-suite/corpus/pycsl-reference/0342.proofs/lean/ \
                   --out 0342.lean.json

# 2. Cross-check.
proof2why3 cross-check 0342.rocq.json 0342.lean.json \
                       --manifest test-suite/corpus/pycsl-reference/0342.crosscheck.toml
# Expected: exit 0, all entries status=reconciled.

# 3. Inspect emitted axioms (sanity check).
PYTHONPATH=src .venv/bin/python -c \
  "from pycsl.pycsl import main; import sys; \
   sys.argv=['pycsl', '--dump-whyml', \
             'test-suite/corpus/pycsl-reference/0342.py']; main()" \
  | grep -A2 "axiom pycsl_axiom_"
# Expected: 6 axiom blocks, names matching the pycsl_target values.

# 4. Full proof mode.
PYTHONPATH=src .venv/bin/python -c \
  "from pycsl.pycsl import main; import sys; \
   sys.argv=['pycsl', 'test-suite/corpus/pycsl-reference/0342.py']; main()"
# Expected: "Verification SUCCESS! All contracts formally proven."

# 5. Reference-test runner: PASS.
bash bin/run-reference-tests.sh --pycsl --start-at 342 --stop-at 342

# 6. Cross-check audit.
bash bin/check-proof-crosscheck.sh
# Expected: all manifests reconciled.

# 7. No regression elsewhere.
bash bin/run-reference-tests.sh --pycsl
```

## 13. Trust analysis

**Trusted:**

- Rocq kernel, Lean kernel (independent, established).
- The Rocq and Lean theorem statements in `0342.proofs/`.
- `proof2why3`'s extractor + canonicalizer (small, auditable, tested).
- Why3, Alt-Ergo, Z3.
- pycsl's WP soundness proof (also in Rocq + Lean).

**Not trusted (checked):**

- The pairing between Rocq and Lean statements — verified by
  canonical-form equality in cross-check.
- The translation from Rocq/Lean IR to Why3 axiom syntax — checked
  by Why3's own type-checker rejecting malformed axioms.
- pycsl's transpiler from PyCSL to Why3 — validated by the WP
  soundness proof.

**Residual risk:**

- **Common-mode bug in both extractors**: e.g., both Rocq and Lean
  extractors translate `nat` to `int` without the `>= 0` precondition.
  Cross-check passes (because both made the same mistake) but the
  emitted axiom is wrong. Mitigation: a small `proof2why3
  self-test` corpus of theorems with hand-computed canonical forms,
  run in CI.
- **Disagreement between the two formalizations of pycsl's
  semantics**: not relevant for 0342 (which is about GCD, not pycsl
  internals), but will matter as the approach scales to self-hosting.
- **Axiom inconsistency**: if the imported Rocq theorem is actually
  false (e.g., the proof has a bug or uses `Admitted`), the emitted
  Why3 axiom is unsound and Alt-Ergo can "prove" anything. Mitigation:
  CI gate that fails if any imported theorem's Rocq proof contains
  `Admitted.` or `admit.`, and similarly `sorry` on the Lean side.

## 14. Risks and scope cuts

- **Effort scope.** The previous plan was 4.5 hours. This plan is
  ~2 weeks. The delta is the cost of doing the architecturally
  consistent thing: build the actual cross-validation pipeline now,
  rather than building it later after committing to a Why3-stdlib
  pattern that doesn't generalize.

- **`pycsl_target` collisions.** Two theorems claiming the same target
  name (within Rocq, within Lean, or one in each) need a deterministic
  resolution rule. v1: the cross-check fails with a duplicate-target
  error. The user must rename one.

- **Theorems with proofs in only one prover.** Common during
  development. v1: warning, axiom emitted from the available side,
  manifest status `rocq-only` or `lean-only`. CI gate can be
  configured to halt on any single-prover entry once the codebase is
  meant to be cross-validated.

- **Statement complexity.** The first-order subset (per the IR in §5)
  covers ~95% of what GCD-style proofs need. Anything outside (higher
  order, dependent types, complex inductive types) surfaces as
  `IR.Unsupported` and halts extraction. v1 accepts this as a hard
  boundary; later versions can extend the subset.

- **Lean's `Nat` vs Rocq's `nat` vs Why3's `int`.** Canonical form
  step (6) normalizes both `Nat` and `nat` quantifiers to `int +
  precondition`. Verified by self-test corpus.

- **Why3 version skew.** The emitted axioms use Why3 stdlib operators
  (`mod`, comparison operators). Pin Why3 ≥ 1.8.x. Earlier versions
  may need adjusted operator names.

## 15. Why this is the right architecture for self-hosting

Once `proof2why3` exists, the path to annotating `pycsl`'s own source
is clear:

1. For each `pycsl` function, write Rocq and Lean theorems stating
   its postconditions, tagged with `pycsl_target` naming the function.
2. Place the proofs alongside the Python source
   (`src/pycsl/Module2_Parser.py.proofs/{rocq,lean}/`).
3. Add `#@ axiom_from rocq <target>` and `#@ axiom_from lean <target>`
   on the Python function.
4. `proof2why3 cross-check` runs in CI, ensuring the two
   formalizations agree about what each function does.
5. pycsl re-verifies its own source using the emitted axioms.

This is exactly the bridge architecture from `pycsl-bridge-plan.md`,
arrived at via the 0342 worked example. The 0342 test is the
*first instance* of the pattern, not a one-off.

Compare to the previous plan's outcome: if 0342 ships with
`#@ uses number.Gcd`, the pattern that gets reused for every
numerical property is "find a Why3 stdlib theory that covers it." That
works for GCD, modular arithmetic, real numbers, sets — but not for
properties about `pycsl`'s parser, transpiler, or WP soundness, since
Why3's stdlib doesn't know about those. Self-hosting would require
building this architecture anyway. Doing it now means 0342 demonstrates
the right pattern from the start.

## 16. Alternatives considered

- **Keep `#@ uses number.Gcd` for 0342, build `proof2why3` later.**
  Pragmatic but creates two patterns in the corpus: stdlib-imported
  tests and proof-imported tests. The pressure to use the easier one
  (stdlib) will drift the codebase toward Why3-stdlib dependence and
  push proof-import out of the critical path. Picking the harder
  pattern for the first instance is a forcing function.

- **`#@ axiom_from` without cross-check.** Build the extractor and
  emitter, skip canonicalization. Faster (~5 days instead of 2 weeks).
  Loses the cross-validation guarantee — `#@ axiom_from rocq X` and
  `#@ axiom_from lean Y` could disagree silently. Acceptable as an
  intermediate milestone but not as the final state.

- **Emit Rocq/Lean statements as Why3 *goals* and try to discharge
  them.** Instead of `axiom`, use `goal` and let Why3 prove the
  imported statement holds. Architecturally cleaner (no axioms in the
  trusted base), but only works if Why3 can prove the statement from
  its stdlib + ambient axioms — for `gcd_divides_a` it can, given
  `use number.Gcd`, but then we're back to the previous plan.
  Worth revisiting as a v2 mode: `#@ axiom_from rocq X
  --recheck-with-why3`.

- **`#@ uses` only, no `#@ axiom_from`.** The previous plan. Rejected
  for the reasons in §15.

## 17. Effort estimate

| Phase | Effort |
|---|---|
| A — proof2why3 extract (Rocq + Lean) | 1 week |
| B — proof2why3 cross-check | 3 days |
| C — proof2why3 emit | 2 days |
| D — PyCSL grammar + Module6 integration | 1 day |
| E — Rewrite 0342 + verify | 1 day |
| F — CI integration | 1 day |
| Documentation updates | 1 day |
| **Total** | **~2 weeks** |

The bulk of the work is reusable for every subsequent test that
imports proof-assistant theorems, including the entirety of pycsl
self-hosting. The marginal cost of the next `#@ axiom_from` use is
"write the Rocq + Lean theorems and tag them with `pycsl_target`" —
a few minutes per theorem.

## 18. References

- `lean2pycsl-plan.md` — Phase 1 is exactly proof2why3-extract for Lean.
- `rocq2pycsl-plan.md` — Phase 1 is exactly proof2why3-extract for Rocq.
- `pycsl-bridge-plan.md` — sections 2 (linking), 3 (reconciliation), 5
  (trust analysis) are inherited wholesale.
- Why3 reference manual, chapter on `axiom` declarations and theory
  imports.
- Lean 4 attribute API: `Lean.Elab.Attribute`.
- Coq attribute API: Coq Reference Manual, section "Attributes".
