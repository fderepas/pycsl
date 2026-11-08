# OPEN ROUTE #582 — A METHOD CALLED THROUGH A CLASS-BODY ALIAS (n = m; also two-level, unbound C.n(c, 5), subclass alias) IS AN OPAQUE RECEIVER-LESS CALL WITH NO writes, SO THE WRITTEN RECORD FIELD STAYS UNCHANGED IN THE PROOF
**Status: REPAIRED (driver run #6, executor u36 off 822621340 = ghost-assign-bc6 at run #6 start, branch run6-u36; annotations §7.582). Mechanism (front end, `pycsl.py::_run_pipeline` on the standard-library AST, twin `\trusted`; inline, no new def, no axiom): a name bound in a class body by anything but a `def` (or stored on a file class from outside, `C.n = ...` / `setattr`) is a possible method unless its value is plain data or resolves, through further aliases, to exactly one function whose frame is `#@ assigns \nothing`; a call `<x>.n(...)` in any function is then REFUSED, new `PYCSL-R582-CLASS-BODY-ALIAS-CALL` (keyed on the name for every receiver; `X.n(...)` through a file class `X` consults `X`'s file MRO only).** Opened as: Status OPEN, Severity 1 (driver run #5, 2026-11-07, red team rt55 family R55-F8). Evidence: the REPAIR section below.
Exemplar witnesses-r582/hb1600_plain.py. Driver repro 2026-11-07T19:4xZ (scratchpad/run5/rt55repro.txt): Verification SUCCESS on BOTH main (pycsl-mainbase, before the L1 landing) and run5-int51, while CPython breaks the claim — PRE-EXISTING, not introduced by the run #5 changes being landed.

## REPAIR (driver run #6, executor u36, base 822621340, branch run6-u36, commit c0058a372 + the docs commit)

- RULE (annotations §7.582): `pycsl.py::_run_pipeline`, on the standard-library AST: a name bound in a class body by
  anything but a `def` (assignment, annotated assignment with a value, augmented assignment, loop / `with` / walrus
  target, import), or stored on a class of this file from outside its body (`C.n = ...`, `setattr(C, "n", ...)`; a
  computed `setattr` name counts as every name), is a possible METHOD unless its value is plain data (constants,
  displays / arithmetic of constants, a constant f-string, a dataclass `field(...)` with a plain-data `default`) or
  resolves, through further class-body aliases, to exactly one IR function (`n = m` of the same class, `n = C.m`, `n =
  f` a module function) whose frame is `#@ assigns \nothing`. A call `<x>.n(...)` in any function is then REFUSED,
  `PYCSL-R582-CLASS-BODY-ALIAS-CALL`: for every receiver by the name, except `X.n(...)` through a CLASS of this file,
  which consults `X`'s file MRO only. Twin `\trusted`; inline, no new def, no axiom.
- MIRROR: the FIRST spelling (every receiver by the name, no `\nothing` admission) REFUSED the `frontend/pure_ast.py`
  mirror (`Constant.__new__(cls, ...)` in `_new`, with `__new__ = _new` in `Num` / `Str` / `Bytes` / `NameConstant`).
  Made exact rather than exempted: `_new` is `#@ assigns \nothing` (the alias admitted). The pure_ast emission is
  byte-identical to the base.
- WITNESSES: the 12 rt55 witnesses x default / typed / store 36/36 REFUSED R582 (all EMITTED at base; the driver measured
  hb1600 PROVED). u36 probes `witnesses-r582/u36-probes/`: a module function bound in the class body (`n = g`), an
  annotated alias (`n: Any = m`) 6/6 R582; `staticmethod(lambda ...)` in the body, a module-level `C.n = C.m`, `setattr(C,
  "n", C.m)` 9/9 refused by pre-existing rules (computed-receiver / function-name rebinding, already at base).
- CORPUS: 9283-9290 and 9292 FAIL (PROVED at base, REFUSED R582 x 3 models at HEAD); 9291 (module function in the body)
  FAIL (at base a Why3 typing error on `self: Any`; REFUSED at HEAD). Controls 9293 (plain-data class bindings; R582's
  advice 'call the method by the name of its `def`' = `witnesses-r582/advice/a582_call_def_name.py`), 9294 (the second
  advice, an own `def n` calling `m` = `advice/a582_own_def.py`) and 9296 (an alias of a `\nothing` method admitted) PASS
  at base and HEAD.
- INERTNESS (vs the driver base scratchpad/run6/base): corpus root 3023 -> 3029 .mlw 0 MOVED / 0 GONE / 0 APPEARED (+6 new
  controls), python-reference 2185 0 / 0 / 0, mirror 53/53 0 / 0 / 0 (nothing owed); rt55's 208 honest controls (CPython
  does not breach them): front-end verdicts identical, 81 emissions byte-identical. Fidelity / planes: run #6 README entry.
