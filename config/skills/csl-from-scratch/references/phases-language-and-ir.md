# Phases 4–5 — Annotation language + IR tightening

Once the prototype verifies and the 6-module pipeline exists,
formalize the annotation language itself and tighten the IR
schema. Load when designing the contract surface or hardening
the Module 5↔6 boundary.

---

## Phase 4 — *CSL reference guide + traceability matrix

> **Squeeze → S3 (annotation traceability).** A second
> traceability matrix squeezes the annotation language: every
> `#@` form maps to a test and an IR node. Drift between the
> written reference and the implementation is a build-time error.

Now formalize the *annotation language* itself in writing.

**Three documents**:

1. **Concrete syntax reference** — every `#@` form's grammar.
   Cite
   [`docs/pycsl-concrete-syntax-reference.md`](../../../../docs/pycsl-concrete-syntax-reference.md)
   as the shape this takes.
2. **Static semantics reference** — typing rules, scope
   resolution, well-formedness conditions. Cite
   [`docs/pycsl-static-semantics-reference.md`](../../../../docs/pycsl-static-semantics-reference.md).
3. **Dynamic semantics reference** — the intended runtime
   meaning of each contract form. Mostly self-evident but
   exception model + ghost code need explicit semantics.

**Second traceability matrix**: each annotation form → reference
test + verdict + IR shape. Add ~150-300 new tests covering
every contract form. Numbering continues monotonically from the
host-language corpus.

**Pattern**:

```
| Annotation form          | Test ID | IR node          | Verdict |
|--------------------------|---------|------------------|---------|
| requires <bool>          | 0201    | requires_clause  | PASS    |
| ensures <bool>           | 0202    | ensures_clause   | PASS    |
| ensures \result == ...   | 0203    | result_subst     | PASS    |
| assigns x[lo..hi]        | 0205    | assigns_region   | PASS    |
| assigns \nothing         | 0206    | frame_nothing    | PASS    |
| ghost x : int = e        | 0210    | ghost_decl       | PASS    |
| loop invariant <bool>    | 0220    | loop_invariant   | PASS    |
| loop variant <expr>      | 0221    | loop_variant     | PASS    |
| \forall k; P             | 0230    | quantifier       | PASS    |
| \old(x)                  | 0240    | old_operator     | PASS    |
| \result                  | 0241    | result_ref       | PASS    |
| \at(x, label)            | 0250    | at_operator      | PASS    |
| raises Exc when P        | 0260    | raises_clause    | PASS    |
| no_exception E1, E2      | 0265    | no_exception     | PASS    |
```

**Anti-pattern to avoid**: writing the language reference *after*
the implementation has diverged. The traceability matrix forces
"every form in the grammar has a test in the corpus, and every
test in the corpus traces to a form" as a hard discipline.

---

## Phase 4b — Sugar: grow the surface by desugaring (not the TCB)

> **Squeeze → S3 still holds.** A sugar form is *not* exempt from traceability:
> it gets a test and a normative-surface entry like any directive. Its IR-node
> column simply reads `(desugars to …)` instead of naming a new node.

Not every new `#@` form needs its own IR node + backend case. A form that is
expressible in terms of forms you already have should be added as **sugar**: a
parser rule plus a **desugaring pass in the weaver** that lowers it to existing
primitives, leaving Module 5/6, the IR schema, and the formal-semantics mirrors
**untouched** — **0 `\trusted` preserved**.

Sugar adds **zero proving power** (by construction — it lowers to things you can
already prove), so it earns its place only through **ergonomics**: readability,
or a single source of truth that the hand-written expansion would duplicate. If
a host-language idiom is rare, *document the raw idiom instead of adding sugar* —
TCB-minimalism is the default.

**Worked example — `act` (guarded contract cases; PyCSL's ACSL-"behavior").**
The surface is a Pythonic block; the weaver desugars it:

```
#@ act b: given A ; ensures E   →   ensures \old(A) ==> E
#@ act b: given A ; requires R  →   requires A ==> R
#@ complete b1, b2              →   ensures \old(g1) || \old(g2)
#@ disjoint b1, b2              →   ensures not (\old(gi) && \old(gj))   (per pair)
```

Each guard `A` is written **once** (its `given`) — the DRY win that justifies the
construct, since the raw `ensures \old(g) ==> …` idiom repeats every guard across
its case, the completeness disjunction, and each disjointness pair. See
[`act.md`](../../../../act.md) and `annotations.md` §2.1.15.

**The discipline (each item is a real trap we hit):**

1. **Verify the target primitive's *actual* semantics before lowering onto it.**
   A statement `assert` may be a **prover no-op** (emitted and dropped) — it
   cannot discharge a goal. A "these cases are complete" claim is a **proof
   obligation** (an `ensures`/`assert`), *not* a `requires` (which is *assumed*,
   never proved — lowering completeness to it makes an incomplete set pass).
   Ask of every primitive: *proved, assumed, or dropped?*
2. **Contain the front-end change.** Gate the new parsing/folding on the sugar
   actually appearing, so non-sugar inputs are **byte-identical** — prove it with
   the corpus differential (this is the S-layer squeeze applied to the ingestor).
3. **Negative test — the sugar must have teeth.** A malformed or false instance
   (e.g. a case set with a gap) must *fail* verification; otherwise the sugar is
   cosmetic-and-wrong.
4. **Document on every normative surface.** A sugar form is still a directive:
   concrete-syntax, static-semantics, translational, README, and the canonical
   reference — its translational rule shows the desugaring, its traceability row
   names no new IR node.
5. **Determinism + attribution.** Desugar in source order (never via a `set`);
   carry the source construct's name through to emission so a proof failure names
   the original case — the prover only ever sees the desugared form.

---

## Phase 4c — Whole-program sugar: meta-properties that expand to per-site obligations

The same move scales to **program scope**. A cross-cutting meta-property (PyCSL's
**HAPPY** — the equivalent of MetAcsl's HILAREs) is one module-level declaration that
*expands* into many ordinary per-site obligations: surface → existing primitives →
0-`\trusted`, only now the expansion pass walks the **whole program** instead of one
function. The worked instance is region integrity over a shared array field
([`meta.md`](../../../../meta.md)):

```
#@ happy R: region LO .. HI writes self.f outside region except m1, m2
   →  at every write self.f[i]=… (point/slice/augmented) in every method ∉ {m1,m2}:
      inject  #@ check  i < LO || i >= HI    (slice [a:b]:  b <= LO || a >= HI)
```

It reuses the **statement-level `#@ check`** primitive (Phase 4b's first customer): the
meta-pass *synthesizes* `CheckPoint` nodes and attaches them exactly as a hand-written
`#@ check` would — **zero new IR/backend**, the obligation is parsed through the same
grammar so it is byte-identical to a hand-written one.

**The non-obvious part is soundness, and it is a *theorem*, not a hope.** The naïve
reading — "enumerate the syntactic writes to the protected name and check them" — is
**unsound**: it misses *indirect* writes (a callee mutates the field) and *aliasing* (a
local pointer to the field), and a CSL with no alias/effect/points-to analysis cannot
close either gap by inspection. Two design choices dissolve both:

1. **State the obligation at the location *actually written*** (the index/address in the
   write-shape `self.f[i]=…`), never at a syntactic name. Aliasing then cannot matter —
   the check constrains the concrete cell that is written, whatever name reached it; in a
   value-semantic model a local alias cannot mutate the shared field at all.
2. **Universal coverage replaces the call graph.** Inject the check into *every*
   body-verified function's own write sites. An indirect write through a callee is caught
   at **the callee's own site** — so cross-function reasoning, and the call graph, are not
   load-bearing. The only residual gap is **bodyless functions** (trusted/abstract): they
   carry an *effect declaration* (a region-preservation `ensures`) assumed at the trust
   boundary. Coverage of bodies + a declaration on the trusted surface ⟹ no execution
   violates the property. Write this proof down before building the pass.

**Traps we actually hit (all instances of Phase 4b's discipline, recurring at scale):**

- **The sub-feature may need a primitive you don't have.** The trusted-boundary
  declaration wanted `self.f[i]` and `\old(self.f[i])` *inside a contract* — but the only
  self-field-array form was `\length(self.f)`, and an `assigns` frame had **no teeth in the
  value-semantic model** (it is meaningful only in a heap model). "Verify the target
  primitive" (Phase 4b item 1) applies recursively: a meta-feature can bottom out on a
  missing real primitive. **Surface the gap and decide** (build the primitive, narrow
  scope, or defer) — do **not** silently emit a declaration with no semantic content.
- **Synthesize the trusted declaration; don't pattern-match a hand-written one.** Recognizing
  "did the author write an adequate preservation `ensures`?" is brittle *and* unsound (a too-
  weak guard slips through). Instead take a minimal opt-in marker (`#@ \preserves`) and have
  the tool **generate the canonical declaration**, so the guard always covers the full region.
  Absent the marker on a non-exempt bodyless mutator → hard error (the boundary has teeth).
- **A meta-property surfaces missing contracts — report honestly, don't fake the proof.** On
  the real worked target the one declaration injected its checks correctly, but several did
  not discharge: the property was *true* yet the underlying methods never stated the bounds
  it needs (a bitmap writer bounded only `< capacity`, not `< region_start`). That is the
  meta-property doing its job — exposing under-specified methods — but **closing those is
  separate verification work**. Demonstrate the expansion (the N→1 ergonomic win) without
  claiming an end-to-end proof you don't have; leave the target green.

---

## Phase 5 — Second refactor: tighten semantic analyzer + IR

> **Squeeze → S6 (IR schema, tightened).** The JSON schema
> becomes the hard contract between Modules 5 and 6. The
> semantic analyzer (Module 4) squeezes annotation inputs;
> the schema squeezes IR outputs. Together they close the
> "garbage in, garbage out" path.

After the language reference exists, retrofit Module 4 to
*enforce* every well-formedness rule from the static semantics
reference. Examples of rules that have to land here:

- `\result` only in `ensures`/`raises`/postcondition contexts.
- `\old(e)` only in `ensures`; `e` must reference a function
  parameter or class field, not a local.
- Frame condition variables must be in scope at function entry.
- Loop invariants well-typed under the loop's binding context.
- Quantifier variables don't shadow function parameters.
- Ghost variables can't be assigned by non-ghost code.

Tighten Module 5's output to a *JSON schema*. Cite
[`src/pycsl/ir_schema.py`](../../../../src/pycsl/ir_schema.py) as
the schema-validation pattern: `validate_ir(ir_data)` checks
every IR tree against the schema and fails fast on shape drift.

The schema becomes the contract between Modules 5 and 6. Phase 6
formalizes against this schema; Phase 7's cross-check operates
on terms derived from this schema.
