# OPEN ROUTE #451 — a field DEFAULT / assignment contradicting its str/dict annotation (None) is accepted; the derived class is the annotation (AttributeError)
**Status: REPAIRED (executor r3, driver run #3, 2026-10-29), Severity 1.** Red-team round 36 (2026-10-29, SYSTEMATIC census of operators / dunders / scoping / call binding / modules after #440-#443 on 8fe7204c3: 1723 probes all fully proved / 240 proved / 209 confirmed; rt35's 175 all closed). Census TSV `scratchpad/rt36/census.tsv`; the family block below is quoted from `scratchpad/rt36/FINDINGS.txt`.
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

## REPAIR (executor r3, driver run #3, 2026-10-29, off db6c57253; annotations §7.201, translational §T.6.211)

Code inline in route #350's default-kind check (`_run_pipeline`, src/pycsl/pycsl.py; mirror twin `\trusted`, no
new def, no axiom, no emission change). The check's obligation set now also takes, judged as the value `None` against the
field's annotation: (i) a class-body `x: T = None` (or `field(default=None)`) of a `@dataclass` / `NamedTuple` class;
(ii) an annotated attribute store `o.f: T = v` in a lowered function with `v` the constant `None` or a parameter whose
annotation has a `None` arm or whose default is `None`; both only for a field name some function claiming
`no_exception` covering AttributeError / TypeError reads as an attribute. Refused when no arm of `T` admits `None`
(`PYCSL-R451-FIELD-DEFAULT-ANNOTATION`).
OVER-REFUSAL MEASURED, RULE NARROWED: the first candidate applied the full #350 kind check to every class-body default and
every annotated store: it refused 33 root-corpus files (4 expected PASS: 0900 / 1190 `self.type: str = type_` from an
UN-annotated parameter, 2128, 4444 `m: int = 2.0`; 13 more without an expected verdict, e.g. 0746 / 0772 `d: Dict[..] =
None` on a dataclass with no claim reading it) and 8 mirror files (mixin declarations `_record_array_locals: Dict[str, str]
= None`, `_MUTATING_METHODS: int = {..}`, `self.type: str = type_`). The narrowed rule refuses none of them (re-measured:
root 0 GONE from #451, mirror 53 / 53).
Witnesses 7010-7014 (all 5 red-team probes: PROVED at base, REFUSED). Control 7015 (`name: str = ""`, `alt: Optional[str] =
None`, `retries: int = 3`): PROVED at base and candidate.

GATES (one candidate, one battery for #447 / #451 / #452 / #454 / #456 / #459; see the README run-#3 r3 entry): fidelity sync / mirror-check rc=0; root corpus 2569 base -> 2581 candidate .mlw, 0 MOVED, 3 GONE (5066 / 5071 / 5072, expected FAIL route-#375 witnesses `[*self]` / `(*self,)` / `g(*self)` on a field-less class: VERIFY-FAIL -> REFUSED by #454), 0 APPEARED; pyref 2186 / 2186 0 / 0 / 0; mirror 53 / 53 0 / 0 / 0 (no OWED proof); planes / ledgers: see the README entry.

## RESIDUALS: a plain class's class-body `x: str = None` (a class attribute; usually shadowed by `__init__`); a non-`None`
kind mismatch of a field default (route #236 judges dataclass defaults by value); a store whose value is computed
(`self.s: str = f()`); a field never read by a claimed function (a claim-free ensures that relies on the field's class).
