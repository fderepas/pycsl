# OPEN ROUTE #357 — VALUES OF A FIELD-LESS CLASS OTHER THAN `self` / PARAMETERS ARE NOT ERASED
**Status: REPAIRED, candidate (gen #37, 2026-10-25; r357 executor off 1a9cfa42 — see REPAIR). Was OPEN, Severity 1.** Red-team round 26 (2026-10-25, probes around the #339/#340/#343-#345 repairs); driver-reproduced on main 3d937bdb (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt26/driver-repro.txt`).
Witnesses `witnesses-r357/`: `r01_self_method_returns_self.py`, `r15_type_self_call.py`, `r22_dunder_class_ctor.py`, `r38_self_me_lt_noexc.py`, `r40_self_me_eq.py`, `r41_self_me_into_int.py`, `r50_type_self_ctor_args.py`.

Route #343 erases parameters and the receiver only. `s = self.me()` (`-> "W"`) keeps int laws (r01 `s - s == 0`, r40 `s == s`, r38 `s < s`, r41 into an `int` param); `type(self)()` / `self.__class__()` are emitted `any int` (r15, r22; r50 ignores a required `__init__` arg). CPython 1 / False / TypeError.

Repair: Erase every expression whose static type is a field-less class: method / callee results annotated with it (string annotations included), `type(e)()`, `e.__class__()`; refuse `type(e)(..)` construction when the constructor cannot be checked.

## REPAIR (2026-10-25, r357 executor off 1a9cfa42, repaired with routes #358 / #359; code 0bd03380 / fb898973 / 66f2f2ea / acec0e22 / af97b85a, corpus + docs 570c626f (annotations §7.31, translational §T.6.42), census 66f2dd33)
**Design: erase, and refuse the uncheckable constructor.** (1) In `_reset_function_state`'s route #255 resolution (Module 6,
mirror twin `\trusted`), a method candidate whose name is already in the unit-level `any_ret` set (return annotation outside
the lowered tags since route #336: a field-less class, `-> "W"` included) now adds the call spelling itself (`self.me`), so
`s = self.me()` joins route #249's erased set; both copies of the erased-expression walk (fixpoint and `_handle_binop`) answer
yes for an `UnknownPyExpr` (Module 5's catch-all: `type(self)()`, computed callees) and for a call `<e>.__class__(..)`. Route
#252 then refuses their flow into builtin-typed slots and `_handle_binop` takes the laws off. (2) In `_run_pipeline` (inline,
before route #290's computed-callee rule; mirror twin `\trusted`), a call `type(e)(..)` / `<e>.__class__(..)` is REFUSED
(`PYCSL-R357-DYNAMIC-CONSTRUCTOR`, one new raise site, witnessed by 4806/4822/4823) when it sits in a function whose IR
contract declares any `no_exception`, or passes a non-literal argument (the dynamic class's `__init__` may raise or mutate it).
The mirror's one site (`pure_ast` `type(self)(_avoid_backslashes=True)`, a literal keyword, no `no_exception`) is admitted.
**Probe table** (full proof via heavy.sh; base = 1a9cfa42 worktree; CPython violates each, `__main__` ground truth in the corpus file):
| witness | corpus | base | after |
|---|---|---|---|
| r01 `s = self.me()` (`-> "W"`), `s - s` | 4800 | rc=0 PROVED | rc=1 REFUSED (R252 flow into `-> int`) |
| r15 `type(self)()`, `t - t` | 4801 | rc=0 PROVED | rc=1 REFUSED (R252) |
| r22 `self.__class__()`, `t - t` | 4802 | rc=0 PROVED | rc=1 REFUSED (R252) |
| r38 `s < s` under no_exception | 4803 | rc=0 PROVED | rc=1 FAIL (PyCSL-R252 assertion) |
| r40 `s == s`, user `__eq__` -> False | 4804 | rc=0 PROVED | rc=1 FAIL (uninterpreted `==`) |
| r41 `h(self.me())` into `n: int` | 4805 | rc=0 PROVED | rc=1 REFUSED (R252 int parameter) |
| r50 `type(self)()` under no_exception, `__init__(k)` | 4806 | rc=0 PROVED | rc=1 REFUSED (PYCSL-R357-DYNAMIC-CONSTRUCTOR) |
| NEW latent: `type(self)(ys)`, `__init__` appends to `ys` | 4822 | rc=0 PROVED | rc=1 REFUSED (R357, non-literal argument) |
| NEW latent: `self.__class__(ys)`, same | 4823 | rc=0 PROVED | rc=1 REFUSED (R357) |
| control: `-> int` method result keeps `v - v == 0`; `type(self)()` / `self.__class__()` unused, no `no_exception` | 4830 | rc=0 PROVED | rc=0 PROVED |
Adjacent shapes already closed at base (probed): `t = W()` (R325), `mk() -> W` and `w.me()` on a parameter (route #337 erasure).
**Blast radius** (`bin/byte-diff-sweep.sh` in a base worktree at 1a9cfa42 vs candidate 570c626f, `bin/byte-diff-compare.py`): root
2308 base / 2324 candidate, 0 MOVED / 2 GONE (both declared, both `pycsl-expected: FAIL`, census rows re-measured VERIFY-FAIL ->
REFUSAL): `1313_route115_immediately_applied_lambda` (`return (lambda y: y + 1)(x)` from `-> int`: the `UnknownPyExpr` is now
erased, so route #252 refuses its flow — this route's rule), `1457_route147_unmodelled_foreign_ancestor` (`Cee(Exception, Ay)`:
route #359's rule, `BaseException.__init__` precedes `Ay.__init__`) / 0 APPEARED (18 of the 31 new files emit); pyref 2186/2186
0/0/0; mirror 53/53 0/0/0 (`bin/mirror-emit-sweep.sh`, `--min-files 50`) — no mover, no OWED whole-file proof. Ledger 3, no new
def, one new refusal code (witnessed), no gate loosened.
**Gates**: see the shared gate list in route #359's REPAIR.
**Residuals.** (1) The erased value's WhyML type is still `int` (as route #343). (2) A non-`self` typed receiver's method
result is erased only through the receiver's own erasure (a field-less parameter is erased since route #337); a RECORD
receiver's method annotated with a field-less class is erased by the same `any_ret` rule only when resolved by symbol type.
(3) A dynamic construction with literal arguments outside `no_exception` is admitted: its `__init__`'s effects on GLOBAL state
are not modelled (as for any opaque call). (4) Every `UnknownPyExpr` is now an arbitrary object: returning one through `-> int`
is refused (1313) even when the unrepresented expression is in fact an int.
