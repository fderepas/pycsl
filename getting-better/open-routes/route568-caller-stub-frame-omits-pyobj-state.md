# ROUTE #568 — A METHOD CALL IS MODELLED THROUGH A CALLER-SIDE STUB BUILT FROM THE *DECLARED* `#@ assigns`, WHICH CAN OMIT `_pyobj_state` WHILE THE BODY WRITES IT (a hidden attribute write; even an honest `assigns self.a, self.flag` whose non-record label is filtered; an unresolved receiver typed `C` / `Any` gets NO frame and the caller is treated as pure), SO TWO `getattr` READS AROUND THE CALL COLLAPSE AND A FALSE POSTCONDITION PROVES
**Status: REPAIRED (driver run #5, 2026-11-06, executor u30, branch run5-u30 off 693e20184 = run5-int40).** Opened in driver run #5 (u29 finding, driver-reproduced on 85a942c5e); the opening record follows.
Opening record (Severity 1): Found by repair executor u29 (item 3; draft with emissions and three fix options: witnesses-r568/u29-route-draft.md). The verified method's OWN frame is honest; the caller-side stub (_resolve_dotted_signature) is not, and the #109 / gen #32 fallback adds _pyobj_state only when EVERY declared target is filtered. No plane compares the caller-side stub with the verified frame.
Driver repro on main 85a942c5e (2026-11-06T01:0xZ, scratchpad/run5/r568/repro.out), caller declared `ensures \result == 1`, CPython returns 2 for every probe: w568_pa16 Verification SUCCESS; w568_pa18 (honest declaration) Verification SUCCESS; w568_pa22 (receiver typed Any) Verification SUCCESS; control c568_pa21 (the same claim through self.m(), whose stub carries _pyobj_state) Verification FAILED (correct). w568_pa19 per u29.


## Census of u29's three fix options (instrumented emission at 693e20184, emission-identical to the base: the
## instrumented mirror sweep and a clean u30base sweep agree on 53/53 files)

| option | what it changes | mirror | corpus (root + python-reference) |
|---|---|---|---|
| 1: add the cell when the label filter drops ANY declared target | 161 stub resolutions | 4 files move (Module5_IREmitter, expressions, statements, stmt_control_flow: whole-file proofs owed) | 0 |
| 2: refuse a definition whose frame gains the cell while its stub would not | 7 definitions | 6 files REFUSED (Module3_Weaver, Module6_WhyMLTranspiler, pure_ast, expressions, stmt_control_flow x2) | 3 refused (2064-2066) |
| chosen (a): the stub carries the cell when the callee's EMITTED frame does | 0 stub resolutions where the emitted frame has the cell and the stub lacks it | 0 | 0 |
| chosen (a) backstop: a stub minted cell-less before its definition gains the cell | 0 | 0 | 0 |
| 3 broad: every unresolved-receiver stub writes the cell | 71 stubs | 14 files carry one; scoped to observing functions it still moved 4 (desugar, expressions, functions, types) and REFUSED `pycsl.py` (route #310: `os.close` became an effectful operand) | 1738 files carry one |
| chosen (b): an unresolved stub writes the cell when a FILE method of that name declares an effect, in observing functions | 2 stubs (pure_ast, not observing) | 0 | 0 |

Option 2 refuses honest mirror methods (none of its 7 definitions is ever called through a stub, which is why
option (a)'s count is 0), option 1 widens 161 mirror stubs whose callees write no cell. Option (a) is option 2
restricted to the definitions whose stub really exists, turned from a refusal into the honest frame.

## Repair (no new def, no axiom, no `\trusted`; all three mirror twins `\trusted`; one new code)

- `expressions._resolve_dotted_signature`, both arms (`self.` and record-typed receiver): the stub's coarse-cell
  flag (slot 6) is also set when the callee is in `_pyobj_state_writers`, i.e. its emitted `let` frame carries
  `_pyobj_state` (the body-derived rule of `functions._emit_function`). The method itself writes nothing new.
- `expressions._handle_dotted_call`: (i) a resolved callee whose stub is minted WITHOUT the cell is recorded in
  the IR dict (`__r568_cellless__`); (ii) an UNRESOLVED non-`self` receiver (no method table for its class:
  a parameter of a file class without a record, `Any`, a subclass inheriting the method) gets
  `writes { _pyobj_state }` when some file method named like the call declares a non-`\nothing` `#@ assigns` AND
  the emitting function observes attribute state (it, or a function reaching it by the forward closure over
  call / function-name / attribute-name references, contains a `getattr`; computed once per IR in
  `__r568_obs__`); placed after the #13 / #14 / #162 mutator refusals; (iii) a zero-argument receiver-less stub
  keeps its `writes` clause.
- `functions._emit_function`: when a concrete method's frame gains the cell and a cell-less stub of it was
  minted earlier (a recursion cycle the SCC order cannot break), refuse: `PYCSL-R568-STUB-FRAME-ORDER`.

## Why it is sound

`_pyobj_state` is read only by `_lower_getattr`'s UNKNOWN arms (every `!_pyobj_state` in the emitter), so the
keyed-read equality is sound iff every operation between two reads that can rebind an attribute writes the cell.
(a) A resolved method call's effect on the cell is exactly its verified `let` frame (Why3 checks the body
against it), now copied to the stub; a stub minted before the definition is known is refused when the
definition turns out to write the cell. (b) An unresolved call dispatches by name; a file method that can write
the cell must declare a non-`\nothing` `#@ assigns` (`_emit_function` turns a cell write under `\nothing` into
`writes { }`, which Why3 rejects), so the name test over-approximates every in-file callee. Off the observing
set no reader of the cell is reachable from the call, so the frameless stub changes no provable claim there; a
caller of an observing function sees the effect through the callee's derived frame (`_pyobj_state_writers`).

## Evidence

Witnesses x default (hoare) / typed / store, base = worktree at 693e20184, HEAD = run5-u30:

| corpus | shape | base hoare | base typed / store | HEAD (all three) |
|---|---|---|---|---|
| 9060 | pa16 hidden `self.flag` store under `assigns self.a` | PROVED | NOT PROVED (unrelated `int_mem` L3-tc) | NOT PROVED (frame check: unlisted write) |
| 9061 | pa18 honest `assigns self.a, self.flag` | PROVED | NOT PROVED | NOT PROVED (frame check) |
| 9062 | pa19 no-record class, parameter receiver | PROVED | NOT PROVED | NOT PROVED |
| 9063 | pa22 `Any` receiver, caller `assigns \nothing` | PROVED | NOT PROVED | NOT PROVED (frame check: `_pyobj_state` left out) |
| 9064 | the unresolved call inside a helper | PROVED | NOT PROVED | NOT PROVED |
| 9066 | method inherited from a file base class | PROVED | NOT PROVED | NOT PROVED |
| 9067 | recursion cycle m -> g -> c.m | PROVED | NOT PROVED | REFUSED `PYCSL-R568-STUB-FRAME-ORDER` |
| 9068 | CONTROL pa21, `self.m(..)` | NOT PROVED | NOT PROVED | NOT PROVED (unchanged) |
| 9070-9073 | PASS controls | PROVED | NOT PROVED (pre-existing) | identical to base |

Inertness (base = 693e20184; the corpus baseline is the census sweep, run on an instrumented tree whose emission
equals the base: its mirror sweep and a clean u30base mirror sweep agree on 53/53 files): corpus root 2967 -> 2978
.mlw 0 MOVED / 0 GONE / 0 APPEARED (+11 emitted of the 12 new u30 files; 9067 is refused), python-reference
2191 0 / 0 / 0, mirror 53/53 0 / 0 / 0 (no declared movers, no `--fun`, no whole-file proof owed). rt43 / rt44
149 honest controls: front-end verdicts identical base / HEAD (22 emitted, 0 of their .mlw moved; 127 refused as
at the base). Planes: `bin/run-soundness-planes.sh` 62/62 green; fidelity (`check-self-annotate-sync.sh`,
`self-annotate-mirror-check.sh`, `doc-coherency.py --check`) rc 0; `\trusted` 406 unchanged; proof-axiom
ledger untouched (no .v / .lean change). Per-model table: `witnesses-r568/RESULTS-base-693e20184-vs-u30.txt`.

## Residuals (named, not repaired)

- An unresolved receiver whose method lives OUTSIDE the file (standard library, an imported module or class):
  `witnesses-r568/residual/r568_stdlib_receiver_close.py` (`f.close()` between two reads of
  `getattr(f, "closed", 0)`) PROVES at base and HEAD. Framing every unresolved call is option 3 broad (above:
  4 mirror movers + the `pycsl.py` mirror refused); a sound narrower form needs a model of which
  standard-library methods rebind attributes.
- A free-function caller of a cell-writing method (9060 / 9061 shape) is now rejected by Why3 even when its claim
  is true: the gen #36 seam inserts `writes { _pyobj_state }` without the parameter's record fields (`c.a`).
  Over-refusal, not a hole; no corpus or mirror file has the shape (census: 0).
