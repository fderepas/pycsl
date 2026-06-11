A **proof companion** is the generated `<file>.proofs/` directory that stores
the **paired Rocq and Lean** proof scripts for the verification conditions and
cited lemmas the SMT solvers cannot discharge automatically. Its canonical
layout is `<source>.proofs/{rocq,lean}/`: every cross-validated fact lives
*twice*, once as a Rocq `.v` file and once as a Lean `.lean` file proving the
**same** statement.

---

## Why proof companions matter in PyCSL

Most VCs are discharged *Valid* by Alt-Ergo 2.6.2 or Z3 4.13.3 within their
per-goal time budget. The proof companion is the fallback layer for the smaller
set of hard facts the SMT solvers leave *Unknown* or *Timeout* — properties that
need induction, uninterpreted-predicate constraints, or cross-function
relational reasoning that trigger-based quantifier instantiation (E-matching)
cannot reach.

These facts are not proved by the SMT backend at all. They are proved **offline,
in both Rocq and Lean**, cited from the Python source via *paired* `#@ proof`
directives, and injected into the Why3 module preamble as `axiom` declarations
(see [axiom registry](axiom-registry.md)). The proof companion also gives you a
stable place to keep manual proof work while the source file evolves.

---

## Dual-kernel cross-validation is the philosophy

PyCSL — like every member of the \*CSL family — is built on **Rocq + Lean
cross-validation**, not Rocq alone. A cited lemma is trusted only because **two
independent proof-assistant kernels** each accept it:

- **Rocq and Lean are independent kernels.** Their type theories, their
  standard libraries, and their communities evolved separately and audit each
  other's foundational definitions from different angles. A theorem that
  canonicalizes to the same proposition in both has crossed *two* audits.

- **Cross-validation guards against a single assistant's soundness bug.** No
  kernel is infallible; both Rocq and Lean have had soundness-relevant bugs over
  their histories. A fact accepted by *both* is far more trustworthy than one
  resting on a single prover — a single-kernel soundness defect can no longer
  silently admit a false lemma into the verification.

- **Two provers is the entire point.** Single-prover citation exists only as an
  escape hatch; the intended and required path is the *pair*. The `proof2why3`
  cross-check halts with a hard failure (a structured diff, manifest status
  `disagreement`) if the Rocq statement and the Lean statement for the same
  qualified name canonicalize to different propositions — it never picks a
  winner, never emits either axiom on disagreement.

There is no Why3→Lean backend: "Rocq + Lean" means the **lemma statement** is
independently proved in both assistants and then cited as a single Why3 axiom —
not that the raw VC is discharged in Lean.

---

## Paired `#@ proof` directives

Every cross-validated lemma is cited from the Python source by **both** a Rocq
directive **and** a Lean directive naming the same dotted qualname:

```python
#@ proof rocq Pycsl.Reference.Gcd.gcd_step
#@ proof lean Pycsl.Reference.Gcd.gcd_step
```

The qualified name is identical across the source citation, the Rocq theorem,
and the Lean theorem; it is the address that lets a reader follow the directive
to the proof in `<source>.proofs/rocq/` and `<source>.proofs/lean/`. The
canonical example is `test-suite/corpus/pycsl-reference/0342.py` (Euclidean
GCD), which cites all seven GCD lemmas in both kernels. The `UnixFs.Dir.*`
directory-scan lemmas follow the same pattern, paired across
`unix-filesystem/UnixInodeFileSystem.proofs/{rocq,lean}/`.

---

## audit_proof requires BOTH kernels to accept

`src/pycsl/audit_proof.py` is the cross-check that enforces the dual-kernel trust
model. For each cited qualname it verifies **both** halves of the pair, offline:

1. **Both files declare the cited statement.** Line-oriented parsers confirm the
   qualname is declared in a `.v` file under `<source>.proofs/rocq/` **and** in a
   `.lean` file under `<source>.proofs/lean/`.

2. **Both kernels accept it with no extraneous axioms.** The reverify path runs
   `coqc` on the Rocq file and `lake env lean` on the Lean file, then inspects the
   assumption base:
   - **Rocq:** `Print Assumptions` must report *Closed under the global context*
     (the empty-assumption marker) or only allow-listed kernel axioms.
   - **Lean:** `#print axioms` must show only allow-listed kernel axioms, i.e.
     a subset of `{propext, Classical.choice, Quot.sound}`.

   The allow-lists live in `src/pycsl/proof_axiom_allowlist.py`
   (`ROCQ_KERNEL_AXIOM_ALLOWLIST` / `LEAN_KERNEL_AXIOM_ALLOWLIST`). Any
   non-allow-listed assumption — `Admitted`, `sorry`, an `axiom`/`Axiom`, a stray
   `Parameter` — is a hard failure.

A failure on *either* kernel is a hard transpilation error. A lemma proved in
Rocq but absent or admitted in Lean (or vice versa) does **not** pass — the
companion only earns trust as a matched pair.

---

## Concrete workflow

### Generate the proof skeletons

`pycsl --rocq DIR file.py` exports Rocq skeletons for the remaining VCs; the
paired Lean skeletons populate `<source>.proofs/lean/` so each fact has a `.v`
and a `.lean` proving the same statement.

### Manual proof replay

`pycsl --rocq-proofs DIR file.py` replays the completed proofs against the
current obligations.

### No kernel runs during the `pycsl` proof

The Rocq and Lean kernels run **only offline**, when the proof companion is built
or audited (`coqc` / `lake env lean` under `audit_proof.py`). A routine `pycsl`
proof run discharges its VCs entirely through Why3 weakest-precondition VC
generation and the SMT solvers (Alt-Ergo / Z3); the cited lemmas enter as Why3
preamble axioms that the SMT backend may instantiate via E-matching. Neither Rocq
nor Lean is invoked during that run — their guarantees are banked in advance and
carried by the audited companion.

### Scratch proof directory

When source annotations change, it is often safer to generate a fresh temporary
proof directory first, compare the new VC set, and only then replace or merge the
retained proof companion.

---

## Why this term is broader than one script

The proof companion is not just the `.v` files, and not just the Rocq side. It is
the whole retained manual-proof layer attached to a source file — generated
skeletons, completed scripts, and replay against regenerated VCs — held as a
**matched Rocq + Lean pair** under `<source>.proofs/{rocq,lean}/`, with both
sides cross-validated by `audit_proof.py`.

---

## Related terms

- [axiom registry](axiom-registry.md) — the catalogue of cross-validated
  lemmas these proofs back
- [verification condition](verification-condition.md)
- [solver budget](solver-budget.md)
- [reference test](reference-test.md)

> **In short:** the proof companion is the **dual-kernel** manual-proof sidecar
> for the VCs SMT leaves behind — every cited lemma proved in Rocq *and* Lean,
> checked offline, cited via paired `#@ proof rocq`/`#@ proof lean` directives,
> and admitted only when `audit_proof` confirms *both* kernels accept it with no
> extraneous axioms.
