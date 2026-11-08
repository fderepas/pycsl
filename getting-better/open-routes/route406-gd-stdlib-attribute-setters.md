# OPEN ROUTE #406 — GD's STORE CENSUS (§7.53) MISSES STDLIB CALLS THAT SET ATTRIBUTES ON AN ARGUMENT
**Status: OPEN, Severity 1.** Red-team round 32 (2026-10-26, probes around the allow-list repairs #392-#402 + R5-str); driver-reproduced on 085ee3dcc (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt32/driver-repro.txt`).
Witnesses `witnesses-r406/`: `c20_getattr_ns_init.py`, `f49_getattr_ns_init_module_fn.py`, `c21_getattr_update_wrapper.py`, `f44_getattr_parse_args_ns.py`, `k01_getattr_optparse.py`, `k02_getattr_mock_patch.py`, `f47_getattr_objgetattribute_dict.py`, `k04_getattr_ns_classattr_hash.py`, `h14_classattr_ns_shadow.py`.

```
#406 GD's STORE CENSUS (§7.53) MISSES STDLIB CALLS THAT SET ATTRIBUTES ON AN ARGUMENT  [slips past §7.43 / §7.53 / §7.49 (2)]
  c20  R.__init__: argparse.Namespace.__init__(self, k=5); getattr(r, "k", 0) == 0 PROVED      5
  f49  same call from a module function on the receiver
  c21  functools.update_wrapper(self, S(), assigned=(), updated=("__dict__",))                 5
  f44  argparse.ArgumentParser().parse_args([], namespace=self)                                5
  k01  optparse.Values.__init__(self, {"k": 5});  k02 unittest.mock.patch.object(self, "k", 5, create=True).start()
  f47  object.__getattribute__(self, "__dict__")["k"] = 5 (the `__dict__` touch is a STRING)  5
  k04  the same Namespace call rebinding a FIELD x = [1]; {r.x} PROVED                          TypeError
  h14  class attribute K = 1 shadowed by Namespace.__init__(self, K=[1]); {c.K} PROVED          TypeError
  (setattr through functools.partial / map / importlib, object.__setattr__ via a dict lookup, a subclass
  __getattr__ / __getattribute__ are refused: n01, n02, k03, c30, h10, h11.)
  REPAIR (allow-list): a receiver (self, or any object) passed as an argument to a callee that is not a file
  function / a modelled builtin with a known frame, or appearing in `object.__getattribute__(x, "__dict__")` /
  any string-named dunder access, makes its class's binding set UNKNOWN for GD and its fields / class-attribute
  reads UNKNOWN as hashed-value sources.
```

## REPAIR (g1, driver run #3, 2026-10-26/27) -- candidate, REFUSAL polarity tightened

RULE (allow-list of callees; annotations §7.63, translational §T.6.74): outside the `__main__` driver, a call passing an object-valued
argument to a standard-library callee of a module outside a fixed list of modules that never store attributes on an argument
(`argparse`, `optparse`, `functools.update_wrapper` / `wraps` / `partial`, `unittest.mock`, `types.SimpleNamespace`, ... are outside it),
to a method of an object such a call returned (`p.parse_args(.., namespace=self)`), to a non-read-only dunder of a builtin class
(`object.__getattribute__`), or a string constant `__dict__` / `__setattr__` / `__delattr__` / `__class__`, makes every class UNKNOWN
for GD (`PYCSL-R376-GETATTR-CLASS-BINDING`) and every field / class-attribute read UNKNOWN as a hashed value
(`PYCSL-R349-UNHASHABLE-RECORD`).
Witnesses 5987-5995 (c20, c21, f44, f47, f49, h14, k01, k02, k04): PROVED rc=0 at base -> REFUSED rc=1. Control 6023 (`math.floor` and a
file function called on `self`, `getattr(r, "k", 0) == 0`) PROVED at base and candidate.
Measured and NOT landed: (a) counting the `__main__` driver too GONEs control 5464 (its driver calls `setattr`; GD's documented
convention excludes the driver); (b) counting every unread callee (user-module functions, local callables, unknown methods) GONEs 6
mirrors (`audit_proof`, `frontend/pure_ast`, `module6_whyml/expressions` / `statements` / `stmt_control_flow`, `proof2why3/parser`);
(c) folding `setattr` / `vars` / `__dict__` into the hashed-value sources GONEs `frontend/pure_ast.py` (its `setattr(self, name, value)`).

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

Residuals: the `__main__` driver's own calls; user-module callees (§7.43's residual); `setattr(self, "x", [1])` then `{r.x}` still
PROVES (measured; cost (c) above).
