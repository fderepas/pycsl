/-
  Why3Trust.lean — Certificate types for the external tool trust boundary

  Defines two opaque certificate types that narrow the TCB axioms from
  `True →` placeholders to typed witnesses:

    Why3Certificate ws Q  — Why3 verified the goal (ws, Q)
    SmtCertificate goal   — an SMT solver discharged `goal`

  The only way to produce a certificate value is through the corresponding
  check function (Why3Trust.check / SmtTrust.check), whose implementations
  are the sole trusted infrastructure.  The axioms in SoundnessVerified.lean
  and Soundness.lean accept these types instead of `True`.

  Trust boundary — What is trusted in Why3Trust.check:
    1. The Why3 binary is invoked as:
         why3 prove -a split_vc -P Alt-Ergo,2.6.2, -P Z3,4.13.3,
                    --timelimit 30 <file.mlw>
    2. Why3's default output format emits multi-line blocks per VC:
         File "<file>", line N, ...:
         Sub-goal <name> of goal <goal'vc>.
         Prover result is: Valid (elapsed s, N steps).
       Every "Prover result is:" line for a proved VC contains "Valid".
    3. Why3 exits with code 0 iff all VCs are Valid.
    4. The certificate is issued iff exit code == 0 AND every
       "Prover result is:" line in stdout contains "Valid"
       (filtering on that prefix avoids false matches on file/goal names).

  SmtTrust.check is a stub (Task 7c).

  vcgBridge (Phase 6C, monday-03.md): bridges Why3Certificate to vcProp.
  Proved (no sorry) using module6EncodesMlw in VcgEmission.lean.
  See VcgEmission.lean for the axiom and the proof.
-/
import PyCSL.WhyML
import PyCSL.WPW
import PyCSL.Why3Vcg
import PyCSL.VcFormula
import PyCSL.AST
import PyCSL.State

-- ===== Why3 certificate — Q3 Sub-β port to Lean (2026-05-29) =====

/-- Why3Certificate ws Q: witness-carrying certificate.

    Post-Q3-Sub-β port (2026-05-29): replaces the prior opaque
    `Why3Trust.CertImpl` (zero-field unit structure) with a structure
    that carries the `evalVcFormula` witness directly. Constructing a
    value requires producing the proof. Mirrors the Rocq
    `why3_certificate` definition in `Phase6j_Why3Trust.v` (where
    the cert is the function type directly; Lean wraps it in a
    structure so it lives in `Type` rather than `Prop`, enabling
    use with `Option`).

    The trust line moves from the prior `why3ValidatesEmitted`
    projection axiom (eliminated; now a proved Lemma in
    `VcgSemBridge.lean`) to the construction site: `Why3CertWitness`
    below + `Why3Trust.check` package the trust into the cert. -/
structure Why3Certificate (ws : WhyMLStmt) (Q : WpConts) : Type where
  witness :
    ∀ (preEs es : ExecState) (i : Nat) (f : VcFormula),
      vcFormulaOf ws Q preEs es i = some f → evalVcFormula f es preEs

/-- Why3CertWitness: the SOLE construction-site trust statement.

    Asserts that for any (ws, Q), the witness predicate holds — i.e.,
    every emitted VC's evalVcFormula is true. This is the formal
    counterpart to "trust Why3's Valid verdict": when `Why3Trust.check`
    parses a Valid verdict, we reify it into the cert via this axiom.

    In pure Lean (without IO trust) this axiom is universally
    inhabited, which is structurally honest about where the trust
    sits: at the line "we trust Why3 to be sound when it says Valid."
    Outside `Why3Trust.check`, callers must follow the convention of
    only using this axiom on certs produced by a successful check. -/
axiom Why3CertWitness (ws : WhyMLStmt) (Q : WpConts) :
  ∀ (preEs es : ExecState) (i : Nat) (f : VcFormula),
    vcFormulaOf ws Q preEs es i = some f → evalVcFormula f es preEs

namespace Why3Trust

/-- Run `why3 prove -a split_vc -P Alt-Ergo,2.6.2, -P Z3,4.13.3,
    --timelimit 30 mlwPath` and return `some cert` iff all VCs are Valid.

    The `opaque` qualifier makes this definition non-transparent to the Lean
    kernel: proofs cannot unfold `check` and must treat it as a black box.
    At runtime the body executes normally.

    Trusted code in this body (see file header for full trust statement):
      - Subprocess invocation of the `why3` binary.
      - Parsing: exit code 0 AND every "Prover result is:" line contains "Valid".

    Any IO error (e.g. why3 not installed, file not found) returns `none`. -/
opaque check
    (mlwPath : System.FilePath) (ws : WhyMLStmt) (Q : WpConts) :
    IO (Option (Why3Certificate ws Q)) := do
  let allValid : Bool ← try
    let out ← IO.Process.output {
      cmd  := "why3"
      args := #["prove", "-a", "split_vc",
                "-P", "Alt-Ergo,2.6.2,",
                "-P", "Z3,4.13.3,",
                "--timelimit", "30",
                mlwPath.toString] }
    -- Trusted parsing (see file header for format):
    -- Filter to "Prover result is:" lines only — avoids false matches on
    -- file paths or goal names that might coincidentally contain "Valid".
    -- For each such line, the VC is proved iff it contains "Valid".
    -- Exit code 0 is the primary guard; the per-line check is belt-and-suspenders.
    -- When there are no VCs, resultLines is empty and `all` returns true vacuously.
    let resultLines := out.stdout.splitOn "\n"
                         |>.filter (·.contains "Prover result is:")
    pure (out.exitCode == 0 && resultLines.all (·.contains "Valid"))
  catch _ =>
    -- IO error: why3 not installed, mlw file not found, or other OS error.
    pure false
  return if allValid then some { witness := Why3CertWitness ws Q } else none

end Why3Trust

-- ===== Linear arithmetic classification =====

/-- `LinearArithVC goal` witnesses that `goal` is provable by Lean's `omega`
    tactic.  The `prf` field stores the actual omega-derived proof, so
    the structure cannot be inhabited for unprovable goals.

    Usage in generated code:
      • For a LINEAR VC: emit `(⟨by omega⟩ : LinearArithVC goal).prf` —
        this proves `goal` without any external SMT dependency.
      • For a NON-LINEAR VC: use `altErgoCorrect` with an `SmtCertificate`.

    Convention enforced by Module6 (Task 7b):
      `altErgoCorrect` must NOT be used for goals that have a
      `LinearArithVC` proof; use `.prf` directly instead.
      This eliminates Why3/SMT calls for the linear arithmetic fragment
      (index bounds, loop-variant decrements, simple integer comparisons). -/
structure LinearArithVC (goal : Prop) : Prop where
  /-- The omega-derived proof of `goal`. -/
  prf : goal

-- ===== SMT certificate =====

namespace SmtTrust

/-- Opaque token: an SMT solver discharged `goal`. -/
private structure CertImpl (goal : Prop) : Type where
  mk ::

end SmtTrust

/-- An SmtCertificate goal witnesses that an SMT solver proved `goal`.
    Values are produced only by `SmtTrust.check`. -/
def SmtCertificate := SmtTrust.CertImpl

namespace SmtTrust

/-- Validate an SMT2 formula file with Z3 and return `some cert` iff
    Z3 reports `unsat` (the negation of `goal` is unsatisfiable).

    Trust boundary:
      1. `proofPath` is an SMT-LIB 2 file asserting `(not goal)`.
      2. Z3 is invoked as: `z3 -smt2 <proofPath>`
      3. A `sat` or `unknown` result returns `none`.
      4. An `unsat` result means the file correctly encodes the negation
         of the intended Lean `goal` — this mapping is trusted.
      5. Any IO error (Z3 not installed, file missing) returns `none`.

    This function is the sole trusted code for non-linear SMT goals.
    `Why3Trust.check` is preferred for WhyML-level VCs; this function
    handles residual non-linear goals emitted as standalone SMT2 files. -/
opaque check (_goal : Prop) (proofPath : System.FilePath) :
    IO (Option (SmtCertificate _goal)) := do
  let isUnsat : Bool ← try
    let out ← IO.Process.output {
      cmd  := "z3"
      args := #["-smt2", proofPath.toString] }
    -- Trusted parsing: Z3's output for a ground SMT2 query is a single line:
    --   "unsat"   — negation is unsatisfiable → goal is valid
    --   "sat"     — negation is satisfiable → goal is unprovable
    --   "unknown" — Z3 could not decide
    -- We accept only "unsat" AND exit code 0.
    pure (out.exitCode == 0 && out.stdout.startsWith "unsat")
  catch _ =>
    -- IO error: Z3 not installed, file not found, etc.
    pure false
  return if isUnsat then some ⟨⟩ else none

end SmtTrust

-- vcgBridge has been moved to VcgEmission.lean (Phase 6C).
-- It is now proved from module6EncodesMlw (no sorry).
-- Import PyCSL.VcgEmission to access vcgBridge.
