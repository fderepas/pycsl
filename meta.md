# Implementation plan: meta-properties in PyCSL (`#@ assert`/`check` → HAPPY)

> Standalone plan. Consolidates and supersedes the earlier `act → statement-assert → MetAcsl`
> roadmap and its two refinement passes (now folded in here). The proven precedent it builds
> on is `act.md`.
>
> **HAPPY** = **H**igh-level **A**ssertion-**P**roducing **PY**thon requirement — PyCSL's
> equivalent of ACSL/MetAcsl's **HILARE** (HIgh-Level Acsl REquirement). One HAPPY declares a
> cross-cutting property and **expands** into many ordinary per-site assertions, which Why3
> discharges. (We keep **HILARE** only when referring to the ACSL/Frama-C original; "hilare"
> is best left to the French.)

## Scope

The value of meta-properties for PyCSL is **cross-cutting whole-program integrity /
confidentiality invariants over many functions** — *not* the Frama-C multi-plugin ecosystem
(PyCSL has a single Why3/SMT backend, so the plugin-coordination machinery buys nothing).
Same stance as `act`/`given` vs ACSL's `behavior`/`assumes`: borrow the **idea** (high-level
surface → existing primitives → **0 `\trusted`**), not the plugin-shaped design or vocabulary.

## What `act` taught us (the operating discipline, applied at every phase)

1. **Desugar/expand to existing primitives — never grow the TCB.** `act` added a whole
   construct with **0 new IR nodes, 0 backend change, 0 `\trusted`**, entirely in the
   front-end. HAPPY does the same at *program* scope: expand one requirement into many
   ordinary per-site obligations.
2. **Verify the target primitive's *real* semantics first.** `act` sidestepped a missing
   primitive — PyCSL's `assert` is emitted as `()` and **never proved**
   (`module6_whyml/statements.py:1198`) — by lowering `complete`/`disjoint` to
   `ensures \old(…)`. **HAPPY cannot sidestep it** (it expands to per-*site* obligations =
   statement-level asserts), so **Stage A must build a real statement-level proof obligation
   first.** Ask of every primitive: *proved, assumed, or dropped?*
3. **Contain the front-end change; prove byte-identical.** Gate new behavior on the new
   directive; prove non-users harvest/emit unchanged (the corpus differential — `act` proved
   all 410 files identical).
4. **Emission has coercion gotchas.** The `_to_bool` fix (`\old(comparison)` is boolean,
   `expressions.py`) was needed for `act`; Stage A/B assertions over comparisons reuse it.
5. **Gates are non-negotiable:** 5-surface doc-coherency, reference-corpus demos *including a
   negative case with teeth*, determinism (ordered, `PYTHONHASHSEED=0`), SY3 mod-index regen,
   `audit-pycsl-language`, RAG, full `run-reference-tests.sh`.

## Stages & dependency

```
Stage A  real statement-level proof obligation (#@ assert / #@ check)
         ├─ first customer: migrate act's complete/disjoint onto an entry assert
         │  (removes act's normal-return-only caveat)
         └─ prerequisite for ▼
Stage B  HAPPY meta-properties: expand one whole-program requirement
         into per-site Stage-A obligations
```

Stage A ships value on its own (statement assertions are independently useful) and **locks
nothing** (the surface is stable; only lowerings change). Do it first.

---

## Stage A — `#@ assert P` / `#@ check P` (statement-level proof obligations)

A genuine proof obligation at a program point: **`assert`** = prove-**and-assume** (P becomes
a hypothesis afterward); **`check`** = prove-**and-discard** (no hypothesis) — mirroring ACSL
and WhyML (`assert`/`check`/`assume` are reserved in `module6_whyml/identifiers.py`).
**Distinct from** the Python `assert` statement, which stays a no-op (`statements.py:1198`) —
do not conflate them.

These are **statement-position** `#@` directives — same shape as `#@ label L`, so reuse that
machinery:

- **Module1** — own-line `#@ assert P` / `#@ check P` before a statement; harvest like
  `label` (no `act`-style folding). *Contained:* non-assert harvesting byte-identical.
- **Module2** — grammar `assert_decl: "assert" expr` / `check_decl: "check" expr`; node
  `CheckPoint(kind, expr)`. (Confirm `assert`/`check` are free as contract keywords vs the
  existing reserved set.)
- **Module3** — attach to the following `ast.stmt` (the post-weave `ast.walk` step that
  attaches `csl_labels` is the template → `csl_checkpoints`).
- **Module5** — emit a **new** IR stmt `{"stmt": "ProofAssert", "kind": "assert"|"check",
  "test": …}`, prepended before the statement's own IR (the `Label` prepend is the template).
  Leave the Python-`assert` `Assert` IR and its `()` emission **unchanged**.
- **Module6** — emit `assert { P }` / `check { P }` for `ProofAssert` (a real obligation Why3
  discharges); reuse `_expr_to_whyml` + the `_to_bool` boolean handling.
- **Module4** — validate the expression in the statement's scope (position rules for
  `\result` etc., via the existing `_validate_contract`).

**First customer — migrate `act`'s `complete`/`disjoint`.** Re-lower them (Module3 desugar)
from `ensures \old(g1)||…` to a **function-entry** `#@ assert (g1 || …)` (per-pair for
disjoint). At entry the preconditions are hypotheses, so this discharges `Pre ⟹ …` on **all**
paths — removing `act`'s documented normal-return-only caveat, and exercising Stage A on a
known case before Stage B relies on it.

**Stage A gates:** corpus byte-identical for non-assert files; doc-coherency 5 surfaces for
`assert`/`check`; demos — a true `#@ assert` proves, a **false one fails** (teeth), and
`check` vs `assert` differ on whether the fact is usable downstream; act-migration demos
(`0454`–`0456`) keep their verdicts (`0456` still fails completeness, now via the entry
assert).

---

## Stage B — HAPPY meta-properties

### Why naive site-enumeration is unsound

A HAPPY expands into per-site obligations. The tempting "enumerate write/read sites and inject
a check at each" hides the two facts that decide soundness — **indirect writes through
callees** and **aliasing** — and PyCSL has **no alias/effect/points-to analysis** (only the
SCC call graph in `module6_whyml/scc.py`, used for emission ordering).

Both dissolve once the obligation is stated at **the location actually written** rather than a
syntactic name — and that location exists in **either** model: an **address** in `typed`/
`store` (a true cross-object heap, `int_mem := Map.set !int_mem a v`), **or** an **index** into
a **shared instance field** in `hoare` (e.g. `self.disk[i] = v` — value-semantic but shared
through `self`). The executed gate (below) **proved** the `hoare`/shared-field framing, so the
flagship integrity property is **hoare-first**; reach for `typed`/`store` only when the
property spans a genuinely global heap, not a single object's field. Either way, composition
is *provable*, not asserted.

### The composition theorem (proven, not asserted)

Take a `\writing` HAPPY as a predicate `φ(ℓ)` over **the location written** `ℓ` — e.g.
*integrity:* `φ(ℓ) ≜ ¬ in_region(ℓ, secret) ∨ current_fn = encrypt`. Each memory model has a
**single write-shape** with a concrete `ℓ`: in `typed`/`store` it is the address `a` in
`int_mem := Map.set !int_mem a v`; in `hoare` over a shared instance field it is the index `i`
in `self.field[i] = v`.

> **Theorem (modular soundness of a `\writing` HAPPY).** If
> (1) **every body-verified function** carries, at **each** write-shape site, a proven
>     `#@ check { φ(ℓ) }`, and
> (2) **every function that can mutate the shared state** is either body-verified (covered by
>     (1)) or **trusted/abstract carrying an effect declaration** bounding its writes to
>     `φ`-locations (checked/assumed at the trust boundary),
> then **no execution performs a write violating `φ`.**
>
> *Proof.* Every mutation occurs at some write-shape site inside some function `f`. If `f` is
> body-verified, that site discharged `check { φ(ℓ) }`. If `f` is trusted, its effect
> declaration bounds its writes to `φ`-locations. There is no third source of mutation. Hence
> every mutation satisfies `φ`. ∎

**Why this needs neither alias analysis nor caller-side reasoning:**
- **Aliasing is irrelevant** — the obligation constrains the *actual location written* (`a` in
  `Map.set … a v`, or `i` in `self.field[i] = v`), not a syntactic name; in `hoare`,
  value-semantics additionally bars a local alias from mutating the shared field at all.
  `in_region`/disjointness is plain index arithmetic (`hoare`) or address arithmetic +
  `\valid`/`\separated` (`typed`).
- **Indirect (callee) writes are caught at the callee's own site** — if `f` calls `g` and `g`
  writes the secret, the violating write-shape is **inside `g`**, where `g`'s injected `check`
  fails. The call graph is **not** load-bearing for soundness; **universal coverage** is.

So cross-function composition reduces to two *checkable* obligations — universal coverage of
bodies, and an effect declaration on the (already-trusted, small) stub boundary.

### Stage-B gate — build only if a concrete property demands it (fuses B0 + B4)

Stage B is a large, research-flavored build; like `act` it must be **demand-driven and
measurable**, not justified by the *category* "integrity." Gate it on a named HAPPY over
**existing** repo code that PyCSL **cannot express today**, with a hand-proof before any
machinery.

> **Target HAPPY (typed/store):** on `unix-filesystem/UnixInodeFileSystem.py` —
> *"No function except `_write_inode` / `_write_directory` writes the inode/directory block
> region"* (variant: *"the free-block bitmap is mutated only by the allocator"*).

It qualifies: genuinely cross-cutting (spans most methods), a shared-state property (the
location-level obligation applies — **index** into `self.disk` in `hoare`, not a heap address),
and not expressible today without duplicating a region-disjoint `assigns` obligation into every
method by hand.

**The gate passes only when, in order:**
1. **Necessity / DRY threshold** — the obligation would land in **≥ 3 functions / ≥ ~10 write
   sites**; hand-annotation is clearly impractical (the measured driver, as DRY-on-guards was
   for `act`).
2. **Hand-proof spike (= B0 on real code)** — with **Stage A only**, manually inject
   `#@ check { ¬in_region(i, inode_region) }` at the relevant sites and **prove the property**
   on the clean file, empirically validating the theorem + the location predicate (index, in
   `hoare`) + the single-write-shape (`self.disk[...]`) assumption.
3. **Teeth (= the B4 negative)** — plant a stray writer; confirm it **fails at that function's
   own site**, and that per-function contracts alone miss it.
4. **Automation payoff** — only now build B1–B5 to auto-inject what the spike hand-wrote;
   acceptance = same property proven, planted violation still fails, **one HAPPY replaces N
   hand-sites** (record the N→1 ROI).

**YAGNI exit:** if step 1 or 2 fails (cheaply hand-encodable, or won't prove by hand), **do
not build Stage B** — document the manual `assigns`-disjointness idiom instead.

> **GATE EXECUTED — VERDICT: PASS (hoare framing).** Ran on
> `unix-filesystem/UnixInodeFileSystem.py` (inode region = bytes `[512, 2560)`,
> `offset = 512 + inode_num*64`). Findings:
> - **Feasibility/proof:** with Stage A's `#@ check start >= 2560` injected at
>   `_block_roundtrip`'s write (`start = block*512`, `block >= 6`), the file proves
>   in full Why3 (~42 s). The index-level integrity obligation is expressible *and*
>   provable.
> - **Teeth:** the disjoint-from-inode-region check injected into `_write_inode`
>   (which writes *into* `[512,2560)`) **fails** — the obligation correctly catches an
>   inode-region write at its own site.
> - **DRY:** **14 `self.disk[...]` write sites across ~7 methods** (`_set_bitmap`,
>   `_write_inode`, `_block_roundtrip`, `_write_directory`, `_write_entry`, unlink,
>   rename) — far above the ≥3-functions/≥10-sites threshold; hand-injecting + re-checking
>   on every edit is impractical.
> - **B0 soundness (hoare):** all 14 mutations are syntactic `self.disk[...]` sites
>   (sole path); value-semantic arrays prevent a local-alias escape; the predicate is
>   plain integer arithmetic on the index.
>
> **Amendment to this plan's premise:** the gate ran **hoare-first** and *worked* — a
> **shared instance field** (`self.disk`) is shared mutable state in `hoare` too, with
> the obligation stated at the **index** level (not heap `Map.set`), and value-semantics
> *removes* the aliasing worry. So "typed/store-first" is **not** required for the
> flagship integrity property; `hoare` over a shared field is the simpler first target.
> ⇒ **The HAPPY meta-pass (B1–B5) is justified** — build it next (a separate pass) to
> auto-inject the per-site `#@ check` the spike hand-wrote.

> **IMPLEMENTED (B1–B5).** The meta-pass ships, hoare-first, exactly as gated:
> - **Surface** (B1): a module-level `#@ happy NAME:` block (`region LO .. HI` /
>   `writes self.<field> outside region` / `except …`), folded in Module1 (mirroring
>   `act`), parsed to `HappyProperty` (Module2), hoisted to the module node (Module3).
> - **Expansion** (B2/B3): `Module3._expand_happy_properties` injects a per-site
>   `#@ check` (point: `i < LO || i >= HI`; slice `[a:b]`: `b <= LO || a >= HI`;
>   augmented subscript = point) as synthesized `CheckPoint`s — reusing the Stage-A
>   `ProofAssert → check {}` pipeline, **no new IR/backend**. Each check carries an
>   `origin` comment naming the HAPPY + site.
> - **Writer identity** = **A** (static per-function specialization via the `except`
>   set). **Trust boundary** = **C**, realized in **hoare** form: a new field-subscript
>   contract surface `self.<field>[i]` (Module2/5; the existing hoare subscript-of-record
>   lowering in module6 needed no change) lets a non-exempt `\trusted`/`\abstract` writer
>   carry `#@ \preserves`, which synthesizes the assumed region-preservation `ensures`
>   `\forall i; (LO <= i and i < HI) ==> self.<field>[i] == \old(self.<field>[i])`. Its
>   absence is a hard error. *(Amends B1a's "option C is typed/store-only": in hoare it is
>   a region-preservation postcondition, not an `assigns` frame.)*
> - **Validation** (Module4): bad `except` name → hard error; inert field → warning.
> - **Corpus**: `0459` (proves), `0460` (in-region write fails at its site), `0461`/`0462`
>   (trusted boundary with/without `#@ \preserves`). 5-surface doc-coherency green.
> - **Worked target** (`unix-filesystem/UnixInodeFileSystem.py`): the single
>   `#@ happy inode_integrity` declaration **auto-injects 10 per-site checks** across the
>   non-exempt methods (14 sites total incl. the 2 exempt writers) — the N→1 ROI,
>   confirmed via `--no-proof`. Full multi-site proof is **deferred**: the property is
>   semantically true but ~4 sites need bounds the methods don't yet state (e.g.
>   `_set_bitmap` writes `[0,512)` but only requires `byte_offset < 131072`; the bitmap
>   index also hits the same bitwise-arithmetic hardness `_get_bitmap` already discharges
>   via a Coq axiom). Strengthening those contracts is fs-verification work tangential to
>   the meta-pass and is left as a follow-on; the annotation is therefore not committed to
>   the flagship file (which stays green). The mechanism itself is fully proven by the
>   corpus above.

### B0 — Soundness spike (the analysis half of the gate; before any surface work)

A read-only analysis producing a written soundness argument (or a hole list). Establish,
against the real pipeline:
1. **Single write-shape** — confirm the model's write-shape is the **sole** way a body mutates
   the shared state: `int_mem := Map.set …` (typed/store) or `self.field[i] = …` (hoare shared
   field). Audit Module5/6 emission (`ArraySet`, `FieldAssign`, `FieldAugAssign`, ghost/heap
   writes). A hidden path is the unsoundness to close first (theorem clause 1's linchpin).
   *(Gate result on `UnixInodeFileSystem.py`: `self.disk[...]` is the sole path — 14 sites.)*
2. **Statability of `φ(ℓ)`** — region membership / disjointness is expressible: plain **index
   arithmetic** in `hoare`, or **address arithmetic** + `\valid`/`\separated` in `typed`.
3. **Trust boundary is the only gap** — enumerate bodyless functions (`\trusted`/`\abstract`/
   external); decide their effect-declaration form (theorem clause 2); confirm it's bounded to
   the already-trusted stub surface.
4. **Coverage mechanism** — the expansion pass can reach **every** body-verified function.

If 1–4 hold, Stage B is sound by the theorem; otherwise scope B1 to a stated, **loudly-
diagnosed** boundary rather than claiming whole-program soundness.

### B1 — Surface + parse (hoare-first / shared field; per-function; no `\caller`)

A module-level HAPPY over a context (`\writing`/`\reading`) and a location predicate `φ(ℓ)`
(index for a shared field, address for a heap). The
property is **per-function** (a function-modular verifier proves each function not knowing its
callers — so there is **no `\caller`**; "only `encrypt` writes secret" = "in every function
other than `encrypt`, every write is outside `secret`"). Working directive name `#@ happy …`
(concrete syntax open); parse to `HappyProperty(context, predicate, region)`; Module4
validates meta-variable usage (`\written`/`\read` only in their context).

### B1a — Enforcing writer-identity: the option space (`\caller` is the wrong axis)

The property restricts the **writer** (the function performing the write), whose identity is
**known statically** at expansion — so `\caller` (who invoked me) is a category error here;
it's needed only for a *call-chain-dependent* property. Six ways:

- **A. Static per-function specialization** *(plan's choice for bodies).* The expander knows
  each function's name; inject `check { ¬in_region(a, secret) }` at every write site of every
  function **except the exempt set** `{encrypt}`. The `current_fn = encrypt` disjunct resolves
  statically — no `\caller`, no new state; sound by universal coverage. Simplest; modular.
- **B. Capability / permission ghost token.** A `#@ ghost` capability the write `requires` and
  only `encrypt` holds. Compositional; threads through callers. *For delegable permissions,
  not a fixed allowlist.* Heavy ghost threading.
- **C. Effect / frame contracts per function** *(plan's choice for the trusted boundary).*
  Each function **declares** its write region (region-typed `assigns`); meta checks every
  non-`encrypt` frame is disjoint from `secret`. Composes through **callee contracts**, so it
  covers **bodyless trusted/abstract** functions (declare a frame, no body). Needs precise
  `assigns` (typed/store only).
- **D. Encapsulation / region ownership (structural).** Make `secret` a private field whose
  only mutator is `encrypt`; holds by construction (only `encrypt`'s body has the
  `FieldAssign`). Reduces to a coverage check; needs that structure.
- **E. Whole-program effect closure (non-modular).** Transitive "writes-secret?" summaries
  over the call graph. **Subsumed by A** (universal coverage gives the transitive guarantee);
  reach for it only if coverage is unattainable.
- **F. Literal `\caller` via ghost caller-tag threading.** Faithful to ACSL `\caller` but
  invasive and unnecessary here (writer ≠ caller). Reserve for call-chain-dependent properties.

**Decision:** flagship integrity = **A (bodies) + C (trusted boundary)**. D when `secret` is
naturally an encapsulated field; B for delegable permissions; E/F usually unnecessary. Keep
`\caller` out of the surface until a call-chain property demands it.

### B2 — Direct-site identification (per function)

Enumerate the **direct** write sites (`\writing`) / read sites (`\reading`) emitted per
function in `typed`/`store`. Per the theorem, **only direct sites need enumerating** —
indirect writes are covered by other functions' direct sites. This is the mechanical pass,
now *justified* by the theorem rather than assumed complete.

### B3 — Expansion to Stage-A obligations (with the trust-boundary clause)

- **Body-verified functions:** at each direct write site, inject a Stage-A obligation
  instantiating `\written`→`a` (or `\read`→`a`). **The emitted primitive is context-determined
  (§B3a), not a default**; the flagship `\writing` integrity property uses `check`.
- **§B3-trust — trusted/abstract functions:** require an **effect declaration** bounding heap
  writes (frame/`assigns` extended with a disjoint-from-`secret` obligation), discharged or
  assumed at the trust boundary. Theorem clause 2 — the only place a per-function effect
  contract is needed, on the already-trusted stub surface.

### B3a — Which primitive to inject (`check` vs `assert`): context-determined, not a default

`#@ assume`/`requires` introduces an **axiom** — making `P` a downstream hypothesis is sound
only if `P` is *guaranteed* at every reaching point. So "may I assume it afterward?" = "is it
**maintained** or only **checked pointwise**?" — exactly MetAcsl's weak/strong-invariant
distinction. The emitted primitive **follows the HAPPY's context**:

| Context | Emission | Assumed downstream? |
|---|---|---|
| `\writing` / `\reading` (per-site legality) | per-site `#@ check { φ(a) }` | no — a single write's legality isn't reusable (flagship case) |
| `weak_invariant I` (boundary) | per-function `requires I` + `ensures I` — **existing primitives** | yes, at boundaries; transiently breakable inside |
| `strong_invariant I` (continuous) | `requires I` at entry + `#@ assert I` after **every** affecting write | yes, continuously |

Options: (1) **context-determined emission** (the fix); (2) per-HAPPY `check`/`assert`/`assume`
override; (3) decouple `check`-at-obligation-site from `assume`-at-use-site *with the
side-condition that every `assume P` is backed by a `check`/`assert P` at all reaching points*;
(4) **conservative v1 — `check`-only**, ship `\writing`/`\reading` and defer invariant contexts
(the flagship is `\writing`, so the default is already correct — **recommended sequencing**);
(5) reuse **class invariants** for record-scoped strong invariants; (6) reuse the
loop/function-invariant discharge pattern for the maintained case.

### B4 — Worked property + corpus (typed model first; the spike half of the gate)

A multi-function **typed-model** demo where the integrity HAPPY holds (incl. `encrypt`, the
legitimate writer); a **negative** demo where a non-`encrypt` function writes into `secret` and
its injected `check` **fails at that function's site**; and a **trusted-stub** demo exercising
§B3-trust (a `val` whose effect declaration is required — and whose absence makes the property
fail, proving clause 2 has teeth). Confidentiality (`\reading`) and any `hoare`-expressible
variant follow once integrity lands.

### B5 — Docs + gates

5-surface doc-coherency for the HAPPY directive(s); reference-corpus pairs incl. the negative +
trusted-stub demos; determinism (ordered site enumeration); attribution (each injected `check`
names the HAPPY + site, so a failure points to the property and the offending write).

---

## Cross-cutting discipline (every phase)

Verify-before-lower; containment + corpus byte-identical differential; negative-test-for-teeth;
determinism + attribution; **0 `\trusted`** preserved (bodies); per-feature gates (SY3
mod-index, `doc-coherency --check`, `audit-pycsl-language`, `rag-build`/`verify`, full
`run-reference-tests.sh`).

## Verification (end-to-end)

1. **Stage A:** `pycsl` proves a true `#@ assert`/`check`; a false one FAILS; `check` leaves no
   downstream hypothesis (a contrived test that closes only if `assert` did); act-migration
   corpus (`0454`–`0456`) unchanged in verdict; non-assert corpus byte-identical (Module1) +
   emission-identical (old vs new).
2. **B0 / gate:** the written soundness argument holds (sole `Map.set` path; `φ` statable;
   trust boundary bounded) and the hand-proof spike proves the target HAPPY on
   `UnixInodeFileSystem.py` — or its holes are scoped with a loud diagnostic / the YAGNI exit
   is taken.
3. **Stage B:** the typed-model integrity demo proves; the violating demo **fails at the
   offending function's own site** (message names HAPPY + site); the trusted-stub demo proves
   only with its effect declaration (and fails without it); non-meta corpus unaffected; the
   N→1 annotation ROI is recorded.

## Open decisions

Resolved: model order (**hoare-first for a shared instance field** — the gate proved this
works and is simpler than typed/store; heap `Map.set` only when the property spans a true
heap); composition (**theorem: universal coverage + per-site obligations + trusted-boundary
effect declaration**); the `\caller` mismodel
(**per-function property**; option space A–F in §B1a; flagship = A + C); `check`-vs-`assert`
(**context-determined per §B3a**; flagship `\writing` = `check`; invariant contexts deferred);
the **use-case gate** (concrete `UnixInodeFileSystem` integrity HAPPY + hand-proof spike + N→1
ROI, with a YAGNI exit).

Resolved by the executed gate: the sole-write-path question — for the `hoare`/shared-field
framing, `self.disk[...]` is the sole mutation path (14 sites, grep-confirmed); the index-level
obligation is expressible and provable; the gate PASSED.

Still open (for the meta-pass build): the concrete HAPPY `#@` syntax (a `happy`/`act`-style
block vs a flat directive); the exact effect-declaration form for trusted writers (extend
`assigns`, or a new `writes_outside` clause); and — *if* a future property spans a true heap —
the typed/store `Map.set` sole-path check (the hoare gate above does not settle that case).
