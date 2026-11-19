# ROUTE #565 — A None-INITIALISED LOCAL REBOUND BY A TUPLE-UNPACK ASSIGNMENT (`t = None; if x > 0: t, u = 1, 2`) STILL HAS `t is None` FOLDED TO TRUE (`pycsl_none = pycsl_none`), SO A FALSE `ensures` PROVES
**Status: REPAIRED (driver run #5, 2026-11-05, executor u28, branch run5-u28 off b432460d6 = run5-int36).** Opened in driver run #5 (lever executor lvC side probe, driver-reproduced on e6a0be3ba).
Exemplar `witnesses-r565/w565_unpack_rebind.py`: `def f(x: int) -> int` with `#@ ensures \result == 0`: `t = None; u = None; if x > 0: t, u = 1, 2; if t is None: return 0; return 1`. CPython: f(1) == 1 (VIOLATION). Control `witnesses-r565/c565_plain_rebind_control.py`: the same with `t = 1` (plain assignment) is correctly NOT PROVED.

## Root cause

`_erased_truthy_locals` (Module 6) carries the DECIDED facts about a local bound to `None` (`None#empty`: a read
is the shared opaque `pycsl_none`, so `t is None` is `pycsl_none = pycsl_none`, truthiness is `false`, two such
reads compare equal) and to NaN (`NaN`: `t == t` is `false`). Two writers keep it, and BOTH only knew the plain
single-name `Assign`:
1. the LINEAR recorder in `statements.py::_handle_assign_stmt` writes / clears the record per emitted plain
   assignment — a `TupleUnpack`, a `for` target (name or tuple), a walrus `NamedExpr` and a `match` capture
   never reach it, so the record survived the rebinding even at the TOP LEVEL;
2. the route #46 AMBIGUITY pre-scan in `functions.py::_reset_function_state` collected only `Assign` nodes, so a
   name bound to `None` by `Assign` and to something else by any other form was never marked `AMBIG`.
Two siblings of the same record, found by the family sweep:
3. a NESTED `def t` (and only `def`: a nested `class t` is already refused) is LIFTED to a sibling and its
   binding of `t` in the enclosing function is DROPPED, so `t = None; def t(): ...; t is None` folded True;
4. an `Optional[...]` (or `IrONone` / `IrSNone` / `emit_ir`) carrier marked `AMBIG` by the pre-scan had the mark
   POPPED at its first assignment (route #46's carrier gate), after which the linear recorder RE-RECORDED
   `None#empty` at the next `None` binding: `t: Optional[int] = None; if x > 0: t = 5 else: t = None; if t:`
   decided `false` after the join (CPython 1).

## Repair (no new def, no new code, no axiom, no `\trusted`; all three mirror twins `\trusted`)

- `functions.py::_reset_function_state` (pre-scan): every `TupleUnpack` target, `For` target / `tuple_targets`,
  `NamedExpr` target and `match` `Capture` name is recorded as an OTHER binding at NESTED depth, so a name also
  bound to `None` / NaN becomes `AMBIG` / `AMBIG#nan`: the read is the ordinary `!t`, truthiness and `is None`
  are undecided, a NaN comparison is refused (route #46's existing message). Comprehension targets are NOT
  collected (they do not leak; control 8994 keeps the decided fold).
- `Module3_Weaver.process` (lift marks): a nested `def` whose name is also bound by an enclosing function
  (parameter, Name store, import, except name) is a lifted-name collision — refused by the existing Module 6
  lift refusal.
- `statements.py::_handle_assign_stmt`: the carrier drop is STICKY (`AMBIG#opt#empty`): it survives every later
  binding, `_to_bool` skips it (`#empty`), the read site does not treat it as `None#empty`, so the carrier is read.

## Evidence

- Witness family `witnesses-r565/q*.py` (43 probes; CPython breaches every one under `ulimit -v 2000000`) x default
  (hoare) / typed / store, table `witnesses-r565/RESULTS-base-b432460d6-vs-u28.txt`: base b432460d6 **41 PROVED**
  (q01 / q02 / q03 tuple unpack nested / top-level / `is not None`, q07 `for` target, q09 walrus, q13 swap, q20
  truthiness, q30 two rebound Nones equal, q34 unpack in `else`, q35 in `try`, q37, q38 single-element target,
  q46 Optional join: all three models; q27 nested def, q28 call-returned pair: default only) -> HEAD **0 PROVED**
  (q11 / q22 NaN and q27 now REFUSED, the rest NOT PROVED). Forms refused upstream at base and HEAD alike (not
  modelled, so never folded): list / starred / nested targets (#301), tuple `for` target read after the loop,
  walrus in a comprehension (#180), `except ... as` read (#233), `with ... as`, `nonlocal`, `global`, import-as,
  nested `class`.
- Controls `witnesses-r565/controls/` (14): every control PROVED at base is PROVED at HEAD in all three models;
  `k06` (walrus-bound local read back) newly PROVES (the base read the stale `pycsl_none`).
- Corpus `8980`-`8991` FAIL (PROVED at base in all three models, `8990` default only; NOT PROVED / REFUSED at HEAD
  in all three), `8992`-`8999` PASS (base and HEAD, all three models). Census rows appended for the 12 FAIL files.
- Byte-diff vs b432460d6: root 2929 -> 2948 0 MOVED / 0 GONE / 0 APPEARED (+19 emitted new files), python-reference
  2191 0 / 0 / 0, mirror 53/53 0 / 0 / 0: no movers, no mirror proof owed. rt43 / rt44 149 honest controls:
  verdicts identical, 0 .mlw moved.
- Fidelity: `bin/check-self-annotate-sync.sh`, `bin/self-annotate-mirror-check.sh`, `bin/doc-coherency.py --check`
  rc 0. No `\trusted`, no axiom added.
