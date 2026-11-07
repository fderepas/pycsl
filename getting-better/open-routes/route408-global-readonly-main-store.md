# OPEN ROUTE #408 — THE READ-ONLY TEST OF A MODULE CONTAINER GLOBAL (§7.49 (1)) DOES NOT SEE A SUBSCRIPT STORE IN THE __main__ DRIVER
**Status: OPEN, Severity 1.** Red-team round 32 (2026-10-26, probes around the allow-list repairs #392-#402 + R5-str); driver-reproduced on 085ee3dcc (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt32/driver-repro.txt`).
Witnesses `witnesses-r408/`: `b02_global_sub_store_main.py`.

```
#408 THE READ-ONLY TEST OF A MODULE CONTAINER GLOBAL (§7.49 (1)) DOES NOT SEE A SUBSCRIPT STORE IN THE __main__ DRIVER  [slips past #394]
  b02  XS = [1, 2]; f hashes {XS[0]}; __main__ does XS[0] = [5] then calls f                   TypeError
  (The same store in a module function (b01), a rebinding of K in __main__ (b07), XS.append in __main__ (f23),
  G["a"] = .. / del G["a"] in __main__ (f24, f28), C.XS[0] = .. in __main__ (f25) are refused. f26 / f27, the
  ensures / IndexError forms, time out -- not counted.)
  REPAIR: the read-only census counts every Store-context Subscript / AugAssign whose base is the global, in the
  driver too (the rebinding census already reads the driver).
```

## REPAIR (g1, driver run #3, 2026-10-26/27) -- candidate, REFUSAL polarity tightened

RULE (annotations §7.64 (2), translational §T.6.75): a global's bindings are its store-context names only (`XS[0] = ..` anywhere, the
driver included, is a load of `XS`, not a second binding that made its value underivable); the store makes `XS` not read-only (`_rx394`
reads the whole file), so its elements are UNKNOWN (`PYCSL-R349-UNHASHABLE-RECORD`).
Witness 6006 (b02): PROVED rc=0 at base -> REFUSED rc=1. Control 6025 (a module list never stored to, its element hashed) PROVED at
base and candidate.

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
