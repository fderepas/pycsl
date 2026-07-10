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
