# OPEN ROUTE #404 — S1 ADMITS `type` AS A BASE, SO A FILE METACLASS IS MODELLED AS NOTHING: ITS __eq__/__hash__/__bool__/ATTRIBUTES ARE IGNORED
**Status: OPEN, Severity 1.** Red-team round 32 (2026-10-26, probes around the allow-list repairs #392-#402 + R5-str); driver-reproduced on 085ee3dcc (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt32/driver-repro.txt`).
Witnesses `witnesses-r404/`: `a12_metaclass_eq_hash.py`, `f07b_metaclass_hash_raise.py`, `f10_metaclass_classattr.py`, `f12_metaclass_instance_hash.py`, `j36_metaclass_eq_tuple_hash.py`, `j35b_metaclass_bool_while.py`, `h15_metaclass_attr_fallback.py`, `j33_metaclass_init_raise_attr.py`.

```
#404 S1 ADMITS `type` AS A BASE, SO A FILE METACLASS IS MODELLED AS NOTHING: ITS __eq__/__hash__/__bool__/ATTRIBUTES ARE IGNORED  [slips past S1 BASE-MODEL / §7.49 (1)(2)]
  a12  class M(type) with __eq__ only; class K(metaclass=M); {K} PROVED (a class is "a hashable object")  TypeError
  f07b M.__hash__ raises (conditionally);  {K}                                                     ValueError
  f10  {C.K} for a nested class K(metaclass=M);  f12 {type(k)};  j36 {(C, 1)}                     TypeError
  j35b `if C:` with M.__bool__ raising (no_exception)                                              ValueError
  h15  {C.K} where K is bound only on the metaclass (M.K = [1])                                    TypeError
  j33  {C.K}: C's body binds K = 1 but M.__init__ stores cls.K = [1]                               TypeError
  (h16 metaclass @property K, h21 / h25 / j30 / j34 ensures forms, f08 / j32b Type[B] params: Unknown / refused.)
  WHYML: `{K}` -> `any int`; `if C` -> `c <> 0` over a `val constant c`; C.K reads the class body binding.
  REPAIR: drop `type` from the BASE-MODEL table (S1 refuses `class M(type)` like any unmodelled base) unless the
  metaclass defines nothing; or: a class whose metaclass is a file class is UNKNOWN for hashing / truthiness /
  class-attribute sources, and `metaclass=` with a non-`type`/non-ABCMeta/non-EnumMeta value refuses the class.
```

## REPAIR (g1, driver run #3, 2026-10-26/27) -- candidate, REFUSAL polarity tightened

RULE (S1; annotations §7.61, translational §T.6.72): `builtins.type` left the BASE-MODEL table; a base `type` is admitted only when
the class body is a docstring / `pass` / `...` and no code stores an attribute on the class; a `metaclass=` keyword must name `type`,
`abc.ABCMeta`, `enum.EnumMeta` / `EnumType` or a file class, and the metaclass of every checked class is itself checked wherever it is
named (`PYCSL-S1-UNMODELLED-BASE`, base message extended, new keyword message).
Witnesses 5974-5981 (a12, f07b, f10, f12, h15, j33, j35b, j36): PROVED rc=0 at base -> REFUSED rc=1. NEW latent 6015 (`metaclass=` a
FUNCTION returning `[1]`, `{K}`; CPython TypeError; ill-typed in WhyML at base, refused on the candidate by the new keyword site).
6017: route #380's `__call__` refusal is now unreachable through a file metaclass (S1 refuses it first: witness 5156's row moved to
S1), so #380's site is demonstrated through `metaclass=enum.EnumMeta` (refused at base and candidate). NEW latent 6018 (`M2(M)` with `M(type)` empty and
`M2` binding `__eq__`, `{K}` for `K(metaclass=M2)`): a class deriving from `type` through file classes must define nothing too. Control 6021 (a metaclass with
only a docstring, `metaclass=abc.ABCMeta`) and existing control 5171 PROVED at base and candidate.

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

Residual: pyref `0080` / `0082` (metaclasses defined inside a function) emit nothing at base either (0 pyref movers).
