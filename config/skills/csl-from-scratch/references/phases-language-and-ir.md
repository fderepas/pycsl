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

**Whole-program sugar is the same move.** Cross-cutting meta-properties
(PyCSL's **HAPPY** — the equivalent of MetAcsl's HILAREs) *expand* one
high-level requirement into many ordinary per-site obligations — surface →
existing primitives → 0-`\trusted`, just at program scope instead of function
scope. See [`meta.md`](../../../../meta.md).

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
