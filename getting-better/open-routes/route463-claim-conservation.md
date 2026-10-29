# OPEN ROUTE #463 — A WRITTEN `#@` CLAIM CAN BE SILENTLY DROPPED (redefined def; indented claim block)
**Status: OPEN, Severity 1 (worst kind: "All contracts formally proven" for a file whose only written claim is false).**
Red team 37 (2026-10-29) families F5 / F6; driver re-run on the landed main 33f7ac681 (`scratchpad/rt37/rerun-on-33f7ac681.txt`):
all 6 witnesses rc=0 Verification SUCCESS; CPython breaks the written contract (`VIOLATION contract`).
Witnesses `witnesses-r463/` (6): `e19_r100_second_def_wins.py`, `e20_s105_both_claimed.py` (F5: a second module-level
`def f` replaces the first; the claim written on the first is dropped), `e21_a110_tab_indent_claim.py`,
`e22_t100_four_space_indent.py`, `e22_t101_one_space_indent.py` (F6: a `#@` block indented with spaces or a tab above a
column-0 `def` is treated as a plain comment, so the function is lowered with NO contract), `e21_a106_space_after_hash.py`
(`# @ensures` -- not PyCSL syntax, but a near-miss spelling that should be refused, not ignored).

```
#463 CLAIM CONSERVATION: every `#@` line (and every near-miss spelling `# @`, `#  @`) in the file must be either
     attached to exactly one lowered declaration or refused with a message; a declaration bound twice at module level
     (or in a class body) whose earlier binding carries a claim is refused.
  REPAIR (proposed, fail-closed): count claim blocks at parse time; count claim blocks consumed by the lowering;
  refuse on any difference (orphan / dropped / shadowed). Measure the corpus / mirror cost.
```
