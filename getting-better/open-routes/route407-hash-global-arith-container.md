# OPEN ROUTE #407 — §7.49 (1) "PRIMITIVE ARITHMETIC" (AND BoolOp / IfExp / slice) OVER A CONTAINER GLOBAL IS TAKEN AS HASHABLE
**Status: OPEN, Severity 1.** Red-team round 32 (2026-10-26, probes around the allow-list repairs #392-#402 + R5-str); driver-reproduced on 085ee3dcc (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt32/driver-repro.txt`).
Witnesses `witnesses-r407/`: `b04_global_arith_list.py`, `f29_global_add_lists.py`, `f30_global_or_list.py`, `f31_global_dict_union.py`, `f32_global_set_minus.py`, `f35_global_slice_list.py`, `f36_global_ifexp_list.py`, `q07_global_listdisplay_mul.py`, `q18_global_tuple_add_list.py`, `q17_classattr_list_mul.py`.

```
#407 §7.49 (1) "PRIMITIVE ARITHMETIC" (AND BoolOp / IfExp / slice) OVER A CONTAINER GLOBAL IS TAKEN AS HASHABLE  [slips past #394]
  b04  A = [1]; K = A * 2; {K} PROVED                                                          TypeError
  f29  K = A + B;  f30 K = A or 1;  f31 K = A | {"b": 2} (dict);  f32 K = A - {2} (set);  f35 K = A[:];  f36 K = A if A else (1,)
  q07  K = [1] * 2 (no global operand at all);  q18 K = .. if False else B + [3];  q17 the same in a CLASS body, {C.K}
  (list(..), a comprehension, [*A], sorted(..), a set display, {**A} are refused: q08-q12, q20.)
  (b05 `K = (1, A)` is refused correctly: the tuple source reads its components.)
  REPAIR: arithmetic `+ * | - & ^` with a container operand has the container's class; BoolOp / IfExp is the union
  of the operand classes; a slice of a list / str / tuple is that class; anything else UNKNOWN.
```

## REPAIR (g1, driver run #3, 2026-10-26/27) -- candidate, REFUSAL polarity tightened

RULE (annotations §7.64 (1), translational §T.6.75): in a module / class-body initializer, arithmetic / a unary operator with a
container operand is that container with UNKNOWN elements; a BoolOp / IfExp is the union of its operands; a slice of a list / tuple is
that container, an index of a list / tuple / dict its elements' classes (read-only displays) else UNKNOWN; an attribute / method call /
unary operation over a container is UNKNOWN; a class-body name read in the same body is that binding (`PYCSL-R349-UNHASHABLE-RECORD`).
Witnesses 5996-6005 (b04, f29, f30, f31, f32, f35, f36, q07, q17, q18): PROVED rc=0 at base -> REFUSED rc=1; NEW latent 6016
(`K = A.copy()`, PROVED at base -> REFUSED). Control 6024 (int arithmetic, a read-only display element, a tuple concatenation, an IfExp
of strings, a class-body int product hashed) PROVED at base and candidate.

Measurements (g1 executor, driver run #3; base worktree at 4431ef86f; logs in `getting-better/systematic-soundness-r3/g1-r403-410/`).
One landing for routes #403-#410 (annotations §7.60-§7.64, translational §T.6.71-§T.6.75; inline in `_run_pipeline`, mirror twin
`\trusted`, refusals only, no emission change, ledger unchanged):
- final candidate: root 2441 -> 2449 (+8 controls 6020-6027), 0 MOVED / 0 GONE / 0 APPEARED; pyref 2186 -> 2186 0/0/0; mirrors
  53/53 0/0/0; `pycsl_lib` --no-proof screen identical (104 files, 87 rc 0 / 17 rc 1).
- over-refusal measured and NOT landed (first candidate, `cmp-*-firstcandidate.log`): #406 counting the `__main__` driver GONEs
  root control 5464; #406 counting every unread callee (user-module functions, local callables, unknown methods) and `setattr` for
  hashed values GONEs 6 mirrors (audit_proof, frontend/pure_ast, module6_whyml/expressions, statements, stmt_control_flow,
  proof2why3/parser). The landed rules move nothing.
- census (`bin/refusal-witness-census.tsv`, via `_census_row`): 48 new rows (5970-6014 red-team witnesses, latents 6015 / 6016 /
  6018, #380 coverage 6017); 6 re-measured rows changed (5156 -> S1, 5785-5789 R402 message text); every other REFUSAL row's
  --no-proof message byte-identical base vs candidate (`refmsg-*.tsv`, 1518 rows). Coverage 320 demonstrated / 5 undemonstrated
  (ceiling 5); advice audit: R402 re-audited (hash updated), R405 audited FOLLOWABLE.
- witnesses: 45 red-team witnesses PROVED rc=0 at base (`base-wit-verdicts.tsv`) -> all REFUSED rc=1 on the candidate
  (`cand-verdicts.tsv`); controls PROVED at base and candidate.

Residual: an initializer of no recognised form stays UNDERIVABLE (admitted), as §7.49 records (the full allow-list flip refuses 27
mirrors).
