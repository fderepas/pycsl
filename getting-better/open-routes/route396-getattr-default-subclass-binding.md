# OPEN ROUTE #396 — GD FOLDS getattr's DEFAULT WHEN ONLY A SUBCLASS BINDS THE ATTRIBUTE
**Status: OPEN, Severity 1.** Red-team round 31 (2026-10-26, probes around systematic rules S1/GD/TC/SB and the §7.46/§7.47 hash rules); driver-reproduced on 7859e8fb0 (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt31/driver-repro.txt`).
Witnesses `witnesses-r396/`: `g01_subclass_sets_k.py`, `k52_subclass_classattr.py`, `k53_subclass_dataclass_field.py`, `k54_grandchild.py`, `k60_subclass_for_target.py`, `k61_subclass_property.py`, `k62_subclass_method.py`, `k63_subclass_mangled_self.py`, `g29_mangled_in_subclass.py`.

```
#396 GD FOLDS getattr's DEFAULT WHEN ONLY A SUBCLASS BINDS THE ATTRIBUTE  [slips past GD §7.43 / #376]
  g01  getattr(r, "k", 0) == 0 for r: R; S(R).__init__ stores self.k = 5                         CPython 5
  k52  S(R) class attribute k = 5;  k53 @dataclass S(R) k: int = 5;  k54 grandchild T(S(R)) stores k;  k61 S(R) @property k;
  k62  S(R) def k (getattr(r, "k", None) is None proved, CPython bound method);  k60 S(R) `for self.k in [5]`
  g29 / k63  getattr(r, "_S__k", 0) with S(R) storing self.__k (the #389 mangling repair maps only R's own fields)
  WhyML: `let f (r: r) : int ensures { result = 0 } = 0`. The class_binds_r376 map walks the receiver's MRO, never its
  descendants, although a receiver typed R may hold any subclass instance (§7.21 already says this for fields).
  REPAIR: in class_binds_r376 a class binds k when it, any base or ANY FILE DESCENDANT binds k (class body, field store,
  mangled spelling, property/method), and a class with descendants defined in __main__-reachable code counts them too.
```
