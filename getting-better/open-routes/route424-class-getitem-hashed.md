# OPEN ROUTE #424 — A CLASS SUBSCRIPT `K[i]` (`__class_getitem__`) IS ADMITTED AS A HASHED VALUE 
**Status: OPEN, Severity 1.** Red-team round 33 (2026-10-27, convergence measurement after the run #3 allow-list repairs; 653 screened / 385 fully proved / 116 confirmed); driver-reproduced on main (see `scratchpad/rt33/driver-repro.txt`).
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
