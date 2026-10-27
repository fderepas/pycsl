# OPEN ROUTE #424 — A CLASS SUBSCRIPT `K[i]` (`__class_getitem__`) IS ADMITTED AS A HASHED VALUE 
**Status: REPAIRED, Severity 1.** Red-team round 33 (2026-10-27, convergence measurement after the run #3 allow-list repairs; 653 screened / 385 fully proved / 116 confirmed); driver-reproduced on main (see `scratchpad/rt33/driver-repro.txt`).
Witnesses `witnesses-r424/` (2): `a10_meta_new_returns_list.py`, `j23_cgi_glob.py`.

```
#424 A CLASS SUBSCRIPT `K[i]` (`__class_getitem__`) IS ADMITTED AS A HASHED VALUE   [new source]   (2)
  a10  class K: def __class_getitem__(cls, item) -> list: return [item];  {K[1]} PROVED           CPython TypeError
  j23  G = K[1] at module level; {G}
  (j20 a raising __class_getitem__ under no_exception, j21 / j26 its result in an ensures: Timeout, not counted.)
  REPAIR: a subscript of a class value calls __class_getitem__ (or the metaclass __getitem__): it is a call whose result
  class is the method's `-> T` (UNKNOWN when absent) and whose exceptions / contract must be the method's; simplest: refuse
  subscripting a file class that defines __class_getitem__ (typing generics excepted).
```

## REPAIR (executor g3, driver run #3, 2026-10-27, off ac28806be; annotations §7.113, translational §T.6.124)

PYCSL-R424-CLASS-GETITEM: a file class whose file MRO binds `__class_getitem__` may not be subscripted or aliased outside annotations; in `_ty383` a subscript of a `#H` value (class / function object) is `#UNK`. Witnesses 6297-6298; control 6333.

Executor g3, driver run #3, 2026-10-27, off ac28806be. Gates (final candidate): root byte-diff 2497 -> 2512 0 MOVED / 0 GONE / 0 APPEARED (15 new sources); pyref 2186 / 2186 0/0/0; mirrors 53/53 0/0/0 (a first candidate GONE 2 mirrors -- frontend/pure_ast `type.__instancecheck__`, module6_whyml/statements a str-row `.get` -- both fixed before landing, so NO mirror refusal); pycsl_lib --no-proof screen identical (104 files, rc0 87); fidelity rc=0; soundness planes 61/61 green; getattr-erasure (control 6337 registered) / clause-survival / assumed-facts --emit-dir / open-route-carriers / refusal-witness-coverage / refusal-advice-audited rc=0. Logs: getting-better/systematic-soundness-r3/g3-r421-429/.

## RESIDUALS (honest)

A class passed as a VALUE (`f(K)` then `cls[1]`) is covered for hashing by the `#H` row only; its exceptions are not modelled.
