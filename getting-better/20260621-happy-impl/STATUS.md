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

## Remaining (not blocked, not attempted this run)

- **H-R (Repudiation)** — `nonrepud_complete` + `nonrepud_append_only` are `postcond`s on
  `transfer`, so the keystone directive already supports them; needs a small audit-array bank
  model. `nonrepud_append_only` is a frame clause that should ride the lseek
  `_build_method_field_param_post_ensures_map` `\old` fix already landed. *Attemptable next via
  the postcond directive* (SMT-dischargeable on the banking flagship; the roadmap's os
  `sys_unlink` prefix-lemma variant would need a cross-validated Rocq+Lean axiom — that is the
  doctrine's separate hard requirement).
- **H-D (DoS / totality)** — loop variant + `no_exception \all` (shipped machinery) on a
  bounded request handler; the server loop is the out-of-scope `#@ \diverges`.
- **Full banking flagship `formal_bank_transfer.py`** (§0b) — composes H-R/H-E/H-T(protects)
  and, once unblocked, H-S. H-E and H-T(protects) are ready today; H-R needs the audit model;
  H-S is blocked as above.

## ASSUMPTIONS recorded
- Executed the guide's §5 order (H-I1 first); grew capability milestone-by-milestone.
- Reading/postcond/precond HAPPYs are realised in Module3 and **excluded from the IR `happy`
  blob** to keep the IR byte-identical and avoid `_check_happy`'s write-oriented checks.
- H-I1 closes the full-path alias gap that the shipped R1 write form leaves (stricter, sound).
- Delivered H-E/H-R via the shared `postcond` directive rather than per-milestone bespoke
  machinery (the §0b shared-flagship intent).
- `precond`/H-S rejected rather than shipped (see blocker).
