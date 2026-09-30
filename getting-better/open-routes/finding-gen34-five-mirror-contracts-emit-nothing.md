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
