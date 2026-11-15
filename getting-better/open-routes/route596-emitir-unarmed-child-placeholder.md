# OPEN ROUTE #596 — AFTER A TEST OF AN IR NODE'S CLASS, A CHILD READ THAT NO CONSTRUCTOR ARM CARRIES (IfExpr .test, Forall/Exists .body, DictComp/MapValueIs .value, Lambda .body, ProjExpr .tuple; gated clause constructors Ensures/Requires/invariants .expr, GhostAssignDecl, GhostArraySetDecl, Proj; every StmtIR receiver) READS THE IrOther "" PLACEHOLDER, SO THE MODEL DECIDES A BRANCH CPYTHON TAKES
**Status: REPAIRED (driver run #7, executor u43; annotations §7.596). RULE: a read on an emit_ir value that no constructor arm of the receiver carries is an OPAQUE `iratt[s]_<f>_unk e` / `irget_<k>_unk e` (a `val function` of the receiver, decided by nothing), never the `IrOther ""` placeholder; the arms are generated from `_IRNODE_CTORS` + the ADT (IrForall/IrExists `.body`, IrDictComp `.key`/`.value`, the comprehension `.elt` added).** Opened as: Status: OPEN, Severity 1, pre-existing (red team rt57 F1, 44 default-model false proofs; every exemplar checked (19) also proves on the pre-run-#6 base 822621340). Same class as #583-#588: an unmodelled child must be an opaque read (or refused), never the placeholder; the attribute and the dict view (.get("value", {})) are both affected. Witnesses witnesses-r596/; full material /home/fabrice/git/pycsl/scratchpad/rt57 (FINDINGS.txt, families.txt).

## REPAIR (driver run #7, executor u43)
Same repair for routes #596 / #586 / #587 / #588 / #594 (one coherent change, driver run #7, executor u43, branch run7-u43 off 1ffab454c; annotations §7.596; full evidence `getting-better/run7-u43-projectors.md`).
- `transpile`'s field-projector splice: every `iratt_<f>_of` / `iratts_<f>_of` ends `| _ -> <name>_unk e` with
  `val function <name>_unk (e: emit_ir) : ...` declared beside it; `irget_value_of` / `irget_lower_of` /
  `irget_upper_of` likewise (`expressions.py::_EMIT_IR_FIELD_PROJ_DEFS`). So after `x.kind == "IfExpr"` (an
  `IrOther "IfExpr"` or an `IrIfExpr` without a test) `x.test` is opaque, and every StmtIR receiver (`x.kind ==
  "Assign"` admits only `IrOther "Assign"`) reads opaque children.
- Witnesses: the 44 rt57 F1 probes (`scratchpad/u43/w596/`, copied from `scratchpad/rt57/g1800`) all PROVED (false)
  at base 1ffab454c (re-measured after the reboot) and are NOT PROVED at head (postcondition Timeout, no type error);
  corpus 9740-9751 (expected FAIL). Typed / store: see the evidence doc.
