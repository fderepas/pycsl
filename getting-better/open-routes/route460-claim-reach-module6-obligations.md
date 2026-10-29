# OPEN ROUTE #460 — A CALLER'S CLAIM DOES NOT REACH ITS CALLEES' MODULE 6 OBLIGATIONS / #161 ADMISSION
**Status: OPEN, Severity 1.** Measured by executor r1 (driver run #3, 2026-10-29, routes #444-#458 increment 2) and
driver-reproduced: `scratchpad/rt36/r460_factorial_unclaimed_callee.py` PROVES rc=0 (Verification SUCCESS) on main
8fe7204c3 AND on the post-#444-#459 candidate, while CPython raises `ValueError: factorial() not defined for negative
values` (`scratchpad/rt36/../` driver repro: `/tmp/.../scratchpad/rp36/r460.txt`, 2026-10-29T07:06Z).
Witnesses `witnesses-r460/` (2): `r460_factorial_unclaimed_callee.py`, `e3_k002_property_getter_raises.py` (red team 37: an un-claimed
`@property` getter's `self.d['k']` KeyError reaches the claimed reader `c.v`; driver-reproduced rc=0 on 370db7dc2).

```
#460 CLAIM REACH: `#@ no_exception \all` on f; f calls an UN-claimed g; g's Module 6 obligations (#160 / #434 / #436 /
     #437 ...) and route #161's admission are judged under g's OWN (empty) claim, so g's exceptions are owed nowhere.
  def g(n: int) -> int: return math.factorial(n)        # no claim
  #@ no_exception \all
  def f(n: int) -> int: return g(n)                     # PROVED; f(-1) -> CPython ValueError
  Partial closures already landed: route #178's callee summary (#430 hashing, #434-#436 sites), r1's `_rc444` claim
  reach for the #444-#458 opaque-fallback rules and #441's builtin-function rows (`_xf440`). r1 measured that extending
  the WHOLE #432 / #440 claim to callees refuses 10 accepted corpus files (`super()` receivers in reached constructors,
  `list.pop`), so it was not landed.
  REPAIR (proposed, structural): compute the reached-claim set of every function ONCE (the union of its callers'
  claims, through the call graph, `_rc444`) and make every claim-gated check -- Module 6 obligation emission
  (`_current_no_exception_all`), #161 admission, #432 / #440 receiver rules -- read the reached claim, not the
  function's own; measure the corpus cost per rule and narrow the 10 known over-refusals (constructor super() receivers,
  list.pop) with explicit rows.
```

## REPAIR (executor c460, driver run #3, 2026-10-29, off 370db7dc2; annotations §7.210, translational §T.6.220)

CENSUS FIRST: `getting-better/systematic-soundness-r3/c460/claim-gated-census.tsv` -- 31 claim-gated sites (every read
of a function's claim in `src/pycsl/`: the Module 6 `_current_no_exception*` state and its 60 readers, the
`_reset_function_state` refusal walks, the spec-level escape sets, the pycsl.py front-end and post-emission rules).
At base 3 were REACHED (r1's `_rc444` / `_xf440`), 4 were own claim + a transitive callee SUMMARY for a fixed site list
(#178, #430, #272, #179), the rest OWN. After the repair 19 read the reached claim (the 16 body checks below + the 3 of
r1), 4 stay SUMMARY, and 8 stay OWN by design or as measured residuals (2 RELATIONS on declared contracts, #278 and
Module 4's contradiction checks, must stay own; #432-family, #347, #357, #395 / #402, #439, ir_inline).

ONE REACHED-CLAIM SET. `_run_pipeline` (inline after route #444's closure; mirror twin `\trusted`) derives, from r1's
`_rc444`, `_rx460[IR name]` = what the claims of the defs that may call a def add to its own (names; `\all` as a
flag), and hands it to Module 6 as `transpiler.reach_r460`. Module 6's `_reset_function_state` (mirror twin
`\trusted`) joins it into the BODY context only: `_current_no_exception` / `_current_no_exception_all` (every trigger
assert of expressions.py / statements.py / stmt_control_flow.py / the transpiler) and the claim sets of the #64, #65
and #71 walks (refusals #64 / #65 / #66 / #71 / #72 / #160 / #161 / #173 / #207 and #178's `_act178`). The #434
fail-closed site census, #451 and #459 (post-emission, pycsl.py) count the reached claim too. The SPECIFICATION keeps
the declared claim: #304's own-raise wrapper, #171's widening, `callee_escaping`, `_wrap_call_with_callee_raises_assert`
(its `\all` arm now reads the declared flag), the claim a call site reads (`_module_func_no_exception`) and #178's
`_decl178`, so a modelled raise still escapes into the reached def's `raises` and is judged at its call sites.
A Module 6 refusal while some def is reached gains `NOTE (route #460)`, naming the reached defs.

DESIGN MEASURED BEFORE LANDING (sweep s1, the first cut: the reached claim written into the IR `contracts` Module 6
consumes, so the SPEC read it too): root corpus 25 MOVED, 2 GONE, 8 APPEARED -- explicit raises of reached callees
became `own raise reachable -> false` obligations (route #100 / #105 / #106 / #108 / #140 / #141 / #186 / #252 / #272 /
#278 corpus files moved), and 8 refused witnesses of #178 / #182 / #430 / #434 / #436 / #438 EMITTED (the summary
deferred to the callee's now-"declared" claim while the front-end hashing / bare-tuple checks of the callee still read
its own). Not landable; the body-only design above is what landed.

ROWS (the over-refusals the reach exposed; each narrower than the #161 default it relaxes): a zero-argument `super()` in
a PLAIN method of a file class with a positional first parameter (`meth_r460`, from the source decorators); and
`super().__str__()` / `super().__repr__()` (no arguments) in the same-named method of a file class whose bases are all
`object` / `BaseException` / a modelled builtin exception. Both measured on corpus control 6982 (r450), refused by the
first cut (an `Exception` subclass's `__str__` is reached as a file-class dunder).

WITNESSES (all PROVED at base 370db7dc2, CPython raises; at the candidate): 7050 `math.factorial` in an un-claimed
callee (REFUSED, #161 in g), 7051 `assert n > 0` in an un-claimed callee (FAIL: `no_exception: AssertionError
reachable` in g), 7052 the same in an un-claimed METHOD reached through `a.take(n)` (FAIL), 7053 transitive f -> g -> h
`math.factorial` under `no_exception ValueError` (REFUSED in h). CONTROLS (PROVED at base and candidate): 7054 g's
assert discharged by g's own `requires`, 7055 un-claimed callee and method with no raising site, 7056 a DECLARED
`raises ValueError when n < 0` in an un-claimed g, guarded by the claiming caller.

COST: corpus 0 PASS files refused (0 GONE), 2 MOVED (0382, 0383: a `256 // n` in a reached callee now carries
`assert { no_div_zero (n) }`, M1: both PROVED at base and candidate), pyref 0, mirror: see GATES. The 10 accepted files
r1 measured for the WHOLE #432 / #440 claim are not touched: that family stays own-claim (residual R1 below).

ADVICE (NOTE): `getting-better/systematic-soundness-r3/c460/advice/` -- a460_drop_claim (7050 with the caller's claim
dropped), a460_repair_there (#161's "give the callee a contract" applied in the reached g: a verified `fact` with
`requires n >= 0`, g guarded by its own requires), a460_requires_there (7051's g given its own `requires`): see GATES
for the verdicts. The NOTE is appended to an existing refusal (not a new `raise PyCSL*Error` site), so the advice-audit
plane does not key it; the audit is recorded here.

INCREMENT 2 (the #432 family). `_cx432` (read by #432 / #437 / #440 / #443 / #447 / #452) is joined with `_rc444`
for every def except a constructor (`__init__` / `__post_init__` / `__new__`). MEASURED FIRST, the whole reach (r1's
`_cx432 |= _rc444`) on the 1200 claimed corpus files: 12 accepted files refused -- 4690 4880 4882 4885 4886 5091 5680
6871 (#443: `super()` / `super(B, self)` receiver of `.__init__` underivable), 5270 (PASS) and FAIL witnesses 5240 /
5259 (#440 `self.disk.pop()`), all inside a CONSTRUCTOR reached only as a file-class dunder (no claimed caller of
those files constructs the class), and 6982 (`super().h` in a reached override); mirror 0 MOVED / 0 GONE. ROWS: a
constructor keeps its own claim for this family; #443's underivable-receiver refusal skips a `super(...)` receiver
when the def's OWN claim covers no AttributeError (the attribute is #450's to judge). Re-screened: 0 GONE, 0 APPEARED.
Witness 7059 (`b.find(n)`, int `n`, in an un-claimed callee: PROVED at base, CPython ValueError; REFUSED by #452 now),
control 7060 (`b.find(98)`: PROVED both). Red team 37's carrier `rt37/e3/k002_property_getter_raises.py` (an
un-claimed `@property` reading `self.d['k']`) is witness 7057: PROVED at base, FAILS now (reached through the
attribute-load edge; it fails by a Why3 type error `unbound ... str_hash_op`, which the SAME getter claiming `\all`
itself also hits at base -- a pre-existing emission defect of claimed property getters, fail-closed, residual R5);
control 7058 (a safe un-claimed getter: PROVED both).

RESIDUALS. R1: a constructor's #432-family rows read its own claim (a claimed caller's `C(..)` runs it: those
rows are not reached; the Module 6 body checks ARE). R2: #347 (partially-built objects), #357, #395 / #402 (run before the
closure exists), #439 (imported modules: another file's call graph). R3: the reach is route #444's over-approximation
(method tails on any receiver, every file-class dunder), so a def may be judged under a claim no caller actually
reaches it with (over-refusal, measured 1 corpus file before the rows above, 0 after). R4: a reached def's IMPLICIT
obligations are judged under its own `requires` only; a caller that guards an implicit raise in an un-claimed callee
(`if n > 0: g(n)` with `g` asserting `n > 0` and no `requires`) now FAILS where CPython is fine -- the repair is the
callee's own `requires`, which the NOTE names. R5: a claimed (own or reached) `@property` getter with a dict read
emits `str_hash_op` without its declaration (Why3 type error, fail-closed).
R6: a FRONT-END refusal (#432 family, as r1's `_xf440` rows already did) raised in a reached def says "this function
claims `#@ no_exception`" without the NOTE (it is the calling function's claim; "drop the claim" means the caller's --
followed for 7059: f without its claim VERIFIES only in the sense of being unclaimed, i.e. base behaviour).
