# OPEN ROUTE #455 — builtin DECORATOR misuse not modelled: `@property` / `@typing.overload` on a module or nested function, then called (TypeError / NotImplementedError)
**Status: REPAIRED (executor r2, driver run #3, 2026-10-29, with #448 / #449 / #450 / #455 together), Severity 1.** Red-team round 36 (2026-10-29, SYSTEMATIC census of operators / dunders / scoping / call binding / modules after #440-#443 on 8fe7204c3: 1723 probes all fully proved / 240 proved / 209 confirmed; rt35's 175 all closed). Census TSV `scratchpad/rt36/census.tsv`; the family block below is quoted from `scratchpad/rt36/FINDINGS.txt`.
Witnesses `witnesses-r455/` (6): `c18_k009_deco_property_module.py`, `c21_d000_overload_no_impl.py`, `c21_d001_typing_overload_dot.py`, `c21_d002_property_nested.py`, `c21_d004_property_realistic.py`, `c21_d008_property_ensures.py`.

Driver repro: 16/16 family exemplars rc=0 Verification SUCCESS on main 8fe7204c3 at 2026-10-29T02:35Z, each violating under CPython (scratchpad/rt36/driver-repro.txt).

```
FAMILY F12 -- builtin DECORATOR misuse not modelled: `@property` / `@typing.overload` on a module or nested function, then called (TypeError / NotImplementedError)   (6)
  EXEMPLAR c21/d004_property_realistic.py  PROVED (rc=0 Verification SUCCESS):
    | @property
    | def size(p: str) -> int:
    |     return len(p)
    | 
    | 
    | 
    | #@ no_exception \all
    | def f(path: str) -> int:
    |     return size(path)
    CPython 3.14: f('ab')  ->  VIOLATION TypeError 'property' object is not callable
  MECHANISM: A builtin DECORATOR on a module-level or nested function is ignored: `@property def size(p)` lowers to a
  plain `let size` that `f` calls (mlw/d004), but CPython binds `size` to a property object (not callable);
  `@typing.overload` without an implementation lowers to the stub's body (mlw/d000), while CPython's overload
  stub raises NotImplementedError. Every other decorator tried at module level is refused (user decorators,
  classmethod, functools.cached_property / lru_cache, typing.final / no_type_check, abc.abstractmethod: c18 / c21),
  so property and overload are presumably admitted as known (class-body) decorators regardless of the site.
  REPAIR: ALLOW-LIST of decorators PER DEFINITION SITE: property (and setter / deleter) only on a method in a class body,
  never at module or nested-function level; a call of a name whose only definitions are @overload stubs (no
  undecorated implementation) is refused (NotImplementedError); everything else stays refused as today.
  MEMBERS: c18/k009_deco_property_module.py c21/d000_overload_no_impl.py c21/d001_typing_overload_dot.py c21/d002_property_nested.py c21/d004_property_realistic.py c21/d008_property_ensures.py
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

THIS ROUTE (#455): WITNESSES (corpus, expected FAIL; each PROVED rc=0 at base -- pycsl-v-s1base, src = db6c57253 -- and
REFUSED at the candidate): 6966 (module-level `@property`), 6967 (nested `@property`), 6968 (`@overload` without implementation), 6969 (`@typing.overload`). CONTROLS (expected PASS, PROVED at base and candidate): 6984 (`@property` on a class-body method; an `@overload` chain with its implementation). Route witnesses
(--no-proof screen at the candidate): 6 of 6 route witnesses refused (R455).
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
