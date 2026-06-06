# Plan: typed & bounded quantification in PyCSL (implementation)

Code-ready implementation plan for `quantification-spec.md`. The spec says *what must hold*; this
says *what to change, in what order, behind which gate*. It reshapes the spec's P1–P4 phasing onto
PyCSL's actual pipeline and the project's gating discipline (`pycsl-how-to-develop` §8):
**demand-driven (FAIL-driver first), phased, reuse existing machinery, every accepted contract
type-sound at the WhyML level, induction routed through the existing `#@ proof` import.**

House style: re-derive `file:line` by symbol — anchors below are the symbols, not frozen line numbers.

---

## Context & verdict

**The restriction is one line, the fix is a node.** PyCSL's quantifier lowering is
`expressions.py::_expr_to_whyml`'s `Forall`/`Exists` arm, which emits
`forall {expr['var']} : int. …` / `exists … : int.` **unconditionally** — the binder type is
hard-wired to `int`. The grammar (`Module2_Parser.py`, the `forall_expr`/`exists_expr` productions
in the `?expr`, `?impl_rhs`, `?or_rhs`, `?and_rhs` alternations) accepts only a bare `CNAME` binder,
and the `Forall(var, body)` / `Exists(var, body)` nodes carry no type. So `\forall j; P(j)` with `j`
meant as a `#@ datatype` value lowers to `forall j : int`, then applies datatype observers to an
`int` — **front-end green, Why3 type-error.** This is the false-green hole the spec names.

Why3 is first-order *polymorphic* logic: a binder may range over any term type. The capability is
one layer down; this plan lifts it into the surface in four gated phases, each adding exactly the
binder-type vocabulary the phase's driver needs and no more.

**Verdict.** Add a typed/bounded binder to the quantifier node and thread one binder-type through
Module4 (well-formedness) → Module5 (IR) → Module6 (emit). **Reuse** the datatype/record type
emission, the `#@ proof` axiom-import path for induction, and the existing set operators; **gate**
each binder-type class behind a real driver; **reject** (don't silently `int`-default) an
unresolved or higher-order binder. Legacy integer quantifiers stay **byte-identical** (the gate).

---

## Gate A — the demand-driver (write and commit FIRST, `# pycsl-expected: FAIL`)

The flagship is the spec's own §11 type-soundness hole: a quantifier whose binder is a declared
`#@ datatype`, which today emits `forall … : int` and is **rejected by Why3's typechecker**, not by
PyCSL. Commit it FAIL-first; it flips to PASS at P1.

```python
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
_ = 0  # anchor

#@ datatype Color = Red | Green | Blue
#@ ensures \forall c: Color; rank(c) >= 0 and rank(c) <= 2
def classify(...) -> ...: ...
```

Plus the per-phase negative twins (each committed `# pycsl-expected: FAIL`, each *staying* failing
for its own reason): an **unresolved binder type** (`\forall x: Bogus; …` → hard Module4 error, not
`int`), a **legacy datatype mis-use** (`\forall j; is_ctor(j, Red)` — bare binder used as a datatype
value → now an error, was a silent mis-lowering), and the phase-specific gap/overlap/missing-lemma
twins (§ Drivers). Add all to `test-suite/corpus/pycsl-reference/` (next free number — currently the
high-water mark is **0553**, so quantification starts at **0554**; docstring + `# pycsl-flags:` +
`_ = 0 # anchor`), per the reference-corpus requirement.

---

## The one structural change (shared by all phases)

**The typed-binder node.** `Forall`/`Exists` (in `Module2_Parser.py`) gain two optional fields:

```python
@dataclass
class Forall(QuantifierNode):
    var: str
    body: CSLNode
    binder_type: Optional[str] = None   # None ⇒ legacy int (BACKWARD COMPATIBLE)
    domain: Optional[CSLNode] = None    # the `in S` term, or None
@dataclass
class Exists(QuantifierNode): ...        # same three new fields
```

`binder_type=None` ⇒ the legacy path, emitting `forall var : int.` **verbatim** — this is what keeps
every existing quantifier byte-identical. Only an explicitly-typed or bounded binder takes the new
path. The IR (`Module5_IREmitter._csl_to_ir` quantifier case) carries
`{"type":"Forall","var":…,"body":…,"binder_type":…,"domain":…}`; Module6 reads `binder_type`/`domain`
and falls back to `int` when both are absent.

**Grammar (Module2).** The binder production changes in **all four** quantifier sites (`?expr`,
`?impl_rhs`, `?or_rhs`, `?and_rhs` — they each inline the `\forall CNAME ; expr` form). Extract a
shared `quant_binder` rule to avoid four-way drift:

```
quant_binder : CNAME                               -> binder_plain      // legacy int
             | CNAME ":" quant_type                 -> binder_typed
             | CNAME "in" expr                      -> binder_in         // int element, bounded
             | CNAME ":" quant_type "in" expr       -> binder_typed_in
quant_type   : "int" | "bool" | "str" | "float" | CNAME    // CNAME = datatype / class name
             | "set" "[" quant_type "]"
```

The desugaring of `in` is done at lowering (§ per-phase), **not** in the grammar, so the bound term
keeps its source span for diagnostics (open question §12.4 — defer span preservation, but don't
desugar so early it's impossible later). Transformer `forall_expr`/`exists_expr` build the node from
the `quant_binder` parse; the legacy `binder_plain` keeps `binder_type=None`.

**Multi-binder note (spec §3 `binders ::= binder ("," binder)*`).** The current grammar is
single-binder. Multi-binder is additive sugar — `\forall x: T, y: U; P` ≡ nested
`\forall x: T; \forall y: U; P`. Desugar in the transformer to nested nodes; keep P1 single-binder
and add the comma form in P3 (where set membership makes it useful), gated on its own driver.

---

## Phasing (each gated on its driver + full corpus sweep + byte-diff before the next)

### P1 — Finite sum types / enums (LOW risk; no instantiation, no induction)
The flagship's home. Delivers a typed binder over a **declared `#@ datatype`** plus the
finite-conjunction fast-path.

- **Module4** (`_validate_contract` / the quantifier walk): resolve `binder_type` against the
  module's `#@ datatype` names (already collected — `node.csl_datatypes` / the datatype registry) and
  the scalars. Unknown name ⇒ hard `PyCSLSemanticError` (spec §5.1, no silent `int`). Type-check the
  body under the binder (spec §5.3): a datatype binder may appear only in equality and pure
  observer/projection calls (`\is_ctor`/`\payload` and `assigns \nothing` functions) — reject
  arithmetic on a datatype binder.
- **Module6** (`_expr_to_whyml` Forall/Exists arm): when `binder_type` resolves to a lowered
  datatype `d`, emit `forall var : d. P'`. Ensure the type `d` is already emitted/`use`d (it is —
  `_emit_type_decls` runs before functions; quantifier binders need no new `use`).
- **Finite expansion fast-path (spec §8.3):** when the datatype is **all-nullary** (an enum) and the
  body has no payload binder, expand `\forall x: E; P(x)` to `(P(C1) /\ … /\ P(Cn))` (one conjunct
  per constructor) — discharged with **no** instantiation search. Constructors with payloads fall
  back to the general `forall x : e` form. Reuse the constructor registry (`_constructors`, the same
  one `\is_ctor`/`\payload` use). `\exists` over an enum expands to the disjunction.
- **Gate / drivers:** flagship 0554 (`Color`/`rank`) flips to PASS; negative twins — unresolved
  binder type, bare-binder-as-datatype — stay FAIL.

### P2 — Recursive datatypes (MEDIUM; induction obligations)
`forall x : d` over a recursive / mutually-recursive datatype (corpus 0533/0534 are eligible binder
types). The binder-type resolution is the same as P1; the **discharge** is the work.

- **Surface:** `#@ by induction on <binder>` (a new clause-level annotation, parsed like the other
  `#@` markers; weave onto the contract). It routes the obligation to Why3's `induction_ty_lex`
  transformation when applicable, **else** to an imported Rocq/Lean lemma via the existing `#@ proof`
  mechanism (`_AXIOM_REGISTRY` / the namespace-audited reconciliation manifest) — **no new trust**
  (spec §8.1/§8.2). A bare recursive-datatype `\forall` with no induction annotation and no
  first-order proof is left as an honest unproven goal (it fails, as it should).
- **Module6 / proof engine:** emit the goal as today; when `#@ by induction on x` is present, drive
  the Why3 transformation in the proof harness (the engine already invokes Why3 — add the
  transformation step for the tagged goal), or splice the imported axiom (the A4 mirror-involution
  pattern, 0542, is the template: imported lemma quantified over a recursive datatype, emitted AFTER
  the type decls).
- **Gate / drivers:** a tree/forest "fold equals its spec for all trees" PASS backed by an induction
  lemma; a FAIL twin with a **missing/unreconciled lemma** (stays FAIL — the audit rejects it,
  proving the boundary has teeth).

### P3 — Sets & bounded quantification (MEDIUM; trigger brittleness)
`set[T]` binder type, `x in S` desugaring, real finite-set theory, trigger inference.

- **`use set.Fset`** (new preamble import, scanned-in only when a quantification context needs it —
  keep it behind a `needs_fset` flag like `needs_seq`, so non-set files stay byte-identical). Map, in
  **quantification context only**, `member`→`Fset.mem`, `\set_card`→`Fset.cardinal`,
  union/inter/diff→the `Fset` operators. The existing `map`-as-set ghost encoding
  (`SetMem`/`SetCard`/`SetUnion`… in `_EXPR_DISPATCH`) stays for mutable ghost state; this adds the
  Fset *theory* view the solver needs for membership lemmas.
- **Desugaring (spec §3 table):** `\forall x: T in S; P` ⇒ `forall x : t. Fset.mem x S' -> P'`;
  `\exists … in S` ⇒ `exists x : t. Fset.mem x S' /\ P'`. Done in the Module6 Forall/Exists arm from
  the node's `domain` field; Module4 checks `S : set[T]` (spec §5.4).
- **Trigger inference (spec §7):** for each emitted quantifier, select a trigger from the body's pure
  function calls / field accesses / membership terms mentioning every bound var; refuse
  interpreted-only patterns (`+`,`*`,`and`, nested quantifiers) to avoid matching loops. Emit Why3
  `[pattern]` syntax. `#@ trigger f(x), g(x)` overrides. Module4 warns when no admissible trigger
  exists ("valid but never instantiated").
- **Gate / drivers:** set membership + cardinality PASS; a **missing-trigger** FAIL twin (warns and
  fails to instantiate); a trigger-override regression asserting loop-free pattern selection.

### P4 — Classes / objects (HIGH; deferred runtime heap)
Value-mode and ghost-collection-mode object quantification — **no runtime heap** (spec non-goal §2).

- **Value mode:** `\forall o: C; inv_C(o) ==> P(o)` ⇒ `forall o : c. inv_C o -> P'`, where `c` is the
  class record (already emitted) and `inv_C` is the class invariant **auto-inserted as the
  antecedent** (spec §6.4 — a raw `forall o : c` ranges over invariant-violating shapes). Reuse
  `type_decl.class_invariants`.
- **Ghost-collection mode:** `\forall o: C in registry; P(o)` via the P3 `Fset` membership path with
  element type `c` — the recommended "all live objects" form (an explicit ghost `set[C]`, not a
  heap). Open question §12.3 (decidable equality on `c`) gates which classes may be set elements:
  records with `str`/`real` fields need the documented equality story first → reject as set element
  until then.
- **Gate / drivers:** an account-collection invariant PASS (value mode + ghost-collection mode); a
  FAIL twin omitting the invariant guard (raw `forall o : c` admits a bad shape → unprovable).

---

## Reuse map (what already exists — do NOT reinvent)
- **Datatype/record type emission + `use`:** `preamble.py::_emit_type_decls` / `_fmt_variant`; the
  binder type is whatever this already emits (`type d`, `type c`). Constructor registry
  `_constructors` (drives `\is_ctor`/`\payload`) → drives finite expansion (P1).
- **Induction / no-new-trust:** the `#@ proof` axiom-import path (`_AXIOM_REGISTRY`,
  `_AXIOM_FUNCTIONS`, post-type-decl emission, namespace audit) — the 0542 mirror-involution over
  recursive `Json` is the exact template for a P2 imported lemma.
- **Set operators:** the `Set*` `_EXPR_DISPATCH` handlers (ghost map-as-set) stay; P3 adds the `Fset`
  theory view alongside.
- **Quantifier walk / scope:** `Module4_SemanticAnalyzer.extract_variables` + the `Forall`/`Exists`
  child-map already traverse the body; extend, don't rewrite.
- **Preamble feature flags:** the `needs_seq`/`use seq.Seq` pattern → `needs_fset`/`use set.Fset`.

---

## Gates (per phase)
- **Byte-diff (additivity):** legacy `\forall i; …` (binder_type=None) emits **byte-identical**
  `.mlw` across the whole corpus (`PYTHONHASHSEED=0 --no-proof --keep-mlw`, honor `# pycsl-flags:`,
  all four memory models). New typed/bounded binders emit new, verified WhyML. This is the central
  safety property — the typed-binder node MUST be inert when `binder_type=None`.
- **Type-soundness gate (spec §11, the headline):** every accepted typed quantifier must produce
  WhyML that Why3 **typechecks**. Add `bin/why3-typecheck-corpus.sh` running `why3 prove` to first
  failure on type errors (or a `--type-only`-style invocation) over the quantification drivers,
  independent of SMT discharge — closing the false-green hole directly.
- **Full corpus sweep**, zero new regressions, after each phase.
- **Positive + negative driver** per phase (PASS + FAIL twin); negatives stay failing.
- **No new trust:** a typed quantifier is never an axiom; induction obligations route through the
  audited `#@ proof` path only. 0 `\trusted` introduced.

## Drivers (per phase, next free numbers from 0554)
- **P1:** 0554 enum `\forall c: Color; rank bounds` (PASS) · unresolved-binder-type (FAIL) ·
  bare-binder-as-datatype (FAIL) · finite-expansion enum coverage (PASS).
- **P2:** recursive tree fold-vs-spec with induction lemma (PASS) · missing/unreconciled lemma (FAIL).
- **P3:** `set[int]` membership + cardinality (PASS) · missing-trigger (FAIL) · trigger-override
  regression (PASS).
- **P4:** account-collection invariant, value + ghost-collection mode (PASS) · missing
  invariant-guard (FAIL).

Each driver: docstring + `# pycsl-flags:` + `_ = 0 # anchor`; FAIL twins committed FAIL-first.

## Out of scope / boundaries (documented, not faked)
Higher-order quantification (binding predicates/functions) — rejected at Module4 (spec §2, §5.5).
Runtime-heap "all allocated objects of C" — deferred to `store`/`typed` models (spec §2, open Q
§12.1). Coinductive/infinite datatypes. Set elements with `str`/`real`-payload datatypes until the
decidable-equality story is documented (open Q §12.3).

## Suggested order
P1 (the flagship, low risk, closes the false-green hole) → P2 (induction routing, reuses the 0542
bridge) → P3 (sets + triggers) → P4 (objects). Stop at the YAGNI exit if a phase's driver doesn't
materialize; P2–P4 each start only on a real driver.

## Critical files (re-derive line numbers by symbol)
- `Module2_Parser.py` — `Forall`/`Exists` nodes (+`binder_type`/`domain`); the four quantifier
  productions (`?expr`/`?impl_rhs`/`?or_rhs`/`?and_rhs`) → a shared `quant_binder` rule;
  `forall_expr`/`exists_expr` transformers; the new `#@ by induction on` / `#@ trigger` decls.
- `Module3_Weaver.py` — weave `#@ by induction on` / `#@ trigger` onto the contract clause.
- `Module4_SemanticAnalyzer.py` — `extract_variables` / quantifier walk: typed-binder
  well-formedness (spec §5 rules 1–6), unresolved-type hard error, trigger-absence warning.
- `Module5_IREmitter.py` — `_csl_to_ir` quantifier case carries `binder_type`/`domain`.
- `module6_whyml/expressions.py` — `_expr_to_whyml` Forall/Exists arm: typed emission, `in`→`Fset.mem`
  desugar, finite-conjunction expansion, trigger emission. The hard-wired `: int` is here.
- `module6_whyml/preamble.py` — `needs_fset`/`use set.Fset`; ensure binder datatype/record types are
  emitted before use; the `#@ proof` axiom path for P2 induction lemmas.
- `bin/` — new `why3-typecheck-corpus.sh` (type-soundness gate); reuse the proof-sweep + byte-diff
  harness.

## References
Spec: `quantification-spec.md`. Templates: 0542 (imported lemma over a recursive datatype — P2),
0533/0534 (mutually-recursive datatypes — eligible binders), the `\is_ctor`/`\payload` projector
machinery (datatype observers in contracts). Canon: Why3 (ESOP 2013), Dafny/Verus trigger selection.
```
