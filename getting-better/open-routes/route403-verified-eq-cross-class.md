# OPEN ROUTE #403 — #402's "VERIFIED __eq__" IS VERIFIED FOR `other` OF ITS OWN CLASS ONLY; A SET / DICT COMPARES ACROSS CLASSES
**Status: OPEN, Severity 1.** Red-team round 32 (2026-10-26, probes around the allow-list repairs #392-#402 + R5-str); driver-reproduced on 085ee3dcc (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt32/driver-repro.txt`).
Witnesses `witnesses-r403/`: `a04_eq_hetero_set.py`, `f02_eq_hetero_two_classes.py`, `f03_eq_hetero_false.py`, `f05_eq_hetero_str_tuple.py`.

```
#403 #402's "VERIFIED __eq__" IS VERIFIED FOR `other` OF ITS OWN CLASS ONLY; A SET / DICT COMPARES ACROSS CLASSES  [slips past #402]
  a04  class A with `#@ no_exception \all` __hash__ (returns 1) and __eq__(self, other: "A") -> self.x == other.x;
       {a, 1} under no_exception PROVED                                                          CPython AttributeError
  f02  {a, b}, B a file class whose verified __hash__ also returns 0                            AttributeError
  f03  {a, False};   f05  {(a, 1), (0, 1)} (tuple hashes collide, tuple eq calls A.__eq__)     AttributeError
  WhyML: the set lowers to `any int`; the eq-risk test only asks whether A.__eq__ is verified, and it is verified
  under its annotation `other: A`. (n14 `s = {a}; s.add(b)` and f01 / f04 dict / `in` forms were ill-typed.)
  REPAIR: a __eq__ counts as verified for a hashing site only if its `other` parameter is annotated `object` (or
  unannotated) and the body is proved under that type (isinstance-guarded); otherwise a site that may compare a
  value with an element of a DIFFERENT static class (mixed display, a tuple component, Union / int / bool elements)
  is refused PYCSL-R402-UNVERIFIED-EQ.
```

## REPAIR (g1, driver run #3, 2026-10-26/27) -- candidate, REFUSAL polarity tightened

RULE (annotations §7.60, translational §T.6.71): a `def __eq__` counts as VERIFIED for a hashing site only with the signature exactly
`(self, o: object)` (two positional parameters, the second annotated by the builtin `object`), besides #402's conditions
(`no_exception \all`, no `requires`, `-> bool`, one top-level undecorated `def`); otherwise the class is EQ-RISKY and every site that may
compare refuses it (`PYCSL-R402-UNVERIFIED-EQ`, message and advice extended; advice re-audited FOLLOWABLE, hash updated).
Witnesses 5970-5973 (a04, f02, f03, f05): PROVED rc=0 at base -> REFUSED rc=1. Control 6020 (`__eq__(self, other: object)` returning
`False`, compared with `1`, `False`, inside tuples) PROVED at base and candidate; existing control 5800 (`o: object`) unchanged.
Measured: `a04` with `other: object` and the same body FAILS on the candidate (PyCSL-R358: `other.x` on an erased value).

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

Residual / over-refusal: a body that reads an attribute of `o` is not verifiable even under `isinstance(o, A)` (measured FAIL, R358 /
R252: the `object` parameter is erased and `isinstance` does not narrow it), so a field-wise `__eq__` in a comparing hashing position is
refused until that narrowing is modelled. Census of verified `__eq__` in both corpora / mirrors / `pycsl_lib`: one (`5800`, `o: object`).
