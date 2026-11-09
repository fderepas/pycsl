# OPEN ROUTE #583 — `.value` OF AN `ast.Attribute`-TESTED emit_ir VALUE IS LOWERED TO `svalue_of`, THE SUBSCRIPT PROJECTOR (`IrOther ""` ON AN IrAttr), SO THE MODEL DECIDES `isinstance(x.value, ast.Name)` / `x.value.id == ...` FALSE WHERE CPYTHON TAKES THE BRANCH
**Status: OPEN, PRE-EXISTING (present at run6-int54 c914766a6, before capability R1). Severity 1 (a false claim is a theorem of the model). Found by driver run #6 executor lvL while converting the capability-R1 Module5 functions; opened on the driver's instruction.**

## Mechanism
- `expressions.py::_handle_attribute_expr`, the emit_ir branch (gated on `@mutable_state` / a tparam collector):
  `.value` is not in `_EMIT_IR_STR_ATTRS`, `_EMIT_IR_NODE_ATTRS` or (outside `_py_stmt_augassign`, whose scoped entry
  uses the unified `avalue_of`) `_EMIT_IR_HANDLER_ATTR_PROJ`, so it falls to the default `(svalue_of <recv>)`; the
  reflection table `_EMIT_IR_PROJ` maps `"value"` to `svalue_of` too.
- `svalue_of` (preamble, emit_ir theory) is `match e with IrSub v _ -> v | _ -> IrOther ""`: the SUBSCRIPT value. On
  an `ast.Attribute` (an IR class, `_AST_CLASS_TO_IR_KIND["Attribute"] = "Attribute"`, modelled `IrAttr o a`) the
  Python `.value` is the OBJECT `o` (`object_of` / `avalue_of` read it), but the model reads `IrOther ""`.
- Hence after `isinstance(x, ast.Attribute)` (`is_attribute x`), `isinstance(x.value, ast.Name)` lowers to
  `is_var (svalue_of x)` = `is_var (IrOther "")` = false, and `x.value.id` to `name_of (IrOther "")` = `""`. The
  model decides the branch impossible; CPython takes it for `self.a`.

## Witness (user program)
`witnesses-r583/w583_attr_value_svalue.py`: `if isinstance(x, ast.Attribute) and isinstance(x.value, ast.Name): if
x.value.id == "self": return 1` / `return 0` under `ensures \result == 0`. CPython `Em().f(<self.a>)` returns 1.
MEASURED: default model `Verification SUCCESS` (a false claim PROVED) at base c914766a6 (lvL spike,
`witnesses-r1/results/proof.base.p01.log`) and at the lvL head (see EVIDENCE). So this is a false proof, not only a
vacuity gap.

## Where it bites in the mirror
`frontend/Module5_IREmitter.py::_collect_final_registry`, the `self.<attr>: Final[T]` branch (`isinstance(sub.target,
ast.Attribute) and isinstance(sub.target.value, ast.Name) and sub.target.value.id == "self"`): a `#@ assert 1 == 2`
injected there is PROVED (lvL `mres/mutself.log`), so a conversion of that function is vacuous on that path; it stays
`\trusted` (driver decision, run #6). Any other converted function reading `.value` on an Attribute-tested emit_ir
receiver has the same dead path (lvL checked the five R1 conversions: see the run #6 lvL report).

## Repair direction (not built)
Lower `.value` on an emit_ir receiver with the unified `avalue_of` (IrAttr -> object, IrSub -> value) everywhere, as
`_py_stmt_augassign` already does -- or decide by the receiver's tested class; it moves every emission that reads
`.value` on emit_ir (mirror re-proofs owed) and must keep the Subscript path byte-identical where only IrSub is possible.

## EVIDENCE
- `witnesses-r583/w583_attr_value_svalue.py` (CPython: 1 for `self.a`, contract `\result == 0`): default model
  Verification SUCCESS at base c914766a6 AND at the lvL head (191f0624c + docs) -- a FALSE PROOF, not only a vacuity
  gap. typed / store: L3 `unbound type symbol 'array'` (the pre-existing emit_ir gap of those models), so the false
  proof is the default model's. Front end x hoare: EMITTED (no refusal).
- Mirror: `#@ assert 1 == 2` injected in `_collect_final_registry`'s `self.<attr>` branch PROVED (4/4 Valid) and in
  `_union_arm_tag`'s `ast.expr` / `ast.stmt` / `ast.AST` arm PROVED, i.e. both branches are dead in the model; the lvL
  leaf-reachability run (`witnesses-r1/results/leaf-reachability.txt`, one assertion per leaf block, 30 blocks of the
  five R1 conversions) found no other dead leaf. Both functions stay `\trusted` (driver decision).
