# FINDING (gen #34): FIVE CONVERTED MIRROR METHODS EMIT `requires { true } ensures { true }` AND NOTHING ELSE

**Status: VERIFIED as a measurement, CAUSE NOT YET LOCALISED, no repair built.** Not a soundness route
as it stands (a missing postcondition proves LESS, and a missing `writes` on a `let` lets Why3 infer the
effect rather than believe an empty one) — but it is a **claim the mirror asserts and the artifact never
proves**, in the layer whose whole purpose is IR-construction faithfulness.

## THE MEASUREMENT (mine, not inherited — the probe that raised it got the discriminator wrong)

`src/self-annotate/src/frontend/Module5_IREmitter.py` carries **74** clauses of the form
`#@ ensures \result["type"] == "<Kind>"`. The emitted `frontend__Module5_IREmitter.mlw` carries **69**
`kind_of result`. 74 − 69 = **5**, and the five are named:

    pycsltojsonemitter___py_expr_compare      #@ ensures \result["type"] == "BinOp"
    pycsltojsonemitter___py_expr_genexp       #@ ensures \result["type"] == "GenExp"
    pycsltojsonemitter___py_expr_listcomp     #@ ensures \result["type"] == "ListComp"
    pycsltojsonemitter___py_expr_setcomp      #@ ensures \result["type"] == "SetComp"
    pycsltojsonemitter___py_expr_dictcomp     #@ ensures \result["type"] == "DictComp"

**AND IT IS NOT ONE CLAUSE, IT IS THE WHOLE CONTRACT BLOCK.** Emitted side by side, a keeper and a
dropper from the SAME mutually-recursive `with` group, same emitted return type `emit_ir`:

    with pycsltojsonemitter___py_expr_unaryop (self: pycsltojsonemitter) (expr: unaryop) : emit_ir
      requires { true }
      ensures  { ((kind_of result) = "UnaryOp") }
      diverges
      ensures  { self._final_registry = old self._final_registry }
      ensures  { self._fresh_var_counter = old self._fresh_var_counter }
      ensures  { self._m5_dc_unknown = old self._m5_dc_unknown }
      ensures  { self.program_ir = old self.program_ir }
      writes {  }

    with pycsltojsonemitter___py_expr_compare (self: pycsltojsonemitter) (expr: py_compare_node) : emit_ir
      requires { true }
      ensures  { true }
    =
      (IrBinOp (pycsltojsonemitter___py_op_to_str self (compare_op0_ast expr)) …)

So the dropper loses its postcondition, its four frame-preservation `ensures`, AND its `writes { }` —
which is the clause that CHECKS `#@ assigns \nothing` against the body on a concrete `let`. **Both of
this method's declared contract clauses are unenforced, and the mirror source reads as if they were
guarantees.**

## THE DISCRIMINATOR IS *NOT* THE RETURN ANNOTATION — THAT HYPOTHESIS IS REFUTED

The obvious story is the mirror's int-erased return annotation: all five droppers are annotated
`-> int` in the mirror while the LIVE twins are `-> Dict[str, Any]`, and `_py_expr_list` (a keeper) is
`-> Dict[str, Any]` in both. That would make it the backlog-#60a guard at
`src/pycsl/module6_whyml/functions.py:2607-2624`, whose condition is
`_emitting_val_contract and _func_return_type != "emit_ir"`.

**It is refuted by measurement.** Of the seven mirror defs carrying such a clause and annotated
`-> int`, **`_py_expr_unaryop` and `_py_expr_binop` are also `-> int` and KEEP the clause** (five
emitted `ensures` each). So `-> int` is necessary-looking and not sufficient, and any repair derived
from it would be built on a refuted premise.

What separates the two groups, unexplained: the two `-> int` KEEPERS both carry `#@ \diverges` and the
five droppers do not. That is a correlation over n = 7 and is the next thing to test, **not** a cause.

## THE MIRROR RETURN ANNOTATIONS HAVE DRIFTED, INDEPENDENTLY OF THE CAUSE

Verified against the live source: **seven** `_py_expr_*` mirror defs say `-> int` where the live says
`-> Dict[str, Any]`. That is the exact shape `bin/check-mirror-field-parity.py` was built for on
FIELDS — an int-erasure that is weaker, not unsound — and no plane covers it for RETURN types
(`check-mirror-signature-drift.py` is green at this HEAD). Retyping them is a candidate repair *for the
drift*, and it is worth doing on its own merits; it must not be presented as the fix for the dropped
contracts until the cause above is actually located.

## WHAT TO DO NEXT, IN ORDER

1. **Localise the cause** by instrumenting the emission of one dropper, not by reading the guard. The
   campaign's rule applies: a mechanism story is a hypothesis separate from the drop's existence, and
   this one already ate a wrong discriminator.
2. **Test the `\diverges` correlation** by adding `#@ \diverges` to ONE dropper in a scratch worktree
   and re-emitting (`bin/mirror-emit-sweep.sh`, 52 s). Cheap, and it either kills or promotes the
   hypothesis in one pass.
3. **Then** decide the repair. If the five clauses start being emitted they must PROVE; if they do not,
   that is a faithfulness failure worth more than the clause.

---

# CAUSE LOCALISED, AND IT IS A DEFECT **CLASS** OF 25 EMITTERS, NOT ONE METHOD

`src/pycsl/module6_whyml/functions.py:4438-4451`, `_expr_bespoke_body`:

    return [
        f"  let {name} (self: {cls}) (expr: {param_ty}) : emit_ir",
        "    requires { true }",
        "    ensures  { true }",
        "  =",
        f"    {body_expr}",
    ]

It never reads `func`'s contract. **HARD-CODED.** And the mirror's own comment beside
`_py_expr_compare` names the mechanism in advance — *"A bespoke Module6 lowering
(`functions.py _emit_py_expr_compare_bespoke`, keyed on the method name under `_uses_stmt_ir`) emits
it FAITHFULLY as the certified `IrBinOp` ctor"* — it says FAITHFULLY of the BODY and says nothing
about the contract, and nobody asked.

## TWO HYPOTHESES REFUTED BEFORE THE CAUSE WAS FOUND — BOTH WOULD HAVE PRODUCED A WRONG REPAIR

1. **The int-erased return annotation** (the delegated probe's discriminator): refuted, because
   `_py_expr_unaryop` and `_py_expr_binop` are ALSO `-> int` in the mirror and KEEP the clause.
2. **`#@ \diverges`** (my own, from the n = 7 correlation): refuted by measurement in a disposable
   worktree — adding `#@ \diverges` to `_py_expr_compare` and re-emitting left the block at
   `requires { true } / ensures { true }`, and **dropped the `diverges` clause too.** That is what said
   the WHOLE contract block is bypassed rather than one clause filtered.

## THE CENSUS, WHICH IS THE PART THAT MATTERS

Every one of the **25** `*_bespoke` emitters in `functions.py` hard-codes `requires { true }
ensures { true }` (or delegates to `_expr_bespoke_body`, which does) and **not one of them reads the
source contract.** Mirror methods reaching a bespoke dispatch key: **23**. Of those, **TWELVE carry a
non-trivial clause that is silently discarded:**

| mirror method (all `frontend/Module5_IREmitter.py`) | discarded clause |
|---|---|
| `_py_expr_compare` | `#@ ensures \result["type"] == "BinOp"` |
| `_py_expr_dictcomp` | `#@ ensures \result["type"] == "DictComp"` |
| `_py_expr_genexp` | `#@ ensures \result["type"] == "GenExp"` |
| `_py_expr_listcomp` | `#@ ensures \result["type"] == "ListComp"` |
| `_py_expr_setcomp` | `#@ ensures \result["type"] == "SetComp"` |
| `_py_stmt_assign` | `#@ assigns ir_stmts` |
| `_py_stmt_delete` | `#@ assigns ir_stmts` **and** `#@ raises PyCSLSemanticError when True` |
| `_py_stmt_match` | `#@ assigns ir_stmts` |
| `_py_stmt_try` | `#@ assigns ir_stmts` |
| `_py_stmt_with` | `#@ assigns ir_stmts` |
| `_emit_ghost_assign` | `#@ assigns self._fresh_var_counter` |
| `_synthesize_overload_guard` | `#@ assigns self._fresh_var_counter` |

>>> **A BESPOKE HAND-WRITTEN LOWERING THAT HARD-CODES ITS CONTRACT DISCARDS THE SOURCE'S, AND THE
>>> MIRROR GOES ON READING AS IF IT WERE PROVED.** Every one of these twelve is WEAKER than declared,
>>> so nothing false is derived and the class is FAIL-CLOSED — but twelve declared clauses in the
>>> mirror's IR-construction layer are not obligations, and five of them are the IR-faithfulness
>>> postconditions that are the entire point of that layer.

**AND THERE IS A PLANE THAT ALREADY MADE EXACTLY THIS ARGUMENT ONE STEP AWAY.**
`bin/check-emit-ir-arm-postconditions.py` exists because an emit_ir always-present arm was *"sound only
while the methods that REACH them carry no real postcondition, and until now that was PROSE"*. The
bespoke lowerings are the same argument with the same missing gate, and nothing checks them.

## THE REPAIR, IN TWO PARTS — NEITHER BUILT

1. **THE GATE (cheap, no prover):** assert that every mirror method reaching a bespoke dispatch key
   carries no clause stronger than `True`, with the twelve above as a ratcheted baseline that may only
   SHRINK. Negative-test it by adding a real `ensures` to a thirteenth. This makes the class
   fail-closed BY CONSTRUCTION instead of by luck, and it can land before the real fix.
2. **THE REAL FIX:** have the bespoke scaffolds emit the declared contract instead of `true`. Then the
   five faithfulness postconditions become obligations — and **if they do not prove, that is a
   faithfulness failure worth more than the clause.** `kind_of (IrBinOp …) = "BinOp"` should follow from
   the emit_ir theory that already discharges 69 siblings. Price it with `bin/mirror-emit-sweep.sh`
   (52 s) first; the scaffolds' own comments claim corpus-inertness ("each caller keys on a named
   mirror method under `_uses_stmt_ir`") — **verify that, do not inherit it.**
