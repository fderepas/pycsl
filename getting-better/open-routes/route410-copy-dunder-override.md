# OPEN ROUTE #410 — §7.49 (4) copy.copy(x) / copy.replace(x) "HAS x's CLASS" IGNORES __copy__ / __replace__
**Status: OPEN, Severity 1.** Red-team round 32 (2026-10-26, probes around the allow-list repairs #392-#402 + R5-str); driver-reproduced on 085ee3dcc (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt32/driver-repro.txt`).
Witnesses `witnesses-r410/`: `m01_copy_dunder_copy.py`, `m06_replace_dunder.py`.

```
#410 §7.49 (4) copy.copy(x) / copy.replace(x) "HAS x's CLASS" IGNORES __copy__ / __replace__  [slips past #394]
  m01  D.__copy__ returns [1]; {copy.copy(d)} PROVED                                            TypeError
  m06  D.__replace__ returns [1]; {copy.replace(d)} PROVED                                      TypeError
  (__reduce__ / __reduce_ex__ forms m02 / m05 and copy.deepcopy m03 are refused or fail.)
  REPAIR: the source holds only when no class of x's closure defines __copy__ / __deepcopy__ / __replace__ /
  __reduce__ / __reduce_ex__; otherwise the result class is that method's annotated return, else UNKNOWN.
```

## REPAIR (g1, driver run #3, 2026-10-26/27) -- candidate, REFUSAL polarity tightened

RULE (annotations §7.64 (4), translational §T.6.75): `copy.copy` / `copy.deepcopy` / `copy.replace` / `dataclasses.replace` of x has x's
class only when no class a value of x's static class may be (its MRO and every file subclass's) binds `__copy__` / `__deepcopy__` /
`__replace__` / `__reduce__` / `__reduce_ex__` (and no such name is stored dynamically); otherwise UNKNOWN
(`PYCSL-R349-UNHASHABLE-RECORD`).
Witnesses 6013-6014 (m01, m06): PROVED rc=0 at base -> REFUSED rc=1. Control 6027 (`copy.copy` of a frozen dataclass) PROVED at base
and candidate.

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

Residual: a `__deepcopy__` override is refused earlier anyway (`copy.deepcopy` is not a no_exception-known operation).
