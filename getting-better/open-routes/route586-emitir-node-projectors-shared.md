# OPEN ROUTE #586 — emit_ir NODE PROJECTORS SHARED ACROSS CLASSES (left_of / right_of for .dict / .key / .head / .left; sindex_of for .index) DECIDE CPYTHON-LIVE READS
**Status: REPAIRED (driver run #7, executor u43; annotations §7.596). RULE: `.dict/.key/.head/.tail/.left/.right/.lo/.hi/.size/.default` (and the swap-family handler slots, and the scoped annotation-walker `.slice` / augassign `.value`) read the per-constructor `iratt_<f>_of`; the dict view `left/right/index/object/orelse` and `.get("body", {})` likewise; `_EMIT_IR_NODE_ATTRS` is retired.** Opened as: Status: OPEN, Severity 1, pre-existing (run #6 executor u38 finding while repairing #584/#585; false proofs at base and head). Witnesses witnesses-r584/u38/f01-f06 (on run6-u38 / int56). Same class as #583-#585: choose the projector by the receiver's constructor. Left out of u38 because the fix moves every mirror handler.

## REPAIR (driver run #7, executor u43)
Same repair for routes #596 / #586 / #587 / #588 / #594 (one coherent change, driver run #7, executor u43, branch run7-u43 off 1ffab454c; annotations §7.596; full evidence `getting-better/run7-u43-projectors.md`).
- Witnesses u38 f01-f06 + x04 (`.lo` of IsSorted) + x05 (`.set` inside a method named `_handle_set_add_expr`, the
  scoped `left_of` slot) + x07 (`.size` of GhostMake): PROVED (false) at base, NOT PROVED at head. Corpus 9752-9759, 9773.
