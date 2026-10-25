# OPEN ROUTE #343 — A FIELD-LESS CLASS'S RECEIVER IS STILL `type <c> = int` — R337-SELF-OPERATOR IS SYNTACTIC ON THE TOKEN `self`
**Status: REPAIRED, candidate (gen #37, 2026-10-24; r343 executor off b83a217b — see REPAIR). Was OPEN, Severity 1.** Red-team round 25 (2026-10-24, probes around the #336-#342 repairs); driver-reproduced on main 78c92b39 (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt25/driver-repro.txt`).
Witnesses `witnesses-r343/`: `b01_self_alias_sub.py`, `b04_self_lt_alias_noexc.py`, `h01_self_abs_noexc.py`, `h03_self_alias_eq.py`, `h05_self_range.py`, `h06_self_walrus_sub.py`, `h07_self_return_int.py`, `h08_self_list_elem_sub.py`, `h10_nested_def_self.py`, `l05_self_to_int_param.py`, `l06_self_in_int_list.py`, `l08_self_to_float.py`.

Route #337's repair refuses an operator only when an operand is literally spelled `self`. Any alias (`s = self`, `(s := self)`, `[self][0]`, `t = self; u = t`) keeps the int type and every int law; so do builtins taking `self` (`abs`, `range`, `max`), `self` flowing into an `int` parameter / `List[int]`, and `self` returned through `-> int`. Emission: `type p = int`, `let p__m (self: p)`, `py_range_1 self`. Contrast: a receiver named `me` is erased and refused (b02).

Repair: Give a field-less class's receiver the same route #249 erased type its parameters already get (preferred), or follow aliases and int-slot flows; measure the 21 mirror `type c = int` aliases first (#336 finisher found the mirror depends on them).

## REPAIR (2026-10-24, r343 executor off b83a217b; code 9b8ee8b8 / e8f0cc77, corpus 3aa9c2b2, docs e1ea6c14 (annotations §7.27, translational §T.6.38) + route docs)
**Design: the preferred fix — the receiver is erased, the alias stays.** In `_reset_function_state`'s route #249 pre-scan (Module 6,
mirror twin `\trusted`) the receiver `self` of a method whose class is neither a record nor a variant joins the erased set before
the binding fixpoint, exactly like a field-less-class PARAMETER since route #337. The fixpoint propagates it through every binding
form (alias, walrus, container element, builtin passthrough), `_handle_binop` takes the laws off `==` / arithmetic / ordering, and
route #252 refuses its flow into an `int` / `float` / `str` / `bool` / `bytes` parameter / field / return. Its WhyML type is
unchanged (`type <c> = int`, `(self: c)`), so the mirror's 21 alias-typed emitter classes are untouched: MEASURED first — erasing
`self` naively GONE'd mirror `module6_whyml/functions` (`getattr(self, "_record_types", {})` flowed into `-> str`); hence an
attribute read / `getattr(self, ..)` / method call ON `self` is not a use of the erased value (both copies of the walk skip the
`self` base; `self.m()` was never erased). Base-inert by construction: `self` was never in the erased set before.
Adjacent latent (needed for h05): a builtin call on an erased argument (`range(x)` for `x: Any`, too) carried NO exception VC.
Under `no_exception`, a program-context call of a dunder-dispatching / type-checking builtin (`range`, `abs`, `len`, `min`/`max`,
`sum`, `sorted`, numeric / str / container constructors, `hash`, `iter`/`next`, `chr`/`ord`/`bin`/`hex`/`oct`, `print`, ...) not
shadowed by a unit function, with an argument route #251's `r251_erased?` probe calls erased, is now preceded by
`assert { [@expl:PyCSL-R343 ..] false }` (inline in `_expr_to_whyml`'s dispatch, mirror twin `\trusted`).
**Probe table** (full proof via heavy.sh; base = b83a217b worktree; CPython violates each, `__main__` ground truth in the corpus file):
| witness | corpus | base | after |
|---|---|---|---|
| b01 `s = self; s - s`, user `__sub__` -> 1 | 4610 | rc=0 PROVED | rc=1 REFUSED (R252 flow into `-> int`) |
| b04 `s = self; s < s` under no_exception | 4611 | rc=0 PROVED | rc=1 FAIL |
| h01 `abs(self)` under no_exception | 4612 | rc=0 PROVED | rc=1 REFUSED |
| h03 `s = self; s == s`, user `__eq__` -> False | 4613 | rc=0 PROVED | rc=1 FAIL |
| h05 `range(self)` under no_exception | 4614 | rc=0 PROVED | rc=1 FAIL (PyCSL-R343) |
| h06 `(s := self) - s` | 4615 | rc=0 PROVED | rc=1 REFUSED |
| h07 `return self` through `-> int` | 4616 | rc=0 PROVED | rc=1 REFUSED |
| h08 `xs = [self]; xs[0] - xs[0]` | 4617 | rc=0 PROVED | rc=1 REFUSED |
| h10 `t = self; u = t; u - t` | 4618 | rc=0 PROVED | rc=1 REFUSED |
| l05 `h(self)` into `n: int` | 4619 | rc=0 PROVED | rc=1 REFUSED |
| l06 `xs: List[int] = [self]` | 4620 | rc=0 PROVED | rc=1 REFUSED |
| l08 `max(self, 0)` | 4621 | rc=0 PROVED | rc=1 REFUSED |
| NEW latent: `range(x)`, `x: Any`, no_exception | 4622 | rc=0 PROVED | rc=1 FAIL (PyCSL-R343) |
| control: field-less `self.h() + 1`, `s is self` | 4630 | rc=0 PROVED | rc=0 PROVED |
| control: record receiver `h(self) - self.x` | 4631 | rc=0 PROVED | rc=0 PROVED |
| control: `range(n)` / `len(xs)` / `max(n, 0)` on int, no_exception | 4632 | rc=0 PROVED | rc=0 PROVED |
**Blast radius** (base worktree at b83a217b vs candidate, `bin/byte-diff-sweep.sh` + `bin/byte-diff-compare.py`): root 2284 base /
2293 candidate, 0 MOVED / 0 GONE / 0 APPEARED (9 new witness files emit; the 5 GONE of the first compare were files lost to a
concurrent `check-assumed-facts` sweep in the same tree, re-emitted individually: identical); pyref 2186/2186 0/0/0; mirror
53/53 0/0/0 (`bin/mirror-emit-sweep.sh`, `--min-files 50`) — no mover, no OWED whole-file proof. Ledger 3, no new def, no new
refusal code (the R343 assertion is a VC label; #345 reuses `PYCSL-R341-CLASS-BASE-NOT-A-NAME`), no gate loosened.
**Gates** (all three routes, one run on e1ea6c14 + route docs): GATES_PLACEHOLDER
**Residuals.** (1) The WhyML type of a field-less receiver is still `type <c> = int`; soundness rests on the erased-set
discipline (routes #249/#251/#252 + this one), not on the type. (2) A nested def / lambda capturing `self` is a separate unit whose
`self` is a free name, not the erased receiver (h10's original title; not reproduced as a false proof). (3) Attribute-protocol
builtins (`getattr` / `setattr` / `vars` / `dir`) on an erased value are not covered by the R343 assertion (a `getattr` without
default may raise AttributeError — pre-existing, not this route's). (4) `PYCSL-R337-SELF-OPERATOR` stays (now redundant for
field-less classes, harmless).
