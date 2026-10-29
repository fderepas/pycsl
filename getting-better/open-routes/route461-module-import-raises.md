# OPEN ROUTE #461 — A VERIFIED FILE WHOSE IMPORT ITSELF RAISES (class creation / module-level statements)
**Status: OPEN, Severity 2 (arguable — the claimed function is never callable; the PROGRAM crashes at import).**
Red team 37 (2026-10-29, on 370db7dc2; driver-salvaged after the executor hung on a glob-rm prompt): 641 census rows /
27 proved / 22 confirmed, of which these 20 are module-level. Driver repro (`scratchpad/rt37/driver-repro.txt`):
m007 (module-level 1/0), k035 (MRO conflict), m005 (dataclass order= with a user __lt__) rc=0 Verification SUCCESS on
370db7dc2, CPython raises at import.
Witnesses `witnesses-r461/` (20): `e12_m000_class_int_str_layout.py`, `e12_m001_class_bool_base.py`, `e12_m002_enum_dup_member.py`, `e12_m003_namedtuple_default_order.py`, `e12_m004_namedtuple_underscore.py`, `e12_m005_dataclass_order_lt.py`, `e12_m006_frozen_from_nonfrozen.py`, `e12_m007_module_div_zero.py`, `e12_m008_module_key.py`, `e12_m010_module_int_parse.py`, `e12_m011_module_assert.py`, `e12_m012_class_body_raises.py`, `e12_m016_slots_dup_layout.py`, `e12_m017_init_subclass_kw.py`, `e12_m018_dataclass_field_no_ann_default.py`, `e15_c017_init_subclass_called.py`, `e3_k030_slots_class_default_conflict.py`, `e3_k031_dataclass_mutable_default.py`, `e3_k033_dataclass_nondefault_after_default.py`, `e3_k035_mro_conflict.py`.

```
#461 PyCSL verifies f under `#@ no_exception \all` in a module whose IMPORT raises: class-creation errors (instance
     layout conflicts, `bool` as a base, Enum duplicate member, NamedTuple field order / underscore names, dataclass
     order= overwriting __lt__, frozen-from-non-frozen, mutable default, non-default after default, field without an
     annotation, __slots__ vs class variable, MRO conflict, __init_subclass__ keyword mismatch) and raising module-level
     statements (1/0, d['k'], int('x'), assert False, a class body that raises).
  REPAIR (proposed, allow-list): a claimed file's MODULE TOP LEVEL (and every class body) is admitted only when each
  statement is in an exception-free allow-list (imports of known modules, def, class with validated bases / decorators /
  keywords, literal / annotated constant assignments, `if __name__ == "__main__":`, TYPE_CHECKING guards), and class
  creation is checked statically against CPython's rules (C3 MRO already computed as _mro363; dataclass / NamedTuple /
  Enum / __slots__ field rules); anything else refused under any claim in the file.
```
