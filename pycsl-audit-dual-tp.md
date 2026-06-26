# Dual-prover (Rocq + Lean) axiom-plumbing — audit & improvement tasks

**Audience:** agents working on PyCSL's dual-prover axiom-plumbing.
**Provenance:** external code audit of a fresh `main` clone — read `src/pycsl/audit_proof.py`,
`src/pycsl/audit_proof_reverify.py`, `src/pycsl/proof_axiom_allowlist.py`,
`src/pycsl/proof2why3/` (`__init__`, `crosscheck.py`, `crosscheck_ir.py`), `bin/check-proof-crosscheck.sh`,
the `Makefile` proof targets, and the cross-validated pair
`unix-filesystem/UnixInodeFileSystem.proofs/{rocq,lean}/UnixDirScan.{v,lean}`.
This file records what is **already strong** (do not regress it) and the **concrete defects** to close,
each with acceptance criteria. It is deliberately scoped to the *trust machinery*, not the proofs themselves.

---

## 0. Verdict in one paragraph

The strategy is sound and unusually rigorous: trust-bearing axioms are SMT-escalation valves, each backed
by a **paired Rocq + Lean proof**, and the binding from the cited theorem to the Why3 formula the solver
actually assumes is **mechanically cross-checked** (`proof2why3/crosscheck_ir.py`: extract both prover
statements → shared IR → canonicalize → 3-way structural equality against `_AXIOM_REGISTRY`). The
`UnixDirScan` pair is genuinely parallel and faithful, and uses the sound-witness pattern correctly
(`slot_inode_nonneg` carried as an explicit antecedent, discharged separately over a concrete byte model;
both proofs zero-extra-axiom). The remaining defects are **operational/edge**, not foundational — but two
of them (no CI, SKIP-masks-non-check) can let a "green" mean "did not actually check," which for an
extreme-rigor project is the failure mode that matters most.

---

## 1. Architecture as-found (the map, so you fix the right layer)

Trust is established in **two layers** plus **registry-integrity** gates:

- **Layer 1 — attribution** (`audit_proof.py` + `audit_proof_reverify.py`): the cited
  `#@ proof rocq|lean <qualname>` names a theorem that *exists* in the matching `.proofs/{rocq,lean}` dir
  (name-presence, namespace-aware), and — under `reverify=True` — each such file *compiles* and the cited
  theorem's `Print Assumptions` / `#print axioms` set is allow-listed.
- **Layer 2 — faithfulness/equivalence** (`proof2why3/crosscheck_ir.py`, gated by
  `bin/check-proof-crosscheck.sh` ← `make check-proof-crosscheck` ← `make self-annotate-verify`):
  the **3-way structural** check Rocq-statement ≡ Lean-statement ≡ `_AXIOM_REGISTRY[qualname]`, over a
  canonical first-order IR. This is the load-bearing guarantee.
- **Registry integrity**: `check-axiom-registry-emittable` (every registry body round-trips
  parse→canonicalize→emit→re-parse) and `check-axiom-registry-drift` / `sync-axiom-registry`
  (the registry can be **regenerated from the cross-checked proofs**, eliminating hand-transcription).

**Do not regress these.** In particular: keep the registry derivable from cross-checked IR (`sync-axiom-registry`);
keep the antecedent-discharge pattern (abstract hypothesis carried explicitly, discharged over a concrete
witness — see `UnixDirScan.v`'s `slot_inode_nonneg` Theorem vs Hypothesis); keep the 3-way (not 2-way) check
so the Why3 formula the solver assumes is an anchor, not just "the two provers agree with each other."

---

## 2. Defects & tasks (prioritized)

### P0-1 — No CI; the gate only runs if a human runs `make`
**Finding.** There is no `.github/workflows/`. All enforcement is `make self-annotate-verify` (and the
`check-proof-*` targets it calls). A regression — a citation whose proofs drift from the registry, a proof
that stops compiling, an axiom that creeps in — lands silently unless someone runs make locally.
**Why it matters.** For a project whose thesis is "greens are load-bearing," an unenforced gate is the
single largest hole: the rigor exists but is not *applied* on every change.
**Task.** Add a CI workflow that runs the full proof gate on every push/PR touching `**/*.py`,
`**/*.proofs/**`, `src/pycsl/proof2why3/**`, or `_AXIOM_REGISTRY`. It must install the pinned Rocq **and**
Lean toolchains, then run `make self-annotate-verify`.
**Acceptance.** (a) Workflow present and green on `main`. (b) A deliberately-broken citation (rename a cited
theorem) makes CI **red**. (c) The workflow fails (not skips) if either prover toolchain is missing
(see P0-2).

### P0-2 — Cross-check gate is fail-OPEN when a prover is absent
**Finding.** `bin/check-proof-crosscheck.sh` runs `crosscheck_ir … 2>&1 || true` and parses a summary
line with `sed`; if `coqc`/`sertop`/`lake env lean` is unavailable (or `crosscheck_ir` errors before
printing a summary), `p`/`s`/`fl` default to `0` and the file contributes **nothing** — no FAIL. Likewise
`audit_proof_reverify` degrades to `coqc-unavailable`/`lean-unavailable` version strings rather than failing.
**Why it matters.** "Prover not installed" then reads as "passed." A green build can mean the cross-check
never executed — the exact coherent-and-wrong an extreme-rigor pipeline must forbid. (Compare: a sound gate
*fails closed* when its oracle is unavailable.)
**Task.** Make absence of either prover, or a crosscheck run that emits no parseable summary, a **hard
FAIL** (non-zero exit) — not a skip. Distinguish three states explicitly: PASS / FAIL / `INFRA-MISSING`,
where `INFRA-MISSING` is non-zero. Print the prover versions actually used.
**Acceptance.** Running the gate with `coqc`/`lean` off `PATH` exits non-zero with a clear
`INFRA-MISSING` message; it cannot report aggregate PASS.

### P0-3 — The canonicalizer is now trust-critical but under-tested
**Finding.** Layer-2 soundness rests entirely on `proof2why3/extract.py` + `parser.py` /
`from_sexp.py` (SerAPI) / `from_lean_json.py` + `canonical.py` (~488 lines) faithfully representing each
statement. A canonicalizer bug that maps **two different propositions to the same canonical IR** would let a
wrong Rocq/Lean/Why3 triple pass the 3-way check — a *silent soundness hole*, not a crash.
**Why it matters.** The manual trust assumption did not disappear; it **moved into the IR layer**. That
layer deserves the same adversarial scrutiny the proofs get.
**Task.** Add an adversarial/property test suite for `canonical.py` + extraction:
  - **Negative pairs (must NOT be equal):** curated statement pairs that are *almost* the same but
    semantically distinct — swapped quantifier order, `<` vs `≤`, `16` vs `15`, hypothesis dropped,
    arguments transposed, `∀`/`∃` flipped, an extra conjunct. Each must produce *unequal* canonical IR.
  - **Positive pairs (must be equal):** the same proposition spelled differently per prover (e.g. Rocq
    `0 <= k < 16` vs Lean `0 ≤ k ∧ k < 16`; implicit vs explicit binders; notation vs raw).
  - **Round-trip & idempotence:** `canonicalize(canonicalize(x)) == canonicalize(x)`; registry
    emit→parse→canonicalize is a fixpoint (you already have `check-axiom-registry-emittable` — extend it
    with mutation cases).
  - **Differential fuzz (optional):** generate random first-order terms, render to each surface syntax,
    confirm extraction+canonicalize round-trips.
**Acceptance.** A documented corpus of ≥20 negative pairs and ≥20 positive pairs, all asserted, in CI; a
deliberately-weakened canonicalizer (e.g. one that ignores numeric literals) makes that suite red.

### P1-1 — Allow-list does not match the advertised trust bar
**Finding.** `proof_axiom_allowlist.py` accepts, for **Lean**: `{propext, Classical.choice, Quot.sound}`;
for **Rocq**: `Closed under the global context` **or** `{propositional_extensionality,
functional_extensionality[_dep]}`. The doctrine docs describe a stricter bar (Lean `⊆ {propext,
Quot.sound}`; Rocq "Closed / Section-Variables-only"). All accepted axioms are universally-accepted and
sound, so this is **not** an unsoundness — but the prose overstates what is enforced, and the Rocq parser
would actually *reject* bare Section Variables (they are not in the list), contradicting the
"Section-Variables-only" wording.
**Task.** Make code and doctrine agree. Either (a) tighten the lists to the advertised sets, or (b) keep
`Classical.choice`/extensionality and **rename the trust class** in the docs to its honest content
("standard classical + extensionality axioms"), and state per-axiom which standard axioms each cited proof
actually uses. Decide deliberately whether classical choice is in-scope; if it is, say so everywhere.
**Acceptance.** `proof_axiom_allowlist.py`, `stdlib-extreme-rigor.md`, and the glossary name the *same*
allowed set, with a one-line rationale per axiom.

### P1-2 — `reverify` (axiom-cleanliness) is opt-in; the default attribution check is name-only
**Finding.** `audit_proof.audit_both(...)` defaults to `reverify=False`, and `tests/test_audit_proof.py`
exercises only that path — so pytest confirms *names exist*, not that proofs compile or are axiom-clean.
The axiom check runs only when a `make` target passes `reverify=True` (or via the crosscheck path).
**Why it matters.** It is easy to believe "tests pass ⇒ proofs are axiom-clean"; they don't.
**Task.** Make the gating entry point always run with `reverify=True`, and add at least one pytest that
fails when a proof file gains a non-allow-listed axiom (a fixture proof citing `Classical.em` in Rocq, say).
**Acceptance.** A fixture proof with a disallowed axiom turns the *default* gate red.

### P2-1 — Doctrine doc drift (`stdlib-extreme-rigor.md`)
**Finding.** On `main`, `config/skills/csl-from-scratch/references/stdlib-extreme-rigor.md` reads
**Coq-only** (single prover; no Lean, no 3-way cross-check) — stale relative to the implemented dual-prover
reality in `proof2why3`.
**Task.** Reconcile the doctrine docs with the implementation: one canonical description of the
two-layer + 3-way + registry-derivation pipeline, cross-linked from the glossary
(`abstract-op.md`, `trusted-stub.md`, `axiom-registry.md`) and the plumbing internals.
**Acceptance.** No doc describes the trust model as single-prover; the plumbing-internals doc is cited as
the source of truth.

### P2-2 — Statement extraction depends on prover-version-specific output formats
**Finding.** Layer 2 parses `coqc Check` / SerAPI s-expressions and `lake env lean #check`/`#print axioms`
*text*. These formats are version-sensitive; `_cache_key` includes the prover version (good), but a format
change can silently turn a real check into an empty parse (→ relates to P0-2).
**Task.** Pin and record the exact Rocq/Lean versions the extractors target; add a smoke test that the
extractor produces a non-empty IR for a known theorem on the pinned toolchain, and fail-closed if it
doesn't (an empty extraction must never be treated as "trivially equal").
**Acceptance.** A pinned-version smoke test in CI; a forced-empty extraction makes the gate red.

---

## 3. Suggested order of work
P0-2 and P0-1 first (cheap, and they convert "looks checked" into "is checked"); then P0-3 (the real
residual TCB); then P1/P2 (alignment + hardening). P0-3 is the one that takes genuine effort and is the
highest *foundational* value — once the canonicalizer is adversarially tested, the 3-way check is as
trustworthy as it looks.

## 4. What this audit did NOT cover
The individual proofs' mathematical correctness (the prover kernels are trusted for that); the SMT-side
encoding of contracts into Why3; and the transpiler's binding of contracts to the registered symbols beyond
the documented `_axiom_logic_funcs` raw-emission (the abstract-op vacuity guard, which I read and judged
correct in design but did not exhaustively test). Those are separate audits.
