# OPEN ROUTE #587 — emit_ir STRING PROJECTORS SHARED ACROSS CLASSES (.op of UnaryOp, .name of InGlobals, .var of ArrayLen, .ctor of CtorTest) DECIDE CPYTHON-LIVE READS
**Status: REPAIRED (driver run #7, executor u43; annotations §7.596). RULE: the string fields `.op/.name/.var/.ctor/.func/.label/.base/.base1/.base2/.arr` and the dict view `name/attr/field/func/ctor/op` / string `.get("value"[, ""])` read the per-constructor `iratts_<f>_of` (opaque where no constructor carries the field), not `op_of`/`name_of`/`func_of`/`value_of`; `.kind`/`.id`/`.attr` keep `kind_of`/`name_of`.** Opened as: Status: OPEN, Severity 1, pre-existing (run #6 u38 finding; false proofs at base and head). Witnesses witnesses-r584/u38/f09-f14.

## REPAIR (driver run #7, executor u43)
Same repair for routes #596 / #586 / #587 / #588 / #594 (one coherent change, driver run #7, executor u43, branch run7-u43 off 1ffab454c; annotations §7.596; full evidence `getting-better/run7-u43-projectors.md`).
- Witnesses u38 f09-f14 + x01 (`.label` of At) + x02 (`.base` of Valid): PROVED (false) at base, NOT PROVED at head.
  Corpus 9760-9766. Two further probes of the same lowering, x03 (dict `.get("attr") == .get("name")` of a Var) and x10
  (string `.get("value")` of a Number), were NOT PROVED at base already (not false proofs; kept as scratch probes,
  `scratchpad/u43/wx/`), NOT PROVED at head.
