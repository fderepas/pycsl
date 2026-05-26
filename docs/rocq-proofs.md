# Rocq Proof Companions

When pycsl's SMT solvers (Alt-Ergo, Z3) cannot discharge a verification
condition, a **Rocq proof companion** can provide a machine-checked proof
that pycsl replays automatically on every run.

## Quick start

```bash
# Generate proof companions for a file where SMT times out
bin/generate-rocq-proofs.sh myfile.py

# Verify — pycsl auto-detects myfile.proofs/ and replays with coqc
pycsl myfile.py
```

## Automatic helper

If you want one command that first tries normal SMT verification and only
falls back to Rocq + the LLM proof writer when needed:

```bash
bin/pycsl-prove-with-llm.sh myfile.py
```

This helper:

1. runs `pycsl myfile.py`
2. exits immediately on success
3. on failure, creates `myfile.proofs/`
4. generates Rocq `.v` skeletons with `--rocq`
5. runs `agent-rocq-proof-writer.py` on the generated obligations
6. replays the resulting proofs with `--rocq-proofs`

The `.proofs/` directory is kept even on partial failure so you can continue
manually with `make llm`, `make coq`, and `make replay`.

## How it works

### Storage convention

For each `foo.py` that needs Rocq, proofs live in `foo.proofs/`:

```
foo.py                          # Python source with #@ annotations
foo.proofs/
  foo.mlw                       # Frozen WhyML (for staleness detection)
  proof_PyCSL_Program_...v      # Completed Rocq proof script
```

### Verification flow

```
pycsl foo.py
  1. Generate .mlw from .py (fresh, from current source)
  2. Run SMT solvers (Alt-Ergo, Z3) on all split VCs
  3. For each UNPROVEN sub-goal:
     a. Check if foo.proofs/ exists
     b. Compare current .mlw hash against stored .mlw (staleness check)
     c. Compile .v proof with coqc (FULL replay — no caching)
     d. If coqc succeeds → goal proved by Rocq
     e. If coqc fails → goal remains unproven
  4. SUCCESS only if ALL goals proved (SMT + Rocq combined)
```

### Reliability guarantees

- **No blind trust**: pycsl NEVER assumes a `.v` file is valid. It always
  recompiles with `coqc`, which re-checks every proof step through the
  Rocq kernel (the trusted computing base).

- **Staleness detection**: If the `.py` annotations change, the generated
  `.mlw` changes, which causes a SHA-256 hash mismatch with the stored
  `.mlw`. Stale proofs are rejected without attempting `coqc`.

- **Defense in depth**: Even if an attacker modifies the stored `.mlw` to
  match, the `.v` file's goal statement is derived from the original `.mlw`.
  A changed `.mlw` produces different goal statements that won't match
  the proof, so `coqc` will reject it.

## CLI flags

```
pycsl foo.py                     # Auto-detects foo.proofs/ if it exists
pycsl --rocq-proofs foo.py       # Explicitly enable Rocq proof checking
pycsl --rocq-proofs DIR foo.py   # Use DIR instead of auto-detection
pycsl --rocq DIR foo.py          # Generate .v skeletons in DIR (on failure)
```

## Creating proof companions manually

### Step 1: Generate .v skeletons

```bash
pycsl --rocq myfile.proofs/ myfile.py
```

This creates one `.v` file per split VC in `myfile.proofs/`.

### Step 2: Identify the failing VC

The postcondition VC is typically the last file (e.g., `*qtvc9.v`). It
contains `~ (i < n)` (loop exit condition) and the ensures clause as the
goal.

### Step 3: Fill in the proof

For polynomial arithmetic goals, the standard tactic is:

```coq
Proof.
  (* Bring axioms (loop invariants) into the local context *)
  pose proof LoopInvariant as Ha.
  pose proof LoopInvariant1 as Hb.
  pose proof LoopInvariant2 as Hc.
  pose proof H as Hi0. pose proof H1 as Hi1. pose proof H2 as Hi2.
  (* Deduce i = n from loop exit *)
  assert (i = n) by lia. subst.
  (* Non-linear integer arithmetic solves the polynomial identity *)
  nia.
Qed.
```

**Important**: Add `Require Import ZArith Lia.` after the Why3 imports.

### Step 4: Compile and verify

```bash
coqc -R ~/.opam/default/lib/why3/coq Why3 myfile.proofs/proof_*.v
```

### Step 5: Clean up

Remove trivial VCs (the ones SMT already proves) — keep only the
postcondition `.v` and the `.mlw`:

```bash
# Keep only files containing your proof + the .mlw
```

## When Rocq proofs are needed

SMT solvers handle most polynomial arithmetic. The pattern that exceeds
their capabilities is **postconditions requiring multiplication of 3+
independent polynomial hypotheses** at degree ≥12.

Example: a function accumulating `a = Σk`, `b = Σk²`, `c = Σk³` and
returning `a * b² * c` has a postcondition of degree 12 that Alt-Ergo
and Z3 both timeout on, but Rocq's `nia` tactic proves instantly.

## Reference tests

Tests `0211`–`0220` in `test-suite/corpus/pycsl-reference/` are proved
using Rocq companions. Each has a `.proofs/` directory with the compiled
proof.
