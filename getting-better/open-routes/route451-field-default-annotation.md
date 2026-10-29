# OPEN ROUTE #451 — a field DEFAULT / assignment contradicting its str/dict annotation (None) is accepted; the derived class is the annotation (AttributeError)
**Status: OPEN, Severity 1.** Red-team round 36 (2026-10-29, SYSTEMATIC census of operators / dunders / scoping / call binding / modules after #440-#443 on 8fe7204c3: 1723 probes all fully proved / 240 proved / 209 confirmed; rt35's 175 all closed). Census TSV `scratchpad/rt36/census.tsv`; the family block below is quoted from `scratchpad/rt36/FINDINGS.txt`.
Witnesses `witnesses-r451/` (5): `c11_q003_nt_default_none.py`, `c11_q005_dc_default_none_index.py`, `c11_q008_init_default_none_field_ann.py`, `c11_q009_realistic_config.py`, `c3_d034_dataclass_default_none.py`.

Driver repro: 16/16 family exemplars rc=0 Verification SUCCESS on main 8fe7204c3 at 2026-10-29T02:35Z, each violating under CPython (scratchpad/rt36/driver-repro.txt).

```
FAMILY F8 -- a field DEFAULT / assignment contradicting its str/dict annotation (None) is accepted; the derived class is the annotation (AttributeError)   (5)
  EXEMPLAR c11/q009_realistic_config.py  PROVED (rc=0 Verification SUCCESS):
    | @dataclass
    | class Config:
    |     path: str
    |     name: str = None  # type: ignore
    |     retries: int = 3
    | 
    | 
    | 
    | #@ no_exception \all
    | def f(path: str) -> int:
    |     c = Config(path)
    |     return len(c.name.strip())
    CPython 3.14: None  # type: ignore  ->  VIOLATION AttributeError 'NoneType' object has no attribute 'strip'
  MECHANISM: `name: str = None` in a dataclass (and NamedTuple defaults, `d: Dict[..] = None`, `self.s: str = s` with s:
  Optional[str]) is accepted; the field's derived class is its annotation (`str`), so #432 / #443 never see None,
  and the default lowers to the sentinel `pycsl_none_str`; `c.name.strip()` lowers to the receiver-erased
  `c_name_strip_0 ()` (mlw/q009). The same default on a plain __init__ parameter is refused (#350: q001 / q002).
  REPAIR: OBLIGATION: a field default / field assignment must be of the field's annotated class (extend #350's parameter-
  default check to dataclass / NamedTuple field defaults and to annotated field stores `self.f: T = v`); or derive
  the field's class as annotation UNION the classes of its default / stored values, so #432 / #443 refuse the
  method call on the None arm.
  MEMBERS: c11/q003_nt_default_none.py c11/q005_dc_default_none_index.py c11/q008_init_default_none_field_ann.py c11/q009_realistic_config.py c3/d034_dataclass_default_none.py
```
