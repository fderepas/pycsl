# OPEN ROUTE #442 — #432 NARROWING TRUSTS isinstance(R, E) FOR ANY E THAT IS NOT LITERALLY object / Any
**Status: OPEN, Severity 1.** Red-team round 35 (2026-10-28, SYSTEMATIC BUILTIN-PRECONDITION CENSUS after #432-#439 on daaf6ea78: 860 probes / 452 fully proved / 175 confirmed (156 new + 19 inside #432's documented residual); rt34's 63 all closed). Census TSV `scratchpad/rt35/census.tsv`; findings `scratchpad/rt35/FINDINGS.txt` (the family text below is quoted from it).
Witnesses `witnesses-r442/` (6): `w007_isinstance_alias_type.py`, `c000_isinst_alias_O.py`, `c001_isinst_tuple_alias.py`, `c007_isinst_hashable.py`, `c008_isinst_typing_hashable.py`, `c021_isinst_cls_var.py`.

Driver repro: 7/7 family exemplars (A1 n002, A2 s106, B1 k001 + e017, B2 a001, C c007, D b000) rc=0 Verification SUCCESS on main f1c249c4e at 2026-10-28T19:25Z, each violating under CPython (scratchpad/rt35/driver-repro.txt).

```
#442 #432 NARROWING TRUSTS isinstance(R, E) FOR ANY E THAT IS NOT LITERALLY object / Any   (6)
  c007  `if isinstance(x, Hashable): x.upper()` x: Optional[str] PROVED; f(None)        CPython AttributeError.
  w007 / c000 `T = object` / `O = object` aliases; c001 `T = (str, object)`; c021 class attribute `H.t = object`;
  c008 typing.Hashable.
  REPAIR (proposed, allow-list / refuse by default): isinstance narrows only by a class expression RESOLVED to concrete classes none of which is a superclass of NoneType;
  an unresolved name / alias / attribute / tuple variable does not narrow.
```
