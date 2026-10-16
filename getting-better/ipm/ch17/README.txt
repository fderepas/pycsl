W-IPM S-D re-spike (gen #36, ch17) -- artifacts. Verdicts measured at 29a5c07d + the seam.
spike_ds.mlw / spike_ds.log   hand model, axiom-free (realizer + lemma per new val); alt-ergo + z3:
                              controls c1-c7 Valid both; f1/f3/f4/f5 Unknown/Timeout; f2 (stale COPY alias) Valid.
census-ds.txt                 re-census of the 96 dict/set-mutator trusted rows at HEAD.
stale-alias/*.py              11 clear-specific stale-alias counter-programs (claim 1, CPython 0): none proves;
                              j/k/l refused by route #59 guard, h refused by route #243 (F), the rest L3-tc type errors.
opaque-add/*.py               the `add` on an opaque (set_comp) local, built then WITHDRAWN: h/j/k FAIL, i PASS,
                              g (loop-rebound) refused. Withdrawn: the only marker it served is input-blind.
subscript-recv/*.py           mutators on a SUBSCRIPT receiver (`d[0].add`, `ir["functions"].insert`) are erased
                              to a receiver-less op (not refused); all claims measured FAIL (reads non-deterministic).
exceptions/*.py               `.remove`/`.pop` under `#@ no_exception`: REFUSED at HEAD on local, self field, param (e1-e4).
