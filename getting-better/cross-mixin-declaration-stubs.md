# Cross-mixin declaration stubs in the PyCSL self-annotation mirror

**State-of-the-art review request. Wall `cross-mixin-declaration-stubs`, self-tcb-reduction driver run #3.**
Author: dc1 (report author, driver step 3), 2026-10-30. Tree: `c3332a57f` (main `dcf424f75` + one
log commit). No source change is proposed for commit in this report. Every number below comes from a
command listed in the Appendix, and each command was run on that tree.

---

## 0. Summary for the reviewer

- **What the wall is.** PyCSL verifies its own Python implementation through an annotated *mirror*.
  The mirror is verified **one file at a time**. A mixin class in file A often calls a method that
  only exists in a sibling mixin in file B. Both mixins are combined into one runtime object, but only
  at runtime. To make file A type-check and verify alone, the mirror *re-declares* the foreign method
  in A as a bodyless `#@ \trusted` stub. The census tool cannot port a live body into these stubs
  because the declaring class has no live body. It aborts with
  `resolves to 1 mirror / 0 live def(s)`.
- **(a) How many.** **24 of the 408 `\trusted` markers (5.9 %)** are declarations of this kind. The
  408 markers show up as 436 `grep` lines; the other 28 lines are prose that mentions the marker.
  - By where the real definition lives: 23 are defined in another mixin of the same final class
    (`Module6_WhyMLTranspiler`), 1 is defined in a base class (and the stub *overrides* it), and
    **0 are dead** (defined nowhere).
  - They sit in 5 files: `statements.py` 12, `stmt_control_flow.py` 8, `expr_ghost_spec_ops.py` 2,
    `expr_ghost_collections.py` 1, `expressions.py` 1.
- **(b) How the declarations compare with their definitions.** All 24 have the same `requires`,
  `ensures` and `raises` as their definition. That is easy to match, because every one of them is
  `requires True`, `ensures True`, and has no `raises`. **Frames:**
  - 11 are equivalent to the definition's, ignoring `requires True` versus an absent `requires`, and
    an absent `assigns` versus `\nothing`. Both pairs emit the same Why3.
  - 13 differ: 1 is *weaker* (it declares a wider frame), which is safe, and **12 are STRONGER: the
    declaration's frame is smaller than the definition's.**
  - The definition is itself `\trusted` for 21 of the 24 and verified for 3.
- **(c) Soundness finding (flagged).** For 2 of the 12 stronger declarations, the missing fields are
  real fields of the declaring file's Why3 `self` record, and *verified* code applies the declaration:
  - `ControlFlowStmtMixin._match_pattern_cond` declares `assigns \nothing`. Its definition declares 22
    fields, and 12 of them are in the `controlflowstmtmixin` record. The emitted avatar is
    *frameless*. The live body really calls `self._expr_to_whyml`.
  - `ControlFlowStmtMixin._expr_to_whyml` leaves out `_dict_locals`, `_quant_record_binders` and
    `_quant_scalar_binders`.

  So the model assumes, without checking, that those fields are unchanged across the call, while the
  definition says they may change.
  - **Not load-bearing today:** the scratch spike (§4.5) gives both declarations the definition's
    frame. The file still type-checks, and the four verified callers' `--fun` proof pass gives
    **5632 Valid, 0 non-Valid**. So no current proof depends on the false frame. (The
    non-vacuity probe that runs after a green pass was cut off by my 3000 s wall-clock limit;
    see §4.5.)
  - **Still unsound, and not seen:** the frame-honesty plane cannot see the hole (§4.3), and the
    repo already had one such false proved frame (§4.3, `_stmts_to_whyml`).
  - **A second, uncounted instance:** the `#@ requires_method _seq_operand` window in `expressions.py`
    is a declaration with **no `\trusted` marker**. It leaves out 5 model-visible fields and the
    `raises PyCSLSemanticError` of its definition.
- **(d) Mechanisms PyCSL already has.** Each was emitted and the WhyML read:
  1. **Deleting the 6 declarations that have no call site** type-checks. The emitted `.mlw` differs
     only by the 6 unused `val`s. This is honest, but those declarations come back when their live
     callers convert.
  2. **Importing the defining mixin** carries the definition's exact contract into the file. It is
     **REFUTED at L3-tc**: the call site does not bind to it, because every file has its own `self`
     record type and nothing maps one onto another.
  3. **Override refinement** (route #278 static frame/raises inclusion, plus the route #277
     `goal sub__m_refines_base`) is *exactly* the "declaration ⊑ definition" obligation. Today it
     fires only for a base/override pair inside one compilation unit.
  4. **`\abstract` and `requires_method`** would remove markers without checking anything. That is
     trust laundering (§5, §8 R7).
- **Verdict.** This is a *modelling choice*, not a fundamental limit. It comes from (i) verifying each
  file separately and (ii) giving each mixin its own record type instead of the composite object's
  type. The trust a declaration carries is the definition's trust *plus* any difference between the
  two contracts. Only that difference is new trust, and nothing measures it today.
  - The honest first move is a **checked conformance relation between declaration and definition**.
    This is the Why3 `clone`-with-refinement, Dafny refinement-module, or Frama-C/VeriFast
    "one prototype, checked against the definition" discipline. Then fix the 12 narrow frames. No
    marker comes off at that step.
  - Only *after* that does dropping the 24 declaration markers stop being double-counting. The trust
    then stays counted once, at the 14 distinct trusted definitions behind the 21 declarations. The 3 verified definitions are the only
    trust actually removed.

---

## 1. Global picture

### 1.1 PyCSL

PyCSL is a deductive verifier for a subset of Python, in the style of Frama-C/ACSL:
- Contracts are written in comments: `#@ requires`, `#@ ensures`, `#@ assigns` (the frame),
  `#@ raises`, and loop invariants and variants.
- A six-module pipeline lowers them to WhyML, and Why3 discharges them with SMT solvers (Z3,
  Alt-Ergo). The modules are Ingestor, Parser, Weaver, Semantic, IR emitter, and WhyML transpiler.
- The metatheory (`pycsl_soundness`) is checked in both Rocq and Lean.

Two contract modifiers matter here:
- **`#@ \trusted`**: a Python body exists, but PyCSL does *not* verify it. Module 6 emits a bodyless
  Why3 `val` that carries the declared contract, and callers rely on that contract unchecked. Every
  marker is part of the trusted computing base (TCB).
- **`#@ \abstract`**: no meaningful body exists; the contract *is* the definition. It is not counted
  as trust (`test-suite/annotations.md` §2.1.14).

### 1.2 The self-annotation mirror

`src/self-annotate/src/` (53 files) is a copy of PyCSL's own implementation, `src/pycsl/`. Every
function in it is in one of two states:
- **Verified ("converted").** The body is *verbatim* the live body, and Why3 proves the contract
  against it.
- **`\trusted` stub.** The body is a facade (`return ""`, `return False`).

The *self-tcb-reduction* campaign drives the number of `\trusted` markers down. A conversion counts
only if it passes three separate oracle planes:
- **Fidelity:** the mirror body equals the live body (`bin/check-self-annotate-sync.sh`).
- **Proof:** the whole mirror file proves with 0 non-Valid goals.
- **Corpus inertness:** the reference corpus emission is byte-identical.

Count today: **408 markers** (`bin/count-trusted-directives.py`: `markers 408 · grep-substring 436 ·
offset 28`).

Each `\trusted` marker has a row in `getting-better/trusted-reasons.tsv`. Several further "honesty"
planes audit what a trusted stub *claims*, measured against what its live body does:
- `bin/check-trusted-frame-honesty.py` checks `assigns` against the live transitive `self.<f>`
  writes.
- `bin/check-trusted-raises-honesty.py` checks the `raise` statements.
- `bin/check-trusted-termination-honesty.py` checks termination.

### 1.3 How a mixin's `self` is modelled

The live WhyML emitter is one class, `Module6_WhyMLTranspiler`, composed from 7 mixins (the first 5
are named; the full list is in `src/pycsl/Module6_WhyMLTranspiler.py:34-42`):
- `ExpressionEmissionMixin`, which itself inherits `GhostCollectionOpsMixin` and `GhostSpecOpsMixin`;
- `StatementEmissionMixin`, which itself inherits `ControlFlowStmtMixin`;
- `PreambleEmissionMixin`;
- `FunctionEmissionMixin`;
- `TypeInferenceMixin`.

At runtime, `self` is one object, and `self._expr_to_whyml(...)` inside `ControlFlowStmtMixin` is
resolved through the method resolution order (MRO) to `ExpressionEmissionMixin._expr_to_whyml`.

The mirror is verified **per file**, and each file models `self` as **its own** Why3 record type:
- `type controlflowstmtmixin = { mutable _has_early_ret: int; ... }` (25 fields);
- `type statementemissionmixin = { ... }` (75 fields);
- `type ghostcollectionopsmixin = int` (opaque, no fields).

A call `self.m(...)` in a verified body is lowered to an *avatar*, `val self__m_<arity> ...`. The
avatar's `writes` clause is all the caller knows about the call's effect. Module 6 builds that clause
from the `#@ assigns` of the declaration of `m` *in this same file*, keeping only the fields this
file's record carries. Three cases:
- **No declaration in the file:** the avatar is auto-synthesized, typed `int -> int`, has no receiver,
  and has no frame.
- **Declaration with no `#@ assigns`:** the avatar is frameless.
- **Declaration whose assigned fields are all outside the record:** the avatar gets the coarse
  `writes { _pyobj_state }`.

Sources: the docstrings of `bin/check-avatar-frame-parity.py` and
`bin/check-trusted-frame-honesty.py`.

### 1.4 Where the wall sits

A file that calls a sibling mixin's method therefore needs a *local declaration* of that method for
three reasons:
- to give the avatar the right types (otherwise it is `int -> int`, and string-typed calls fail
  L3-tc, as recorded in lessons (r4)/(p4));
- to give the avatar a receiver;
- to give the avatar a frame.

The mirror's convention is a `\trusted` stub with a facade body. For example
(`stmt_control_flow.py`):

```python
#@ \trusted reviewer: pycsl-self-annotate
#@ ensures True
#@ assigns \nothing
def _match_pattern_cond(self, pat, subject, local_refs) -> str:
    return ""
```

The live `ControlFlowStmtMixin` has no `_match_pattern_cond`; it is defined in
`ExpressionEmissionMixin` (`src/pycsl/module6_whyml/expressions.py:1420`). The census instrument
`bin/port-one-mirror-body.py` ports a live body into a same-class, same-file stub. It therefore
aborts on these stubs (`ABORT: ... resolves to 1 mirror / 0 live def(s)`). The cv6 survey
(`/home/fabrice/git/pycsl/scratchpad/cv6/survey.tsv`) lists 21 such PORT-ABORT rows, but only for the
stubs it attempted.

---

## 2. (a) The exact set

**Definition used.** A declaration stub is a `\trusted` mirror def (marker attachment by
`bin/trusted_markers.py`, the same walk the authoritative count uses) whose full qualified name
(`Class.method`) has **no def** in the live file at the same relative path. Each one is then
classified by where the live tree defines the method:
- **base-class:** the method is defined in a transitive base of the declaring class;
- **other-mixin:** the method is defined in another class of a live composite that (transitively)
  inherits the declaring class;
- **module-func-elsewhere:** the method is a module-level function somewhere else;
- **nowhere (dead):** none of the above.

Census: `decl_census.py` (Appendix A1). Output:
`TRUSTED_DEFS_TOTAL=408 DECL_STUBS=24 {'other-mixin': 23, 'base-class': 1}`.

| # | declaring file :: stub | kind | live definition | mirror definition status |
|---|---|---|---|---|
| 1 | expr_ghost_collections :: GhostCollectionOpsMixin._e | other-mixin | ExpressionEmissionMixin (expressions.py) | trusted |
| 2 | expr_ghost_spec_ops :: GhostSpecOpsMixin._e | other-mixin | ExpressionEmissionMixin | trusted |
| 3 | expr_ghost_spec_ops :: GhostSpecOpsMixin._expr_to_whyml_string_ctx | other-mixin | ExpressionEmissionMixin | trusted |
| 4 | expressions :: ExpressionEmissionMixin._add_abstract_op | other-mixin | AbstractOpsMixin (abstract_ops.py) | trusted |
| 5 | statements :: StatementEmissionMixin._add_abstract_op | other-mixin | AbstractOpsMixin | trusted |
| 6 | statements :: ._resolve_dotted_signature | other-mixin | ExpressionEmissionMixin | trusted |
| 7 | statements :: ._is_emit_ir_expr | other-mixin | ExpressionEmissionMixin | trusted |
| 8 | statements :: ._coerce_to_int | other-mixin | ExpressionEmissionMixin | **verified** |
| 9 | statements :: ._expr_to_whyml | other-mixin | ExpressionEmissionMixin | trusted |
| 10 | statements :: ._expr_to_whyml_string_ctx | other-mixin | ExpressionEmissionMixin | trusted |
| 11 | statements :: ._is_string_expr | other-mixin | ExpressionEmissionMixin | trusted |
| 12 | statements :: ._track_collection_metadata | other-mixin | TypeInferenceMixin (types.py) | trusted |
| 13 | statements :: ._e | other-mixin | ExpressionEmissionMixin | trusted |
| 14 | statements :: ._maybe_emit_no_exception_assert | other-mixin | Module6_WhyMLTranspiler (the composite itself) | trusted |
| 15 | statements :: ._mutex_inv_application | other-mixin | PreambleEmissionMixin (preamble.py) | trusted |
| 16 | statements :: ._handle_return_stmt | **base-class** | ControlFlowStmtMixin (stmt_control_flow.py) — the mirror stub **overrides** a verified base method | **verified** |
| 17 | stmt_control_flow :: ControlFlowStmtMixin._is_string_expr | other-mixin | ExpressionEmissionMixin | trusted |
| 18 | stmt_control_flow :: ._add_abstract_op | other-mixin | AbstractOpsMixin | trusted |
| 19 | stmt_control_flow :: ._seq_init_expr | other-mixin | StatementEmissionMixin (statements.py) | trusted |
| 20 | stmt_control_flow :: ._expr_to_whyml | other-mixin | ExpressionEmissionMixin | trusted |
| 21 | stmt_control_flow :: ._coerce_to_int | other-mixin | ExpressionEmissionMixin | **verified** |
| 22 | stmt_control_flow :: ._to_bool | other-mixin | ExpressionEmissionMixin | trusted |
| 23 | stmt_control_flow :: ._stmts_to_whyml | other-mixin | StatementEmissionMixin | trusted |
| 24 | stmt_control_flow :: ._match_pattern_cond | other-mixin | ExpressionEmissionMixin | trusted |

**Counts.**
- **24 / 408 markers** (5.9 %); 24 of the 436 grep lines.
- By kind: 23 other-mixin, 1 base-class, **0 dead**, 0 module-level.
- By the status of the mirror definition: **21 trusted, 3 verified** (rows 8, 16, 21).
- The 24 cover 15 distinct method names. `_add_abstract_op` is declared 3 times; `_e`, `_expr_to_whyml`,
  `_is_string_expr`, `_coerce_to_int` and `_expr_to_whyml_string_ctx` are declared twice each.
- All 24 rows in `trusted-reasons.tsv` are `unclassified -`.
- The population is not new. `bin/check-sibling-concrete-fidelity.py` prints "24 `\trusted`
  cross-mixin stub(s) (by design)" without naming them, and `getting-better/driver-backlog.md` #70
  (gen #32) already ranked "the 24 cross-mixin stubs" as a conversion target (§6, route R5).

**Six of the 24 have no call site at all in their file** (Appendix A3: no `self.<m>(` anywhere in the
file, and no avatar in the emitted `.mlw`). All six are in `statements.py`: `_is_emit_ir_expr`,
`_expr_to_whyml_string_ctx`, `_is_string_expr`, `_track_collection_metadata`, `_e`,
`_maybe_emit_no_exception_assert`. Their live callers are methods the mirror still holds as
`\trusted` stubs. For example, `_is_string_expr` has 13 live callers in `statements.py`, including
`_handle_array_set_stmt` and `_seq_init_expr`. The declarations exist for those callers' future
conversion.

### 2.1 Uncounted relatives (same wall, no `\trusted` marker)

The two `#@ requires_method` windows in `expressions.py` (lines 1491 and 1549) are declarations of
sibling methods with **no marker**:
- `_seq_operand` is defined in `statements.py`, as a `\trusted` stub;
- `_field_type_of` is defined in `types.py`, as a verified method.

The 24 PORT-ABORT stubs are only the *counted* part of the population. The same census run over the
*un-trusted* mirror defs (Appendix A6) finds 26 with no same-file live twin:
- 10 are the per-file `mutable_state` modelling decorator;
- **16 are cross-mixin `sibling_concrete` relocations**. Each is a *verified* copy of a *verified*
  definition. All 16 have `#@` clauses identical to their definition (the 3 lexical differences are
  only the `sibling_concrete` directive itself), and `check-sibling-concrete-fidelity.py` checks
  their bodies.

So the relocated population is already checked declaration-equals-definition. The 24 `\trusted`
declarations and the 2 `requires_method` windows are the unchecked remainder.

---

## 3. (b) Declaration vs definition contracts

**Method.**
- Take the `#@` clauses above each declaration and above its mirror definition (the def of
  `DefClass.m` in the defining class's mirror file), merge continuation lines, normalise whitespace,
  and compare them clause by clause (Appendix A1).
- Then (Appendix A2) intersect `def.assigns − decl.assigns` with the fields of the declaring file's
  *emitted* `self` record. That separates frame gaps a prover could be misled by from gaps that are
  invisible to the model.
- The emitted record comes from `pycsl --no-proof --keep-mlw`, in the scratch worktree.

**`requires` / `ensures` / `raises`.** These are identical in all 24 pairs, but only trivially: every
declaration *and* every definition says `ensures True`, has no `raises`, and says either
`requires True` or nothing. The only lexical differences are `requires True` versus an absent
`requires`, and the emission directive `sibling_concrete` on the two verified `_coerce_to_int`
definitions; neither is a contract clause.
- `check-trusted-raises-honesty.py` reports five of the declarations as SILENT (the live body raises,
  the stub says nothing): rows 9, 20, 22, 23 and `statements::_stmts_to_whyml`'s definition.
- It reports exactly the same verdict for their definitions. So declaration and definition agree,
  and both are silent.

**Frames (`assigns`).**

| class | n | stubs |
|---|---|---|
| identical, or identical modulo `requires True` | 6 | 4, 5, 17, 18, 19, 22 |
| equivalent: decl has no `assigns` and def says `\nothing` (both emit a `val` with no `writes`) | 5 | 6, 8, 14, 15, 21 |
| decl **weaker** (decl frame ⊇ def frame; safe) | 1 | 16 (`_handle_return_stmt`: the decl adds `_abstract_ops`, `_get_return_raw_option`) |
| decl **STRONGER** (decl frame ⊂ def frame) | **12** | 1, 2, 3, 7, 9, 10, 11, 12, 13, 20, 23, 24 |

Total: 6 + 5 + 1 + 12 = 24.

**The 12 stronger declarations, split by whether the model can see the gap** (Appendix A2):

| stub | decl assigns | def assigns | omitted | omitted AND in this file's `self` record | avatar actually emitted | verified callers in this file |
|---|---|---|---|---|---|---|
| 24 CF `_match_pattern_cond` | `\nothing` | 22 fields | 22 | **12**: `_comp_content_counter, _current_params, _current_self_type, _dict_locals, _frame_trigger_active, _func_return_type, _in_spec, _needs_array_init, _quant_record_binders, _quant_scalar_binders, _string_local_vars, _todict_arg_wants_pymap` | `val self__match_pattern_cond_3 (x0: emit_ir) (x1: string) (x2: ...) : string` — **no receiver, no `writes`** | `_handle_match_stmt` |
| 20 CF `_expr_to_whyml` | 17 fields | 22 | 5 | **3**: `_dict_locals, _quant_record_binders, _quant_scalar_binders` | `writes {` 9 labelled fields `}` | `_handle_while_stmt`, `_handle_if_stmt`, `_handle_match_stmt`, `_handle_return_stmt` |
| 10 Stmt `_expr_to_whyml_string_ctx` | (none) | 22 | 22 | 14 | none (no call site) | none |
| 13 Stmt `_e` | (none) | 22 | 22 | 14 | none (no call site) | none |
| 12 Stmt `_track_collection_metadata` | `\nothing` | 4 | 4 | 3: `_known_collection_elements, _known_collection_sizes, _record_array_locals` | none (no call site) | none |
| 23 CF `_stmts_to_whyml` | 18 | 55 | 37 | 0 | `writes {...}` | 5 |
| 9 Stmt `_expr_to_whyml` | 21 | 22 | 1 (`_late_content_ops`) | 0 | `writes {...}` | 7 |
| 11 Stmt `_is_string_expr` | (none) | 3 (`_uses_*_cache`) | 3 | 0 | none | none |
| 7 Stmt `_is_emit_ir_expr` | (none) | 1 | 1 | 0 | none | none |
| 1, 2, 3 Ghost `_e` / `_e` / `_expr_to_whyml_string_ctx` | `\nothing` | 22 | 22 | 0 (`self` is `int` in those files) | `val self__e_2 (x0: emit_ir) (x1: ...) : string` | 21 + 7 + 3 handlers |

What the rows mean:
- **Model-visible and applied by verified code: 2** (rows 24 and 20, both in `stmt_control_flow.py`).
  These are the soundness-relevant ones.
- **Model-visible but never applied: 3** (rows 10, 13, 12). These are traps: they become live the day
  a caller converts.
- **Invisible to the model: 7.** The fields are not in this file's record, or `self` is opaque. The
  annotation is dishonest to a human reader, but the model asserts nothing false.

A caveat on "the definition's frame". The definition's `assigns` is itself a `\trusted` claim for 21
of 24. Gen #32 derived it from an *over-approximating* name-resolved closure of live
`self.<f>` stores (`check-trusted-frame-honesty.py`, constant `TOTAL_RATCHET`). So "decl ⊂ def" is
measured against a frame that may be wider than the truth. For row 24 I checked the live body
directly: `ExpressionEmissionMixin._match_pattern_cond` (expressions.py:1420) calls
`self._expr_to_whyml`, which stores `self._abstract_ops` directly and reaches the
`self._comp_content_counter = n + 1` stores (expressions.py:20101, 20333, 20407) through
`_content_comp`. **I did not establish** that a *reachable* `match` value pattern drives a
model-visible field through that path at runtime.

---

## 4. (c) How the toolchain treats them today, and what the proofs assume

### 4.1 Fidelity plane

`bin/check-self-annotate-mirror-sync.py:247-251` skips every `\trusted` def ("intentionally-divergent
stub"), and separately skips every mirror def with no same-file live twin ("mirror-only function").
`bin/check-mirror-signature-drift.py:130` skips them as "mirror-only scaffolding".
`bin/check-sibling-concrete-fidelity.py:150` counts them ("cross-mixin MRO boundary stub: by design")
and names none. **Nothing checks a declaration's signature or contract against its definition.**

### 4.2 Reasons plane

`bin/check-trusted-reasons.py` → `408 marker(s) · 408 row(s) · missing 0 · orphan 0`. The 24 are
present, all `unclassified -`. Exit 0.

### 4.3 Frame-honesty plane: BLIND to declarations

`check-trusted-frame-honesty.py` looks up each stub's live counterpart as
`live_key = (LIVE_ROOT + path[len(MIRROR_ROOT):], cls, name)` (line 945), which means the same file
and the same class. For a declaration that key does not exist, `trans.get(live_key)` is `None`, and
the stub is silently treated as "no live writes".

Measured: `--verbose`, rc=0, 273 s:
`179 method(s) declare assigns \nothing; 1 stand for a live body that transitively writes self state
... 0 MODEL-VISIBLE`. The only trusted offender listed is `pure_ast._Unparser.write`. **None** of
rows 1, 2, 3, 12 and 24 is listed, although each declares `\nothing` over a definition that declares
4 to 22 written fields.

**The plane's headline "0 model-visible false trusted frames" therefore does not cover these 24
stubs.**

The repo has paid for this exact hazard before. The `MAX_TRAP` note in
`bin/check-assigns-writes-survival.py` records it: *"the `_stmts_to_whyml` protocol stub in
stmt_control_flow claimed `assigns self._in_spec` only, so the verified `_handle_while_stmt` proved
`self._for_idx_init = old self._for_idx_init` while live takes it '0' -> '3'."* That was a false
proved frame, produced by a declaration stub. It was repaired by hand, and no rule was added to
prevent a recurrence.

### 4.4 Other planes

**Avatar-frame parity.** `bin/check-avatar-frame-parity.py` measures the opposite gap: an inheriting
file with *no* declaration (bucket "INHERITED", ratchet 7). Its docstring records two routes that
were tried and measured:
- Route 1: read the declaration from the defining class's mangled entry. It moved nothing, because
  "an inheriting mirror does not import the defining mixin".
- Route 2: a coarse `_pyobj_state` frame. Refuted at L3-tc.

Its recommended residual is "add a `\trusted` protocol stub carrying the honest `#@ assigns` to each
inheriting mirror". **That is exactly the population studied here, and nothing then checks that the
assigns stays honest.**

**Raises honesty.** This plane falls back to a *name-only* live match for a relocated def
(lines 269-280), so it does see declarations; 5 are SILENT, consistent with their definitions.

**Termination honesty.** This plane reports the definitions (`statements.py _seq_init_expr`
loop-without-variant, `_stmts_to_whyml` self-call) and not the declarations. That is consistent
with "the declaration inherits the definition's termination assumption".

### 4.5 What the mirror proofs actually assume, and whether any proof depends on the narrow frames

**Assumption, from the emitted WhyML.** In each verified caller, a call to a declared sibling
becomes an avatar `val`. The avatar has the declaration's types, `ensures true`, no `raises`, and the
declaration's frame intersected with the record. The bodyless
`val <cls>___m (self: <cls>) ... ensures {true} [writes {...}]` that the stub itself emits is **never
applied**. Every call goes through the avatar; Appendix A3 counts the symbols. A declaration that
has no `#@ assigns` emits a `val` with **no `writes`**, which Why3 reads as "writes nothing"
(e.g. `statementemissionmixin___e`, `statements.mlw:1337`).

**Spike S1** (scratch worktree, never committed). I replaced the `#@ assigns` of rows 20 and 24 with
the definition's `#@ assigns` line, verbatim (Appendix A4), then emitted and proved:
- `--no-proof --keep-mlw` → `L3-tc ✓`.
- `.mlw` diff:
  - `self__match_pattern_cond_3` gains a receiver `(self: controlflowstmtmixin)` and a 12-field
    `writes`;
  - `self__expr_to_whyml_2` gains `_dict_locals, _quant_record_binders, _quant_scalar_binders`;
  - two dependent `writes` lines widen.
- `--fun` proof of the four verified callers (`_handle_match_stmt`, `_handle_while_stmt`,
  `_handle_if_stmt`, `_handle_return_stmt`) and their dependencies: the proof pass printed **5632 `Valid`, 0 `Unknown`/`Timeout`/`Invalid`**.
  pycsl reaches its non-vacuity gate only when returncode = 0 and there are no unknown or invalid
  goals (`src/pycsl/pycsl.py:26314`), and that gate was running when my `timeout 3000` (which
  includes heavy.sh queue time) killed it. So: **proof green, non-vacuity not measured.** No base
  run was made for comparison; the claim is only that the honest frames do not break these
  callers.

**Reading.** The narrow frames are a **trap, not a hole**: no current proof depends on them. The
verified callers already declare all of those fields in their own `assigns`, because they reach them
through other callees, and their `ensures` are `True`. So the false "unchanged" fact is never used.
The same was true of `_stmts_to_whyml` until the day it was not (§4.3).

---

## 5. (d) Mechanisms PyCSL already has, each emitted and read

| mechanism | what it would do here | evidence | verdict |
|---|---|---|---|
| **Delete a declaration that has no call site** | removes the 6 `statements.py` declarations listed in §2 | S2: delete the 6 defs (Appendix A5); `--no-proof --keep-mlw` → `L3-tc ✓`; `.mlw` diff = only the 6 unused `val statementemissionmixin___{e, expr_to_whyml_string_ctx, is_emit_ir_expr, is_string_expr, maybe_emit_no_exception_assert, track_collection_metadata}` disappear (each `ensures { true }`, applied nowhere). An unapplied `val` contributes no hypothesis to any VC. | **WORKS, honest, −6 markers.** The 6 come back when the live callers (`_handle_array_set_stmt`, `_handle_ghost_assign_stmt`, `_handle_assign_stmt`, `_handle_del_subscript_stmt`, ...) convert. 3 of the 6 (rows 10, 12, 13) are the model-visible stronger frames, so deleting them also removes 3 traps. The gate battery was NOT run; this is a spike. |
| **Import the defining module** (`from module6_whyml.expressions import ExpressionEmissionMixin`, with `--import-path src/self-annotate/src`) instead of the local declaration | the importer gets `expressionemissionmixin__<m>` stubs carrying the definition's *own* contract — one source, identical by construction | S3, on `expr_ghost_collections.py` (Appendix A7): `Imported class ... ExpressionEmissionMixin (record + 95 method stub(s))`. The emitted `val expressionemissionmixin___e (self: expressionemissionmixin) ... writes { <the definition's 22 fields> }` is present, **but the call site does not bind to it**: `self._e(...)` in `GhostCollectionOpsMixin` falls back to an auto-synthesized `val self__e_2 (x0: int) (x1: int) : int`, and L3-tc fails (`This expression has type PyCSL_Program.emit_ir, but is expected to have type int`, line 1189). | **REFUTED as is.** The contract travels; the receiver does not. Each file's `self` is a different record type, and no mapping from mixin to composite exists. Two further problems: imported methods are injected with `trusted = True` (ir_resolve.py:2114), and the whole toolchain runs with `--import-path src/pycsl`, the *un-annotated* live tree, from which an import would bring in **empty** contracts. |
| **Override refinement** (route #278 static: an override may declare at most the base's `raises`/`assigns`, keep its parameters, and return a subtype; route #277: `goal sub__m_refines_base`) | exactly the "decl ⊑ def" obligation: pre-weakening and post-strengthening as a Why3 goal, frame inclusion and raises inclusion as a hard static check | S4 (Appendix A8): `Base.m assigns \nothing`, `Sub(Base).m assigns self.x` → `PIPELINE ERROR [ir-semantic] override 'sub__m' of 'base__m' assigns a location base__m's assigns does not name ... (route #278)`. With the frame fixed: `L3-tc ✓`, and the `.mlw` carries `goal sub__m_refines_base : forall self: sub, result: int. ((true) -> (true)) /\ (((result >= 0)) -> ((result >= 0)))`. | **The obligation exists and has teeth, but only for a base/override pair inside ONE unit.** Applying it to declarations needs a generated *conformance unit* per pair (§6, R2). Not built or spiked beyond S4. |
| **`#@ mixin` / `depends_method` / `requires_method` / `compose_from`** (Tier-1 mixin composition, annotations.md §2.7) | a mixin states its sibling dependencies with contracts; `compose_from` checks there is a unique provider and flattens the providers in | Read `ir_resolve.apply_composition` (ir_resolve.py:2982). Its docstring says **S2b (`provider ⊑ dependency`) "has no implementation"**: it is discharged only *implicitly*, by re-verifying the flattened clone inside the composer's unit. The mirror has **no** `#@ mixin` or `compose_from`; it uses 2 bare `requires_method` windows (§2.1). | **Not a check in the mirror today.** A `requires_method` window is a declaration that is not counted and not checked, and one of the two already understates its definition (§5.1). Using it to replace `\trusted` declarations would be laundering. |
| **`#@ \abstract`** | a bodyless `val` that does not count as trust | annotations.md §2.1.14: for when "there is *no meaningful body to check*" | **Dishonest here**: there IS a body (the definition). Same emission as `\trusted`, minus the accounting. |
| **`#@ interface` / `#@ reveal`** (contract opacity, annotations.md §2.10) | a definition exports a narrower interface; a narrowing VC proves definition ⟹ interface *in the owning unit* | Read the docs only; not emitted. | Orthogonal. It narrows what importers see, so it would only help *after* the import route works. |
| **`#@ sibling_concrete`** relocation (a verified concrete copy of the sibling's body in the declaring file; gated by `check-sibling-concrete-fidelity.py`, 25 SAME / 0 DIVERGING at gen #32) | replaces a declaration with a *proved* body | Prior measurement, backlog #70 and lessons (o4)/(r4)/forwarder: the cost is the body's callee closure; a forwarder (`_e` → `_expr_to_whyml`) moves trust to an uncounted auto-synthesized `val`; a missing string-typed callee costs a new `\trusted` shim (net zero). | Honest only where the definition is verified *and* its closure is present: rows 8, 21 (`_coerce_to_int`) and 16 (`_handle_return_stmt`). Elsewhere it re-verifies a body whose callees stay assumed. |

### 5.1 The uncounted declaration, measured

The `requires_method _seq_operand` window (`expressions.py:1491-1492`) is a declaration with no
`\trusted` marker. Compared with the definition, `statements.py:_seq_operand`, which is `\trusted`,
has `#@ raises PyCSLSemanticError when True`, and a 51-field `assigns`:
- the window declares 22 fields;
- **5 of the omitted fields are in the `expressionemissionmixin` record**: `_array_locals`,
  `_lambda_locals`, `_record_array_locals`, `_record_locals`, `_todict_aliases`;
- the window has **no `raises`**.

The emitted avatar `self__seq_operand_2` carries only the window's frame and no `raises`. Its caller
`_ifexpr_seq_arm` is **verified**. The live `_seq_operand` (statements.py:1844-1874) has no direct
`raise` and no direct store. It calls `_add_abstract_op`, `_expr_to_whyml` and
`_seq_value_producing`, so whether the five omitted fields and the exception are *reachable* is again
an over-approximation question I did not settle. The structural point stands either way:
- **this declaration is not counted by any trust metric;**
- **its frame and raises are stronger than its definition's.**

---

## 6. Is the wall fundamental or a modelling choice?

**It is a modelling choice.** Two independent decisions produce it:

1. **Verification unit = file.** Each mirror file is verified alone, so a cross-file call needs a
   local specification of its callee. This is the normal *modular* verification set-up. It is not a
   limitation in itself, as long as the local specification is *checked against* the definition,
   which is the whole point of modular verification.
2. **`self` type = the declaring mixin, not the composite.** Each file builds its own record from the
   fields that file touches. So the definition's contract (written over `expressionemissionmixin`)
   cannot simply be imported into `controlflowstmtmixin` (spike S3): field names coincide, but the
   types differ. An honest cross-file contract needs either:
   - a shared composite state type (one record for `Module6_WhyMLTranspiler`, used by every mixin
     file), or
   - a field-wise projection: a frame over `D`'s fields, restricted to the fields `C`'s record also
     carries.

   The avatar machinery already performs that restriction, field by field, from a *local* `assigns`.

So the part that is fundamental is small: Python mixins are composed at runtime, and the verifier
must choose a unit. Everything else is the specific choice to discharge "declaration ⊑ definition"
by *reviewer trust* (`\trusted`) instead of by an *obligation*.

**How much trust do the 24 markers actually represent?**
- **21 declarations of trusted definitions.** If the contracts were equal, the declaration would add
  *no* assumption beyond the definition's, which is already counted. These markers double-count.
  Where the contracts differ (the 12 stronger frames, all among these 21), the difference is **new,
  uncounted-as-such, unchecked trust**.
- **3 declarations of verified definitions** (2 × `_coerce_to_int`, `_handle_return_stmt`). These are
  genuine, removable trust: a proof already exists for the definition.
  - Rows 8 and 21 declare an empty frame (no `assigns`), and the definition declares `\nothing`;
    both have `ensures True`. Equal.
  - Row 16 (`_handle_return_stmt`) declares a *wider* frame. It is weaker, so it is sound for callers
    in `statements.py`. However, it *overrides* a method that is verified in the base mirror class:
    the `statements.mlw` callers reason with the declaration, not with the base proof.

---

## 7. The SOTA lens

How mature modular verifiers handle "a declaration here, the definition elsewhere":

- **Why3.**
  - A `val f ... requires ... ensures ... writes ...` in an interface module is refined by a
    `let f ...` through `clone M with val f = f`. The clone **generates refinement VCs**: the
    implementation's pre is implied by the declaration's, the declaration's post is implied by the
    implementation's, and the declared effects (`writes`, `raises`) must *include* the
    implementation's.
  - Why3 rejects an implementation whose effect is not covered by the cloned `val`'s (an "unlisted
    write effect"-type error), the same family of error Why3 already reports on PyCSL's own `let`s.
  - So a declaration is free of trust exactly when a clone ties it to its definition.
- **Dafny.**
  - Refinement modules (`module B refines A`) and abstract modules: a body-less method in `A` is
    implemented in `B`, and the refinement check requires the same signature and that the
    implementation satisfies the abstract spec, including `modifies`.
  - Traits require an implementing class's method to refine the trait's spec, as a proof obligation.
  - Mutually dependent "mixins" are modelled as a trait (the composite interface) with
    `modifies this`-style frames over a shared object.
  - A `{:extern}` or body-less method is the explicit trust escape and is reported as an assumption
    (`/warnShadowing`, `dafny audit`).
- **Frama-C / ACSL.**
  - One function, one contract. A prototype in a header carries the contract; WP uses that contract
    at call sites and proves the definition against *the same* contract, because ACSL merges a
    prototype's contract with the definition's when both are visible to the same linker.
  - Divergent contracts in different translation units are a known source of unsoundness. That is
    why Frama-C's kernel merges or warns on mismatching specs, and why projects keep the contract
    *only* in the header.
  - Assigns-frame mismatches are a classic WP soundness pitfall. MetAcsl and E-ACSL both treat a
    missing or incorrect `assigns` on an undefined function as an assumption to be listed
    (`-wp-warn-memory-model`, the "no assigns specification" warning).
- **VeriFast / VCC / Viper-style separation-logic tools.**
  - A function prototype or predicate family is declared once and *imported*. A module's
    implementation is checked against the very same declaration. VeriFast's module system rejects
    a link when an imported prototype's spec differs from the exporting module's.
  - Frames are carried by the separation-logic footprint, so a declaration cannot claim a smaller
    footprint than the definition without a link-time failure.
- **Common lesson.** No mature tool lets a local re-declaration be *trusted*. A re-declaration is
  either the *same text* (single source: header or interface, imported) or *checked* to be refined
  by the definition (clone, refinement module, trait implementation, link check). An uncheckable
  re-declaration is reported as an assumption, never silently believed.

  PyCSL already has both halves:
  - a single-source mechanism (imports), blocked here by the `self`-type issue;
  - a refinement obligation (override refinement #277/#278), scoped to one unit.

  It has not connected either to the mirror's cross-file declarations.

---

## 8. Honestly costed routes

Markers are counted against the 408. Honesty test for each route: *is the assumption still counted
once, and is "declaration ⊑ definition" checked?*

| route | markers removed | honest? | cost (estimate; only S1–S4 were run) |
|---|---|---|---|
| **R0. Measure first.** Teach `check-trusted-frame-honesty` to resolve a declaration to its definition through the MRO of the live composite (the same resolution `_self_write_fixpoint` already uses for call edges), and add the 2 `requires_method` windows to the population. | 0 | yes; it makes the 12 stronger frames visible and ratchets them | small: one lookup change, plus a re-baseline note per the plane's "analysis got sharper" rule |
| **R1. Fix the 12 stronger frames.** Give each declaration the definition's `#@ assigns` verbatim, and the `_seq_operand` window too. | 0 | yes: removes unchecked trust without touching the count | S1 measured it for 2 of the 12 in `stmt_control_flow.py`: L3-tc ✓, callers' `--fun` proof 5632 Valid / 0 non-Valid (non-vacuity unmeasured). The rest: 3 have no call site (or delete them, R3); 3 are in opaque-`self` files (no emission change expected); 4 have avatars in `statements.py`/`stmt_control_flow.py` (whole-file re-proofs: `statements.py` measured 2h19m in backlog #70, `stmt_control_flow.py` shorter). Then the mirror-emit sweep and the three L planes. |
| **R2. Make "declaration ⊑ definition" a gate.** Either a **sync rule** (each declaration's `#@` clause set must be byte-identical, after normalisation, to its definition's; signature identical up to the documented type layer), or, stronger, a **generated conformance unit** per pair (`class Decl: <decl stub>` / `class Def(Decl): <def contract>`) fed to `pycsl --no-proof`, so routes #278 and #277 discharge frame, raises and pre/post refinement with existing machinery (S4). | 0 by itself | yes. This is the Why3 clone / Dafny refinement / VeriFast link check, transposed. | sync rule: ~1 checker plus ratchet, small. Conformance unit: medium (generator; the types of `self` must be bridged by giving `Decl` and `Def` the same field set). |
| **R3. Delete declarations with no call site.** | **−6** (S2) | yes: an unapplied `val` asserts nothing | small: one edit to `statements.py`, `trusted-reasons --sync --write`, then the battery. `statements.py` needs no re-proof in principle (the VCs are unchanged), but the protocol requires the planes. The 6 return when their callers convert, so this is a "do not carry dead trust" move, not a capability. |
| **R4. After R1 + R2, reclassify the declarations.** A declaration whose contract is *proved* to be refined by its definition no longer carries its own trust. Count it under a distinct, non-`\trusted` marker (e.g. a `#@ declared_in <file>::<Class.m>` the gate resolves), and keep counting the definition. | **−24 in the marker count** (−18 if R3 has already taken 6). **Real TCB reduction: 3** (rows 8, 16, 21, whose definitions are verified); the other 21 stay counted at their 14 distinct trusted definitions. | yes **only with R2 in place**; without it, this is laundering | small once R2 exists (a language or tool marker plus the count tool's attachment walk) |
| **R5. `sibling_concrete` relocation** (backlog #70) | up to 3 honestly (the verified-definition rows); elsewhere net zero or laundering (forwarder lesson, (r4)) | partially | per backlog #70: priced by callee closure; the dispatchers (`_expr_to_whyml` 1217 lines, `_is_string_expr` 567, `_to_bool` 403) are expected to refuse |
| **R6. One composite state type** (a single `Module6_WhyMLTranspiler` record used by every mixin file), or full `compose_from` flattening of the 7 mixins into one unit | 24, and the 7 INHERITED avatar gaps too | yes | research-grade or large: the composite unit is the union of `statements.py`, `expressions.py`, `stmt_control_flow.py`, ... — currently hours of proof per file; S2b ("provider ⊑ dependency") would need a real implementation instead of the flattening proxy |
| **R7. `\abstract` / bare `requires_method` instead of `\trusted`** | 24 | **NO**: same emission, no check, trust leaves the metric | trivial, and must be refused |

**Recommended order:** R0 → R1 → R2 → (R3) → R4.
- R0 and R1 remove *unsoundness risk*.
- R2 builds the check every mature tool has.
- R4 then cashes in the count, honestly.
- **Gross −24, net TCB −3, plus a closed blind spot.** Anyone presenting "−24" without R2 is
  double-counting in reverse.

---

## 9. Honest limits of this report

- The definition frames are themselves `\trusted` for 21 of 24, and come from an *over-approximating*
  name-resolved closure. "Decl ⊂ def" therefore proves the declaration *understates its definition*,
  not that a reachable live run writes the omitted field. I did not build a runtime witness for
  rows 20, 24 or `_seq_operand`.
- The census classifies by the *live* MRO, using class names only (no aliasing, no `getattr`
  dispatch). The answer "0 dead" depends on that resolution.
- S1 was a `--fun` proof of four callers (plus their transitive dependencies), not a whole-file
  proof. S2 and S3 were `--no-proof` only. None of the spikes ran the three-L-plane battery. Nothing
  here is banked; the scratch worktree `/home/fabrice/git/pycsl-dc1-scratch` holds the edits.
- The SOTA paragraphs describe the tools' documented mechanisms from the author's knowledge. They
  were not re-checked against tool versions in this session.
- The un-trusted census (A6) compares `#@` clauses only. The 2 `requires_method` windows are not
  defs, so they were examined by hand.

---

## Appendix: reproduction

Scratch directory used: `/tmp/claude-1000/-home-fabrice-git-pycsl/0119d6ca-595a-4b95-ab54-21d812c2f0f2/scratchpad/dc1/` (abbreviated `$D`).
Every Python or pycsl job ran as `/home/fabrice/git/pycsl/scratchpad/heavy/heavy.sh <cmd>`.

- **A0. Count.** `python3 bin/count-trusted-directives.py` → `markers 408 · grep-substring 436 ·
  offset 28 · attached 408`.
- **A1. Census.** `heavy.sh python3 $D/decl_census.py <tree> > $D/census.tsv`. A pure-AST script: it
  imports `bin/trusted_markers.py`, and for each trusted mirror def with no same-file live qualname it
  walks the live class graph and the mirror definition. stderr: `TRUSTED_DEFS_TOTAL=408
  DECL_STUBS=24 {'other-mixin': 23, 'base-class': 1}` / `def-status: {'trusted': 21, 'verified': 3}
  cmp: {'DIFFERENT': 22, 'identical': 2}`. The "22 DIFFERENT" is lexical; §3 normalises it to
  6 + 5 + 1 + 12.
- **A2. Visibility.** Emit the 6 module6 mirrors in a scratch worktree:
  `PYTHONHASHSEED=0 heavy.sh .venv/bin/python3 src/pycsl/pycsl.py src/self-annotate/src/module6_whyml/<f>.py --import-path src/pycsl --no-proof --keep-mlw`
  for `<f>` ∈ {expr_ghost_collections, expr_ghost_spec_ops, stmt_control_flow, statements,
  expressions, abstract_ops}. All rc=0, `L3-tc ✓`. Then run
  `heavy.sh python3 $D/decl_visibility.py <tree> $D/census.tsv <scratch>/src/self-annotate/src > $D/visibility.tsv`.
- **A3. Call sites.** `grep -oE "self__<m>_[0-9]+|<cls>___<m>" <file>.mlw | sort | uniq -c`. Every
  `<cls>___<m>` declaration `val` occurs once (its declaration); the calls go through
  `self__<m>_<n>`.
- **A4. S1.** `python3 $D/sync_decl_frames.py <scratch> $D/census.tsv "ControlFlowStmtMixin._match_pattern_cond" "ControlFlowStmtMixin._expr_to_whyml"`,
  then re-emit with `--no-proof` (`L3-tc ✓`) and run
  `$D/run_fun.sh <scratch> module6_whyml/stmt_control_flow.py $D/spike1_fun.log controlflowstmtmixin___handle_match_stmt controlflowstmtmixin___handle_while_stmt controlflowstmtmixin___handle_if_stmt controlflowstmtmixin___handle_return_stmt`.
  `run_fun.sh` wraps heavy.sh. Result: `--- Verification Results ---` 5632 Valid, 0 Unknown/Timeout/Invalid; then the vacuity gate, killed by `timeout 3000` (`DONE rc=124 3000s`).
- **A5. S2.** Delete the 6 def blocks (the `#@` lines plus the def) from the scratch
  `statements.py`, then `--no-proof --keep-mlw`: `L3-tc ✓`. The diff against the base `.mlw` is only
  the 6 `val ... ensures { true }` blocks.
- **A6. Un-trusted mirror-only census.** `heavy.sh python3 $D/decl_census_untrusted.py <tree>`, the
  same census over un-trusted defs. Output: `DECL_STUBS=26 {'OTHER(...)': 10, 'other-mixin': 16}` /
  `def-status: {'-': 10, 'verified': 16} cmp: {'-': 10, 'DIFFERENT': 3, 'identical': 13}`. The 3
  DIFFERENT rows differ only by `sibling_concrete`. (In this variant the label `TRUSTED_DEFS_TOTAL=965`
  counts the un-trusted defs scanned.)
- **A7. S3.** In the scratch `expr_ghost_collections.py`: add
  `from module6_whyml.expressions import ExpressionEmissionMixin` and delete the `_e` declaration.
  Then
  `pycsl.py ... --import-path src/self-annotate/src --no-proof --keep-mlw` → rc=1, `line 1189 ...
  This expression has type PyCSL_Program.emit_ir, but is expected to have type int`. The scratch file
  was reverted afterwards.
- **A8. S4.** `$D/sp4/refine_frame.py` (Base `assigns \nothing`, Sub `assigns self.x`) → rc=1, route
  #278 message. `$D/sp4/refine_ok.py` (frames aligned) → rc=0; `refine_ok.mlw:38` holds
  `goal sub__m_refines_base`.
- **A9. Planes, on the unmodified tree.**
  - `heavy.sh python3 bin/check-trusted-frame-honesty.py --verbose` → rc=0 (273 s): trusted
    0 model-visible / 1 total (`_Unparser.write`); the declarations are absent.
  - `heavy.sh python3 bin/check-trusted-raises-honesty.py --verbose` → rc=0: 67 / 19 declared /
    48 SILENT. Rows 9, 20, 22, 23 are SILENT, matching their definitions.
  - `heavy.sh python3 bin/check-trusted-termination-honesty.py --verbose` → rc=0 (mirror 48).
  - `heavy.sh python3 bin/check-trusted-reasons.py` → rc=0: 408 ↔ 408, unclassified 256.
