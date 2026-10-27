# OPEN ROUTE #427 — UB-7.1 DOES NOT SEE THROUGH A GENERATOR EXPRESSION OVER THE MUTATED COLLECTION 
**Status: REPAIRED, Severity 1.** Red-team round 33 (2026-10-27, convergence measurement after the run #3 allow-list repairs; 653 screened / 385 fully proved / 116 confirmed); driver-reproduced on main (see `scratchpad/rt33/driver-repro.txt`).
Witnesses `witnesses-r427/` (6): `g07_genexp_dict.py`, `m10_genexp_keys.py`, `m13_genexp_set.py`, `m14_genexp_cond.py`, `w11_genexp_set_discard.py`, `w12_genexp_nested_gen.py`.

```
#427 UB-7.1 DOES NOT SEE THROUGH A GENERATOR EXPRESSION OVER THE MUTATED COLLECTION   [slips past §7.74 / route #416]   (6)
  g07  for k in (x for x in d): d[k + 100] = 0 under no_exception \all PROVED                     CPython RuntimeError
  m10  (x for x in d.keys())   m14  (x for x in d if x > 0)   w12  (x for x in (y for y in d))
  m13  a SET: for x in (y for y in s): s.add(x + 100)   w11  the same with s.discard(x)
  (enumerate / zip / iter / reversed / map / filter / itertools.chain / iter(d.items()) / a view bound to a name / an alias
  of d / a helper mutating d / comprehension and any() / sum() forms: refused or failed. m15 / m16 (del, a named genexp):
  failed / timeout.)
  REPAIR: a GeneratorExp iterable whose (first) generator iterates <recv> (or a view of it) counts as iterating <recv>.
```

## REPAIR (executor g3, driver run #3, 2026-10-27, off ac28806be; annotations §7.116, translational §T.6.127)

UB-7.1 collects the iterated receivers through every generator of a `GenExp` (recursively) and views; comprehensions / list() are snapshots. Witnesses 6310-6315; control 6336. (probe q06, a mutating genexp inside `sum(..)`: REFUSED.)

Executor g3, driver run #3, 2026-10-27, off ac28806be. Gates (final candidate): root byte-diff 2497 -> 2512 0 MOVED / 0 GONE / 0 APPEARED (15 new sources); pyref 2186 / 2186 0/0/0; mirrors 53/53 0/0/0 (a first candidate GONE 2 mirrors -- frontend/pure_ast `type.__instancecheck__`, module6_whyml/statements a str-row `.get` -- both fixed before landing, so NO mirror refusal); pycsl_lib --no-proof screen identical (104 files, rc0 87); fidelity rc=0; soundness planes 61/61 green; getattr-erasure (control 6337 registered) / clause-survival / assumed-facts --emit-dir / open-route-carriers / refusal-witness-coverage / refusal-advice-audited rc=0. Logs: getting-better/systematic-soundness-r3/g3-r421-429/.

## RESIDUALS (honest)

`map` / `filter` / `zip` over a genexp rely on their existing refusals.
