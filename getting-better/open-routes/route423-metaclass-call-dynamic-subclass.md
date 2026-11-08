# OPEN ROUTE #423 — DYNAMIC SUBCLASSES THROUGH ANY METACLASS CALL OTHER THAN `type(..)` ESCAPE §7.62 
**Status: REPAIRED, Severity 1.** Red-team round 33 (2026-10-27, convergence measurement after the run #3 allow-list repairs; 653 screened / 385 fully proved / 116 confirmed); driver-reproduced on main (see `scratchpad/rt33/driver-repro.txt`).
Witnesses `witnesses-r423/` (12): `a20_type_alias_call.py`, `a23_dyn_abcmeta_call.py`, `a25_dyn_type_call_dunder.py`, `a27_dyn_meta_subclass_call.py`, `a34_dyn_getattr_alias.py`, `j00_dyn_abcmeta_new.py`, `j01_dyn_m_new.py`, `j02_dyn_m_alias.py`, `j04_dyn_enummeta_call.py`, `j05_dyn_abcmeta_from_import.py`, `j08_dyn_type_new_alias.py`, `j09_dyn_classmethod_mk.py`.

```
#423 DYNAMIC SUBCLASSES THROUGH ANY METACLASS CALL OTHER THAN `type(..)` ESCAPE §7.62   [slips past §7.62 / route #405]   (12)
  a20  T = type; D = T("D", (B,), {"__hash__": None}) in __main__; f(b: B) hashes {b} PROVED          CPython TypeError
  a23  abc.ABCMeta("D", (B,), ..)   j05 `from abc import ABCMeta; ABCMeta(..)`   j00 abc.ABCMeta.__new__(abc.ABCMeta, ..)
  a25  type.__call__(type, "D", (B,), ..)   j09 (same)   j04 (same, behind an `if False` arm)
  a27  M("D", (B,), ..) for the file metaclass M(type) (empty, admitted by §7.61)   j01 M.__new__(M, ..)   j02 MM = M; MM(..)
  j08  tn = type.__new__; tn(type, ..)
  a34  T = type; S = T("S", (R,), {"k": 5}); getattr(r, "k", 0) == 0 PROVED (GD)                     CPython 5
  (Refused: B.__class__(..), type(B)(..), getattr(builtins, "type"), eval("type"), builtins.type(..), type(*a), vars(builtins)
  ["type"]; the ensures-override forms a30-a33 / m20-m22 refuse on the erased lambda / def.)
  REPAIR: refuse a call (in the driver too) of any expression whose value may be `type`, `type.__new__`, `type.__call__`, a
  standard-library metaclass (abc.ABCMeta, enum.EnumMeta / EnumType, any `type` subclass) or a file metaclass, through any
  alias (a name bound to such a value, `from abc import ABCMeta`), with >= 2 positional arguments -- or polarity: admit a
  3-argument class creation only when the callee is literally `type` AND its bases are `()`.
```

## REPAIR (executor g3, driver run #3, 2026-10-27, off ac28806be; annotations §7.112, translational §T.6.123)

Reference-based polarity (after §7.62's rule): every load of a CLASS-CREATING value (`type`, a stdlib `type` subclass resolved through imports, a file class deriving from one) is admitted only as a class base / metaclass=, isinstance / issubclass argument, comparison operand, receiver of `__name__` / `__qualname__` / `__module__` / `__doc__` / `__instancecheck__` / `__subclasscheck__` / `__mro__` / `__bases__`, one-argument `type(x)`, or callee of a call with literal bases `()`; anything else PYCSL-R405-DYNAMIC-SUBCLASS (new raise site, advice audited FOLLOWABLE). Also a stdlib class whose METACLASS overrides `__call__` (`enum.Enum("D", "A", type=B)`) called with >= 2 arguments / keywords (probe q03 REFUSED). Witnesses 6285-6296; control 6332.

Executor g3, driver run #3, 2026-10-27, off ac28806be. Gates (final candidate): root byte-diff 2497 -> 2512 0 MOVED / 0 GONE / 0 APPEARED (15 new sources); pyref 2186 / 2186 0/0/0; mirrors 53/53 0/0/0 (a first candidate GONE 2 mirrors -- frontend/pure_ast `type.__instancecheck__`, module6_whyml/statements a str-row `.get` -- both fixed before landing, so NO mirror refusal); pycsl_lib --no-proof screen identical (104 files, rc0 87); fidelity rc=0; soundness planes 61/61 green; getattr-erasure (control 6337 registered) / clause-survival / assumed-facts --emit-dir / open-route-carriers / refusal-witness-coverage / refusal-advice-audited rc=0. Logs: getting-better/systematic-soundness-r3/g3-r421-429/.

## RESIDUALS (honest)

A FILE Enum class without members called functionally (`E("D", "A B")`) is not confined (unprobed for a violation).
