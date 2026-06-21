# HAPPY implementation — autonomous run status

Date: 2026-06-21 · Branch: `happy-impl` · PR #68

Executing `happy-roadmap-impl.md` unsupervised. Choices recorded as **ASSUMPTION:**;
halting at the first **HARD BLOCKER**.

## Done (landed + gated)

### Doc refresh + macsl coherence (commit on branch)
`happy-roadmap-impl.md` refreshed (paths/pipeline/gates) and made name-coherent with the C
sibling **macsl** (github.com/canonical/macsl): shared taxonomy, directive-vocabulary
correspondence, C↔Python differences table, the shared banking `transfer` flagship. Two
acronyms recorded (PyCSL: *High-level Assertion-Producing PYthon requirement*; macsl:
*Hyperproperty Analysis for Program PolicY*).

### H-I1 — read confinement (commit d2cc4534)
The read mirror of the shipped H-T region form:
`#@ happy <name>: region LO .. HI reads self.<field> outside region [except …]`.
Per-READ-site `#@ check (idx outside region)`; hard-error guards for exempt-non-method,
non-exempt dynamic `exec`, aliasing the protected field (full path AND prefix — closes a gap
R1 leaves), and non-exempt trusted/abstract readers. Realised in Module3 (AST), skipped from
the IR `happy` blob → IR byte-identical for write-confinement files, no IR_VERSION bump.
Drivers 0715 (positive) / 0716–0718 (negatives). **Gated:** conformance 38/38 core + 38/38
front-end; corpus 672/674 (only the pre-existing 0700/0701 fail); formal 121/121; 0715
non-vacuous.

### General `targets`/`postcond` directive + H-E (commit f5a139b2)
The macsl-coherent named-postcondition form:
`#@ happy <name>: targets <method> postcond <expr>` — attaches `<expr>` to `<method>` as an
`ensures`, verified in the method's own body. **H-E `priv_monotonic`** delivered:
`\forall i; role[i] >= \old(role[i])` on `transfer`. Drivers 0719 (positive) / 0720
(negative — lowers a role → postcondition VC fails). annotations.md §2.5 rows 6 & 7.
**Gated:** conformance 38/38 + 38/38; 0719 non-vacuous; (full corpus/formal re-run in flight).

## H-S (Spoofing / check-before-use) — UNBLOCKED + done

The blocker was: PyCSL does not enforce a callee's precondition at a self-call site
(`self.<m>(…)` lowers to a *contractless* abstract `val`; even `self.f(-5)` against
`requires x>0` passed). Investigating the C sibling **macsl** (../macsl `src/macsl.ml`
`emit_requires`) showed H-S there is just a plain `requires` — *checked by WP's automatic
call rule at every call site* (the `unauth_endpoint` red in `tests/small_example/attacks.c`).

PyCSL has no such automatic call rule for the abstract stub, so we get the SAME effect the
PyCSL-idiomatic way: the `precond` HAPPY (a) attaches the clause as a `requires` so the
target ASSUMES the capability (sound), and (b) **injects `#@ check <clause>` before every
`self.<target>(…)` call site** (the HAPPY check primitive) so the caller must PROVE it. A
caller that skipped the grant gets an unprovable VC IN THE CALLER — exactly macsl's
`unauth_endpoint`. Drivers 0721 (positive) / 0722 (negative — fails in `handle`).

**ASSUMPTION:** scoped to `self.<target>(…)` self-call sites (the H-S flagship pattern) with
minimal blast radius — receiver-var call sites and full macsl-parity *universal* precondition
checking at *all* call sites are a documented follow-up.

## H-R (Repudiation) — done

`nonrepud_complete` (any balance change implies the audit log grew) + `nonrepud_append_only`
(every earlier record is unchanged) as named `postcond`s on `transfer`, over an audit-array
bank model. SMT-dischargeable (append-only is the single-slot frame; completeness is the
both-paths implication). Drivers 0723 (positive) / 0724 (completeness negative — moves money
without logging) / 0725 (append-only negative — overwrites an earlier record). Mirrors macsl
main.c's two H-R policies.

## H-D (DoS / totality) — done

`#@ happy availability: targets parse total` (macsl's `\context(\total)`). PyCSL is
total-by-default — Why3 emits a termination VC and each loop needs a `#@ loop variant` — so
the policy NAMES that guarantee and rejects the only opt-out (`#@ \diverges` on the target is
a hard error). Drivers 0726 (positive — bounded loop + variant + `no_exception \all`) / 0727
(negative — `\diverges` rejected) / 0728 (negative — unbounded variant-less loop fails its
termination VC, i.e. the DoS).

## Remaining (out of scope here)

- **Full banking flagship `formal_bank_transfer.py`** composing all five named policies on one
  `transfer` — the per-milestone drivers above already prove each policy; the single-file
  composition is a packaging follow-up.
- **Full macsl-parity for H-S** (universal callee-precondition checking at ALL call sites,
  receiver-var call sites) — beyond the scoped self-call injection shipped here.
- **os-flagship H-R/H-E variants** needing cross-validated Rocq+Lean axioms (the prefix lemma /
  privilege lattice) — the doctrine's separate hard requirement; the banking variants shipped
  here are SMT-dischargeable.
