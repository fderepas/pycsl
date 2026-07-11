# Post-M1 go/no-go census (2026-07-10) — the M2 recognizer build is a real project, not a quick win

*The measure-before-build gate `m1-size-rename-project.md` §6 mandates before the M2 recognizer build. M1
(the `size`-rename, committed `63f48806`) removed the `@mutable_state`+pyval `size` COLLISION. This census
measures what M1 actually unblocks for the flat-`Dict[str,str]` reader cluster in `TypeInferenceMixin`.*

## Method
Applied the M1-enabled full scaffold to the mirror `TypeInferenceMixin` (`@mutable_state @dataclass` + the
self-field decls) — now type-checkable post-M1 (was "Symbol size is already defined"). Then (1) re-proved
the 4 already-VERIFIED methods under the scaffold (regression check), and (2) ported a reader candidate to
measure its first blocker. `--fun` whole-body proofs; reverted.

## Findings

### 1. `@mutable_state` on `TypeInferenceMixin` REGRESSES an existing verified method (a real cost)
Under the scaffold: `_val_is_bool` ✓, `_bool_ir_to_int_wrap` ✓, `_collect_tuple_array_locals` ✓ — but
**`_split_tuple_type` type-FAILS**: `types.mlw:448 This expression has type seq.Seq.seq string, but is
expected to have type array.Array.array 'mu` — the `@mutable_state` **seq-model** changes its `List[str]`
lowering (seq vs array). So flipping `@mutable_state` on the mixin (required for the getattr-self-field
readers) is NOT free — it regresses `_split_tuple_type`, which must be repaired (a known seq/array-boundary
class, but additional work, and a +0/−? net until fixed).

### 2. Readers still need the UNBUILT recognizers (M1 removed the collision, not the recognizer gap)
`_rhs_yields_map` ported under the scaffold still fails: `types.mlw This expression has type string, but is
expected to have type int` — the **param `Dict[str,Any]` `.get("type")` collapse** (needs the unbuilt A2
param-TypedDict-view). Consistent with the earlier reader-census: every cluster reader bottoms out in an
unbuilt recognizer —
- `_rhs_yields_array`/`_rhs_yields_map`/`_first_assign_kind`: **A2** (param TypedDict-view) + set-membership.
- `_call_return_whyml_type`: **A3** (rpartition) + **A4** (option-return) + **U** (union-return) +
  getattr-field + string-`or`-chain.
- `_field_type_for`/`_callable_tag_to_whyml`: **nested-dict** projection.
- `_field_type_of`: emit_ir-attr + Gap-C `or`-`{}`.

## Verdict: NO-GO for a cheap post-M1 win; the M2 build is a deliberate multi-recognizer project
M1 was the necessary structural prerequisite (collision removed, `@mutable_state` now viable), but the
**reachable-with-existing-recognizers count is 0**: converting even one cluster reader requires the full
M2 recognizer set (A2/A3/A4/U + getattr-field + string-`or`-chain + nested-dict, per method) PLUS repairing
the `_split_tuple_type` `@mutable_state` seq/array regression. That is the `m2-reader-emitter-build.md`
project — a multi-session recognizer build, correctly gated as such, NOT a squeeze-loop increment.

**Honest campaign state:** the reader frontier's bounded-increment supply is exhausted at the 1 banked −1
(`_is_float_expr`). M1 unblocked the *collision* but the *recognizer* cost is unchanged and large. The M2
build is worth doing only as its own scoped initiative (est. 5+ recognizers + 1 regression repair to land
the first −1, then the cluster rolls). Recommend: pursue M2 only under an explicit multi-session mandate;
otherwise the reader cluster stays leave-trusted with M1 banked as the enabling prerequisite for when M2 is
undertaken.

## orelse_of / IrIfExpr increment — scope measured (2026-07-10): a sanctioned mini-M1
`_rhs_yields_map`'s IfExpr arm recurses on `.get("body")`/`.get("orelse")`. The emit_ir ADT has NO
`IrIfExpr` constructor (IfExpr → `IrOther`), so `body_of`/`orelse_of` would return the sentinel and the
`variant { size val_ir }` FAILS (no size-decrease). Termination needs a real `IrIfExpr emit_ir emit_ir`
constructor. Measured consequences:
- **No new axiom / no cert** — adding a constructor follows the `IrBinOp` precedent (git shows IrBinOp's
  addition never touched `src/formal-semantics/`; emit_ir is not cert-referenced). Ledger stays 3.
- **NOT byte-diff-0** — the emit_ir theory block is emitted IDENTICALLY across all 15 corpus emit_ir
  programs (1 distinct `type emit_ir` line); adding `IrIfExpr` grows it → all 15 change. Semantics-
  preserving (additive constructor they don't use) but a **sanctioned shared-theory change** requiring the
  M1 discipline: diff-review = exactly-the-additive-constructor, then re-prove the 15 affected programs.
- **Build = mini-M1:** IrIfExpr (constructor + kind_of arm + is_ifexpr + body_of/orelse_of + size arm +
  size_body_dec/size_orelse_dec lemmas) → `_EMIT_IR_PROJ` "body"/"orelse" (disambiguate IfExprExpr from
  `stmts_of`) → sanctioned 15-program re-proof → convert `_rhs_yields_map` (−1). Reusable: `orelse_of`
  also unblocks the `_is_string_expr` IfExpr arm. Best done as a focused increment with the M1 discipline.

### orelse_of mini-M1 — REFINED: the `body`/`stmts_of` disambiguation is the HARD blocker (2026-07-10)
Deeper measurement of the mini-M1 found a SECOND, genuinely-hard sub-problem beyond the sanctioned IrIfExpr
theory change: `_EMIT_IR_PROJ["body"]` = `stmts_of` (`array int`, the If/For/While/Try stmt-list), but an
IfExpr's `.get("body")` must be a SCALAR `body_of` (`emit_ir`). The two collide on the key `"body"` with
DIFFERENT WhyML types. The existing context-override precedent (`"value_of" if key=="value"`,
`"svalue_of" if key=="pattern"`) is KEY-based — but `body` is ambiguous by key, and the receiver's node
kind is DYNAMIC (a param, not statically IfExpr). So disambiguation needs EXPECTED-TYPE-driven lowering
(the `.get("body")` result flows into an `emit_ir`-expecting recursive `_rhs_yields_map` call) — genuinely
new bidirectional-typing recognizer machinery, NOT a mechanical projector add. Combined with the sanctioned
IrIfExpr theory change (15-program re-proof), the orelse_of increment is a substantial build with a hard
core — best undertaken as a dedicated focused session, not a tail-of-session increment. `_rhs_yields_map`
stays trusted pending it.

### Cross-file ExprIR-reader census (2026-07-10) — REFUTED: dependency stubs are fidelity-blocked
Censused `statements.py` (already `@mutable_state`) trusted ExprIR-reader stubs. A triage `--fun` sweep
flagged `_field_label` + `_val_is_bool` as "convertible", but the FULL gate battery refutes them: the
fidelity gate (`self-annotate-mirror-check.sh`) errors *"un-trusted mirror def not in source:
StatementEmissionMixin._field_label"*. Root cause: these are **dependency stubs** — `_field_label` is
DEFINED on `ExpressionEmissionMixin`, `_val_is_bool` on `TypeInferenceMixin`; the live
`StatementEmissionMixin` defines NEITHER (it inherits/mixes them). A mirror class can only un-trust a
method its LIVE class actually DEFINES; a same-class live body must exist for fidelity. So a class's
trusted stubs for methods defined elsewhere are **structurally unconvertible in that file** (the −1 must be
taken where the method is DEFINED, not where it is USED). The census's other 4 candidates are the same
dependency-stub class (doubly-blocked: fidelity + a recognizer gap). Consequence: the byte-0 cheap-win
supply via cross-file dependency stubs is EMPTY; the only genuine statements.py targets are the
StatementEmissionMixin-DEFINED handlers (`_handle_*_stmt`, `_stmts_to_whyml` — large), and the reader
cluster's remaining −1s are all behind the mini-M1 (orelse_of) or nested-dict. Lesson: census by
DEFINING-class, not using-class.

### _is_string_expr post-orelse_of probe (2026-07-10) — IfExpr arm CLEARED, next blocker = getattr-None-default
Ported _is_string_expr (238-line ExprIR reader) after the orelse_of mini-M1 landed. CONFIRMED: the IfExpr
arm now emits `self__is_string_expr_1 (body_of ir)` / `(orelse_of ir)` — orelse_of unblocked it (the
earlier `ir_get_2 <hash>` int-collapse is gone). BUT --fun hits a NEXT blocker (expressions.mlw:593
"type int, expected string"): the same IfExpr guard's `getattr(self,"_current_self_type",None) in
getattr(self,"_mutable_state_classes",set())` lowers the set-membership KEY to `Map.get ... (0)` (int) —
the `getattr(self,"<str-field>",None)` with a NONE default collapses the string field to int. Distinct
recognizer gap: **getattr-self-field with None-default on a STRING field, used as a set-membership key**.
_is_string_expr's 238 lines (G1/G2 record.get, str-value methods, FString, Attribute/FieldGet, str-or-chain)
likely hold further blockers past this. So _is_string_expr is NOT a clean -1 post-orelse_of — it needs the
getattr-None-default-string recognizer next (and a full port-to-first-blocker sweep to enumerate the rest).
Stays trusted. Reader-cluster remaining -1s all still need a NEW recognizer (nested-dict / getattr-None /
A2 / A3-A4-U / stmt-walker).
