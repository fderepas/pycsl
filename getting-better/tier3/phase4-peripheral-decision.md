# Tier-3 Phase 4 — peripheral-subsystem decision: `pure_ast` and `proof2why3`

**Task:** T3.4.1 / T3.4.2 / T3.4.3 of `triage-ranked-tcb-tier3.md`. Decide, with a rigorous
evidence-backed soundness argument, whether the two peripheral `\trusted` masses —
`frontend/pure_ast.py` (~258 stubs) and `proof2why3/*` (~115–130 stubs) — should be **left
trusted** or **converted** as part of the tier-3 value-ADT effort.

This is a DECISION + DOCUMENTATION deliverable. No `src/pycsl`, emitter, mirror, or
`why3-semantics` change is made. The crux is a per-subsystem **false-verifies vs. fail-stop**
classification, mapped to the certified trust boundary of `src/formal-semantics/README.md` and
the front-end↔core contract of `docs/ir.md`.

---

## 0. The frame: what the 3-axiom ledger actually certifies

The mechanized soundness proof (`src/formal-semantics/README.md §1, §4, §9`) certifies exactly
one thing: that the **weakest-precondition (WP) calculus at the core of the IR pipeline is sound
with respect to a structural operational semantics** of the supported Python subset. Concretely,
the certified object is the chain

```
resolved-IR  →  WhyML  →  WP  →  SOS      (LINK 1/2/3; 3 named axioms)
```

The theorem `pycsl_soundness` / `pycslSoundnessVerified` says: *if* the emitted WhyML's VC is
discharged, *then* the program satisfies its contract **relative to the SOS of the IR it was
handed**. The README §9 trust diagram is explicit that everything *upstream* of that chain — the
**"Python parser", "Transpiler", "Syntactic desugar", "multi-file import"** — is **TRUSTED BY
DESIGN**, outside the proven box. The certified boundary begins at the **resolved IR**
(`docs/ir.md §1`, the "front-end ↔ core wire contract"): the core is independently invokable on a
serialized IR with *no front-end present* (`bin/core-only-conformance.py` asserts at import time
that no `Module1..5` / `pure_ast` module leaked into `sys.modules`).

Two consequences frame the whole decision:

1. **`pure_ast` is strictly UPSTREAM of the certified boundary.** It is the source→AST reader; its
   output flows source → AST → (Module 2 `#@`) → … → resolved IR → *[certified chain begins]*. A
   bug in it corrupts the IR *before* the certificate applies.
2. **`proof2why3` is not on the WP chain at all.** It sits on the *certification-ingestion* path
   (the cited `#@ proof` mechanism), and — as §2 establishes with a decisive code fact — it is not
   even on the *runtime* trust path of that mechanism.

These are two different kinds of "peripheral", and they get two different (but both leave-trusted)
arguments. The honest work is to name the residual gap in each precisely, rather than wave at
"peripheral".

---

## 1. `pure_ast` — the source→AST reader

### 1.1 What it is
`src/pycsl/frontend/pure_ast.py` (3827 LOC; 258 hard-architectural `\trusted` stubs in the mirror)
is a **pure-Python reimplementation of the stdlib `ast` module**: the full ASDL-derived node
hierarchy (`AST`, `Module`, `BinOp`, …), a hand-written tokenize+recursive-descent `parse`, every
helper (`dump`, `walk`, `unparse`, `NodeVisitor`, …), targeting the Python 3.12 grammar. It is the
**first stage** of the front end — the thing that turns program *text* into a tree.

### 1.2 The soundness verdict: **FALSE-VERIFIES POSSIBLE (in principle)**
Be blunt: a bug in `pure_ast` **can** cause PyCSL to verify a program that is not the one the user
wrote. If `parse` produces an AST that does not faithfully represent the source text's Python
semantics, then every downstream stage — Module 2..5, the resolved IR, the WhyML, the discharged
VC — is *about a different program*. The 3-axiom ledger still holds (the WP is sound for the IR it
was handed), but the IR is unfaithful to the source. This is a **genuine, distinct trust
boundary**: **source→IR faithfulness**, which is *not* the WP-soundness the ledger covers. Calling
it "just peripheral" would be dishonest. It is, in the strict sense, a "verify-the-wrong-program"
risk.

So the interesting question is not "is there a gap" (there is) but "**is conversion the right
control for it, and is it caught elsewhere**".

### 1.3 The decisive observation: conversion does NOT close this gap
Self-annotation proves that each `pure_ast` method satisfies **its own contract** — type-safety,
frame (`assigns`), structural post-conditions on the method's *internal* data. It does **not**, and
cannot, prove the property that actually matters here:

> *"`pure_ast.parse(src)` yields the AST that faithfully represents the Python semantics of `src`."*

That is a **differential-conformance property against CPython's grammar**, and there is **no
mechanized formal semantics of the Python grammar to verify a self-contract against**. No `ensures`
clause can express "this tree is what CPython 3.12 means by this text". Converting all 258 stubs
buys type-safety/frame assurance on the reader's *internals* — real but orthogonal — while leaving
the soundness-relevant property (grammar faithfulness) exactly where it was. **Marginal soundness
value of conversion ≈ 0.**

### 1.4 What DOES cover the residual gap (compensating assurance)
The source→IR-faithfulness gap is **bounded, not eliminated**, by three controls that are already
in place and are the *correct* controls for a differential property:

1. **Fail-closed design.** Unsupported constructs raise `PyCSLSyntaxError` — a *loud* failure,
   **never a silently-wrong tree** (module docstring, "COVERAGE MANIFEST"). The dangerous case (a
   silent structural misparse to a valid-but-wrong tree) is the only residual; outright gaps
   fail-stop.
2. **CPython differential validation.** The module's COVERAGE MANIFEST records the exact
   differential oracle: on the CPython 3.12 standard library, **512 / 517 files parse to a
   byte-identical `ast.dump(...)` against the stdlib `ast`, 0 mismatches, 0 crashes**; the 5
   residual files are *deliberately* deferred and `PyCSLSyntaxError`-loud. This oracle — compare
   `pure_ast`'s tree to CPython's own tree on a large real corpus — is precisely the assurance a
   self-contract cannot give, because it checks against the *reference implementation's* grammar,
   not against a (non-existent) formal one.
3. **Standing source→IR conformance.** `bin/frontend-only-conformance.py` (`docs/ir.md §10.2`)
   re-derives the resolved IR from source for every reference driver and structurally diffs it
   against a frozen golden — a live regression on `pure_ast`→…→IR *stability* over the corpus, run
   in `bin/run-reference-tests.sh`.

The honest summary: the residual gap is a **silent structural misparse of a construct inside the
supported subset**, and the differential oracle against CPython's own `ast` is what keeps that
bounded. That control should be **maintained and, ideally, CI-wired** — it is worth strictly more,
per unit effort, than converting the stubs would be.

### 1.5 The cost side (value tradeoff)
Even setting aside that conversion wouldn't close the gap, the cost is the **largest ADT in the
whole frontier**:
- A **second, larger ADT than the Module-6 emitter ADT** tier-3 is building — the full CPython
  `ast.*` node hierarchy (dozens of ASDL node kinds vs. the emitter's IR-dict node model),
- plus dynamic `getattr`/`setattr` over node fields, `tokenize`-module dependence, and
  recursive-descent parser *state* — none of which the Module-6-core ADT machinery (§Phase 1) is
  designed for.

Per the tier-1/tier-2 calibration (`triage-ranked-tcb.md §Tier 1/2`; the tier-2a REVERT): a large
`--no-proof` fan-out overstates the *convertible* yield 3–5×, and heterogeneous-tree recursion is
exactly what stalls on termination/reflection VCs. `pure_ast` is that pattern at maximum surface.

### 1.6 Decision: **LEAVE TRUSTED**
- **Residual-gap statement (explicit):** leaving `pure_ast` trusted leaves an open **source→IR
  faithfulness** trust boundary — a silent structural misparse could make PyCSL verify a
  program other than the source. This is a *distinct* boundary from the 3-axiom WP-soundness ledger
  and is not covered by it.
- **Why acceptable:** (a) conversion would not close it (self-contracts can't express grammar
  faithfulness — §1.3); (b) it is *compensated* by a fail-closed reader + the CPython differential
  oracle (512/517 byte-identical, 0 mismatches) + the standing frontend-only conformance corpus
  (§1.4); (c) the cost is the frontier's largest, most reflection-heavy ADT (§1.5).
- **Condition that flips the decision:** convert `pure_ast` **only if** a *verified* source→IR
  faithfulness artifact is wanted for its own sake AND a mechanized Python-grammar conformance
  oracle exists to verify against (today it does not). Even then, the faithfulness assurance would
  come from the differential oracle, not the self-annotation — so the correct investment in that
  scenario is to **strengthen and CI-wire the CPython differential test**, not to convert the 258
  stubs. Conversion for *internal* type-safety/frame assurance is defensible but is a low-priority
  ride-along on the Module-6 ADT machinery, distinct and larger, undertaken only after the
  soundness-bearing Module-6 core is done.

---

## 2. `proof2why3` — the cited-proof ingestion cross-check

### 2.1 What it is
`src/pycsl/proof2why3/*` (~3400 LOC; 115–130 `\trusted` stubs) is the Rocq/Lean s-expression →
WhyML proof-ingestion pipeline: a `Term` variant ADT (`ir.py`), an s-expr parser (`from_sexp.py`),
a Lean-JSON projector (`from_lean_json.py`), regex normalization (`normalize.py`,
`canonical.py`), a `sertop` subprocess bridge (`sertop.py`), and the three-way cross-check
(`crosscheck.py`, `crosscheck_ir.py`). Its stated job (`proof2why3/__init__.py`) is a **mechanical
cross-check between cited Rocq/Lean theorems and the Module 6 axiom registry**.

### 2.2 The decisive architectural fact: `proof2why3` is NOT on the runtime trust path
This is the crux, and it is a verifiable code fact, not a judgement call:

- The object the verifier actually **trusts** is the **hand-curated `_AXIOM_REGISTRY`** dict in
  `src/pycsl/module6_whyml/preamble.py` (qualname → WhyML axiom body). *That* dict is what emits a
  WhyML `axiom` block the SMT solver consumes. Its header comment is explicit: it is a "registry of
  **hand-curated** axiom bodies … cross-checked **manually** for the MVP".
- **`pycsl.py` — the verification entrypoint — does not import `proof2why3` at all** (grep:
  `proof2why3` absent from `pycsl.py`). Every `import proof2why3` in `src/pycsl/` is *internal* to
  `proof2why3`'s own modules, or from **offline `bin/` scripts** (`proof2why3-emit.py`,
  `check-proof-crosscheck.sh`, `proof2why3-merge-registry.py`). It is **not on the
  source→IR→WhyML→VC pipeline**.
- The `--audit-proof` path (`pycsl.py:_run_audit_mode`) uses `audit_proof.py` — a
  namespace-presence audit, optionally recompiling each cited proof via `coqc`/`lake env lean` and
  checking `Print Assumptions` / `#print axioms` against the kernel-axiom allow-list. **This
  independent anchor does not go through `proof2why3` either.**

So `proof2why3` is an **auxiliary assurance/authoring tool** that *compares* cited theorems to the
registry (3-way diff) and can *propose* candidate axiom bodies for a human to paste
(`proof2why3-emit.py` → "pasted into `_AXIOM_REGISTRY`"). It is **not trust-conferring**.

### 2.3 The soundness verdict: **FAIL-STOP / ASSURANCE-DEGRADATION ONLY — cannot false-verify**
Enumerate what a bug in `proof2why3` can do:

- **False MATCH** (reports the registry agrees with the theorem when it does not): this **degrades
  an assurance check**, but it does **not add or alter any axiom**. The axiom the SMT trusts is the
  registry body, which is (a) human-curated and reviewed, and (b) independently anchored by the
  cited Rocq **and** Lean proof plus `--audit-proof --reverify` (coqc/lean `Print Assumptions`
  against the allow-list). A false MATCH cannot *inject* an unsound axiom; it can only fail to
  *catch* a discrepancy that the two independent controls above are the real guard against.
- **False MISMATCH:** pure fail-stop noise (the `check-proof-crosscheck.sh` gate goes red).
- **Bad `emit` output** (proposes a wrong candidate body): gated by **human review** before paste
  **and** by `--audit-proof --reverify`. It cannot silently reach the trusted registry.

There is **no path** by which a `proof2why3` bug silently makes the SMT solver trust a false axiom
and thereby verify a false program. The trust flows *registry → SMT*, anchored *registry ↔ cited
proof* by `--audit-proof`; `proof2why3` sits *beside* that, as a cross-check, never *inside* it.

### 2.4 Cost side, and why it is doubly-weak value
- Converting `proof2why3` needs its own ADT: the `Term` variant + s-expr/JSON tree recursion (the
  A7 triage's ~77 architectural stubs) — a *second* recursive-tree ADT distinct from the Module-6
  emitter ADT.
- A large remainder is **near-floor external opacity** anyway: `sertop.py` (Coq `sertop`
  subprocess), the `tokenize`/regex layer, and Lean-JSON `subprocess` — irreducible `val`s in the
  same class as the 4 genuine floor stubs (`triage-ranked-tcb.md §FLOOR`). So even a full ADT
  effort would not verify the trust-relevant part (there isn't one) and would leave a subprocess
  floor.

### 2.5 Decision: **LEAVE TRUSTED** (most strongly justified of the two)
- **Residual-gap statement (explicit):** leaving `proof2why3` trusted leaves **no
  false-verifies gap at all** — it is not on the runtime trust path. The only residual is a
  *degraded auxiliary cross-check*: a `proof2why3` bug could weaken the `check-proof-crosscheck.sh`
  assurance that the hand-curated registry matches the cited theorems. That assurance is redundant
  with the human curation and the independent `--audit-proof --reverify` anchor, so its degradation
  is an **availability/assurance** issue, never a soundness one.
- **Why acceptable:** the actual soundness anchor for a cited `#@ proof` axiom is
  (registry body) + (dual Rocq/Lean proof) + (`--audit-proof --reverify` against the kernel-axiom
  allow-list) — all independent of `proof2why3`. Cost to convert is a second tree ADT over a
  subprocess/regex floor, with zero trust-path value.
- **Condition that flips the decision:** convert (or otherwise formally control) `proof2why3`
  **only if** it is ever promoted to **auto-generate `_AXIOM_REGISTRY` entries consumed at runtime
  without the human-review + `--audit-proof --reverify` gate** — i.e. if `emit` output is wired
  directly into the trusted registry. In that world it *moves onto the trust path* and a bug could
  inject an unsound axiom, so it would then require conversion **or** (preferably) a hard
  requirement that its output remain gated behind `--audit-proof --reverify`. As long as the
  reverify audit stands between `proof2why3` and the trusted axiom, leave-trusted is sound.

---

## 3. Summary table

| Subsystem | On WP trust chain? | Bug ⇒ false-verifies? | Compensating assurance | Decision | Flip condition |
|---|---|---|---|---|---|
| `pure_ast` (~258) | No — **upstream** of the certified resolved-IR boundary (source→IR) | **Yes, in principle** (silent structural misparse ⇒ verify-the-wrong-program) — a *distinct* boundary from the 3-axiom ledger | Fail-closed `PyCSLSyntaxError` (never a wrong tree) + CPython differential (512/517 byte-identical `ast.dump`, 0 mismatch) + standing `frontend-only-conformance` | **LEAVE TRUSTED** | A verified grammar-faithfulness oracle is wanted **and** a mechanized Python grammar exists to verify against — then strengthen the differential test, not convert |
| `proof2why3` (~115–130) | No — **beside** the cited-proof path; **not imported by `pycsl.py`**; verifier trusts the hand-curated `_AXIOM_REGISTRY`, anchored by `--audit-proof --reverify` | **No** — fail-stop / assurance-degradation only; cannot inject an axiom | Registry is human-curated; axiom independently anchored by dual Rocq/Lean proof + `--audit-proof --reverify` (kernel-axiom allow-list) | **LEAVE TRUSTED** | `proof2why3 emit` is ever wired to auto-populate `_AXIOM_REGISTRY` **without** the review + `--audit-proof --reverify` gate |

## 4. Verdict vs. the plan's prior stance
The tier-3 plan (`triage-ranked-tcb-tier3.md §Phase 4`) and `triage-ranked-tcb.md §Tier 3`
recommended leave-trusted for both, calling them "peripheral to the WP-soundness story". This
analysis **confirms both leave-trusted decisions**, but **sharpens the justification and corrects a
loose claim**:

- For `proof2why3` the prior "peripheral" label is *understated in PyCSL's favour*: it is not
  merely peripheral, it is **provably off the runtime trust path** — a clean fail-stop. Strong
  leave-trusted.
- For `pure_ast` the prior "peripheral" label was **too glib**: there **is** a genuine
  source→IR-faithfulness false-verifies boundary here, distinct from the ledger. Leave-trusted is
  still the correct call — but for the *sharper* reason that **conversion would not close that gap**
  (self-contracts can't express grammar faithfulness), while the CPython differential oracle does
  bound it. The recommendation is therefore refined: leave the stubs trusted **and treat the
  differential oracle as the load-bearing compensating control** — maintain/CI-wire it rather than
  pour ADT effort into the reader.

No revision to the *decision* is warranted; the plan's recommendation stands, with the residual gap
for `pure_ast` now named precisely and the compensating control identified.
