# Wall: raw-`Dict[str,Any]` emitter param → emit_ir-ADT bridge (the foundational Module6 enabler)

**Status:** state-of-the-art wall statement (U). Awaiting an INDEPENDENT fable review with an oracle artifact.
**Base loop:** self-tcb-reduction, branch ghost-assign-bc6, HEAD 901cb301, count 1041, ledger 3.
**Author:** driver (may be tainted — the fable reviewer must independently CONFIRM/REFUTE from repo + oracle).

## 1. Context — the reachable-cheap frontier is exhausted; this is the foundational Module6 wall
The entire Module5 AST→IR lowering surface is converted; the Module6 WhyML emitters (`module6_whyml/
expressions.py` ~57 trusted, `statements.py` ~61) are the remaining cluster. A probe + independent triage found
the reachable-now subset is EMPTY at the current tool level, blocked uniformly by ONE keystone limitation. Three
builds are needed (this wall is #1, the prerequisite): (1) THIS raw-dict→ADT bridge; (2) array-element-local
typing (`expr.get("args")[i]`); (3) iteration/fold handling. This report is ONLY about #1.

## 2. The claim to adjudicate (CONFIRM or REFUTE with an oracle artifact)
**CLAIM A (the keystone limitation):** the mirror's "model an IR-node param as the `emit_ir` ADT" keystone fires
ONLY for a param annotated `"ExprIR"` AND whose body calls `.to_dict()` (the Phase-B `_handle_*_expr` handlers,
already converted). A trusted `-> str` emitter that takes a raw `Dict[str,Any]` param (or an `"ExprIR"` param but
does `ir.get("type")`/`ir["left"]` DIRECTLY without `.to_dict()`) is modeled as a WhyML `map` — so
`ir.get("type")` → an abstract `*_get_str`/`contains_check` (NOT `kind_of`), `ir["left"]` → `subscript_get`, and
crucially, when such a value is passed to a sibling emitter whose trusted stub is typed `ExprIR` (= emit_ir ADT),
it TYPE-ERRORS: `This expression has type int, but is expected to have type PyCSL_Program`. Confirmed on
`_e`, `_expr_to_whyml_string_ctx`, `_typeddict_field_access`, etc. (0 converted last round).

**CLAIM B (the fix + its corpus-inertness — the crux):** make the dict→ADT keystone ALSO fire for an `"ExprIR"`-
annotated param that reads via `.get("type")`/`ir["field"]`/`ir.get("field")` WITHOUT a `.to_dict()` call — i.e.
lower `.get("type")` → `kind_of`, `ir["left"]`/`ir.get("value")` → the emit_ir projectors (`left_of`/`svalue_of`/
…), for a bare `"ExprIR"` param. Since `"ExprIR"` is a MIRROR-emitter annotation that NO reference-corpus program
uses, this keystone-trigger change is plausibly CORPUS-BYTE-DIFF-0 (like the str_of_int fix, 901cb301, which was
emitter-only). IF SO it is a bounded tool-recognizer fix that unlocks ~4-5 named-field emitters immediately
(`_expr_to_whyml_string_ctx`, `_handle_ifexpr_expr`, `_typeddict_field_access`, `_recognize_field_decode_idiom`, …)
and is the PREREQUISITE for the array-element (#2) and iteration (#3) builds. IF corpus programs DO exercise this
lowering path, it is a corpus-affecting change (bigger, authorize-first).

## 3. The question for fable (Gate R)
1. **CONFIRM CLAIM A** with an oracle artifact: retype one raw-dict emitter's param to `"ExprIR"`, emit its `.mlw`
   (`pycsl … --keep-mlw`), and show `ir.get("type")` lowering to an abstract `*_get`/`map` op (NOT `kind_of`) and/or
   the `int vs PyCSL_Program` type error at the sibling-emitter call — i.e. that `.to_dict()` is the trigger.
2. **CONFIRM or REFUTE CLAIM B (corpus-inertness) — decisive.** Where is the keystone (grep `src/pycsl/module6_whyml/`
   + the mirror-modeling for how `"ExprIR"` params + `.to_dict()` become emit_ir)? Can the trigger be broadened to
   bare `.get("type")`/subscript on an `"ExprIR"` param CORPUS-BYTE-DIFF-0 (run `bin/byte-diff-sweep.sh`; do any
   corpus programs have `"ExprIR"` params / hit this path)? Or does it perturb corpus emission?
3. **VERDICT: CHEAP-BREAKABLE** (corpus-inert keystone-trigger broadening → est. yield ~4-5 + prerequisite; sketch
   the make-or-break spike: broaden the trigger, convert one named-field emitter, whole-file proof + byte-diff 0) /
   **BIG-BUILD** (corpus-affecting, authorize-first) / **BOUNDARY** (the raw-dict helpers have other blockers — e.g.
   the sibling emitters are themselves trusted-`ExprIR` stubs whose contracts don't propagate, or getattr-self-dict
   reflection like `_current_self_type in _mutable_state_classes` — beyond the keystone).

## 4. Constraints (base-loop L)
Fixed contract shape; 3-axiom ledger unchanged; corpus byte-diff 0 is the make-or-break for CHEAP; whole-file proof
is the gate (`--fun` unreliable — see `config/skills/self-tcb-reduction/emit-ir-conversion-lessons.md` §1). Beware
CROSS-MIXIN FACADE STUBS (a `\trusted` stub whose real body is in another file — do not convert it in the wrong file).
