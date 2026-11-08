# OPEN ROUTE #463 — A WRITTEN `#@` CLAIM CAN BE SILENTLY DROPPED (redefined def; indented claim block)
**Status: REPAIRED (executor cc1, driver run #3, 2026-10-29), Severity 1 (worst kind: "All contracts formally proven" for a file whose only written claim is false).**
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

## REPAIR (executor cc1, driver run #3, 2026-10-29, off a9eac4a08; annotations §7.240, translational §T.6.250)

Fail-closed accounting in the two `\trusted`-twin methods both pipelines share (no new def in a mirrored file, no axiom):
- `Module1_Ingestor.process` (token level, before / after `_Harvester.run`): a `#@` comment after code on its line is
  REFUSED; a NEAR-MISS (`#`, spaces/tabs or more `#`, `@`, then a directive keyword or a `\`-name: `# @ensures`,
  `#\t@requires`, `##@assert`) is REFUSED (prose `# @dataclass` and a quoted `#     #@ ...` are not near-misses);
  then every own-line `#@` comment is accounted for: a FOOTER held by a statement that is not the last of a child suite
  (the F6 shape: an indented block above a column-0 `def` lands on the previous `import`'s footer, which `_emit_suite`
  never emits) is REFUSED; a module header no def / class / loop / `with` consumes is REFUSED (module-scope prefixes
  excepted); a count mismatch with an indented `#@` in the end-of-file tail is REFUSED (the all-column-0 tail is the
  existing end-of-file rule's, message unchanged).
- `Module3_Weaver.process`: in the module and every class body, a name bound 2+ times whose NON-LAST binding is a def /
  class carrying a `#@` claim is REFUSED (property accessor chains and `@overload` chains exempt; an unclaimed earlier
  binding is fine -- control 7194); a statement-level directive (`assert` / `ghost` / `label` / `check`, a loop
  invariant, `critical`) on a statement outside every function body (module level, class body, `__main__` block --
  never lowered; measured PROVED for `x = 1; #@ assert x == 2`) is REFUSED. (Two extractions on one line, which
  `contracts_map` would collapse, cannot arise from `_assign`; no check is spelled for it.)
- The mirror's own shadowed claim: `frontend/ir_resolve.py` defined `_contract_referenced_var_names` TWICE (live and
  mirror; the claimed first one is dead in CPython). The dead first def was deleted in both; the mirror emission is
  byte-identical (the model already kept the last def).

Witnesses (expected FAIL, all REFUSED; PROVED at base unless noted): 7180 / 7181 (F5: e19 / e20), 7182 / 7183 / 7184
(F6: e21_a110 / e22_t100 / e22_t101), 7185 (`# @ensures`, e21_a106), 7186 (trailing `#@`), 7187 (over-indented body
`#@ assert`), 7188 (mixed-indent end-of-file tail), 7189 (header with no consumer), 7190 (module-level `#@ assert`),
7191 (`__main__` `#@ assert`), 7192 (claimed class rebound; base FAILED only on a Why3 duplicate symbol), 7193
(`#\t@requires`; base FAILED with no hint the precondition was written). Controls (PROVED at base and candidate):
7194 (unclaimed def rebound by a claimed one), 7195 (prose / quoted comments), 7196 (trailing body `#@ assert`, a claim
between a decorator and its def), 7197.

OVER-REFUSAL COST (measured): front-end census (Module1 + Module3 only) over 5194 files -- the 4520 + 26 corpus,
2217 python-reference, negative, conformance, 53 mirror and `pycsl_lib` -- identical OK / ERR verdicts and messages
at base and candidate except ONE file: the mirror's `frontend/ir_resolve.py` (the dead duplicate def above, repaired in
the source, not by loosening). Corpus / pyref: 0 newly refused files (byte-diff 0 GONE in both trees); mirror 53 / 53
emitting, 0 MOVED.

## RESIDUALS
- The accounting is at the attachment layer (every `#@` line reaches an anchor whose kind consumes it -- with route #34's
  `_ACCEPTS` table -- or is refused). It does not trace each clause through Module 5 / 6 lowering to an emitted goal;
  `bin/check-clause-survival.py` remains that plane.
- A near-miss is keyed on the directive keyword list; a misspelt keyword after `# @` (`# @ensure`) is still a comment.
