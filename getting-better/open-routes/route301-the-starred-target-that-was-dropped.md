# OPEN ROUTE #301 — A STARRED ASSIGNMENT TARGET IS DROPPED BY THE FRONT END (the bound names keep their old values)
**Status: REPAIRED (gen #37, 2026-10-22; opened the same day), Severity 1.** Found by the r299 executor; driver-reproduced at 379d0f3a (rc=0 on main; CPython g([5]) == 5).
Witness `witnesses-r301/u1_starred_target.py`: `t = 0; [*h, t] = e; return t` under `requires len(e) == 1` proves `\result == 0`.
The starred unpack target is silently dropped, so `t` (and `h`) keep stale values. Repair: lower starred unpacking faithfully
(prefix/suffix slices of the source, length guard ValueError under no_exception) or REFUSE every Starred target (Assign, for,
with, comprehension); census every assignment-target shape the front end drops (starred, attribute/subscript in tuple targets,
nested, `*_`).

## REPAIR (2026-10-22, r301 executor off 25a03299; commits 4a3efe24 + 57217cbd + census + acad5b5d + route docs)
Probe table (`src/pycsl/pycsl.py`, full proof, rc; CPython ground truth in each corpus file's `__main__`):

| shape | 25a03299 | after |
|---|---|---|
| route witness `witnesses-r301/u1_starred_target.py` `[*h, t] = e` | rc=0 PROVED | rc=1 REFUSED |
| 3610 `[*h, t] = e`, `\result == 0` (CPython 5) | PROVED | REFUSED |
| 3611 `*h, t = e` | FAIL (L3-tc) | REFUSED |
| 3612 `[u, t] = e` (List target: NO emitter arm, nothing emitted) | PROVED | REFUSED |
| 3613 `(u, (v1, v2)) = p` (IR kept `targets ["u"]`) | PROVED | REFUSED |
| 3614 `for [t] in e` (became `_for_target`) | PROVED | REFUSED |
| 3615 `for a, (b, c) in ps` (`(b, c)` -> `_`) | PROVED | REFUSED |
| 3616 `for *b, a in ps` | PROVED | REFUSED |
| 3617 `for a[0], b in ps` (store to `a[0]` vanished) | PROVED | REFUSED |
| 3618 `for a[0] in [7]` | FAIL (L3-tc) | REFUSED |
| 3619 `[b for a, (b, c) in ps]` | FAIL (L3-tc) | REFUSED |
| 3620 `a[0], t = p` | FAIL (L3-tc) | REFUSED |
| 3622 `u = 0; for u, v in ps: pass; return u` (flat tuple for-target, component read AFTER the loop) | PROVED | REFUSED |
| 3623 `i = 0; for i, x in enumerate(e): pass; return i` | PROVED | REFUSED |
| 3621 CONTROLS: `u, t = x, x + 1`; `for u, v in ps` (components unread outside); `t = s = e[0]`; two `for k, v in d.items()` loops re-binding the same names | PASS | PASS |

Rules (no new def/field/axiom — ledger 3; the `kwarg_read` (#232) pattern):
(1) `Module5._build_function_ir` walks the function (nested defs included) and RECORDS
`unpack_target_refused` in the function IR for the first Assign / for / async-for / comprehension
target outside {plain Name, flat tuple of plain Names} — List, Starred, a tuple holding a
Starred / Tuple / List / Attribute / Subscript element, and (for loops/comprehensions) a bare
Attribute/Subscript target. Module 6 `_reset_function_state` raises it ("dropped unpacking / loop
target refused (route #301) -- ...") only when it LOWERS the body: an imported library function
or a `\trusted`/abstract one is a bodiless `val` and is not refused (a first version raising in
Module 5 refused the LIVE `Module3_Weaver._dispatch_function_contracts` imported by two mirrors —
`contracts, node.csl_acts, entry_cps = ...`, which IS such a shape but is never lowered).
(2) `_reset_function_state` refuses a tuple for-target COMPONENT read outside its loop when
no re-binding covers it: no binder writes a component back (the #36 write-back is keyed on the
synthetic `_for_target`). Path-sensitive: a read is safe when an earlier statement of a list on
its statement path is a top-level `Assign`/`TupleUnpack` of the name with no tuple loop on the
name in between and none reintroduced deeper (earlier sibling, or an enclosing loop holding one);
reads under a loop / comprehension that itself binds the name, and `assert`s (dropped), are
exempt; a read with no tuple loop on the name before it at all is safe. (A first, path-blind
version refused mirror `expressions.py::_typeddict_record_literal`, whose `v` is re-assigned
before its later read.)
`with ... as <any>` is already refused by the with-as boundary; walrus targets are Names;
augmented tuple targets are a SyntaxError; `match` star captures are refused by #233 when read
outside the arm; chained `a, t = b, c = p` fails L3-tc (closed, unchanged).
CENSUS of target shapes (AST census over corpus, pyref, conformance/negative, `src/pycsl_lib`,
and the 53 mirror files, function bodies only): ZERO occurrences of any refused shape except
`src/pycsl_lib/json/encoder.py:143` (`self.item_separator, self.key_separator = separators`),
a module `check-stdlib-modules-verify.py` already lists as REFUSED (zero annotations).
Blast radius: corpus root 0 MOVED / 0 GONE / 0 APPEARED (1986 base / 1987 candidate, 14 new
sources, 13 refused), pyref 0/0/0 (2186/2186), mirror 0/0/0 (53/53). No mover: no M1 re-proof
and NO mirror proof OWED.
Gates (logs in the r301 executor scratchpad `r301/`): byte-diff-sweep base/after rc=0;
byte-diff-compare root rc=0, pyref rc=0; mirror-emit-sweep base/after rc=0, compare
`--min-files 50` rc=0; check-self-annotate-sync.sh rc=0 (926 verbatim); self-annotate-mirror-check.sh
rc=0 (53); run-soundness-planes.sh fast rc=1, 60/61 green: the one RED,
check-refusal-witness-coverage (UNWITNESSED 6 > 5), is RED AT BASE 25a03299 with the same six
sites (none of them #301's; measured in a base worktree). Ledgers touched: census rows for
3610-3620/3622-3623 (measured by `_census_row`), UNMATCHABLE held at 10 (the Module 6 raise
carries a literal), `check-dropped-mutation.py` classifier: List / Starred / non-Name-element
tuple Assign targets are REFUSED (was DROPPED 0 -> would be 2), trusted-raises unchanged (both
raises land in `_reset_function_state`, already SILENT/refusal). `--slow` NOT run (time).
Residuals: (1) KNOWN FALSE PROOF, route #36's recorded residue, untouched here: a PLAIN-NAME
for-target over a non-index sequence read after the loop keeps its pre-loop value —
`x = ""; for x in e: pass; return x` under `requires len(e) == 1` PROVES `\result == ""`
(rc=0 at 25a03299 and after; CPython e[0]); repro `witnesses-r301/residual_name_target_read_after.py`.
Closing it needs the outer ref's type at the binder (write-back) or a refusal keyed on the
`_r36_wb` decision inside `_handle_for_stmt`, whose mirror stub is `\trusted` WITHOUT a raise
(a raise there moves the trusted-raises ratchet). (2) The component-read check sees `Var` reads
only (as #36 does); a component used as an `object`/`array` string field of another IR node
(method-call receiver, subscript base) is not scanned. (3) Completeness: every refused shape
(e.g. `for i, (a, b) in enumerate(ps)`) must now be unpacked by index.
