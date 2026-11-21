# OPEN ROUTE #302 — A PLAIN-NAME for TARGET OVER A NON-INDEX SEQUENCE, READ AFTER THE LOOP, KEEPS ITS PRE-LOOP VALUE (#36 residue)
**Status: REPAIRED (gen #37, 2026-10-22; opened the same day), Severity 1.** Reported by the r301 executor (route #36's recorded residue, never closed);
witness `witnesses-r302/residual_name_target_read_after.py`: `x = ""; for x in e: pass; return x` under `requires len(e) == 1`
proves `\result == ""` (CPython returns e[0]). Route #36 (relaunch #45) refused a `for` target read outside its loop only for
the index/range lowering; sequence/str/dict iteration still shadows the name inside the body and leaves the outer value stale.
Repair: refuse (or faithfully write back) every loop target read after its loop for EVERY iteration lowering (array/seq/str/
dict-keys/hval/R2b/enumerate/zip/items); flow-aware like #301 (a re-binding before the read kills staleness). Note the
`_handle_for_stmt` mirror stub has no raise: a refusal placed in Module 6 moves the trusted-raises ratchet (lesson d5) — prefer
the IR-level marker + Module 6 refusal pattern #301 used (kwarg_read precedent).

## REPAIR (2026-10-22, r302 executor off d117596a; commits e1df6b99 + 7c5364bd + census + docs)
Probe table (`src/pycsl/pycsl.py`, full proof, rc; CPython ground truth in each corpus file's `__main__`):

| shape | d117596a | after |
|---|---|---|
| route witness `witnesses-r302/residual_name_target_read_after.py` | rc=0 PROVED | rc=1 FAIL (postcondition) |
| 3630 `x = ""; for x in e: pass; return x` (`List[str]` param) | PROVED | FAIL |
| 3631 char loop `for c in s` | PROVED | FAIL |
| 3632 local list literal `xs = [1, 2, 3]` | PROVED | FAIL |
| 3633 loop left by `break` | PROVED | FAIL |
| 3634 body re-binds its own target (`for x in e: x = "z"`; CPython "z") | PROVED | FAIL |
| 3635 `for w in s.split()` | PROVED | FAIL |
| 3636 `range(5, 0, -1)` (element is not the bare counter: #36 did not fire) | PROVED | FAIL |
| 3637 `for x in sorted(e)` over ints | PROVED | FAIL |
| 3638 loop under an `if`, read after the `if` | PROVED | FAIL |
| 3639 loop in a `try` body, read after the `try` | PROVED | FAIL |
| 3640 CONTROLS: re-bound after the loop; faithful write-back proved via `#@ loop invariant x == "" or x == e[0]`; two sequential loops on one name; read BEFORE the loop | PASS | PASS |

Every FAIL is a genuine postcondition failure (no L3-tc error). Other probes (scratchpad only):
`List[int]` param (#36 case) FAIL both; nested `for x in a: for x in b` then `r = x` and a
dict-keys / set / `.keys()` / `reversed` / tuple-element / list-of-lists / literal loop are
L3-tc failures already at base (unchanged); `e[1:]` type-checked at base and is now an
L3-tc FAIL (the write-back exposes the type mismatch — fail-closed); a fresh target read after
its loop is refused by the definite-assignment check (unchanged); `for ... else` is a PIPELINE
ERROR (unchanged).

Rules (no new def/field/attribute/axiom — ledger 3; no new raise, so trusted-raises unchanged):
(1) `_reset_function_state` (Module 6, after the #301 block) runs, for every plain-name `for`
target of a LOWERED body (`\trusted`/abstract skipped), the #301 statement-path walk generalised
to plain loops: a read (a `Var`, an `AugAssign` of the name, a `FieldAssign` through it, a call
of it) is STALE when, walking back along its path innermost-first, an earlier sibling holding a
plain loop on the name is met before a top-level `Assign`/`TupleUnpack` of it, or the enclosing
statement is a non-binding `For`/`While` whose body holds one (a previous iteration). A read in the
body of a loop that binds the name stops the walk (safe); a comprehension binding the name has its
own scope (only its first iterable is walked); a dropped `assert` is not a read. A stale name is
recorded in the existing `_loop_targets_read_outside` set under the key `"#302:<name>"` (not an
identifier, so the #36 `target in ...` test never sees it; no new field, so no mirror `assigns`
change).
(2) `_handle_for_stmt`'s binder (the single exit every plain-target lowering goes through:
array/seq/str chars/split/sorted/R2b/hval/range-with-step/local list...) emits the write-back
`x := <elem>;` for a stale name REGARDLESS of the types (and for a pyval target too). Same type ->
Python's last value exactly, never-ran case included; different type -> L3-tc fails closed.
(3) If the loop body re-binds the target (`Assign`/`AugAssign`/`TupleUnpack`/walrus/an inner `for`
on the name), the write-back before the shadow is not the last value, so that loop binds the
OUTER ref (`x := <elem>;`) and opens no inner `let` (one variable, as in Python).
Census: the binder is the only plain-target exit of `_handle_for_stmt` (the tuple branches return
earlier and are #301's domain); comprehension variables do not leak in Py3 (own scope, exempt);
`while` binds nothing; `with ... as` is refused by the with-as boundary; `for ... else` is refused
(PIPELINE ERROR) and the For IR has no `orelse`.
Blast radius: corpus root 0 MOVED / 0 GONE / 0 APPEARED (1988/1988), pyref 0/0/0 (2186/2186),
mirror 0/0/0 (53/53) — sweeps run on e1df6b99 before the witness files were added (the emitter
did not change afterwards). No mover: no M1 re-proof and NO mirror proof OWED.
Gates (logs in the r302 executor scratchpad `r302/`): byte-diff-sweep base/after rc=0;
byte-diff-compare root rc=0, pyref rc=0; mirror-emit-sweep base/after rc=0, compare
`--min-files 50` rc=0; check-self-annotate-sync.sh rc=0 (926 verbatim); self-annotate-mirror-check.sh
rc=0 (53); run-soundness-planes.sh fast rc=0, 61/61 green. Ledgers: census rows for 3630-3639
(VERIFY-FAIL, measured by `_census_row`); trusted-raises unchanged (no raise added); no new
field (mirror `assigns` unchanged); axiom ledger 3. `--slow` NOT run (time).
Residuals: (1) where the outer ref's type differs from the element's the function FAILS CLOSED
at L3-tc rather than with a refusal message (e.g. `x = ""; for x in e[1:]` type-checked and proved
stale before; now an L3-tc failure) — sound, but an honest program there needs a fresh name.
(2) The read scan sees `Var` / `AugAssign` / `FieldAssign.object` / `Call.func`; a target used
through another string-valued IR field is not scanned (#301 residual (2), same population).
(3) Conservative kills: only a top-level `Assign`/`TupleUnpack` on the read's path kills
staleness (a walrus or a branch-local assignment does not), so some faithful-but-unneeded
write-backs fire — they are exact or fail closed, never a stale proof. (4) Completeness: a
write-back makes the outer name loop-modified, so facts about it after the loop now need a
`#@ loop invariant` on the name (control 3640 `faithful_write_back`).
