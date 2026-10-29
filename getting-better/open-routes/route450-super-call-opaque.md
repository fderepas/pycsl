# OPEN ROUTE #450 — `super().m(..)` lowered as opaque `m_k (super_0 ())`: base lacks m / arity mismatch (AttributeError / TypeError)
**Status: REPAIRED (executor r2, driver run #3, 2026-10-29, with #448 / #449 / #450 / #455 together), Severity 1.** Red-team round 36 (2026-10-29, SYSTEMATIC census of operators / dunders / scoping / call binding / modules after #440-#443 on 8fe7204c3: 1723 probes all fully proved / 240 proved / 209 confirmed; rt35's 175 all closed). Census TSV `scratchpad/rt36/census.tsv`; the family block below is quoted from `scratchpad/rt36/FINDINGS.txt`.
Witnesses `witnesses-r450/` (6): `c11_q092_super_arg_class.py`, `c3_b080_super_missing.py`, `c5_s000_super_missing_arg.py`, `c5_s003_super_self_only.py`, `c5_s006_super_field.py`, `c5_s008_super_two_level.py`.

Driver repro: 16/16 family exemplars rc=0 Verification SUCCESS on main 8fe7204c3 at 2026-10-29T02:35Z, each violating under CPython (scratchpad/rt36/driver-repro.txt).

```
FAMILY F7 -- `super().m(..)` lowered as opaque `m_k (super_0 ())`: base lacks m / arity mismatch (AttributeError / TypeError)   (6)
  EXEMPLAR c3/b080_super_missing.py  PROVED (rc=0 Verification SUCCESS):
    | class B:
    |     def h(self) -> int:
    |         return 1
    | 
    | 
    | class Q(B):
    |     def g(self) -> int:
    |         return super().m()
    | 
    | 
    | #@ no_exception \all
    | def f(p: Q) -> int:
    |     return p.g()
    CPython 3.14: f(Q())  ->  VIOLATION AttributeError 'super' object has no attribute 'm'
  MECHANISM: `super().m(..)` lowers to `(m_1 (super_0 ()))` with both `val`s opaque and raise-free (mlw/b080); nothing checks
  that a base class in the MRO defines m, nor m's arity (s000 `super().h(1)` vs `def h(self)`), nor fields read as
  `super().v` (instance fields are not visible through super).
  REPAIR: Resolve `super()` statically to the next class in the file MRO after the enclosing class; `super().m(..)` is
  admitted only when that MRO slice defines METHOD m (not an instance field) and the call matches its signature
  (F6's binding check); it then lowers to a direct call of that base method, so its contract speaks. A builtin base
  goes through #440's (class, method) table (s004 / s009 are already refused by #393). Else refuse.
  MEMBERS: c11/q092_super_arg_class.py c3/b080_super_missing.py c5/s000_super_missing_arg.py c5/s003_super_self_only.py c5/s006_super_field.py c5/s008_super_two_level.py
```

## REPAIR (executor r2, driver run #3, 2026-10-29, off db6c57253; annotations §7.190, translational §T.6.200) -- routes #448 / #449 / #450 / #455 together

Code inline in `_run_pipeline` (src/pycsl/pycsl.py): file-wide facts before the per-function loop (`_mdf449` module defs bound
once, `_cbd449` class-body defs, `_dk449` decorator kinds, `_sub449` file subclasses, `_umro449`), a per-function block right
after #440 / #441, the cross-constraint rows `_XC448` beside `_MT440`, and a decorator-site pass after the loop. No new def in
a mirrored file (`_run_pipeline` is `\trusted` in the mirror), no axiom, no emission change. Allow-list polarity, refuse by
default. NOT keyed on the function's own claim: an unclaimed callee's TypeError reaches its caller's claim (measured at base:
`def h(n): return g(n, n)` unclaimed, `f` claiming `no_exception \all` and calling `h`, PROVED -- witness 6960; the same
for `len(n, n)` in an unclaimed helper -- witness 6952, a #441-wide transitive gap the claim-keyed table cannot see), so
the checks run in EVERY function that is neither `\trusted` nor `\abstract` (IR flag or its own `#@` block).
  #449 `PYCSL-R449-CALL-SIGNATURE`: a call whose callee resolves -- a module-level def bound once, a def of the function's
    own scope bound once, `C.m(..)` of a file class, `self.m(..)` (every file subclass: dynamic dispatch), `p.m(..)` of a
    parameter annotated with file classes (+ subclasses) -- to a plain / staticmethod / classmethod def binds by CPython's
    algorithm (surplus positional, unknown / duplicate / positional-only keyword, missing required).
  #450 `PYCSL-R450-SUPER-UNRESOLVED`: `super().a` / `super(X, self).a` resolved, for every file class deriving from X, to
    the first class after X in its MRO whose CLASS namespace binds `a` (file body; builtin / stdlib base by its real
    `__mro__`, `object` last); else refused (missing name, instance field, unknown MRO / base, store, bare `super()`); a
    call binds against the file def (#449) or the real base method's `inspect.signature`. `super().__init__` stays #380's.
  #448 `_XC448` row cross-constraints (max / min `default` => 1 positional; sum / enumerate `start`, round `ndigits`, int
    `base` => 1; replace `count` => 2; split `sep` => 0, `maxsplit` => 0..1; `pow` with a modulus => all `int`), checked by
    #441's table under a claim (`PYCSL-R441-BUILTIN-SIGNATURE`) and, with the builtin's real `inspect.signature` where
    published, in every function (`PYCSL-R448-BUILTIN-CROSS-CONSTRAINT`). AUDIT of every keyword-bearing row: only max /
    min `default` slipped at base; the other keyword forms were already refused by #275 / #314 (measured t4-t11).
  #455 `PYCSL-R455-DECORATOR-SITE`: property / accessors / cached_property / classmethod only on a class-body def; the
    last def of a name in its scope never `@overload`; no builtin decorator on a class statement.

THIS ROUTE (#450): WITNESSES (corpus, expected FAIL; each PROVED rc=0 at base -- pycsl-v-s1base, src = db6c57253 -- and
REFUSED at the candidate): 6962 (`super().m()`, no base `m`), 6963 (`super().h(1)` over `def h(self)`), 6964 (`super().v`, an instance field), 6965 (two levels, no `k`). CONTROLS (expected PASS, PROVED at base and candidate): 6982 (`super().h(k)` resolved to the base def; `super().__str__()` of an `Exception` subclass through the real `BaseException.__str__`). Route witnesses
(--no-proof screen at the candidate): 6 of 6 route witnesses refused (R450 / R449).
GATES (candidate 3b87eed15, bases v11/ca + v11/ma = a7f423866 emission, src identical to db6c57253): fidelity
check-self-annotate-sync rc=0 (933 functions) + self-annotate-mirror-check rc=0 (53); root corpus 2569 -> 2574 .mlw, 0 MOVED /
0 GONE / 0 APPEARED (the 5 new controls emit; the 20 new witnesses are refused); python-reference 2186 -> 2186, 0 / 0 / 0;
mirror 53 -> 53, 0 / 0 / 0 (byte-inert: no M1, no OWED mirror proof); run-soundness-planes 61/61 rc=0; trusted-reasons 413
<-> 413 rc=0; assumed-facts --emit-dir rc=0; refusal-witness-coverage rc=0 (344 -> 348 demonstrated); refusal-advice-audited
rc=0 (171 -> 175 audited); dropped-mutation / getattr-erasure / open-route-carriers / trusted-frame-honesty /
trusted-raises-honesty / clause-survival --emit-dir (10 of 1523, ledgered) / stdlib-modules-verify / doc-coherency all rc=0;
\trusted 441 lines (unchanged). Census rows: 20, via `_census_row`. Advice audits: R448 / R449 / R450 / R455 (probes in
getting-better/systematic-soundness-r3/r2-r448-455/advice/, all 8 VERIFY at the candidate).

OVER-REFUSAL COST (measured; the checks run in EVERY non-trusted function, so the whole population is the denominator):
0 corpus files (2569 emitting at base), 0 python-reference (2186), 0 mirrors (53), 0 pycsl_lib modules (--no-proof screen
of all 104 files: 87 emit at base and at the candidate, the same 17 refused alike). Per rule: R449 0, R450 0 (the first cut
refused the mirror `pure_ast.py`: `Ellipsis.__new__`'s `super().__new__` is `\trusted` in its own `#@` block but its IR
record is not found by name -- fixed by reading the def's own `#@` block, a NARROWER skip, not a gate loosening), R448 0,
R455 0. 18 earlier-refused probes (t4-t11 keyword duplicates, `c.m(n, n)` erasure) now refuse earlier with these codes.

RESIDUALS (honest; not judged here): a call of an enclosing function's def from a closure, of a local bound otherwise than
by one def, through a receiver that is neither `self`, a file class, nor a parameter annotated with file classes (locals
`c = C()`, attributes, call results); a `*` / `**` argument (route #379's); a file subclass of the receiver's class whose MRO
is unknown (not visited); a method name that an instance attribute shadows (bound against the class def); a decorated
callee other than staticmethod / classmethod / lru_cache / cache / contextmanager; builtins with no published signature
(`int`, `range`, `max`, `str`, `dict`, `bytes` ...) are judged only by `_XC448` and, under a claim, #441's rows -- so a
class-code mismatch (`len(n)`, n: int) in an UNCLAIMED callee of a claiming caller still proves (the #441-wide transitive
residual, measured on `len(n, n)`: arity is now closed, argument classes are not); what a builtin / stdlib base method
itself raises when reached through `super()` (opaque, as before); class-body statements outside methods.
