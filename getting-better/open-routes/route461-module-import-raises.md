# OPEN ROUTE #461 — A VERIFIED FILE WHOSE IMPORT ITSELF RAISES (class creation / module-level statements)
**Status: REPAIRED (executor m1, driver run #3, 2026-10-29), Severity 2 (arguable — the claimed function is never callable; the PROGRAM crashes at import).**
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

## REPAIR (executor m1, driver run #3, 2026-10-29, off b1611d192; annotations §7.230, translational §T.6.240)

Code inline at the end of `_run_pipeline` (after the WhyML text is final; mirror twin `\trusted`; no new def, no axiom,
no emission change). Gate: any verified def of the file with a `no_exception` claim (`_rc444`). ALLOW-LIST, REFUSE BY
DEFAULT, decided by CPython itself on a SYNTHESIZED EQUIVALENT: the module top level and every class body it reaches are
run statement by statement over REAL values (literals, builtins, standard-library module objects, earlier bindings; a
module attribute that is run-time state -- `os.environ`, `sys.argv` -- is unknown). The only calls made are of
side-effect-free standard-library callables (`_pu461`: `int`, `frozenset`, `re.compile`, `typing.TypeVar`,
`dataclasses.field`, `os.path.join` ...), builtin-type methods, factory closures of `functools` / `dataclasses` / `enum`
/ `typing` / `abc`, the classes being synthesized, and two narrow rows of file code (a `def` whose body is `return
<constant>` called with no argument; a class whose own plain `__init__` only stores constants / parameters on `self`,
called with exactly its positionals -- the stores made for real by `setattr` on `object.__new__(C)`). Every other file
def is a PLACEHOLDER raising a private BaseException when CPython's machinery calls it (a metaclass, a base
`__init_subclass__`, an Enum member `__init__`, `__class_getitem__`, `__post_init__`, `__hash__` ...): refused, the
verifier does not judge code run at import (an identity `def d(x): return x` decorator is the identity). Each class is
created by `types.new_class` on its synthesized namespace (bindings in order, `__module__`, the real `__qualname__`,
`__annotations__` where they evaluate), its decorators applied for real (`dataclass(...)`, `total_ordering` ...), and
`_mro363` must exist. Statements outside the allow-list (`for`, `while`, `with`, `raise`, attribute stores, a walrus, a
class-body `global`, a non-stdlib `*` import) are refused; `if` runs the arm the real test selects (`if __name__ ==
"__main__":`, `if TYPE_CHECKING:` are not run at import); a `try` is admitted when its body is. Code
`PYCSL-R461-IMPORT-RAISES`; the message carries CPython's own exception text.

Witnesses 7130-7149 (all 20 red-team files: PROVED at base, REFUSED; 7137 / 7149 re-proved at base 370db7dc2). Control
7151 (imports, constants, `re.compile` / `frozenset` / `os.path.join` of literals, typing aliases, `if TYPE_CHECKING`,
a `try` import, an identity class decorator, Enum / IntEnum with a nested class, NamedTuple, dataclasses with
`default_factory` / frozen-from-frozen / `order=True`, `__slots__`, a field-initialiser global, the `__main__` driver):
PROVED at base and candidate.

OVER-REFUSAL COST, measured: static screen of every claimed file (1193 corpus + 0 pyref + 0 mirror files carry a
`#@ no_exception` line): a first cut refused 2 corpus PASS files (1297 `_h = Helper()`, 6330 `G = mk()`) -> the two
narrow file-code rows above (field initialiser, `return <constant>`); a too-wide module-attribute filter refused 5040
(`KW_ONLY` is an instance) -> the stable-object modules row; final screen 0 PASS refused. Byte-diff: root 2592 -> 2594
.mlw, 0 MOVED / 0 GONE / 0 APPEARED (2 new controls); pyref 2186 / 2186 0/0/0; mirror 53 / 53 0/0/0 (no OWED proof). Every
corpus FAIL file the screen refuses (40) was already refused or non-emitting at base, so no census row moved.

## RESIDUALS
- A non-standard-library module the file imports is found and its `from` names checked, but ITS OWN top level is not run
  (its import may raise); its values are unknown (a class based on one is refused).
- `if __name__ == "__main__":` is judged as imported: the driver block of a file RUN as a script is not judged.
- Annotations are lazy (CPython 3.14): one that fails on an unbound name / unknown value is kept as its string. A
  dataclass whose annotation would raise otherwise at `get_annotations` is refused (over-refusal: CPython 3.14 measured
  not to evaluate `x: K[1]` there).
- Platform-dependent values (`sys.platform`, `os.sep`) are the verifier's.
- Class statements inside function bodies are the function's own (not judged here).
