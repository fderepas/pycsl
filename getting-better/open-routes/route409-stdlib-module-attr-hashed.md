# OPEN ROUTE #409 — §7.49 (3) A STANDARD-LIBRARY MODULE ATTRIBUTE IS ADMITTED AS A HASHED VALUE WITHOUT CLASSIFYING IT
**Status: OPEN, Severity 1.** Red-team round 32 (2026-10-26, probes around the allow-list repairs #392-#402 + R5-str); driver-reproduced on 085ee3dcc (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt32/driver-repro.txt`).
Witnesses `witnesses-r409/`: `b21_stdlib_mutable_obj.py`, `f37_from_os_environ.py`, `f43_global_stdlib_attr.py`, `f38_sys_argv.py`, `f40_logging_root_handlers.py`, `q13_environ_copy.py`.

```
#409 §7.49 (3) A STANDARD-LIBRARY MODULE ATTRIBUTE IS ADMITTED AS A HASHED VALUE WITHOUT CLASSIFYING IT  [slips past #394]
  b21  {os.environ}  f37 from os import environ; {environ}  f43 E = os.environ; {E}  f38 {sys.argv}
  f40  {logging.root.handlers};  q13 {os.environ.copy()} (a method call on the stdlib object)    TypeError
  (b22 {sys.path} and f39 {sys.modules} are refused by the imports layer.)
  REPAIR: "by the real object" must read the attribute's value: type(value).__hash__ is None (or the object is a
  container) => unhashable; a dotted chain through a non-module object, or an attribute not resolvable => UNKNOWN,
  refused in a hashing position.
```

## REPAIR (g1, driver run #3, 2026-10-26/27) -- candidate, REFUSAL polarity tightened

RULE (annotations §7.64 (3), translational §T.6.75): a standard-library object is classified by its real class: `__hash__ = None`, a
mutable container (`MutableMapping` / `MutableSequence` / `MutableSet`, `list` / `dict` / `set` / `bytearray`) or a raising hash is
UNKNOWN (was underivable); a name reached through an attribute of a non-module, non-class object is UNKNOWN; the result of a method
called on a standard-library object is UNKNOWN; a module global bound to a standard-library name has its class
(`PYCSL-R349-UNHASHABLE-RECORD`).
Witnesses 6007-6012 (b21, f37, f38, f40, f43, q13): PROVED rc=0 at base -> REFUSED rc=1. Control 6026 (`{os.sep, os.getcwd, os.path}`)
PROVED at base and candidate.

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

Residual: the result of a standard-library FUNCTION (`os.getcwd()`) stays underivable (admitted).
