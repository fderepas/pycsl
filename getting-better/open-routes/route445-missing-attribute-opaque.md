# OPEN ROUTE #445 — missing ATTRIBUTE (file class / instance / int receiver) lowered as an opaque getattr or an always-present record field (AttributeError)
**Status: OPEN, Severity 1.** Red-team round 36 (2026-10-29, SYSTEMATIC census of operators / dunders / scoping / call binding / modules after #440-#443 on 8fe7204c3: 1723 probes all fully proved / 240 proved / 209 confirmed; rt35's 175 all closed). Census TSV `scratchpad/rt36/census.tsv`; the family block below is quoted from `scratchpad/rt36/FINDINGS.txt`.
Witnesses `witnesses-r445/` (21): `c11_q028_field_typo_self.py`, `c17_w004_inherited_field_missing.py`, `c17_w008_self_method_typo_call.py`, `c26_a003_nested_class_attr.py`, `c26_a004_self_class_attr_typo.py`, `c26_a005_field_set_in_branch_init.py`, `c26_a007_sub_init_no_super_method.py`, `c26_a010_realistic_sub_forgets_super.py`, `c34_q004_init_type_checking_field.py`, `c4_n013_class_attr_undef.py`, `c42_a000.py`, `c42_a011.py`, `c42_a018.py`, `c43_a002.py`, `c43_a003.py`, `c43_a004.py`, `c43_a005.py`, `c43_a006.py`, `c43_a007.py`, `c43_a010.py`, `c43_a021_int_attr_ensures.py`.

Driver repro: 16/16 family exemplars rc=0 Verification SUCCESS on main 8fe7204c3 at 2026-10-29T02:35Z, each violating under CPython (scratchpad/rt36/driver-repro.txt).

```
FAMILY F2 -- missing ATTRIBUTE (file class / instance / int receiver) lowered as an opaque getattr or an always-present record field (AttributeError)   (21)
  EXEMPLAR c11/q028_field_typo_self.py  PROVED (rc=0 Verification SUCCESS):
    | class P:
    |     def __init__(self) -> None:
    |         self.count = 1
    | 
    |     def g(self) -> int:
    |         return self.cout
    | 
    | 
    | 
    | #@ no_exception \all
    | def f(p: P) -> int:
    |     return p.g()
    CPython 3.14: f(P())  ->  VIOLATION AttributeError 'P' object has no attribute 'cout'
  MECHANISM: `self.cout` (no such field) lowers to the opaque `getattr_p self <hash>` (no raises; the field-miss fallback,
  expressions.py:19072-19082); `P.zzz` (no such class
  attribute) likewise; a base field set only by a base __init__ that the subclass __init__ never calls (w004) is
  read as the always-present record field `self.q_a`; `self.helpr()` (no such method) lowers to an opaque val;
  a field set in only ONE branch of __init__ and read by a method (c26/a005) proves -- the external read of the
  same shape is refused by #347 (c2/u022), so #347 covers external receivers only, not `self` inside methods.
  The same fallback (`getattr_2 (x: int) (f: int) : int`) serves a non-call attribute LOAD on an `int` receiver:
  `n.zz`, `n.upper`, `n.bit_lenght` prove (c42); on str / list / dict / set / bytes / float receivers the WhyML
  does not type-check, and method CALLS are #440's (refused).
  REPAIR: OBLIGATION per attribute load on a file-class receiver: the attribute must be (a) a field DEFINITELY assigned on
  every path of the __init__ chain actually executed (subclass __init__ without super().__init__() does not run the
  base's), (b) a class-body binding / method / property in the file MRO, or (c) refused (AttributeError). The
  opaque `getattr_<cls>` fallback must not be reachable under a no_exception claim.
  MEMBERS: c11/q028_field_typo_self.py c17/w004_inherited_field_missing.py c17/w008_self_method_typo_call.py c26/a003_nested_class_attr.py c26/a004_self_class_attr_typo.py c26/a005_field_set_in_branch_init.py c26/a007_sub_init_no_super_method.py c26/a010_realistic_sub_forgets_super.py c34/q004_init_type_checking_field.py c4/n013_class_attr_undef.py c42/a000.py c42/a011.py c42/a018.py c43/a002.py c43/a003.py c43/a004.py c43/a005.py c43/a006.py c43/a007.py c43/a010.py c43/a021_int_attr_ensures.py
```
