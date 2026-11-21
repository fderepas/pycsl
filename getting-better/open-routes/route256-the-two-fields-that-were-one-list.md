# OPEN ROUTE #256 — TWO LIST FIELDS OF ONE RECORD MAY HOLD THE SAME LIST

**Status: RESOLVED (declared assumption FIELD-DISJOINT), gen #36, 2026-10-17** — was OPEN, Severity 1
(weaker: the alias is built in unverified code). See "Resolution" at the end. Red-team
finding; driver-reproduced at HEAD fa283db6 (rc=0; CPython 7).

## Witness
`witnesses-r256/p34_two_list_fields_store.py`: `T.poke` (`assigns self.xs`) does `self.xs[0] = 7`, returns
`self.ys[0]` under `requires self.ys[0] == 0`; `ensures \result == 0` proves. CPython: `L = [0]; T(L, L).poke()` = 7.

## Mechanism
Why3 regions assume distinct record fields never alias (emitted frame `ensures { self.ys = old self.ys }`). A
verified caller that builds the alias fails closed (R167), so the hole needs an unverified constructor call.

## Repair direction
Either surface "distinct mutable fields of a record are disjoint objects" as a DECLARED model assumption
(soundness report, like FLOAT-FINITE/BUILTIN-EXACT — the ownership doc's rule R1 is the existing statement),
or refuse a method that mutates one array field and reads another of the same type without a separation
precondition. Decide with the blast radius measured.

## Resolution (gen #36, 2026-10-17): option (a), DECLARED MODEL ASSUMPTION FIELD-DISJOINT
Blast radius of option (b) (refuse a method that mutates one mutable field and accesses another), measured
with the new report over the root corpus and the mirror: 15 root files (the `Bank.transfer` drivers
0723-0725, 1132, the #243 field-alias witnesses, 2570) and 7 mirror files / 41 methods (e.g.
`_emit_body_code`, `_build_callee_no_exception_summary`, `_audit_one_prover`) — a refusal would GONE 7 mirror
files, and PyCSL has no separation precondition to offer as the fix. So (a), following FLOAT-FINITE /
BUILTIN-EXACT (f5c7502b): `pycsl --soundness-report` lists FIELD-DISJOINT ("two distinct mutable fields —
list/dict/set/record-valued, of one record or the same field of two record values — hold distinct objects";
the ownership discipline's rule R1) for every function that mutates a mutable field in place (subscript
store/`del`, mutator call, augmented assignment, nested field store) and also accesses another mutable
field. Inline in `pycsl.py::_build_soundness_report` (mirror twin `\trusted`). Docs: static semantics
App. C.1, translational §T.10.1/§T.10.5, README, `bin/check-assumed-facts.py`. Counterexample corpus 2570
(`# pycsl-model-assumption: FIELD-DISJOINT`, PASS). No strict mode. Ledger 3.
