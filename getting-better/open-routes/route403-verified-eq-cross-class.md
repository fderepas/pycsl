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
