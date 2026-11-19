# OPEN ROUTE #589 — raise E(a, <expr>): CONSTRUCTOR ARGUMENTS AFTER THE FIRST ARE NOT EVALUATED, SO THEIR EXCEPTIONS (IndexError / ZeroDivisionError / in f-strings) ARE DROPPED UNDER no_exception
**Status: REPAIRED (driver run #6, executor u39, branch run6-u39; annotations §7.589). Was: OPEN, Severity 1, pre-existing (red team rt56 R56-A; Verification SUCCESS on the run #6 base 822621340 and on int55 while CPython raises; scratchpad/run6/rt56-base6.tsv).** Witnesses witnesses-r589/ (ha1758 xs[9], ha1759 1 // k, ha1760 f-string).

## REPAIR (driver run #6, executor u39, base c55a7b233 = run6-int56, branch run6-u39)

- RULE (annotations §7.589), `pycsl.py::_run_pipeline` right after route #506's census, on the standard-library AST of the
  source (twin `\trusted`; inline, no new def, no axiom; no emission change): Module 5 keeps `exc_type` and the FIRST
  constructor argument of `raise E(a, ...)`; every later positional argument and keyword value is dropped (route #310
  already refuses a dropped CALL). A dropped part may now hold only literals, tuple / list displays of them, a negated
  number, and names bound on entry to the raise (a parameter, a module-level binding, a builtin, or a local assigned by a
  plain assignment preceding the raise, or one of its enclosing statements, in the same statement block). Anything else
  is REFUSED, `PYCSL-R589-RAISE-ARGUMENT-UNEVALUATED`, when the raise is RELEVANT, with route #506's own sets: its
  VERIFIED def claims any `no_exception` (declared or reached, route #460) or a handler may catch from it (`_cb506`, the
  call graph included); a module-level raise and a def the IR does not name are relevant (fail-closed); a `\trusted`
  def is not (no body is proved). Builtin exceptions too (`raise ValueError("a", 1, d["k"])`).
- CROSS-FILE (found while repairing, probe `q5`): an IMPORTED callee `g` whose body is `raise E("a", xs[9])` exports
  `raises { E _ -> true }` only, so a caller's `except IndexError` arm was dead (the honest-lowered twin `v = xs[9]` is
  route #178's refusal). The rule therefore also walks the modules the main file imports (resolved like route #181,
  `from pkg import mod` submodules included) and judges a def there whose NAME the main file's relevant defs call,
  transitively through those modules' calls (name-based, so an over-approximation). Witness 9605.
- MIRROR: the mirror holds three raises with a non-trivial dropped part -- `frontend/pure_ast.py` `error` /
  `unsupported` (the location tuple `(self.filename, t.start[0], t.start[1] + 1, t.string)`, VERIFIED defs) and
  `pycsl.py` `_MergeConservationError(first_n, merged_n, f"...")`. None is relevant (no claim, no handler reaching them,
  no mirror file's relevant def calls them): the mirror stays byte-identical (see INERTNESS).
- RESIDUAL (named): a dropped part's exception is still invisible to a caller OUTSIDE the program's import closure, and the
  name-based closure can only over-refuse. The source-level "bound" judgement does not see a `del` between the
  assignment and the raise.

## WITNESSES, CONTROLS, INERTNESS (routes #589 / #590 / #591 together)

- rt56 witnesses (`witnesses-r589/`, `-r590/`, `-r591/`, 7 files) x default / typed / store: 21/21 REFUSED with their route's
  code (all EMITTED and type-checked at base c55a7b233; the driver measured them PROVED on 822621340 and int55).
- Corpus FAIL (all three models REFUSED at HEAD with the route's code): #589 9590 (`xs[9]`), 9591 (`1 // k`), 9592
  (f-string), 9593 (a builtin `ValueError("a", 1, d["zz"])`, two handlers), 9594 (no claim, an `except IndexError`
  handler only), 9605 (an imported callee, `multi_file_lib/r589_raising.py`); #590 9596 (dataclass), 9597 (plain class +
  `__init__`), 9598 (a non-exception base chain, raised bare), 9599 (`raise mk()` of a def; at base refused R325), 9600
  (`raise "boom"`); #591 9601 (`from 1`), 9602 (`from k`), 9603 (`from str(k)`). PROVED at base c55a7b233 (default
  model, full proof): 12 of the 14 -- every one but 9599 (refused R325 at base) and 9600 (not proved at base) -- so
  each of those 12 is a measured false proof the repair closes. Controls (PASS, the advice followed): 9610 (#589, the operand bound to a
  local first), 9611 (#589, literals / a negated number / a tuple / a parameter / a local assigned earlier in the same
  `try` block), 9612 (#590, `E(B)`, `B(Exception)`, an alias, bare, and a builtin), 9613 (#591, `from None` inside and
  outside a handler, `from ValueError`): all four Verification SUCCESS at HEAD in the default model (the corpus runs them
  in it); under `--memory-model typed` / `store` they are NOT proved (cause not investigated; no
  claim of this repair). Two drafted witnesses were dropped because a PRE-EXISTING rule already refuses
  them (`raise E("a", v)` with `v` possibly unbound: the definite-assignment rule; `from e` after the handler ended: the
  same rule), and `from e` inside the handler is route #233's refusal (a read of `e`).
- rt56 raise families (g1700 + g1760, 280 probes) at --no-proof, base vs HEAD: 268 identical verdicts; the 12 that move are
  the 7 witnesses and 5 CPython-breaching probes that were Why3-ill-typed at base and are now REFUSED R590 (`raise 5`,
  `raise "s"`, `raise None`, `raise f()` of a non-exception function, hi1768 a call returning an instance). rt56's 18
  honest probes in these families (CPython does not breach them): verdicts identical.
- Corpus candidates (every raise of a non-builtin name, with extra arguments, a cause, or a non-name exception: 35 files
  outside 9590-9629, root + python-reference): --no-proof verdicts identical at base and HEAD.
- MIRROR (landability): `bin/mirror-emit-sweep.sh` at HEAD vs the same sweep of the base c55a7b233 (both launched from the
  same cwd), `bin/byte-diff-compare.py --min-files 45`: **53 / 53 byte-identical, 0 MOVED / 0 GONE / 0 APPEARED, rc 0**.
  No mirror file moves, so no mirror re-proof is owed. (Measured before it as well: the 53 mirror files emitted one by one
  at --no-proof, none refused, the same 53 / 53 against the base sweep.)
