# OPEN ROUTE #405 — DYNAMIC SUBCLASSES ESCAPE THE CLOSED-WORLD CLOSURE OF #395 / #396 / route #277
**Status: OPEN, Severity 1.** Red-team round 32 (2026-10-26, probes around the allow-list repairs #392-#402 + R5-str); driver-reproduced on 085ee3dcc (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt32/driver-repro.txt`).
Witnesses `witnesses-r405/`: `a18_type_subclass_main.py`, `f15_make_dataclass_hash.py`, `f16_type_subclass_eq_hetero.py`, `f13_type_subclass_getattr.py`, `f17_type_subclass_method_override.py`.

```
#405 DYNAMIC SUBCLASSES ESCAPE THE CLOSED-WORLD CLOSURE OF #395 / #396 / route #277  [slips past §7.50 / §7.53 / CLASS-EXACT default]
  a18  __main__: D = type("D", (B,), {"__hash__": None}); f(b: B) hashes {b} PROVED            TypeError
  f15  D = dataclasses.make_dataclass("D", [], bases=(B,)) (eq, not frozen)                     TypeError
  f16  type() subclass with __hash__ 0 and a raising __eq__; {b, c}                             ZeroDivisionError
  f13  getattr(r, "k", 0) == 0 with S = type("S", (R,), {"k": 5})                               5
  f17  `b.g()` ensures \result == 1 with type("D", (B,), {"g": lambda s: 2}) -- the override refinement check
       (route #277, default ON) never sees the dynamic override                                 2
  (A `class D(B)` statement in __main__ (a19), in a def (a20), types.new_class (f14) and exec (n03) ARE refused.)
  REPAIR: any call of `type` with 3 arguments, `types.new_class`, `dataclasses.make_dataclass(.., bases=..)` or
  `collections.namedtuple`-like factories anywhere in the file (driver included) whose bases argument is not a
  literal tuple of modelled classes makes every file class named in it OPEN: unhashable at hashing sites,
  UNKNOWN for GD, and its method calls unverifiable (or simply refuse the 3-argument `type` call).
```

## REPAIR (g1, driver run #3, 2026-10-26/27) -- candidate, REFUSAL polarity tightened

RULE (annotations §7.62, translational §T.6.73): anywhere in the file, the `__main__` driver included, a call of the builtin `type` with
two or more arguments (or `type.__new__`), `types.new_class(..)` and `dataclasses.make_dataclass(.., bases=..)` is REFUSED unless the
bases argument is the literal `()` (new `PYCSL-R405-DYNAMIC-SUBCLASS`; advice audited FOLLOWABLE).
Witnesses 5982-5986 (a18, f13, f15, f16, f17): PROVED rc=0 at base -> REFUSED rc=1. Control 6022 (`type(x)`, `type("T", (), {})`,
`make_dataclass` without bases in the driver) PROVED at base and candidate.

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

Residual: `exec` / a class built by a user-module function are outside the census (exec is refused elsewhere, n03).
