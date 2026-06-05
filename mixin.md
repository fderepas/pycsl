# Plan: disciplined mixin composition for PyCSL (self-hosting first)

Derived from `mixin-specification.md` and the review in
`mixin-specification-comments.md`. This plan keeps the spec's idea — make Python
mixin composition machine-checkable via a trait discipline — but reshapes it to
PyCSL's actual mixin reality and the project's gating discipline
(`pycsl-how-to-develop` §8): **demand-driven, tiered, minimal self-hosting
subset first, reuse existing machinery, defer the speculative parts.**

## Context & verdict

**Today.** PyCSL's own emitter is a facade composing many Python mixins
(`Module6_WhyMLTranspiler` ← `ExpressionEmissionMixin`, `StatementEmissionMixin`,
`PreambleEmissionMixin`, …; and after Part B, the sibling sub-mixins
`GhostCollectionOpsMixin`, `GhostSpecOpsMixin`, `ControlFlowStmtMixin`, the
`module5/` package). Composition is unchecked: handlers are reached by
`getattr(self, _EXPR_DISPATCH[t])` / `_STMT_HANDLERS[s]`, every mixin shares
facade state (`self.program_ir`, `self._in_spec`, `self._dict_locals`, …), and
nothing verifies that a sibling's required helper exists or that two mixins don't
silently collide. When PyCSL annotates *its own* source (the self-hosting goal,
`src/self-annotate/`), there is **no surface** to express "this handler mixin
provides `_handle_map_get_expr`, depends on the core's `_e`/`_deref`, and shares
`program_ir`" — so the facade can't be verified compositionally.

**The spec's gap.** Its clean model assumes **disjoint owned fields** and
**abstract `requires_method` holes**. PyCSL's mixins are the opposite: maximally
**shared mutable state** and **concrete cross-mixin helper** dependencies, with
**zero method-name conflicts and no diamonds**. So the spec's heavy machinery
(`resolve`/`exclude`, diamond linearization) targets code PyCSL does not contain,
while the part PyCSL *needs* (shared-state-aware composition of conflict-free
mixins) is exactly the part the spec under-specifies.

**Verdict.** Build the **minimal subset that makes PyCSL's own facade mixins
checkable**, grounded in a self-hosting demand-driver; **reuse** the abstract-op,
class-record, and referential-transparency machinery PyCSL already has; **gate**
the conflict/diamond features behind real drivers; **reject** (don't fake) the
introspection patterns and the contract shapes PyCSL can't discharge.

---

## Gate A — the demand-driver (write and commit FIRST, `# pycsl-expected: FAIL`)

A verification-grade PyCSL file that **fails today only because mixin composition
is unexpressible**, and **passes** when Tier 1 lands. It must be a faithful
miniature of PyCSL's *own* mixin shape (the self-hosting target), not a textbook
toy:

```python
#@ mixin
class CoreEmit:
    #@ shared_state program_ir: int          # the shared facade state (abstracted)
    #@ provides emit
    #@ ensures \result >= 0
    #@ assigns \nothing
    def emit(self, x: int) -> int:
        return x if x >= 0 else 0

#@ mixin
class MapOps:                                  # a sibling handler mixin
    #@ depends_method emit: (self, x: int) -> int   # concrete dep on a sibling, not an abstract hole
    #@   ensures \result >= 0
    #@ provides handle_get
    #@ ensures \result >= 0
    #@ assigns \nothing
    def handle_get(self, k: int) -> int:
        return self.emit(k)                    # cross-mixin call resolved by composition

#@ compose_from CoreEmit, MapOps
class Facade:
    #@ ensures \result >= 0
    #@ assigns \nothing
    def run(self, k: int) -> int:
        return self.handle_get(k)
```

The flagship is backed by one driver per Tier-1 operation (see Verification), and
a **negative** driver per rejection rule (committed `# pycsl-expected: FAIL`,
stays failing): a missing provider, an undeclared field write, a silent method
collision. Add all to `test-suite/corpus/pycsl-reference/` (next free number,
docstring + `# pycsl-flags:` + `_ = 0 # anchor`), per the reference-corpus
requirement.

---

## The two design decisions the spec must resolve (and this plan fixes)

### D1 — Shared facade state vs owned fields
PyCSL mixins share state; the spec's "no two mixins touch the same field without
resolution" would flag the whole facade. **Resolution:** split the field model.

- `#@ touches_field <name>: <type>` keeps its spec meaning for an **owned** field
  (at most one mixin may own a given name; two owners → conflict → resolve, Tier 2).
- `#@ shared_state <name>: <type>` declares a field as **deliberately shared**
  facade state. Multiple mixins may `reads`/`writes` it; it is **not** a conflict.
  Soundness is recovered the PyCSL way — shared state already flows through the
  record model and `assigns`; a write to shared state must appear in the method's
  `assigns` (existing check), and the composed facade carries the conjunction of
  all mixins' invariants over it. This maps the trait model onto PyCSL's *actual*
  facade-with-shared-state pattern instead of fighting it.

### D2 — Concrete cross-mixin helpers vs abstract requirements
PyCSL siblings call concrete core helpers (`_e`, `_deref`, `_stmts_to_whyml`),
not abstract holes. **Resolution:** two relations, not one.

- `#@ requires_method m: <sig> ensures …` — an **abstract** operation the
  *composing class* must supply (the spec's case; Example 5/`Cached`).
- `#@ depends_method m: <sig> ensures …` — a **concrete** dependency on a method
  some *sibling mixin or the core* provides. Composition resolves it against a
  real provider and checks the provider's contract **refines** the declared one
  (behavioral subtyping). This is exactly how PyCSL's facade actually composes.

Both are *modeled the same way at verification time*: the declared contract
becomes an **abstract `val`** (the abstract-op / val-bridge pattern PyCSL already
emits) against which the mixin is verified once; composition then discharges
"concrete provider ⊑ abstract contract." No new proof theory — reuse
`abstract_ops.py` + the class-record model.

### D3 — Determinism/purity = referential transparency (don't reinvent `\old(\result)`)
The spec's `requires_method … ensures \result == \old(\result); assigns \nothing`
(Example 5 memoization) **is** PyCSL's referential transparency. Reuse the
existing RT predicate and UB-7.7 machinery (`_detect_purity`,
`_check_memoization_soundness`, now in `module5/memoization_rt.py`): a
`requires_method` may carry `#@ deterministic` / `pure`, checked by the existing
RT inference, instead of the non-standard `\old(\result)` encoding.

---

## Tiering (build Tier 1; gate the rest on real drivers)

### Tier 1 — the self-hosting subset (BUILD, demand-driven)
Enough to verify PyCSL's *own* conflict-free, diamond-free, shared-state facade:

- Directives: `#@ mixin`, `#@ provides <m>`, `#@ shared_state` (D1),
  `#@ touches_field` (owned), `#@ depends_method` (D2), `#@ compose_from`.
- Init-hook checking (D4 below): a composer's `__init__` must call each composed
  mixin's init-hook; a missing call is a **named** error, not just a downstream
  invariant failure.
- Verify each `#@ mixin` **once** against its abstract `depends_method`/
  `requires_method` interface (abstract `val`s); on `compose_from`, check each
  provider refines each dependency and that every dependency has exactly one
  provider.
- Emission: flatten the composed mixins' provided methods + owned/shared fields
  into the existing class-record + methods; conjoin class invariants.

### Tier 2 — conflict resolution (GATE on a real two-provider conflict)
`#@ resolve <m> from <Mixin>` / `#@ exclude <m> from <Mixin>` + the "two
providers of the same method ⇒ reject unless resolved" rule (spec Example 3).
PyCSL has **no** such conflict today (the dispatch tables guarantee unique
handler names), so this is YAGNI until a real composition needs it.

### Tier 3 — diamonds + full behavioral-subtyping refinement (SHELVE)
Multi-mixin diamonds with shared base linearization (Example 4) and the general
contravariant-arg/covariant-result refinement checker. PyCSL has no diamonds in
its facade; shelve behind both a driver **and** an SMT-feasibility spike for the
refinement check (Gate B).

### D4 — init-hook obligation
`#@ compose_from` synthesizes the obligation: the composer's `__init__` calls
each composed mixin's `__init__<mixin>` exactly once; emit a clear error if not
(rather than relying on an unestablished invariant to surface it later).

---

## Out of scope / soundness boundaries (documented, not faked)

- **Introspection mixins** (`dir`/`setattr`/`__getattribute__`/`__getattr__`
  cross-cutting concerns — the original Example 6): **rejected** with a UB-style
  error, never modeled. PyCSL has no sound model for runtime method patching.
- **`\old(<collection>)`** (whole-array/list pre-state): not supported today
  (only `\old(scalar)` / `\old(arr[i])`); mixin contracts must not rely on it —
  use a `\copy`/`\copy_range` ghost snapshot, the existing pattern.
- **`str(int)` / `\str(int)` content** in contracts: opaque under the string
  model (no code points); example contracts that reason about rendered-int
  content are not dischargeable and must be weakened or dropped.
- Tier 2/Tier 3 (conflicts, diamonds, general refinement): gated/shelved as above.

---

## Stages (each gated on its driver + the full corpus sweep before the next)

- **S0 — surface + parse.** Module1 prefixes; Module2 grammar + AST nodes for the
  Tier-1 directives; Module3 weave onto class/method nodes. Driver: the Gate-A
  file parses (`--no-proof`).
- **S1 — verify-once (mixin in isolation).** Module5/Module6: emit a `#@ mixin`
  class's `depends_method`/`requires_method` as abstract `val`s (reuse
  `abstract_ops.py`); verify each provided method against them. Driver: a mixin
  whose provided method proves against an abstract dependency.
- **S2 — composition check.** New Module4 pass (after MRO): unique-provider check
  per dependency; provider-refines-dependency check; `shared_state` vs owned-field
  classification (D1); init-hook obligation (D4). Drivers: the Gate-A positive
  flips to PASS; the negatives (missing provider / undeclared write / silent
  collision) stay `# pycsl-expected: FAIL`.
- **S3 — flatten + emit composed class.** Compose provided methods + fields +
  conjoined invariants into the existing record model; ensure **non-mixin corpus
  emission is byte-identical** (additive directives). Driver: the composed
  `Facade` proves end-to-end.
- **S4 — RT reuse + docs.** Wire `#@ deterministic`/`pure` on `requires_method`
  to the existing RT inference (D3). Update the τ-table / static-semantics /
  translational / annotations / annotate skill for the new directives; pass
  `doc-coherency --check` across all five surfaces.

---

## Gates (per stage)

- **Emission byte-diff:** the directives are additive — every non-mixin corpus
  file must emit **byte-identical** `.mlw` (`PYTHONHASHSEED=0 --no-proof
  --keep-mlw`, honor `# pycsl-flags:`, all four memory models). Mixin files emit
  new, verified WhyML.
- **Full corpus sweep**, zero new regressions, after each stage.
- **Positive + negative drivers** per rejection rule; the negatives must stay
  failing (the discipline has teeth).
- **5-surface doc-coherency** for each new directive; **0 `\trusted`** (the
  abstract `val`s for declared interfaces are `\abstract`, not `\trusted`).

## Suggested order
S0 → S1 → S2 → S3 → S4 (Tier 1 only). Stop at the YAGNI exit if the self-hosting
driver turns out not to need a piece. Tier 2/3 start only when a real
conflict/diamond appears in an actual composition.

---

## Critical files
- `Module1_Ingestor.py` (directive prefixes); `Module2_Parser.py` (grammar + AST
  nodes); `Module3_Weaver.py` (weave onto class/method nodes).
- `Module4_SemanticAnalyzer.py` — the **composition-checking pass** (the heart:
  unique-provider, refinement, field classification, init-hook), after MRO.
- `Module5_IREmitter.py` — mixin/compose IR; `module5/memoization_rt.py` (RT
  reuse for D3).
- `module6_whyml/abstract_ops.py` (declared-interface `val`s); `preamble.py`
  (composed-record invariants); `functions.py` (verify-once method emission);
  the class-record model.
- Docs: static-semantics §1.4 (τ for mixin/composed class), translational
  (composition + flatten rules), `test-suite/annotations.md` (the new
  directives), `pycsl-annotate` SKILL; `test-suite/corpus/pycsl-reference/`
  drivers per stage. `src/self-annotate/` — the actual self-hosting target the
  driver mirrors.
