# HAPPY Roadmap — From Write Integrity to Full STRIDE Coverage

**Status:** Roadmap — pre-normative. Each milestone below graduates to Normative only
when its directive surface lands in `test-suite/annotations.md` and in all three
reference documents, and the documentation-coherency gate (`bin/doc-coherency.py
--check`) passes for the new directives. Until then, every syntax sketch in this
document is a design proposal, not a grammar production.
**Version:** 0.1
**Source of truth:** the shipped HAPPY meta-pass as specified in
`test-suite/annotations.md` §2.5 (region integrity) and its demonstrated corpus
drivers (`0459`–`0462` region, `0611`–`0613` `protects` ownership, `0614`–`0615`
parametric footprint), cross-referenced against the `--soundness-report`
classification (Modelled / Specified / Stubbed / Confinement).
**Scope:** the extension of the `#@ happy` meta-property language to express and
discharge one property family per STRIDE category. It does NOT cover the TARA
traceability gate that consumes these properties (see the TARA-bridge design
note), and it does NOT define WhyML emission rules — each milestone that ships
must add its own §T sections to `pycsl-translational-reference.md`.
**Companion documents:** `test-suite/annotations.md` §2.5 (the shipped HAPPY
forms); `docs/pycsl-translational-reference.md` (lowering rules);
`config/skills/pycsl-ub-catalog/SKILL.md` (the UB-7.x boundaries that several
milestones lean on).

---

## 0. Where HAPPY stands, stated in the exact machinery

A shipped HAPPY (`region`, `protects`, parametric `protects` + `footprint`) is a
module-level declaration that a **meta-pass** expands before transpilation: at
every write site touching the protected state in a non-`except` method, the pass
injects a per-site `#@ check`, which Module 6 emits as a WhyML `assert { … }`
inside the enclosing `let`. Why3's weakest-precondition calculus turns each
injected assert into a verification condition; Alt-Ergo (then Z3) discharges it
under the per-goal budget, reporting *Valid* when the goal's negation is
unsatisfiable. A non-exempt `\trusted` or `\abstract` method — emitted as a WhyML
`val`, contract only, no body, **no VC of its own** — must instead carry
`#@ \preserves`, which attaches an *assumed* quantified `ensures`; that assumption
enters the trusted computing base and surfaces as **Confinement** in
`--soundness-report`.

That is one STRIDE letter: **Tampering**. The proof obligation is "no unauthorized
write", the enforcement point is syntactic (every write site), and the cost model
is favorable — injected checks are ground assertions, so the dominant SMT cost is
linear arithmetic over indices, not E-matching. The roadmap below extends HAPPY to
the remaining five letters in order of **mechanism reuse**: each milestone is
sequenced so that it composes machinery the verifier already has (ghost state,
quantified `ensures`, `assigns` frames, `no_exception` triggers, loop variants,
`#@ proof`-cited axioms) before any milestone that requires genuinely new WP
plumbing. The codes `H-T`, `H-I1`, `H-R`, `H-D`, `H-E`, `H-S`, `H-I2` introduced
here are intended as stable taxonomy, in the manner of the UB-7.x catalogue codes.

| Code | STRIDE letter | Property family | New machinery required |
|------|---------------|-----------------|------------------------|
| H-T  | Tampering | write confinement | none — shipped |
| H-I1 | Information disclosure (first half) | read confinement | none — symmetric meta-pass |
| H-R  | Repudiation | audit-log completeness | ghost-log injection |
| H-D  | Denial of service | totality + bounded work | bundling + ghost fuel counter |
| H-E  | Elevation of privilege | privilege monotonicity | ghost lattice over `protects` |
| H-S  | Spoofing | check-before-use capabilities | ghost tokens + call-site `requires` |
| H-I2 | Information disclosure (second half) | noninterference | relational VCs (self-composition) |

---

## 1. H-T — Tampering (shipped; hardening only)

Nothing to design; two hardening items keep the foundation honest. First, the
aliasing rule (`x = world.fs` into a non-exempt local is a hard error, driver
`0613`) must stay **syntactically complete** as the expression grammar grows —
any new construct that can smuggle a reference to a protected base out of the
meta-pass's sight reopens the letter. Second, the `\preserves` escape on `val`
boundaries is an assumption, not a proof; the soundness report already classifies
it, and every milestone below inherits the same rule: *an exemption or trusted
boundary inside a security HAPPY's scope is a TARA residual-risk entry, never a
silent pass.*

**Flagship use case (existing):** the inode filesystem model — only
`_write_inode` / `_write_directory` may touch the reserved disk region; a
formatter bug writing at offset 600 fails at its own site, with the HAPPY and the
site named in the diagnostic.

---

## 2. H-I1 — Read confinement (`reads … outside region`)

The cheapest extension in the family, because it is the mirror image of the
shipped pass. Proposed surface:

```python
#@ happy key_confidentiality:
#@     region 0 .. 64
#@     reads self.disk inside region
#@     except _kdf, _sign
```

The meta-pass walks **read sites** (`x = self.disk[i]`, slice reads, reads feeding
calls) instead of write sites and injects the same ground `#@ check i < 0 or
i >= 64` before each, in every non-`except` method. Lowering, VC shape, SMT cost,
and the `\preserves`-style obligation on `val` boundaries (here: an assumed
"reads-nothing-in-region" clause) are all the existing ones with the access
direction flipped. What this **is**: a proof that no non-exempt code path
*syntactically observes* the secret bytes. What it is **not**: noninterference —
it does not bound what the *exempt* readers do with the secret downstream. That
stronger property is H-I2, and conflating the two would be exactly the
"coherent and wrong" failure the philosophy warns about.

**Flagship use case:** a private key stored in bytes 0–64 of the disk array. The
error-message formatter — historically the classic leak channel — must verify
with zero injected checks failing, proving it cannot have read key bytes into the
string it builds. A deliberate negative driver (formatter peeks at
`self.disk[3]`) must fail at the read site.

---

## 3. H-R — Repudiation (audit-log completeness, `audits`)

Non-repudiation, at the level a deductive verifier can honestly claim, is a
**completeness and immutability theorem about a log**: every protected state
change produces a log record, and no code path can rewrite history. Proposed
surface:

```python
#@ happy audit_trail:
#@     audits world.fs.disk into audit_log
#@     except _replay_journal
```

Lowering composes three pieces of existing machinery. The meta-pass (1) declares
a module ghost `audit_log` (a `ghost_list` — erased at extraction, visible to
WhyML), (2) at each write site to the audited path injects the ghost append
*and* a ground `#@ check` that the append precedes the function's return, and
(3) attaches to every non-exempt method two quantified `ensures`: prefix
preservation, `\forall i; 0 <= i and i < \old(\length(audit_log)) ==>
audit_log[i] == \old(audit_log[i])` (the append-only theorem), and completeness,
`world.fs.disk != \old(world.fs.disk) ==> \length(audit_log) >
\old(\length(audit_log))`. These are quantified clauses, so unlike H-T/H-I1 the
dominant solver cost here **is** E-matching on the prefix-preservation
instantiations; the prefix lemma is a prime candidate for the Rocq+Lean axiom
route — proved offline in both kernels, registered, cited with `#@ proof`, and
thereafter instantiated as a module-level assumption rather than re-derived per
goal. No Rocq or Lean kernel runs during the `pycsl` proof itself.

What this is **not**: cryptographic non-repudiation. The verifier proves the
*program* cannot skip or rewrite a record; that the log survives on real storage,
is signed, and binds an identity remains a trusted boundary the TARA must carry.

**Flagship use case:** the filesystem model again — `sys_write` and `sys_unlink`
each provably append exactly one record, and a negative driver in which an
"optimized" unlink path skips logging fails its completeness `ensures`. This is
the use case auditors actually ask for: "show me the deletion that left no
trace" becomes a VC Alt-Ergo refutes.

---

## 4. H-D — Denial of service (totality and bounded work, `total`)

PyCSL already owns every ingredient: `loop variant` / `#@ \variant` make
termination a WP sub-goal; `no_exception \all` turns the implicit Phase-1
exception set into per-operation `assert { trigger }` obligations;
`assumes bounded_int(N)` makes overflow a VC. H-D is therefore a **bundling**
HAPPY plus one new ghost:

```python
#@ happy request_availability:
#@     total parse_request, dispatch
#@     fuel 4 * \length(buf)
```

`total f` is a hard meta-pass error unless `f` (and, transitively, every loop in
it) carries a variant and `no_exception \all` discharges — i.e., the bundle makes
"this function returns normally on **all** inputs" a checked claim instead of a
convention. `fuel` injects a ghost step counter incremented in each loop body,
with the bound carried as an injected loop invariant; the closing VC proves the
counter never exceeds the declared expression. State the claim's strength
precisely, because TARA consumers will over-read it: this proves
**totality and an iteration bound over the modelled loops** — the
never-faults/always-returns promise, which is the weaker, earlier theorem — not
wall-clock complexity, not CPython memory behaviour, not GIL starvation. Those
stay attack paths in the TARA.

**Flagship use case:** a request parser over attacker-controlled bytes. The
historical DoS pattern — a crafted length field that drives a `while` loop past
any bound, or a malformed packet raising an uncaught `IndexError` that kills the
worker — becomes two failing VCs (variant decrease, injected `no_index_oob`
assert) on the negative driver, and a *Valid* verdict on the fixed one, for every
input the quantified VC ranges over, not the sampled few a fuzzer reaches.

---

## 5. H-E — Elevation of privilege (privilege lattice, `privilege`)

The shipped `protects` already prevents a non-owner from writing privileged state
*directly*; the deliberate gap is that it allows going through the API. H-E
closes the gap above the API: it makes the **privilege level itself** protected
state with a monotonicity law. Proposed surface:

```python
#@ happy priv_lattice:
#@     privilege world.proc.priv levels user < admin
#@     raises_only_in sudo_gate
```

Lowering is `protects` applied to a ghost: `world.proc.priv` (or a ghost shadow
of it) gets the standard write-confinement pass with `except sudo_gate`, **plus**
an injected `ensures world.proc.priv <= \old(world.proc.priv)` on every
non-exempt method — privilege may only descend outside the gate. Both pieces are
machinery that exists today (per-site checks; injected ensures, as in
`\preserves`); the lattice order over more than two levels is a small finite
axiom set, registered once and cited, so the solver applies it as an in-scope
assumption rather than re-deriving order facts per goal. The gate itself is where
the proof burden concentrates: `sudo_gate`'s own contract must state exactly the
condition under which it raises privilege, and that contract is what H-S below
supplies.

**Flagship use case:** the filesystem's permission bits. `sys_chmod` running as
`user` must be unable — through any call path, including ones that *do* go
through owner methods — to end a call with `priv == admin`. The negative driver
is the classic confused-deputy: a helper reachable from unprivileged code that
writes the privilege field "temporarily"; it fails the monotonicity `ensures` at
the helper, naming the HAPPY and the site.

---

## 6. H-S — Spoofing (check-before-use capabilities, `capability`)

Spoofing defenses ultimately rest on a cryptographic or external identity check
that a WP verifier over WhyML cannot and should not pretend to prove — the
verifier of `verify_token` is an emitted `val` whose contract is a trusted,
cited specification. What the verifier **can** prove, for all inputs and all
paths, is the *discipline* around it: no protected operation is reachable
without the check having succeeded. Proposed surface:

```python
#@ happy authn:
#@     capability session_ok granted_by verify_token
#@     guards sys_write, sys_unlink, sys_chmod
```

Lowering: a ghost boolean (or ghost token set, for per-principal capabilities)
`session_ok`, assignable only inside `verify_token` — enforced by the H-T pass on
the ghost itself — and a meta-pass that strengthens each guarded method's
`requires` with `session_ok` and injects the corresponding `#@ check` at every
call site. The call-site check is the load-bearing emission: it becomes a WP
sub-goal in the **caller**, so an unauthenticated path to `sys_write` fails in
the code that took the shortcut, not in the filesystem. `verify_token` itself
contributes `ensures \result == 1 ==> session_ok` and stays
`\trusted reviewer:`-or-better; its trust is precisely the assumption the TARA
records ("token verification is correct"), and everything around it is Modelled.

**Flagship use case:** a session-handling layer over the filesystem model. The
negative driver is the forgotten-check bug — a new maintenance endpoint calling
`sys_unlink` directly; the injected call-site check yields an unprovable VC the
moment the file is verified, before review, before deployment. The positive
driver shows the full chain *Valid*: `verify_token` (trusted contract) →
capability ghost → guarded syscall.

---

## 7. H-I2 — Noninterference (the one genuinely new mechanism)

H-I1 proves secrets are not *read* outside the enclave; H-I2 proves the enclave's
**outputs do not depend on them** — noninterference with declassification. This
is the only milestone that cannot be assembled from per-site checks and injected
`ensures`, because the property is **relational**: it compares two executions.
The standard reduction a WP engine supports is **self-composition**: the
transpiler emits the function body twice into one WhyML `let` over disjoint
copies of the store, equates the low-labelled inputs in the `requires`, and the
postcondition asserts equality of low-labelled outputs. Why3's WP then produces
ordinary first-order VCs — but over a doubled state, so E-matching cost grows
sharply with module size; the engineering substance of this milestone is keeping
the composed VC affordable (modular `no_inline` boundaries so each function's
relational proof is done once and reused via its contract, and ground `#@ for`
expansion over fixed-size buffers instead of quantifiers). Proposed surface:

```python
#@ happy no_leak:
#@     secret self.disk[0 : 64]
#@     public \result, world.net.out
#@     declassify _sign
```

What this is **not**: a side-channel proof. Timing, cache, and allocation
behaviour are below the WhyML model; the TARA keeps them. Sequencing note: H-I2
is deliberately last — it should land only after H-I1's labels and enclave
syntax are stable, so the relational pass reuses the same declarations rather
than inventing a second labelling language.

**Flagship use case:** the login path. `check_password(stored, attempt)` must
return a result whose *value* is the only thing that depends on the secret — the
composed VC proves that two runs with different stored passwords but equal
attempts produce equal observable output apart from the declassified boolean.
The negative driver returns early with a length-dependent error message; the
relational postcondition fails, which is the verified version of the oldest
password-oracle bug in the book.

---

## 8. Cross-cutting obligations (every milestone, no exceptions)

Each milestone ships only with: its grammar productions in the concrete syntax
reference, well-formedness rules and error codes in the static semantics
reference, lowering rules (a §T section) in the translational reference, a
canonical-directive entry in `test-suite/annotations.md`, prove/fail corpus
driver pairs in the pattern of `0611`/`0612`, and a clean
`bin/doc-coherency.py --check`. Each new escape hatch (`except`,
`declassify`, a trusted `val` contract) must be classified by
`--soundness-report` so it lands in the TARA residual-risk register
mechanically rather than by memory. A milestone whose checks pass but whose
exemptions are invisible to the soundness report is not done.

## 9. Gap analysis

- **GH1 — Spoofing/Repudiation are discipline proofs, not identity proofs.**
  H-S and H-R prove the program enforces check-before-use and log-completeness;
  the identity check and the log's external integrity are trusted `val`
  contracts. Permanent boundary, by design.
- **GH2 — H-D bounds modelled work only.** Iteration counts over WhyML-modelled
  loops; no claim about CPython memory, GC, or wall-clock.
- **GH3 — H-I2 excludes side channels.** Below the memory model; out of scope
  for any milestone here.
- **GH4 — Concurrent interaction unspecified.** The composition of every H-x
  with `--memory-model concurrent` (havoc + assume/assert critical sections) is
  undesigned; until specified, security HAPPYs are sound only under the
  sequential models.
- **GH5 — Exempt-method behaviour.** Every `except` list transfers the
  obligation from the meta-pass to the exempt method's own contract; a weak
  contract on an exempt writer/reader is the residual attack path the TARA must
  rate.
