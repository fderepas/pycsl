# 0342 Trust Chain — Python ↔ PyCSL ↔ Why3 ↔ Rocq/Lean

How `test-suite/corpus/pycsl-reference/0342.py` — the Euclidean GCD
worked example — is verified end-to-end, and what each
`#@ proof rocq` / `#@ proof lean` directive *means* formally.

This document walks the chain from Python source down to
kernel-checked theorems in Rocq (Coq 8.20.1) and Lean (4.29.1),
explaining each transformation, every piece of trust, and the
confidence the resulting verdict warrants.

---

## 1. The three languages and what each is responsible for

| Language | Role | Trust class |
|---|---|---|
| **Python 3** (the body of `gcd`) | Algorithm to be verified | Source of truth for runtime behaviour |
| **PyCSL** (the `#@`-prefixed annotations) | Specification language, lowered into WhyML | Hoare-logic contracts to be discharged |
| **Why3 / WhyML** (auto-generated `.mlw`) | Verification-condition target language | Intermediate format consumed by SMT solvers |
| **Rocq + Lean** (in `0342.proofs/{rocq,lean}/`) | Independent kernel-checked proofs | Trust anchor for the mathematical statements PyCSL imports as axioms |

Two further "languages" sit in the trust base but are not authored
per-test:

- **SMT solvers** (Alt-Ergo 2.6.2, Z3 4.13.3) — discharge the
  generated VCs. Their soundness is taken on trust.
- **Why3 standard library** (`int.Int`, `int.EuclideanDivision`,
  `ref.Ref`) — pre-existing axiomatizations of integer arithmetic
  and mutable references that the emitted MLW imports.

The whole point of the PyCSL → Rocq/Lean linkage is to replace
"trust an undocumented axiom about GCD" with "trust a Rocq theorem
about `Nat.gcd`, *and* trust the matching Lean theorem about
`Nat.gcd`, *and* trust that the two agree". Disagreement between
the provers is detectable; unilateral error in either is caught
by the other.

---

## 2. The Python source — `0342.py` literally

The function body is the classical Euclidean algorithm:

```python
def gcd(a: int, b: int) -> int:
    x = a
    y = b
    while y != 0:
        r = x % y
        x = y
        y = r
    return x
```

The interesting part of the file is the **PyCSL annotation block**
that surrounds the function. Every line beginning with `#@` is a
PyCSL contract, ghost declaration, loop invariant/variant, or
proof-import directive.

```
#@ proof rocq Pycsl.Reference.Gcd.gcd_result_nonneg
#@ proof rocq Pycsl.Reference.Gcd.gcd_result_positive
#@ proof rocq Pycsl.Reference.Gcd.gcd_divides_a
#@ proof rocq Pycsl.Reference.Gcd.gcd_divides_b
#@ proof rocq Pycsl.Reference.Gcd.gcd_0
#@ proof rocq Pycsl.Reference.Gcd.gcd_step
#@ proof rocq Pycsl.Reference.Gcd.gcd_greatest
#@ proof lean Pycsl.Reference.Gcd.gcd_result_nonneg
#@ proof lean Pycsl.Reference.Gcd.gcd_result_positive
#@ proof lean Pycsl.Reference.Gcd.gcd_divides_a
#@ proof lean Pycsl.Reference.Gcd.gcd_divides_b
#@ proof lean Pycsl.Reference.Gcd.gcd_0
#@ proof lean Pycsl.Reference.Gcd.gcd_step
#@ proof lean Pycsl.Reference.Gcd.gcd_greatest
#@ requires a >= 0
#@ requires b >= 0
#@ ensures \result >= 0
#@ ensures (a > 0 or b > 0) ==> \result > 0
#@ ensures (a > 0 or b > 0) ==> a % \result == 0
#@ ensures (a > 0 or b > 0) ==> b % \result == 0
#@ ensures \result == gcd(a, b)
#@ ensures (a > 0 or b > 0) ==> (\forall k; (k > 0 and a % k == 0 and b % k == 0) ==> k <= \result)
#@ assigns \nothing
```

…and inside the loop:

```
#@ loop invariant x >= 0
#@ loop invariant y >= 0
#@ loop invariant gcd(x, y) == gcd(a, b)
#@ loop invariant (a > 0 or b > 0) ==> (x > 0 or y > 0)
#@ loop variant y
```

The contract says: "for non-negative inputs at least one of which
is positive, `gcd(a, b)` returns the unique positive integer that
divides both `a` and `b` and is greater than or equal to every
other positive common divisor". The loop invariant says the
gcd is preserved across iterations; the variant `y` is the
termination measure (strictly decreasing under the natural
ordering on non-negative integers).

---

## 3. PyCSL — the contract language

PyCSL is a Python-embedded annotation language conceptually close
to Why3's WhyML and ACSL. The `#@` prefix marks Python
*comments* that PyCSL parses as contracts. The Python interpreter
ignores them; only PyCSL ingests them.

Key syntactic forms used in 0342:

| Form | Semantics |
|---|---|
| `#@ requires P` | Function precondition (must hold on entry) |
| `#@ ensures Q` | Function postcondition (guaranteed on exit) |
| `#@ assigns \nothing` | Frame condition — no mutable state changes |
| `#@ loop invariant I` | Holds before each iteration of the next loop |
| `#@ loop variant V` | Strictly-decreasing non-negative measure proving termination |
| `\result` | The function's return value (in `ensures` only) |
| `\forall k; P` | Quantification over integer `k` |
| `==>` | Logical implication |
| `gcd(a, b)` | A *logical function* — defined by axioms, not by Python code |
| `#@ proof rocq <qualname>` | Import an axiom statement from a Rocq theorem |
| `#@ proof lean <qualname>` | Import the same axiom statement from a Lean theorem |


The `gcd(a, b)` call inside the contract is **not** the recursive
Python function being defined. It is an uninterpreted logical
symbol that PyCSL will introduce into Why3 as `function gcd (a :
int) (b : int) : int`. It's because of the `#@ proof` annotations
that this logical symbol is created — Module 6 splices the backing
`function` declaration into the preamble when it sees a citation
whose qualname prefix (here `Pycsl.Reference.Gcd.`) matches its
`_AXIOM_FUNCTIONS` table. The seven `#@ proof` directives then
collectively provide the axiomatic content that gives the symbol
its meaning.

---

## 4. The `#@ proof <prover> <qualname>` directive — formal semantics

### 4.1 What the directive accomplishes

A directive `#@ proof rocq Pycsl.Reference.Gcd.gcd_step` causes the
PyCSL pipeline to:

1. **Look up** the qualified name `Pycsl.Reference.Gcd.gcd_step` in
   an internal *axiom registry* maintained inside
   `src/pycsl/module6_whyml/preamble.py` (`_AXIOM_REGISTRY`).
2. **Emit** the registry's WhyML axiom body into the generated
   `.mlw` file's preamble, sanitized to a unique Why3 identifier.
3. **Audit** that the citation actually points at a kernel-proved
   theorem on disk — by parsing the matching `.v` / `.lean` file
   in the test's `0342.proofs/{rocq,lean}/` directory and
   confirming the qualname is *declared* there (namespace-aware
   presence check via `src/pycsl/audit_proof.py`).

The Why3 axiom for `gcd_step` produced by Module 6 is:

```
(* Pycsl.Reference.Gcd.gcd_step — cross-validated Rocq + Lean *)
axiom pycsl_axiom_Pycsl_Reference_Gcd_gcd_step :
  forall a b : int. b > 0 -> gcd a b = gcd b (mod a b)
```

This is *not* the Rocq theorem's statement copied verbatim. It is
the registry's pre-canonicalized rendering of the joint
Rocq-and-Lean claim into Why3 syntax.

The registry is not trusted blindly. The `proof2why3` pipeline
(in `src/pycsl/proof2why3/`) mechanically extracts each cited
theorem's elaborated AST from Rocq (via `sertop`) and Lean (via a
meta-script using `Lean.Environment` + `Lean.Expr`), canonicalizes
both into a shared first-order IR (`ir.py` / `canonical.py`), and
compares them structurally against the registry body. The
mechanical 3-way cross-check fires on every
`make self-annotate-verify` and exits non-zero if any disagreement
is detected. See §10 below for the full architecture.

### 4.2 The semantics in formal terms

The directive's meaning can be decomposed:

```
[[ #@ proof rocq Pycsl.Reference.Gcd.gcd_step ]] =
    let φ := canonical(Rocq_theorem("Pycsl.Reference.Gcd.gcd_step"))
    in  ASSERT_PREAMBLE(`axiom pycsl_axiom_… : φ`)
        ∧ ASSERT_AUDIT_VISIBLE("Pycsl.Reference.Gcd.gcd_step", rocq)
```

Where:

- `canonical(·)` is the registry-driven canonicalization mapping
  Rocq's `forall a b : nat, b > 0 -> Nat.gcd a b = Nat.gcd b (a mod
  b)` to Why3's `forall a b : int. b > 0 -> gcd a b = gcd b (mod a
  b)`. (`Nat` → `int` is part of the canonicalization: PyCSL works
  over `int` with side-conditions `a >= 0`; this is sound iff the
  preconditions sufficiently restrict the domain.)
- `ASSERT_PREAMBLE(α)` splices axiom `α` into the generated
  `.mlw`'s preamble before any `let gcd …` definitions.
- `ASSERT_AUDIT_VISIBLE(qn, prover)` is a *gate*, not an
  emission. It is enforced by `pycsl --audit-proof` and by
  `make self-annotate-verify`. The gate succeeds iff the parser
  for the named `prover` finds `qn` declared inside the matching
  namespace chain in some file under
  `<test>.proofs/<prover>/`.

A paired Rocq-and-Lean citation
`#@ proof rocq Pycsl.Reference.Gcd.gcd_step` +
`#@ proof lean Pycsl.Reference.Gcd.gcd_step` therefore emits a
*single* axiom (the registry deduplicates by qualname) but raises
the audit's evidence bar: both prover files must declare the
qualname. The single axiom on the Why3 side is justified by *two
independent kernel-checked proofs*.

### 4.3 What the directive does — and does NOT do

**What the directive does:**

Under the always-on cross-check wired into
`make self-annotate-verify`:

- The directive's emitted axiom is **structurally equal** to
  the IR projected from both prover-side theorems. Any drift
  (registry vs Rocq, registry vs Lean, or Rocq vs Lean) is
  caught and fails the build with a per-Term pinpoint diff.

With `--reverify-proofs` (opt-in):

- Invokes `coqc -R . "" <file>.v` and `lake env lean <file>.lean`
  on the cited proof files. Compile failure → audit FAIL.
- Checks each cited theorem's assumption set via
  `Print Assumptions` (Rocq) and `#print axioms` (Lean) against
  a kernel-axiom allow-list (`proof_axiom_allowlist.py`).
  Non-allow-listed assumption → audit FAIL.
- Results are cached by SHA-256 of the proof file; warm runs are
  ~1 second.

With `PROOF2WHY3_USE_SERTOP=1` (opt-in):

- Extracts the Rocq theorem's *elaborated Constr.t* via
  `sertop`'s `(Query () (TypeOf …))` — not pretty-print scraping.
- The result is projected to the shared IR via
  `proof2why3.from_sexp.project_constr`.

With `PROOF2WHY3_USE_LEAN_META=1` (opt-in):

- Extracts the Lean theorem's `Lean.Expr` via a meta-script
  (`bin/proof2why3-lean-extract.lean`) using
  `Lean.Environment.find?` — not `#check` scraping.

**What the directive does NOT do:**

- It does not re-elaborate the proofs in a sandbox different
  from `coqc` / `lake env lean`. We trust the project's pinned
  Coq 8.20.1 / Lean 4.30.0 kernels.
- It does not verify the WhyML output of Module 6 against the
  canonical IR — Module 6's `_AXIOM_REGISTRY` lookup is what
  generates the WhyML axiom; the cross-check verifies that
  lookup against both provers, but doesn't independently
  audit Module 6's *emission* (covered separately by Phase 6
  soundness in `Phase6L_*`).

---

## 5. The pipeline — step by step

### 5.1 Step 1 — PyCSL parses the Python file

`src/pycsl/Module1_Ingestor.py` reads `0342.py` with `libcst`,
preserving comments. The `#@`-prefixed comments are extracted as
*contract strings* and attached to the AST nodes they precede.

`src/pycsl/Module2_Parser.py` (a Lark grammar) parses each
contract string into a typed `CSLNode` tree:
- `#@ proof rocq Pycsl.Reference.Gcd.gcd_step` becomes a
  `ProofAttribution(prover="rocq", qualname="Pycsl.Reference.Gcd.gcd_step")`.
- `#@ requires a >= 0` becomes a `Requires` node wrapping
  `BinOp(Var("a"), ">=", Number(0))`.
- `#@ loop invariant gcd(x, y) == gcd(a, b)` becomes a
  `LoopInvariant` node containing a `CallExpr("gcd", [Var("x"),
  Var("y")])` compared to another `CallExpr`.

### 5.2 Step 2 — Semantic analysis (Module 4)

`src/pycsl/Module4_SemanticAnalyzer.py` validates the contracts
against the Python AST: every `\result` appears only in `ensures`;
every `loop invariant` is attached to a `while` or `for`; `gcd`
inside contracts is recognized as a logical function (not the
Python `gcd` being defined) because the contracts reference it
*before* its body is type-checked; concurrency annotations are
consistency-checked; etc.

### 5.3 Step 3 — Contract weaving (Module 3)

`src/pycsl/Module3_Weaver.py` attaches each parsed contract to
its enclosing Python AST element. The output is an annotated AST
where:
- The `gcd` `FunctionDef` carries a `csl_contract` with
  preconditions, postconditions, frame condition, plus the
  module-level `ProofAttribution` list.
- The `while` carries `csl_loop_invariants` and `csl_loop_variant`.

### 5.4 Step 4 — IR emission (Module 5)

`src/pycsl/Module5_IREmitter.py` walks the annotated AST and emits
a JSON Intermediate Representation that captures both the Python
body and the contracts. For 0342 the IR contains a single function
`gcd` with: parameter list, return type, contract dictionary,
statement list (`Assign`, `Assign`, `While { test, body,
invariants, variant }`, `Return`), and `proof` array containing
the seven Rocq + seven Lean attributions.

### 5.5 Step 5 — WhyML transpilation (Module 6)

`src/pycsl/Module6_WhyMLTranspiler.py` consumes the IR and emits
WhyML. The relevant preamble code path
(`_emit_preamble_axioms`, preamble.py:303) is:

1. Scan every IR function's `proof` array; collect the set of
   distinct qualnames (Rocq and Lean entries with the same
   qualname collapse into one).
2. For each qualname, check it appears in `_AXIOM_REGISTRY`. If
   not, raise `PyCSLIRError` at transpile time — a missing
   registry entry is a build-time failure.
3. For each registered qualname, look up the *backing function
   declaration* (e.g. `function gcd (a : int) (b : int) : int`)
   in `_AXIOM_FUNCTIONS` and emit it once.
4. Emit the axiom statement with the sanitized name
   `pycsl_axiom_Pycsl_Reference_Gcd_<thm>` and a comment recording
   the qualname and the cross-validation tag.

The generated `.mlw` then contains exactly seven axioms:

```
function gcd (a : int) (b : int) : int

(* Pycsl.Reference.Gcd.gcd_0 — cross-validated Rocq + Lean *)
axiom pycsl_axiom_Pycsl_Reference_Gcd_gcd_0 :
  forall a : int. a >= 0 -> gcd a 0 = a

(* Pycsl.Reference.Gcd.gcd_divides_a — cross-validated Rocq + Lean *)
axiom pycsl_axiom_Pycsl_Reference_Gcd_gcd_divides_a :
  forall a b : int. a >= 0 -> b >= 0 -> (a > 0 \/ b > 0) ->
    mod a (gcd a b) = 0
…
(* Pycsl.Reference.Gcd.gcd_step — cross-validated Rocq + Lean *)
axiom pycsl_axiom_Pycsl_Reference_Gcd_gcd_step :
  forall a b : int. b > 0 -> gcd a b = gcd b (mod a b)

(* Pycsl.Reference.Gcd.gcd_greatest — cross-validated Rocq + Lean *)
axiom pycsl_axiom_Pycsl_Reference_Gcd_gcd_greatest :
  forall a b k : int. a >= 0 -> b >= 0 -> (a > 0 \/ b > 0) ->
    k > 0 -> mod a k = 0 -> mod b k = 0 -> k <= gcd a b
```

The function body itself is emitted as a WhyML `let rec gcd …`
with the precondition, postconditions, loop invariants, and loop
variant transcribed from the IR.

### 5.6 Step 6 — Why3 verification-condition generation

Why3 reads the `.mlw` file and runs its weakest-precondition
calculus over the `let rec gcd` body, generating one
verification condition per:
- Precondition check at each `pycsl_div` / `pycsl_mod` call (Why3
  must show `y <> 0` at the modulo).
- Loop invariant *initialization* (each invariant holds before
  the loop's first test).
- Loop invariant *preservation* (each invariant is preserved
  across one body execution).
- Postcondition (the conjunction of all `ensures` holds at
  function exit, taking the loop invariants + the negated loop
  guard at exit).
- Termination (the variant `y` strictly decreases under
  well-founded order).

The seven imported axioms are available throughout this calculus.
For example, the postcondition `\result == gcd(a, b)` is
discharged using `gcd_0` and the invariant `gcd(x, y) == gcd(a,
b)`: at loop exit, `y = 0`, the invariant gives `gcd(x, 0) ==
gcd(a, b)`, the `gcd_0` axiom rewrites the LHS to `x`, and
`\result = x` closes the goal. Similarly the divisibility
postconditions use `gcd_divides_a` / `gcd_divides_b`, and the
maximality postcondition uses `gcd_greatest`.

### 5.7 Step 7 — SMT discharge

Why3 hands each VC, in turn, to Alt-Ergo 2.6.2 with a small
timeout. If Alt-Ergo cannot answer Valid, Why3 tries Z3 4.13.3.
For 0342 the SMT log records about a dozen Valid answers:

```
Sub-goal Postcondition of goal pycsl_div'vc: Valid (0.00s, 316 steps).
Sub-goal Loop invariant init of goal gcd'vc: Valid (0.00s, 1568 steps).
…
```

The 0342 SMT cost is genuinely small because the seven axioms
turn the verification into mostly rewriting plus linear arithmetic.

### 5.8 Step 8 — Audit gate

In parallel with proof, `pycsl --audit-proof 0342.py` invokes
`src/pycsl/audit_proof.py`. The audit:

1. Extracts every `#@ proof rocq <qn>` / `#@ proof lean <qn>`
   line in the Python source.
2. For each prover, reads every file under
   `0342.proofs/<prover>/` matching the right extension (`.v` or
   `.lean`).
3. Parses each file with a namespace-aware line-oriented state
   machine (it does NOT invoke `coqc` / `lake`):
   - For Rocq: `Module X.` pushes `X` onto a module stack; `End
     X.` pops; top-level `Theorem foo …` records the qualname
     `X.foo` (joined by `.`).
   - For Lean: `namespace X.Y.Z` splits on `.` and pushes each
     segment; `end X.Y.Z` pops; top-level `theorem foo …` records
     `X.Y.Z.foo`.
4. Reports PASS iff the cited qualname is in the file's parsed
   set, FAIL otherwise.

For 0342 the audit reads `0342.proofs/rocq/gcd.v`, which opens
with:

```rocq
Module Pycsl.
Module Reference.
Module Gcd.
…
Theorem gcd_step : forall a b : nat,
  b > 0 -> Nat.gcd a b = Nat.gcd b (a mod b).
Proof.
  intros a b Hb.
  rewrite (Nat.gcd_comm a b).
  destruct b as [|b']; [lia|].
  change (Nat.gcd (a mod S b') (S b') = Nat.gcd (S b') (a mod S b')).
  apply Nat.gcd_comm.
Qed.
…
End Gcd.
End Reference.
End Pycsl.
```

So the parser records `Pycsl.Reference.Gcd.gcd_step` and the
citation `#@ proof rocq Pycsl.Reference.Gcd.gcd_step` matches.

The audit does the same for `0342.proofs/lean/Gcd.lean` and the
seven `#@ proof lean …` citations.

`make self-annotate-verify` aggregates the audit verdict across
the whole annotated corpus. For 0342 alone it is 14 PASSES
(7 Rocq + 7 Lean).

### 5.9 Step 9 — Reverify gate (opt-in)

With `pycsl --audit-proof --reverify-proofs`, after the namespace
audit passes, `src/pycsl/audit_proof_reverify.py` actually
**re-runs** the proofs:

- For each cited Rocq qualname: `coqc -R . "" <file>.v`
  (validate the proof compiles under the kernel), then
  `Print Assumptions <qualname>.` (extract the dependency set).
- For each cited Lean qualname: `lake env lean <file>.lean`
  (validate), then `#print axioms <qualname>` (assumption set).
- Each assumption is matched against
  `proof_axiom_allowlist.py`: Rocq accepts propext + funext
  ("Closed under the global context" is the strongest case);
  Lean accepts `propext`, `Classical.choice`, `Quot.sound`.

Results are cached at `.audit-cache/{rocq,lean}/<sha256>.json`
so warm runs cost ~1 second. For 0342: cold run ~4 s, warm
~1.1 s. All 7 Rocq theorems report "Closed under the global
context" (zero assumptions); 6/7 Lean theorems use
`[propext, Quot.sound]`, 1/7 has zero assumptions.

Inject `Admitted.` into one Rocq proof → the assumption set
becomes non-trivial → reverify FAILs the entire audit.

### 5.10 Step 10 — Mechanical 3-way cross-check (always-on)

`make self-annotate-verify` invokes `bin/check-proof-crosscheck.sh`
after the namespace audit. For every annotated file with
`#@ proof` citations, this runs
`python -m pycsl.proof2why3.crosscheck_ir <file>` which:

1. **Extracts** each cited theorem's elaborated AST:
   - Rocq: via the `coqc` + `Check` text path (default) or
     `sertop` elaborated Constr.t (`PROOF2WHY3_USE_SERTOP=1`).
   - Lean: via the `lake env lean` + `#check` text path
     (default) or the `Lean.Environment.find?` meta-script
     (`PROOF2WHY3_USE_LEAN_META=1`).
2. **Parses** the registry body (Module 6's `_AXIOM_REGISTRY[qn]`)
   into the same first-order IR.
3. **Canonicalizes** all three via `proof2why3.canonical`: nat↔int
   side-condition expansion, comparison-direction flip
   (`<=` → `>=`), AC-flatten + sort `\/`/`/\`, arrow-chain dedup,
   alpha-rename to `v0`, `v1`, …, name normalization
   (`wpW` ↔ `wp_w`, `ExecState` ↔ `exec_state`).
4. **Structurally diffs** Rocq IR vs Lean IR vs Registry IR
   using Python's `__eq__` on frozen dataclasses. PASS iff all
   three canonical Terms are byte-equal.
5. On FAIL: emits a per-Term pinpoint diff showing the dissenting
   side (`rocq==lean: PASS`, `rocq==registry: FAIL` fingers the
   registry as the wrong one).

For 0342 the cross-check is **7/7 PASS** with hash-equal canonical
forms across rocq/lean/registry per theorem. A negative test
(corrupt `gcd_0`'s registry body to `gcd a 0 = a + 1`) correctly
identifies the single divergence and makes `make` exit non-zero.

`make self-annotate-verify` aggregate output (current state):

```
=== Cross-check aggregate over 6 annotated files ===
  PASS:  14    (0342 + 0352, gcd-family theorems)
  SKIP:  8     (audit-anchor stubs: True/trivial bodies, no registry)
  FAIL:  0
```

---

## 6. The Rocq side — the actual mathematics

`0342.proofs/rocq/gcd.v` proves seven theorems against
**`Coq.Init.Nat.gcd`** — the standard library's recursive
definition of GCD on natural numbers:

```rocq
Fixpoint gcd a b :=
  match a with
  | 0 => b
  | S a' => gcd (b mod S a') (S a')
  end.
```

The proof file's theorems and their tactical content:

| Theorem | Proof |
|---|---|
| `gcd_result_nonneg : ∀ a b, Nat.gcd a b ≥ 0` | `lia.` (immediate from `nat ≥ 0`). |
| `gcd_result_positive : ∀ a b, a>0 ∨ b>0 → Nat.gcd a b > 0` | Case on `Nat.gcd a b = 0`: `Nat.gcd_eq_0` gives both inputs 0, contradicting hypothesis. |
| `gcd_divides_a : ∀ a b, a>0 ∨ b>0 → a mod (Nat.gcd a b) = 0` | `Nat.Lcm0.mod_divide` + `Nat.gcd_divide_l`. |
| `gcd_divides_b` | Symmetric: `Nat.gcd_divide_r`. |
| `gcd_0 : ∀ a, Nat.gcd a 0 = a` | `Nat.gcd_0_r`. |
| `gcd_step : ∀ a b, b > 0 → Nat.gcd a b = Nat.gcd b (a mod b)` | `Nat.gcd_comm` twice + destructuring on `b` to expose `S b'`. |
| `gcd_greatest : ∀ a b k, a>0 ∨ b>0 → k>0 → a mod k = 0 → b mod k = 0 → k ≤ Nat.gcd a b` | `Nat.divide_pos_le` + `Nat.gcd_greatest` (the divisibility-of-gcd lemma) + `Nat.Lcm0.mod_divide`. |

The whole file has zero `Admitted`, zero `Axiom` (beyond what
`Coq.Arith.PeanoNat` already assumes — i.e. the standard
constructive Coq kernel axioms). Each `Theorem` is closed by
`Qed`, meaning Coq's kernel has type-checked the proof term.

The file is **wrapped** in three nested `Module` declarations:
`Module Pycsl. Module Reference. Module Gcd. … End Gcd. End
Reference. End Pycsl.` This is what makes the qualname
`Pycsl.Reference.Gcd.gcd_step` resolvable by Coq's namespace
system *and* by PyCSL's audit parser. The chosen prefix
`Pycsl.Reference.Gcd` is conventional — every cross-validated
reference test in `test-suite/corpus/pycsl-reference/` uses the
prefix `Pycsl.Reference.<TestName>`.

---

## 7. The Lean side — the same mathematics, independently

`0342.proofs/lean/Gcd.lean` proves the same seven theorems
against **`Nat.gcd`** in Lean 4 / Mathlib.

```lean
namespace Pycsl.Reference.Gcd

theorem gcd_result_nonneg (a b : Nat) : Nat.gcd a b ≥ 0 :=
  Nat.zero_le _

theorem gcd_result_positive (a b : Nat) (h : a > 0 ∨ b > 0) :
    Nat.gcd a b > 0 := by
  rcases h with ha | hb
  · exact Nat.gcd_pos_of_pos_left b ha
  · exact Nat.gcd_pos_of_pos_right a hb

theorem gcd_divides_a (a b : Nat) (_h : a > 0 ∨ b > 0) :
    a % Nat.gcd a b = 0 :=
  Nat.mod_eq_zero_of_dvd (Nat.gcd_dvd_left a b)
…
end Pycsl.Reference.Gcd
```

The Lean proofs use a different proof style (term-mode + `by`
block tactics, plus structured `rcases`/`have`) and a different
library API (`Nat.gcd_pos_of_pos_left`, `Nat.gcd_dvd_left`,
`Nat.dvd_gcd`, `Nat.le_of_dvd`), but they establish the same
statements. There is no `sorry`, no `axiom`, and the file
type-checks under Lean 4.30's kernel.

**Why both?** Lean and Coq have independent kernels, independent
standard libraries, and independent communities. If both prove
the same statement of, say, `gcd_step`, then either:
- The statement is correct, or
- Two independent prover ecosystems are unsoundly broken in
  exactly the same way.

The latter is vanishingly unlikely. The whole point of
cross-prover spec-sources is to reduce a one-out-of-N statement
risk by demanding two independent verifications. PyCSL imports
the *common* claim as a Why3 axiom — the cross-check is the
quality gate on that import.

---

## 8. End-to-end verification verdict

Running `pycsl --keep-mlw test-suite/corpus/pycsl-reference/0342.py`:

```
[*] Parsing and Semantic Analysis for '…/0342.py'...
[*] Memory model: hoare
[*] Running Proof Engine (provers: Alt-Ergo,2.6.2, → Z3,4.13.3,)...

--- Verification Results ---
Sub-goal Precondition of goal pycsl_div'vc: Valid (0.00s, 21 steps).
Sub-goal Postcondition of goal pycsl_div'vc: Valid (0.00s, 316 steps).
…
Sub-goal Loop invariant init of goal gcd'vc: Valid (0.00s, 1568 steps).
Sub-goal Loop invariant preservation of goal gcd'vc: Valid (…).
Sub-goal Postcondition of goal gcd'vc: Valid (…).
Sub-goal Variant of goal gcd'vc: Valid (…).
…
[+] Verification SUCCESS! All contracts formally proven.
```

The verdict `Verification SUCCESS` means *every* generated VC was
discharged. Combined with `make self-annotate-verify` and
`bash bin/run-reference-tests.sh --pycsl --start-at 342 --stop-at
342` (which together check audit + suite + full proof),
0342 is the canonical end-to-end PyCSL example.

---

## 9. Confidence analysis — what does "verified" actually warrant?

The verdict is sound iff every link in the chain is sound. Let
me enumerate every assumption:

### 9.1 Tier-0a (verified, axiom-free)

These are kernel-checked theorems with **zero PyCSL-specific
axioms** in Rocq:
- The seven theorems in `0342.proofs/rocq/gcd.v`. Coq's kernel
  type-checked each `Qed`; the trust here is exactly Coq 8.20.1's
  kernel correctness.
- The PyCSL Module 5 → IR → Rocq stmt converter (`Phase1d_StmtToIr.v`)
  is also axiom-free, but that machinery is used to verify
  *PyCSL itself*, not 0342.

### 9.2 Tier-0b (standard kernel axioms)

- **Coq** assumes: propositional extensionality, functional
  extensionality. These are widely-accepted foundational axioms
  used by Mathlib, Coq stdlib, and the proof-assistant community
  generally.
- **Lean** assumes: `propext`, `Classical.choice`, `Quot.sound`.
  Same comment.
- **Rocq stdlib lemmas** (`Nat.gcd_comm`, `Nat.gcd_divide_l`,
  `Nat.gcd_greatest`, `Nat.gcd_eq_0`, `Nat.Lcm0.mod_divide`,
  `Nat.divide_pos_le`) are themselves kernel-checked theorems —
  axiom-free under Tier-0b.
- **Lean / Mathlib lemmas** (`Nat.gcd_pos_of_pos_left`,
  `Nat.gcd_dvd_left`, `Nat.dvd_gcd`, `Nat.le_of_dvd`,
  `Nat.mod_eq_zero_of_dvd`) similarly kernel-checked.

### 9.3 Tier-1 (named external axioms, PyCSL-specific)

In 0342 specifically:
- **The seven `pycsl_axiom_*` declarations in the emitted MLW**
  are formal axioms from Why3's point of view. They are
  evidentially backed by the Rocq + Lean theorems via the
  `proof2why3` IR cross-check (always-on in `make`), which
  verifies that the WhyML axiom body, the Rocq theorem
  statement, and the Lean theorem statement all canonicalize to
  byte-equal IR. Any drift fails the build.

In the broader PyCSL design:
- `altErgoCorrect`, `trustedContractsAxiom` (Lean only, not
  exercised by 0342 directly).
- `Why3CertWitness` (hidden behind opaque `Why3Trust.check`, Lean
  only).

### 9.4 Tier-2 (trusted-by-design)

- **Why3** — the WhyML→VC pipeline (parser, type-checker, WP
  calculus, prover dispatch). Not formally verified within the
  PyCSL project; trust comes from Why3's age, maturity, and wide
  use.
- **Alt-Ergo 2.6.2 and Z3 4.13.3** — soundness assumed. Both have
  well-known caveats (incompleteness, non-linear arithmetic
  edge cases) but no recent soundness bugs.
- **Why3 standard library** (`int.Int`, `int.EuclideanDivision`,
  `ref.Ref`) — these are axiomatic libraries; their soundness
  rests on Why3's curation.
- **`int` ↔ `nat` canonicalization** — the registry's axiom
  bodies are stated over `int` with side-conditions `a >= 0`;
  the Rocq/Lean theorems are stated over `nat`. The
  `proof2why3.canonical._expand_nat_to_int` step performs this
  conversion mechanically and symmetrically on both sides
  (Rocq's `nat` / Lean's `Nat` get `>= 0` side conditions added;
  the registry's `int` body is kept as-is). The cross-check
  thus verifies the two are equivalent after the same
  normalization. The conversion is sound for the non-negative
  subset, which the function precondition enforces.

### 9.5 Tier-3 (meta-level claims)

- The audit's namespace-aware parser is line-oriented, not a real
  Coq/Lean front-end. Pathological proof files (e.g., with `Module
  Foo := …` aliases, very unusual `Module Type … : SIG := …`
  forms, or Lean's `_root_` prefix) can confuse it. Standard proof
  files used in `0342.proofs/` do not trigger any known parser
  weakness. With `--reverify-proofs`, the parser's verdict is
  also validated against `coqc` / `lake env lean` actually
  compiling, so a parser bug is caught.
- The registry's role is a cache: it remains hand-edited but
  every divergence from the Rocq + Lean theorems is detected on
  every `make self-annotate-verify` via the cross-check.
- **The `proof2why3` IR pipeline** sits in the trust base for the
  cross-check: bugs in `parser.py`, `canonical.py`,
  `from_sexp.py`, or `from_lean_json.py` could in principle
  produce false PASS. Mitigation: (a) negative tests confirm
  pinpoint-correct diff fingering (corrupt `gcd_0` registry →
  FAIL with the right side fingered; Rocq + Lean continue to
  match); (b) the parser/canonicalizer is tested against the
  upstream `wp_gen_correct` theorem and produces byte-equal IR
  cross-prover. A specific class of bug — silent collapse of
  distinct shapes to the same canonical form — remains a
  residual risk, mitigated by hand-eyeballing the diagnostic
  output during registry updates.
- **Extraction backends** (`sertop`, Lean meta-script): sertop
  serializes Coq's kernel-elaborated `Constr.t` directly;
  the Lean meta-script uses `Lean.Environment.find?` against
  the post-elaboration environment. Both produce ASTs as
  Coq/Lean themselves see them. A bug in either serializer
  would be visible at the schema level, not as silent semantic
  drift.

### 9.6 Tier-4 (tool stack)

OCaml 4.14.2 + 5.4.0, Python 3.14, Lake, dune, opam, Coq 8.20.1
kernel, Lean 4.30.0 kernel, `coq-serapi 8.20.0+0.20.0` (sertop).
Standard infrastructure assumed
correct.

### 9.7 Bottom line

For 0342 specifically, what the SUCCESS verdict warrants is:

> Given the soundness of Coq 8.20.1 and Lean 4.30.0 kernels under
> their standard axiom sets, the soundness of Alt-Ergo + Z3 on
> the goals they actually solved, the correctness of Why3's WP
> calculus, and the correctness of the `proof2why3` IR
> canonicalization pipeline, **the Python `gcd` function as
> written satisfies the eight `#@ ensures` clauses for every
> legal call (inputs satisfying the `#@ requires` preconditions)**.
>
> The Rocq + Lean + Registry triple-cross-check, run on every
> `make self-annotate-verify`, mechanically confirms that the
> Why3 axiom bodies are structurally equal to the canonical
> form of both prover-side theorems.

It does **not** warrant:
- That the Python runtime executes `x % y` exactly as WhyML
  computes `mod x y` for negative-handling edge cases. (PyCSL
  models Python's `%` as Why3's `EuclideanDivision.mod`, which
  is true for `a >= 0 and b > 0` — but not generally. The
  precondition `a >= 0`, `b >= 0` + the runtime guard `y != 0`
  cover this for 0342.)
- That `gcd(0, 0)` returns `0` in any *useful* sense; the
  contract has `(a > 0 or b > 0) ==>` antecedents on all but
  the `\result >= 0` and `\result == gcd(a, b)` postconditions,
  meaning `gcd(0,0)` is only constrained to be non-negative and
  equal to the logical `gcd(0,0)` — which the `gcd_0` axiom
  fixes at `0`. The Python implementation returning `0` is
  consistent with this; the runtime assertion `gcd(0, 0) == 0`
  in the main block is consistent but does not prove anything
  beyond what verification already established.

### 9.8 Failure modes that the verdict does NOT catch

- **The Rocq theorem is stated correctly but proves the wrong
  thing**: the cross-check with Lean catches this — if Rocq
  and Lean prove different statements, the canonical IRs
  differ, the 3-way diff fingers the dissenting side, and
  `make` exits non-zero.
- **The Why3 kernel mis-translates one of the imported axioms**:
  not caught. Why3 is in Tier-2 trust.
- **An SMT solver returns Valid on an actually-invalid VC**:
  not directly caught. Mitigation is the parallel prover
  (Alt-Ergo then Z3) — disagreement between solvers would
  surface as Why3 reporting a counterexample. Both solvers
  reporting Valid on an unsound goal would be a coordinated
  soundness bug.
- **`proof2why3.canonical` silently collapses two semantically
  distinct theorems to the same canonical form**: would falsely
  PASS. The risk class is reduced by alpha-rename-after-name-norm
  (so name collisions stay visible) and by the conservative
  rewrite set (only rules whose left/right sides are provably
  semantically equal are applied — nat→int, AC-normalize,
  comparison-direction). No known instance of this failure.
- **`proof2why3` extractor parses ambiguously**: the regex-text
  path (`coqc + Check`) has known fragility under non-standard
  Coq notations; the sertop / Lean-meta paths bypass this entirely
  by consuming kernel-elaborated ASTs.

---

## 10. The `proof2why3` cross-check pipeline

The mechanical 3-way cross-check that fires on every
`make self-annotate-verify` implements the architecture sketched
in `docs/cross-validated-spec-sources.md`:

```
0342.proofs/rocq/gcd.v                  0342.proofs/lean/Gcd.lean
    │ (sertop, --PROOF2WHY3_USE_SERTOP=1)    │ (lake env lean --run …,
    │  default: coqc + Check                 │   --PROOF2WHY3_USE_LEAN_META=1
    ▼                                        ▼   default: lake env lean + #check)
src/pycsl/proof2why3/from_sexp.py        src/pycsl/proof2why3/from_lean_json.py
    │ project_constr(Coq Constr.t)           │ project_to_ir(Lean.Expr JSON)
    ▼                                        ▼
                  shared first-order IR
                  (src/pycsl/proof2why3/ir.py)
                                │
                                ▼
            src/pycsl/proof2why3/canonical.py
              • _expand_nat_to_int (nat/Nat → int + a >= 0 ->)
              • _flatten_foralls (nested ∀ x, ∀ y → ∀ x y)
              • _flip_comparisons (<= → >=, < → >)
              • _dedup_arrow_chain
              • _ac_normalize (sort \/, /\)
              • _iff_app_to_binop (App "iff" → BinOp "iff")
              • _normalize_names (camelCase ↔ snake_case)
              • alpha_normalize (binders → v0, v1, …)
                                │
                                ▼
                       canonical IR Term
                                │
                                ▼
            src/pycsl/proof2why3/crosscheck_ir.py
                Term.__eq__ (frozen dataclass field tuple)
                                │
                                ▼
                       Rocq ≡ Lean ≡ Registry?

Module 6 _AXIOM_REGISTRY[qn] body
    │ (src/pycsl/proof2why3/parser.py — recursive descent over
    │   the Why3 axiom-body subset)
    ▼
        same first-order IR ──→ same canonicalize ──→ same Term
```

What the pipeline catches (negative tests confirm each):

1. **Registry body diverges from both provers** — `gcd_0`
   registry corrupted to `gcd a 0 = a + 1` → cross-check FAIL
   with `rocq==lean: PASS`, `rocq==registry: FAIL`,
   `lean==registry: FAIL` — registry correctly fingered.
2. **One prover's theorem statement drifts** — patch a Rocq
   proof's *statement* (not body) → cross-check FAIL with
   `rocq==lean: FAIL`, `rocq==registry: FAIL`,
   `lean==registry: PASS` — Rocq side fingered.
3. **Proof file stops compiling** (with `--reverify-proofs`) →
   `coqc` non-zero exit → reverify FAIL.
4. **Proof introduces a non-allow-listed axiom** (e.g.
   `Admitted.`) → `Print Assumptions` reports unexpected name →
   reverify FAIL with the offending axiom listed.

What the pipeline does NOT catch:

1. Both provers AND the registry are simultaneously wrong in
   exactly the same way (e.g., `Nat.gcd` is redefined in both
   stdlibs unsoundly). Mitigation: stdlib redefinition is
   detectable at compile time by stdlib's own tests.
2. The first-order IR can't represent the theorem
   (Unsupported nodes propagate). For 0342's gcd-family this
   is never exercised. Predicate-quantified theorems like
   `wp_gen_correct` are also covered by the IR, which models
   `forall` over arbitrary types (including `ExecState → Prop`),
   `iff`, and de-Bruijn-based anonymous-binder detection.

State on 0342:

- `make check-proof-crosscheck`: 14 PASS, 8 SKIP, 0 FAIL.
- `python -m pycsl.proof2why3.crosscheck_ir
  test-suite/corpus/pycsl-reference/0342.py` directly: 7/7 PASS.
- Spot-check hash equality: `hash(rocq_canon) ==
  hash(lean_canon) == hash(registry_canon)` per theorem.
- `wp_gen_correct` (an upstream non-gcd theorem) also passes
  rocq==lean equality via the elaborated-AST extractors,
  exercising the IR's predicate-type and custom-inductive
  binder support.

---

## 11. Why this architecture matters

The 0342 chain is the worked example for what PyCSL itself is
trying to achieve at scale: **formal Python verification anchored
by independently-proved mathematical statements**. Tradeoffs
and design decisions in the chain are deliberate:

- **PyCSL is not its own theorem prover.** It compiles to Why3 +
  SMT, accepting Why3's design-by-trust for the discharger. This
  shrinks the per-test verification cost by orders of magnitude
  compared to writing pure Coq.

- **Mathematical content is anchored in two provers, not one.**
  Two-prover redundancy is the cheapest soundness improvement
  available: each prover is independently developed, and their
  agreement is itself an interesting datum.

- **The `#@ proof` directive separates "what the algorithm needs"
  from "where the math lives".** The Python author writes the
  loop invariant `gcd(x, y) == gcd(a, b)` without needing to
  prove `gcd_step` in either Coq or Lean — they cite an external
  proof. The cite is auditable, swappable, and accumulating over
  time the registry of cited theorems is a reusable spec library.

- **The trust seam is explicit.** Every axiom emitted into Why3
  carries a comment naming the qualname and the cross-validation
  tag. Reviewers reading the `.mlw` can trace each axiom back to
  the proof files in `0342.proofs/`. There is no hidden trust.

The Q4 deliverable in PyCSL's larger roadmap (`closer-to-code.md`)
explicitly references 0342 as the canonical worked example: the
"trust seam = IR boundary" claim is materialized here in that
the IR (Module 5 JSON) carries `proof` attributions that survive
the Rocq round-trip (verified by `Phase1b_IrToStmt.v` +
`Phase1d_StmtToIr.v`). 0342 is therefore not just an end-to-end
GCD test — it's the architectural touchstone for how PyCSL
intends to scale.

---

## 12. Pointers

- **PyCSL source of the directive:**
  `src/pycsl/Module2_Parser.py` (Lark grammar for `#@ proof`),
  `src/pycsl/Module6_WhyMLTranspiler.py` →
  `module6_whyml/preamble.py:303` (`_emit_preamble_axioms`,
  `_AXIOM_REGISTRY`).
- **Audit parser:** `src/pycsl/audit_proof.py` (namespace-aware
  Rocq + Lean state machines).
- **Reverify orchestrator:**
  `src/pycsl/audit_proof_reverify.py` + allow-list at
  `src/pycsl/proof_axiom_allowlist.py`.
- **`proof2why3` IR cross-check (Phases A/B/C/D):**
  `src/pycsl/proof2why3/`
  - `ir.py` — shared first-order IR (Forall, Exists, App, BinOp,
    UnaryOp, Var, IntLit, BoolLit, Unsupported).
  - `parser.py` — recursive-descent parser for Why3 axiom-body
    syntax (registry side).
  - `sertop.py` — Rocq elaborated-Constr.t extractor.
  - `from_sexp.py` — Coq s-expr → IR projector.
  - `extract_lean_meta.py` + `bin/proof2why3-lean-extract.lean`
    — Lean meta-extractor.
  - `from_lean_json.py` — Lean.Expr JSON → IR projector.
  - `canonical.py` — eight-step canonicalization pipeline.
  - `crosscheck_ir.py` — 3-way structural diff driver.
- **CLI flags:** `pycsl --audit-proof [--reverify-proofs]
  <file>` — `src/pycsl/pycsl.py:554`. Environment toggles:
  `PROOF2WHY3_USE_SERTOP=1`, `PROOF2WHY3_USE_LEAN_META=1`.
- **`make` integration:** `bin/check-proof-crosscheck.sh` +
  `check-proof-crosscheck` Makefile target, run by
  `self-annotate-verify`.
- **Architecture document:** `docs/cross-validated-spec-sources.md`.
- **Test entry:** `test-suite/corpus/pycsl-reference/0342.py` +
  `0342.proofs/{rocq/gcd.v, lean/Gcd.lean, README.md,
  lean/lakefile.lean}`.
- **Reference-test runner:** `bash bin/run-reference-tests.sh
  --pycsl --start-at 342 --stop-at 342`.
- **Generated artefact (after `--keep-mlw`):**
  `test-suite/corpus/pycsl-reference/0342.mlw` — the input Why3
  actually verifies.

---

*Document describes the PyCSL toolchain state at HEAD on the
`main` branch. Layer 0 (Rocq) is PyCSL-axiom-free; Layer 0 (Lean)
carries 2 visible PyCSL axioms not exercised by 0342. The
`proof2why3` cross-check pipeline is live: every
`make self-annotate-verify` mechanically diffs Rocq + Lean
elaborated ASTs against the Module 6 `_AXIOM_REGISTRY` body and
fails on any drift. Registry-vs-theorem fidelity is an enforced
predicate, not a manual review.*
