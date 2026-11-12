# OPEN ROUTE #598 — KEYWORD ARGUMENTS TO AN EXCEPTION CONSTRUCTOR (raise ValueError("a", q=1); OSError(...)) ARE DROPPED WITH NO ARITY CHECK, SO no_exception PROVES WHILE CPYTHON RAISES TypeError
**Status: REPAIRED (driver run #6, executor u42, branch run6-u42 off ghost-assign-bc6 bfe0e38fb; annotations §7.598). Mechanism (front end, route #589's raise loop in `pycsl.py::_run_pipeline`, twin `\trusted`; inline, no new def, no axiom, no emission change): the constructor of a raised exception class must accept the call -- a builtin is CALLED by the front end with the literal arguments, a user `__init__` is bound against its signature -- under route #589's relevance; otherwise new `PYCSL-R598-RAISE-CONSTRUCTOR-ARITY`.** Opened as: Status OPEN, Severity 1, pre-existing (red team rt57 F3, 8 probes; all prove on 822621340). R589 (route #589) judges only whether a dropped part can raise, not whether the constructor accepts it.** Witnesses witnesses-r598/.


## The defect

The model keeps the raised class and its first argument (route #589); route #589 judged only whether a DROPPED part
can raise, never whether the constructor accepts the call:

    #@ no_exception \all
    #@ ensures \result == 1
    def f(k: int) -> int:
        try:  raise ValueError("a", q=1)     # also OSError / KeyError / IndexError / RuntimeError / LookupError,
        except ValueError: return 1          #      and ValueError(q="a")
        return 2                             # PROVED; CPython: TypeError "ValueError() takes no keyword arguments"

(rt57 F3, 8 probes; all PROVED on pycsl-base6 822621340.)

## The repair

RULE (annotations §7.598), in route #589's loop (same population: the main file's raises and the dependency defs the
main file's claimed / handler-covered defs reach; same relevance: a verified def that claims or reaches a
`no_exception`, or that a handler may catch from, and every module-level raise), for `raise X(...)` and for a bare
`raise X` (which calls `X()`):

- RESOLUTION: `X` through plain aliases (`A = X`) and `from m import X as A`; a user class with `__init__` / `__new__`
  stops there; a user class without them continues to its (plain-name) bases; a builtin exception class ends it.
- BUILTIN: the front end CALLS the builtin class with the call's literal arguments (`None` for a non-literal one) and
  refuses on `TypeError` -- so `ImportError("a", name="m")` / `AttributeError(.., name=..)` pass, `ValueError("a",
  q=1)` does not; a non-literal argument that the builtin type-checks (`UnicodeDecodeError(enc, ...)`) is refused,
  fail-closed.
- USER `__init__`: bound against its signature (too many positionals without `*args`, an unknown / duplicate /
  positional-only keyword without `**kw`, a missing required positional or keyword-only parameter). A direct
  `E(..)` construction is ALSO route #369's (it refuses the same shapes earlier when the class is a record), so the
  new rule's own reach there is the bare `raise E` of a class whose `__init__` needs an argument.
- UNREAD: a `__new__`, a decorated `__init__`, a decorated class without `__init__` (a dataclass), a non-name base, and
  any `*` / `**` argument: refused when the call passes keywords or more than one positional argument.
- Code `PYCSL-R598-RAISE-CONSTRUCTOR-ARITY` (route #589's code and message unchanged). Advice: pass only the arguments
  the constructor accepts, binding extra data to a local first (audited FOLLOWABLE: advice/a598_first_argument_only.py
  = control 9685).

## Witnesses and measurements

- rt57 F3 (default model, `--no-proof`, base vs HEAD): hr1840, hs1970 / hs1971 / hs1973 / hs1974 / hs1975 / hs1976
  / hs1979 / hs1981 EMITTED at base, REFUSED R598 at HEAD; the route's witnesses (hr1840, hs1981) REFUSED R598 x
  default / typed / store.
- u42 probes `witnesses-r598/u42-probes/`: `ValueError(q="a")` (p598b) and a module alias `VE = ValueError` then
  `VE("a", q=1)` (p598c) REFUSED R598 (EMITTED at base); `ValueError("a", **d)` (p598a) and a user `class
  E(ValueError)` called `E(q="a")` (p598d) are refused EARLIER (route #369's construction arity / `**` rule) at base
  and HEAD. Controls: `ImportError("a", name="m")` (c598a) and a user `__init__(self, a, code=0)` called `E("a",
  code=1)` (c598b) still EMIT.
- CORPUS (expected FAIL, PROVED at base bfe0e38fb in the default model, full proof; REFUSED R598 x default / typed /
  store at HEAD): 9678 (hr1840 ValueError), 9679 (hs1981 OSError), 9680 (hs1971 `KeyError(q="a")`), 9681 (hs1974
  RuntimeError), 9682 (hs1973 IndexError), 9683 (a bare `raise E` of a class whose `__init__(self, a)` needs an
  argument; CPython TypeError). (A user `__init__` arity mismatch `E("a", "b")` and `E("a", q=1)` of a class without
  `__init__` are refused at base by route #369: not used.) CONTROLS (expected PASS, PROVED at base and HEAD): 9685
  (the advice: the keyword dropped, its data bound to a local), 9686 (`ImportError("a", name="m")`).
- RESIDUAL (named): a keyword passed INSIDE a user `__init__` to `super().__init__(msg, code=1)` is not judged here
  (it is a call in the `__init__` body, not the raise).
