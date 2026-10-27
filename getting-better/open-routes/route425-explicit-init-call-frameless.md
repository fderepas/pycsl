# OPEN ROUTE #425 — AN EXPLICIT `x.__init__(..)` CALL IS A FRAME-LESS `val`: NO requires, NO writes, THE CLASS INVARIANT IS KEPT 
**Status: REPAIRED, Severity 1.** Red-team round 33 (2026-10-27, convergence measurement after the run #3 allow-list repairs; 653 screened / 385 fully proved / 116 confirmed); driver-reproduced on main (see `scratchpad/rt33/driver-repro.txt`).
Witnesses `witnesses-r425/` (4): `d14_init_recall.py`, `d22_init_recall_neg_noreq.py`, `n01_class_init.py`, `n07_init_kw.py`.

```
#425 AN EXPLICIT `x.__init__(..)` CALL IS A FRAME-LESS `val`: NO requires, NO writes, THE CLASS INVARIANT IS KEPT   [slips past §7.58]  (4)
  d22  invariant self.n >= 0, __init__ `#@ requires n >= 0` stores n;  g(a): a.__init__(-4); return a.where()  ensures >= 0
       PROVED                                                                                     CPython -4
  d14  the same on a fresh A(1)   n01 a.__class__.__init__(a, -4)   n07 a.__init__(n=-4)
  WhyML: `val a___init___1 (self: a) (x0: int) : int` -- no `requires`, no `writes { self.n }`, so the invariant held before
  the call is still assumed after it. (A.__init__(a, 3), type(a).__init__, a bound `ini = a.__init__`, a method doing
  self.__init__(-4) refuse or fail; d19 / d21 (`a.__init__(3)` then `== 1`) fail, so the call is not simply dropped.)
  REPAIR: lower an explicit call of a file class's __init__ as the __init__ with its contract: `requires` checked, `writes`
  every field it stores, and the class-invariant goal re-established (or refuse explicit __init__ calls on an existing object).
```

## REPAIR (executor g3, driver run #3, 2026-10-27, off ac28806be; annotations §7.114, translational §T.6.125)

PYCSL-R425-EXPLICIT-INIT (outside the `__main__` driver): `.__init__` may be loaded only as the callee of `super().__init__(..)` / `Base.__init__(self, ..)` inside an `__init__`; `getattr` / `methodcaller` / `attrgetter` of "__init__" refused. Advice audited FOLLOWABLE. Witnesses 6299-6302; control 6334 (`super().__init__`; `Base.__init__(self, n)` itself is refused by route #335's construction rule, measured).

Executor g3, driver run #3, 2026-10-27, off ac28806be. Gates (final candidate): root byte-diff 2497 -> 2512 0 MOVED / 0 GONE / 0 APPEARED (15 new sources); pyref 2186 / 2186 0/0/0; mirrors 53/53 0/0/0 (a first candidate GONE 2 mirrors -- frontend/pure_ast `type.__instancecheck__`, module6_whyml/statements a str-row `.get` -- both fixed before landing, so NO mirror refusal); pycsl_lib --no-proof screen identical (104 files, rc0 87); fidelity rc=0; soundness planes 61/61 green; getattr-erasure (control 6337 registered) / clause-survival / assumed-facts --emit-dir / open-route-carriers / refusal-witness-coverage / refusal-advice-audited rc=0. Logs: getting-better/systematic-soundness-r3/g3-r421-429/.

## RESIDUALS (honest)

The driver may still call `a.__init__(..)` (unverified code, as any driver store).
