# OPEN ROUTE #580 — #568 A SUBCLASS OVERRIDE WITH A HIDDEN self.flag WRITE CALLED THROUGH A BASE-TYPED RECEIVER USES THE BASE METHOD'S CALLER-SIDE STUB (NO _pyobj_state WRITE)
**Status: REPAIRED (driver run #6, executor u36 off 822621340 = ghost-assign-bc6 at run #6 start, branch run6-u36; annotations §7.580). Mechanism: a call through a receiver typed as class C runs whichever override the object's class provides, so the stub of `C.m` (`expressions.py::_resolve_dotted_signature`, both arms) writes `_pyobj_state` when `C.m` or ANY override of it (route #278's MRO pairs `ir["overrides"]`, closed transitively) is in `_pyobj_state_writers` (the union of the overrides' emitted frames); an override whose frame gains the cell after a cell-less stub of an ancestor method was minted is refused at its definition (`functions.py::_emit_function`, new `PYCSL-R580-OVERRIDE-FRAME-AFTER-BASE-STUB`; twins `\trusted`, inline, no new def, no axiom).** Opened as: Status OPEN, Severity 1 (driver run #5, 2026-11-07, red team rt55 family R55-F6). Evidence: the REPAIR section below.
Exemplar witnesses-r580/gi1600_override_sub.py. Driver repro 2026-11-07T19:4xZ (scratchpad/run5/rt55repro.txt): Verification SUCCESS on BOTH main (pycsl-mainbase, before the L1 landing) and run5-int51, while CPython breaks the claim — PRE-EXISTING, not introduced by the run #5 changes being landed.

## REPAIR (driver run #6, executor u36, base 822621340, branch run6-u36, commit c0058a372 + the docs commit)

- RULE (annotations §7.580): `expressions.py::_resolve_dotted_signature` (the `self.` arm and the record-typed receiver
  arm): the stub of `C.m` also carries `_pyobj_state` when an override of `C.m` (route #278's MRO pairs,
  `ir["overrides"]`, closed transitively down the hierarchy) is in `_pyobj_state_writers`. `functions.py::_emit_function`
  (route #568's order backstop, one class up): when a method's frame gains the cell and a cell-less stub of an ancestor
  method it overrides (the pairs closed transitively up) was minted earlier, refuse `PYCSL-R580-OVERRIDE-FRAME-AFTER-
  BASE-STUB`. Mirror twins `\trusted`; inline, no new def, no axiom.
- WITNESSES: gi1600 x default / typed / store 3/3 REFUSED R580 (EMITTED at base; the driver measured it PROVED). u36
  probes `witnesses-r580/u36-probes/`: a grandchild override `T(S(C)).m` 3/3 R580; the hidden write reached through
  `self.m()` in an inherited method and through a `touch(s: S)` helper 6/6 refused by route #568's
  `PYCSL-R568-STUB-FRAME-ORDER` (already at base); a WIDER declared record frame on the override 3/3 refused by route
  #278 (already at base).
- CORPUS: 9280 (gi1600) and 9281 (grandchild) FAIL (PROVED at base, REFUSED R580 x 3 models at HEAD). Controls 9282 (the
  same shape with an honest override: the two `getattr` reads agree, `\result == 1`) and 9297 (R580's advice followed:
  the attribute a field of the BASE class listed in both `#@ assigns`; `\result == 1` from `ensures self.flag == v`)
  PASS at base and HEAD.
- RESIDUAL (named): the UNION arm (an override emitted before the base stub is minted) is reached by no measured shape:
  nothing calls the override, so the SCC order emits it after its base-typed callers and the refusal takes them all.
- INERTNESS (vs the driver base scratchpad/run6/base): corpus root 3023 -> 3030 .mlw 0 MOVED / 0 GONE / 0 APPEARED (+7 new
  controls), python-reference 2185 0 / 0 / 0, mirror 53/53 0 / 0 / 0 (nothing owed); rt55's 208 honest controls (CPython
  does not breach them): front-end verdicts identical, 81 emissions byte-identical. Fidelity / planes: run #6 README entry.
