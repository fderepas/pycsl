# OPEN ROUTE #594 — `child.value is None` ON AN ast.AnnAssign (class-body / module walk) IS DECIDED BY THE MODEL WHILE CPYTHON TAKES THE OTHER BRANCH
**Status: REPAIRED (driver run #7, executor u43; annotations §7.596). RULE: `child.value is None` on a raw `ast.stmt` (pyast_stmt walk) is `match child with PSAssign _ _ -> false | _ -> stmt_value_isnone_unk child end` -- an `ast.Assign` always carries its value, every other statement's presence is opaque.** Opened as: Status: OPEN, Severity 1, pre-existing (red team rt56; proves on 822621340 and int55). Related to route #583's F3 (.value of a pyast_stmt). Witnesses witnesses-r594/.

## REPAIR (driver run #7, executor u43)
Same repair for routes #596 / #586 / #587 / #588 / #594 (one coherent change, driver run #7, executor u43, branch run7-u43 off 1ffab454c; annotations §7.596; full evidence `getting-better/run7-u43-projectors.md`).
- Witnesses hk1702 / hk1725: PROVED (false) at base, NOT PROVED at head (postcondition Timeout). Corpus 9771-9772.
  No mirror file emits the shape (the mirror sweep is unchanged by this arm).
