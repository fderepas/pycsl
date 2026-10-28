# OPEN ROUTE #443 — AN Any / BARE-CONTAINER ELEMENT AS A METHOD RECEIVER OWES NO AttributeError
**Status: OPEN, Severity 1.** Red-team round 35 (2026-10-28, SYSTEMATIC BUILTIN-PRECONDITION CENSUS after #432-#439 on daaf6ea78: 860 probes / 452 fully proved / 175 confirmed (156 new + 19 inside #432's documented residual); rt34's 63 all closed). Census TSV `scratchpad/rt35/census.tsv`; findings `scratchpad/rt35/FINDINGS.txt` (the family text below is quoted from it).
Witnesses `witnesses-r443/` (19): `m034_strip_dictval_any.py`, `m035_upper_listelem_any.py`, `m037_upper_tuple_any.py`, `m038_upper_bare_list.py`, `b000_any_elem_recv.py`, `b001_any_elem_recv.py`, `b002_any_elem_recv.py`, `b004_any_elem_recv.py`, `b006_any_elem_recv.py`, `b007_any_elem_recv.py`, `b008_any_elem_recv.py`, `b011_any_elem_recv.py`, `b012_any_elem_recv.py`, `b015_any_elem_recv.py`, `b016_any_elem_recv.py`, `b017_any_elem_recv.py`, `b019_any_elem_recv.py`, `b020_any_elem_recv.py`, `x010_any_elem_realistic.py`.

Driver repro: 7/7 family exemplars (A1 n002, A2 s106, B1 k001 + e017, B2 a001, C c007, D b000) rc=0 Verification SUCCESS on main f1c249c4e at 2026-10-28T19:25Z, each violating under CPython (scratchpad/rt35/driver-repro.txt).

```
#443 AN Any / BARE-CONTAINER ELEMENT AS A METHOD RECEIVER OWES NO AttributeError   (19)
  x010  `row: List[Any]`; `len(row[0].strip())` PROVED; f([42])                       CPython AttributeError.
  (Inside #432's DOCUMENTED residual -- Any / object receivers admitted; a direct `x: Any` receiver is not proved, only
  ELEMENTS of Any-typed containers slip; bare list / dict / tuple elements (int under BARE-CONTAINER-INT) belong to A2.)
  REPAIR (proposed, allow-list / refuse by default): the R-gate analogue: an attribute / method on an underivable (#UND / Any / object) receiver is refused under a claim
  covering AttributeError.
```
