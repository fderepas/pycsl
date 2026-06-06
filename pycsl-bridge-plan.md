# `pycsl-bridge` — Linking and Reconciling Rocq and Lean Spec Sources

**Status:** ⚠️ **Historical document.** This plan uses the
colon-separated `#@ proof rocq:` / `#@ proof lean:` directive form
that was removed from the language on 2026-05-27. The current
directive syntax is `#@ proof <prover> <qualname>` (space-separated,
load-bearing), and the audit machinery now lives in
`src/pycsl/audit_proof.py` rather than a shell script. The text
below is preserved as historical context; do not re-execute its
steps.

A meta-tool on top of `rocq2pycsl` and `lean2pycsl` that solves two
problems specific to self-hosting `pycsl`:

1. **Linking** — how a Python function in `pycsl`'s source identifies
   itself to the Rocq or Lean theorems that specify it (and vice versa).
2. **Reconciliation** — how to ensure both formalizations produce the
   same PyCSL contracts, or to surface disagreements precisely.

This document assumes you have:
- PyCSL's denotational/operational semantics formalized in Rocq.
- The same semantics formalized in Lean 4.
- A proof of the WP calculus' soundness in each.
- Working (or planned) `rocq2pycsl` and `lean2pycsl` per the earlier plans.

---

## 1. Why both problems matter for self-hosting

The goal is to annotate `pycsl`'s own source with PyCSL contracts that
are derived from theorems you have already proven about `pycsl`'s
components (parser, transpiler, etc.). Then `pycsl` re-verifies itself
via Why3+SMT.

The trust chain becomes:

```
Rocq/Lean kernels   ──┐
                      │
WP soundness proof  ──┼──> pycsl correctly emits Why3 ──┐
(both formalisms)     │                                  │
                      │                                  ├──> SMT verdict
pycsl-bridge        ──┤                                  │    on annotated
(linker+reconciler)   │                                  │    pycsl source
                      │                                  │
Why3 + SMT solvers  ──┘──────────────────────────────────┘
```

The WP soundness proof is what closes the loop: if it's correct, then
pycsl's emitted Why3 is a sound abstraction of the annotated Python,
and SMT discharge of the VCs implies the original spec holds. **Having
the proof in two systems gives you cross-validation of WP soundness
itself** — the WP definition is the same, but the two kernels check it
independently. The reconciler extends that cross-validation to the
spec-derivation step.

---

## 2. The linking problem

### 2.1 Design alternatives

| Option | Where the link lives | Pros | Cons |
|---|---|---|---|
| A. Name convention | Theorem name encodes `module__func__property` | No metadata needed | Brittle; renames break everything |
| B. Python-side marker | `#@ verified_by Rocq:thm_name` on the `def` | Visible to Python readers | Edited by tool *and* by hand; merge conflicts |
| C. Proof-side attribute | `@[pycsl_spec "qualname"]` / `#[pycsl_target=...]` | Single source of authoring; proof is the truth | Python source doesn't say where its spec came from |
| D. External manifest | `bridge.toml` listing all pairings | Decoupled; CI-friendly | Yet another file to maintain by hand |
| E. Hybrid (C + reverse pointer + manifest) | C is authored; B and D are auto-generated | Single source of truth, full visibility, auditable | Three artifacts in sync — tool must guarantee that |

**Choose E.** The proof-side attribute (C) is the only place a human
edits the link. The reverse pointer in Python and the manifest are
*outputs* of the bridge tool, regenerated on every run. Stale outputs
are detected by re-running and diffing.

### 2.2 Addressing scheme

Use Python's `__qualname__` rooted at the package:

```
pycsl.parser.Module2_Parser.Parser.parse_expression
pycsl.transpiler.Module5_Transpile.lower_function
pycsl.cli.main
```

This addresses class methods, top-level functions, and nested defs
uniformly. The bridge tool resolves each qualname to a `(file, line,
def_node)` triple at emission time via libcst.

### 2.3 Attribute syntax on each side

**Lean 4:**

```lean
@[pycsl_spec "pycsl.parser.Module2_Parser.parse_expression"]
theorem parse_expression_sound :
    ∀ (src : String), parse_expression src ≠ .error → ... := by
  sorry
```

The attribute is registered by your `PycslExport.lean` library (per the
`lean2pycsl` plan §3 Phase 1). It carries a string literal — the
Python qualname.

**Rocq:**

Modern Rocq supports user-defined attributes via the `Attributes` API:

```coq
#[pycsl_target="pycsl.parser.Module2_Parser.parse_expression"]
Theorem parse_expression_sound :
    forall src, parse_expression src <> Error -> ... .
Proof. ... Qed.
```

Register the attribute in a small `PycslExport.v` companion file:

```coq
From Coq Require Import Strings.String.
From Coq Require Export Attributes.

Declare Attribute pycsl_target : string.
```

(Exact API may need to be checked against your Rocq version; if custom
attributes aren't available, fall back to comment markers
`(* @pycsl-target ... *)` — slightly worse ergonomics, same semantics.)

### 2.4 Reverse pointer in Python (auto-generated)

After the bridge tool resolves theorems → qualnames → Python defs, it
emits **two** kinds of `#@` lines:

```python
#@ requires src != ""
#@ ensures \result != ErrorKind
#@ assigns \nothing
#@ proof rocq: Pycsl.Parser.parse_expression_sound
#@ proof lean: Pycsl.Parser.parse_expression_sound
def parse_expression(src: str) -> Expression:
    ...
```

The `#@ proof` lines are **informational** for PyCSL (they aren't part of
the verification logic) but serve three roles:

1. **Traceability** — anyone reading the Python source can find the
   theorem.
2. **Drift detection** — on the next bridge run, if the resolved theorems
   don't match what the reverse pointer says, the tool surfaces a clear
   warning.
3. **Manifest cross-check** — the manifest (§2.5) must agree with the
   reverse pointers; if not, the source has been edited out of band.

Extend the PyCSL `#@` grammar with a new informational directive:

```ebnf
proof_attribution: "proof" PROVER ":" qualified_name
PROVER: "rocq" | "lean"
```

PyCSL's parser should accept and ignore these — they are documentation,
not specification.

### 2.5 The manifest (auto-generated)

`pycsl-bridge.manifest.toml`, written under version control:

```toml
# Auto-generated by pycsl-bridge. Do not edit by hand.
schema_version = 1

[[entry]]
python  = "pycsl.parser.Module2_Parser.parse_expression"
rocq    = ["Pycsl.Parser.parse_expression_sound"]
lean    = ["Pycsl.Parser.parse_expression_sound"]
status  = "reconciled"   # or "rocq-only", "lean-only", "disagreement"

[[entry]]
python  = "pycsl.transpiler.Module5_Transpile.lower_function"
rocq    = ["Pycsl.Transpile.lower_function_sound", "Pycsl.Transpile.lower_function_preserves_types"]
lean    = ["Pycsl.Transpile.lower_function_sound", "Pycsl.Transpile.lower_function_preserves_types"]
status  = "reconciled"
```

A function may have multiple theorems on either side — the manifest
preserves the full list, and the bridge tool conjoins their contracts
when emitting `#@ ensures` lines.

The manifest is the single artifact that CI inspects to verify pairing
health. A pre-commit hook can run `pycsl-bridge --check` to confirm
the manifest is up to date with the attributes in proof sources.

---

## 3. The reconciliation problem

### 3.1 Where Rocq and Lean specs can diverge

Even with identical mathematical intent, the two formalizations may
produce different surface theorems:

1. **Statement shape.** Rocq: `gcd_divides : ∀ a b, gcd a b | a /\ gcd a b | b`.
   Lean: two separate theorems `gcd_dvd_left` and `gcd_dvd_right`. Same
   content, different decomposition.
2. **Naming conventions.** Rocq uses snake_case, Lean uses camelCase or
   `dvd_left` vs `divides_left`. Cosmetic; absorbed by the linker.
3. **Operator preferences.** Divisibility may be stated existentially in
   one and via `%` in the other. Each is legitimate in its formalism;
   they're logically equivalent.
4. **Bound variable names.** `forall a b` vs `forall x y`.
5. **Quantifier order.** `∀ a b d, ...` vs `∀ d a b, ...`.
6. **Implicit arguments and instances.** Lean's elaborated forms carry
   instance binders that Rocq's don't (or vice versa for type classes).

The first four are *stylistic* — same underlying proposition, different
surface. The last two require care but are tractable.

### 3.2 Canonical form on the IR

Both extractors already produce a shared IR (per the existing plans, §4).
Define a normalization procedure that maps any IR term to a unique
representative of its equivalence class under the stylistic differences:

1. **Strip absorbed binders.** After matching outer quantifiers to the
   target function's parameters, both sides should agree on what's left.
2. **Alpha-normalize.** Remaining bound variables get canonical names
   in order of binding: `v0`, `v1`, … Compute this by a left-to-right
   traversal.
3. **AC-flatten.** Associative-commutative operators (`and`, `or`, `+`,
   `*`) become n-ary nodes with sorted operand lists.
4. **Sort commutative chains.** Use a total order on IR nodes (a
   structural-hash-based comparator).
5. **Arithmetic identities.** Apply a fixed set of obvious rewrites:
   `a + 0 → a`, `a * 1 → a`, `not (not a) → a`, `a == a → True`, etc.
   Keep the set small and confluent.
6. **Divides normalization.** Pick *one* representation per
   configuration (operational or existential) and rewrite the other
   form into it before comparison.
7. **Split top-level conjunctions.** A theorem stated as `P /\ Q` and
   one stated as two theorems `P` and `Q` should canonicalize to the
   same multiset `{P, Q}`. Compare multisets of postconditions, not
   single propositions.

Crucially: **you do not need to prove confluence of the rewrite system
formally.** You only need both extractors to apply the same
normalization. If they do, equivalent inputs produce equal outputs;
non-equivalent inputs produce different outputs (which is the bad case
the diff handles).

If you want a stronger guarantee, you *can* state and prove confluence
of this normalizer in Rocq or Lean — it's a finite, terminating rewrite
system on a first-order term language. Probably not worth the effort
for v1.

### 3.3 The reconciler: `pycsl-bridge`

```
pycsl-bridge \
    --rocq-src     proofs/Rocq/ \
    --lean-src     proofs/Lean/ \
    --python-src   src/pycsl/ \
    --output       src/pycsl/ \
    --manifest     pycsl-bridge.manifest.toml \
    --on-disagreement halt          # or 'warn', 'force'
```

Pipeline:

1. Invoke `rocq2pycsl` in "IR-dump" mode → `contracts_rocq.json`, a
   map from qualname to multiset of IR postconditions (plus
   precondition, variant, purity).
2. Invoke `lean2pycsl` in "IR-dump" mode → `contracts_lean.json`.
3. Compute canonical form on every IR term in both maps.
4. Union the qualname keysets. For each qualname:
   - **In both, canonical forms agree** → emit annotated Python with
     dual attribution. Status: `reconciled`.
   - **In both, canonical forms disagree** → emit structured diff.
     Halt or proceed per `--on-disagreement`. Status: `disagreement`.
   - **In Rocq only** → emit with Rocq attribution + warning. Status:
     `rocq-only`.
   - **In Lean only** → emit with Lean attribution + warning. Status:
     `lean-only`.
5. Write updated manifest.
6. Optionally invoke `pycsl` to verify the emitted Python.

### 3.4 Disagreement diff format

When canonical forms diverge:

```
DISAGREEMENT: pycsl.parser.Module2_Parser.parse_expression

  Rocq: Pycsl.Parser.parse_expression_sound (proofs/Rocq/Parser.v:142)
    canonical postcondition multiset:
      {  src != "" ==> \result.kind != ErrorKind  }

  Lean: Pycsl.Parser.parse_expression_sound (proofs/Lean/Parser.lean:87)
    canonical postcondition multiset:
      {  src != "" ==> \result.kind != ErrorKind,
         \length(src) > 0 ==> \result.position >= 0  }

  diff:
    Lean has an additional postcondition not present in Rocq:
      \length(src) > 0 ==> \result.position >= 0

  suggested resolution:
    - prove the missing postcondition in Rocq, OR
    - remove it from the Lean theorem if it's not actually intended
      to be part of the spec, OR
    - add @[pycsl_optional] on the Lean side to mark it as a
      Lean-specific strengthening
```

The diff is line-based on the canonical form (which is normalized text),
so a standard diff library does the heavy lifting once normalization is
applied.

### 3.5 Optional strengthening

Sometimes you genuinely want one formalism to prove a stronger spec
than the other (e.g., during development, when the Lean proof has
caught up but the Rocq one hasn't). Provide an opt-out attribute:

```lean
@[pycsl_spec "pycsl.parser.parse_expression"]
@[pycsl_optional]
theorem parse_expression_position_nonneg : ... := by sorry
```

`@[pycsl_optional]` tells the reconciler: include this in the contract
emitted on the Python side, but do not require a Rocq counterpart. The
emitted Python is then attributed `proof lean:` only for that specific
postcondition.

The mirror exists in Rocq:

```coq
#[pycsl_target="...", pycsl_optional]
Theorem ... .
```

This gives you a controlled escape valve. Use sparingly — every
`pycsl_optional` is unverified-in-the-other-system, which weakens the
cross-validation guarantee for that obligation.

---

## 4. Combined workflow

```
proofs/Rocq/*.v               proofs/Lean/*.lean
  #[pycsl_target=...]           @[pycsl_spec "..."]
        │                              │
        ▼                              ▼
   rocq2pycsl                    lean2pycsl
   (IR-dump mode)                (IR-dump mode)
        │                              │
        └──> contracts_rocq.json       contracts_lean.json
                  │                              │
                  └─────────┬────────────────────┘
                            ▼
                    pycsl-bridge
                            │
                     canonicalize
                            │
                       reconcile
                            │
            ┌───────────────┴────────────────┐
            ▼                                ▼
       manifest.toml              src/pycsl/*.py (annotated)
       (CI checkpoint)            (with dual attribution)
                                            │
                                            ▼
                                          pycsl
                                            │
                                            ▼
                                          Why3
                                            │
                                            ▼
                                       SMT verdict
```

Each artifact is independently inspectable. CI runs:

```
pycsl-bridge --check          # manifest matches sources
pycsl src/pycsl/              # all VCs discharge
```

---

## 5. Self-hosting and trust analysis

You're verifying `pycsl` using `pycsl`. The interesting question is
where the circularity bottoms out.

**What is trusted:**

- Rocq kernel and Lean kernel (independently audited; established).
- The PyCSL semantics formalization (your work; auditable as a Rocq/Lean
  document).
- The WP soundness proof in each formalism (your work).
- `pycsl-bridge`'s canonicalizer and reconciler (small, auditable code).
- Why3, Alt-Ergo, Z3 (established, externally audited).

**What is NOT trusted (because it's checked):**

- The Rocq → IR translator and Lean → IR translator: their output is
  checked by the *other* translator producing the same canonical IR.
  An error in one translator that produces a wrong spec will be caught
  by the reconciler unless both translators make the same mistake.
- The IR → PyCSL string translator: its output is parsed back by PyCSL
  itself and re-verified. A wrong-but-syntactically-valid translation
  would either fail to discharge (caught) or accidentally match a
  trivially-true spec (uncaught — minor risk).
- `pycsl`'s own transpiler from PyCSL to Why3: validated by the WP
  soundness proof, which is the whole point.

**Residual risk:**

- **Common-mode failure** in both translators. If Rocq → IR and
  Lean → IR both have the same bug (e.g., both translate `(d | n)` as
  `n % d == 0` when they should emit the guarded form), the reconciler
  agrees and the bug goes through. Mitigation: independent
  implementations by independent authors, or stronger: cross-test the
  two translators on the *same* small Gallina/Lean fragment expressed
  in both languages and check that the resulting IRs match.
- **PyCSL semantics formalization disagrees between Rocq and Lean.**
  If your Rocq formalization and your Lean formalization don't describe
  the same language, the WP soundness proofs are about different
  systems and the cross-validation is meaningless. Mitigation: write a
  small *test suite of programs* with hand-computed VCs, run them
  through both formalizations, and check the VCs agree. This is the
  same trick used for compiler validation.
- **Bootstrap circularity.** `pycsl` verifies itself. If `pycsl` is
  buggy in a way that *also* misverifies its own annotations, the
  self-check passes vacuously. This is a known limitation of all
  self-hosting verifiers. The WP soundness proof in two independent
  systems is the strongest mitigation available short of running an
  external verifier on `pycsl`'s output.

In practice this is a strong position to be in. The seL4 project does
not have two independent formalizations of its kernel semantics; you
will, and that's a meaningful improvement.

---

## 6. Implementation effort

Assuming `rocq2pycsl` and `lean2pycsl` are built (or being built) per
the previous plans:

| Phase | Effort | Notes |
|---|---|---|
| Linking: attribute registration on both sides | 2 days | Lean side easy; Rocq side depends on attribute API maturity |
| Linking: qualname index builder | 2 days | Walk Python source via libcst, build qualname → def_node map |
| Reverse pointer emission | 1 day | Augment emitter common library |
| Manifest writer + checker | 2 days | TOML round-trip + drift detection |
| Canonical form: implementation | 5 days | The bulk of the work; iterate until corpus passes |
| Canonical form: test suite | 3 days | Cross-test Rocq and Lean IRs on a corpus of equivalent statements |
| Reconciler: pipeline | 3 days | Wiring; the per-step logic is straightforward |
| Disagreement diff format | 2 days | Diff library + custom pretty-printer |
| Optional strengthening (`@[pycsl_optional]`) | 1 day | Attribute + status flag |
| CI integration | 2 days | Pre-commit hook, manifest check, full-rebuild verification |

Total: **3 weeks** dedicated work on top of the two existing tools.

---

## 7. Open questions

1. **Should the canonical form be normative or advisory?** Normative
   means the bridge enforces it strictly — any divergence halts. Advisory
   means it warns but proceeds. Probably start normative for safety,
   add `--lenient` later if it's too painful.
2. **Should `@[pycsl_optional]` be allowed asymmetrically?** I.e., a
   theorem can be optional in Lean but required in Rocq, or vice versa.
   Probably yes — it's documentation about the development state.
3. **Cross-formalism statement translation as a fallback?** If a Rocq
   theorem exists but no Lean counterpart, can the bridge auto-translate
   the statement to Lean and ask the user to prove it? That's an entire
   research project (Dedukti / Logipedia territory). Probably out of
   scope, but worth noting.
4. **How to handle theorems that mention internal pycsl types?** When a
   spec says "the parser returns an `Expression`", both Rocq and Lean
   need a formalization of pycsl's `Expression` ADT. The mapping
   between those two ADT definitions is implicit — make it explicit via
   a small "shared vocabulary" config that lists corresponding type
   names and their layouts. Without this, even straightforward specs
   may fail to reconcile.

---

## 8. References

**Cross-prover interchange (background, probably out of scope but worth
knowing):**

- Assaf, A., et al. *Dedukti: a Logical Framework based on the
  λΠ-Calculus Modulo Theory.* Unpublished manuscript; many follow-ups.
- Thiré, F. *Sharing a library between proof assistants: reaching out
  to the HOL family.* LFMTP 2018. (Logipedia foundations.)
- Hurd, J. *The OpenTheory Standard Theory Library.* NFM 2011.

**Self-hosting verified tools (precedents and design lessons):**

- Kumar, R., Myreen, M.O., Norrish, M., Owens, S. *CakeML: A Verified
  Implementation of ML.* POPL 2014. The CakeML compiler bootstraps
  itself with a verified-in-HOL implementation. Closest precedent for
  what you're doing.
- Klein, G., et al. *seL4: Formal Verification of an OS Kernel.*
  SOSP 2009. capDL toolchain self-verification at the system-init
  layer.
- Anand, A., et al. *CertiCoq: A verified compiler for Coq.* CoqPL
  2017. Coq verified in Coq.

**Canonical forms and normalization (technical references):**

- Baader, F., Nipkow, T. *Term Rewriting and All That.* Cambridge
  University Press, 1998. Standard reference for confluence and
  termination of rewrite systems.
- Standard SMT-LIB preprocessing literature for first-order canonical
  forms.

**Attribute systems:**

- Lean 4 attribute API: `Lean.Elab.Attribute` in the Lean 4 sources.
- Coq attributes: Coq Reference Manual, section "Attributes".

**PyCSL itself:**

- Your formalization documents (Rocq and Lean).
- Your WP soundness proofs.
- The PyCSL annotation reference.
