# OPEN ROUTE #588 — _to_bool TRUTHINESS OF emit_ir PROJECTOR READS IS DECIDED true
**Status: REPAIRED (driver run #7, executor u43; annotations §7.596). RULE: `if <projected child>:` is `irtru_<proj> <receiver>` -- `true` on the constructors that carry the field, the option's presence on an optional bound, opaque elsewhere; `if v:` on an emit_ir local is `ir_truthy_v v` (IrNone / IrOther undecided).** Opened as: Status: OPEN, Severity 1, pre-existing (run #6 u38 finding; false proofs at base and head). Witnesses witnesses-r584/u38/t01-t03.

## REPAIR (driver run #7, executor u43)
Same repair for routes #596 / #586 / #587 / #588 / #594 (one coherent change, driver run #7, executor u43, branch run7-u43 off 1ffab454c; annotations §7.596; full evidence `getting-better/run7-u43-projectors.md`).
- Witnesses u38 t01-t03 + x06 (`v = x.get("value"); if v:`, the local form): PROVED (false) at base, NOT PROVED at
  head. Corpus 9767-9770; controls 9776-9778 (truthiness through the modelled IrSub / IrAttr arms PROVES).
