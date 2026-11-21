# OPEN ROUTE #434 — ord() OF A STRING NOT OF LENGTH 1 OWES NO TypeError
**Status: REPAIRED (candidate, executor g5, driver run #3), Severity 1.** Red-team round 34 (2026-10-28, convergence measurement after #418-#431 + R-gate on 78b519f63; 497 written / 474 fully proved / 63 confirmed; FINDINGS salvaged by the driver from the stalled executor's on-disk outputs); driver-reproduced on main (see `scratchpad/rt34/FINDINGS.txt` and the driver repro line below).
Witnesses `witnesses-r434/` (7): `bb02_ord_long.py`, `or0_ord_empty.py`, `or1_ord_lit2.py`, `or2_ord_slice.py`, `or4_ord_upper_sz.py`, `or6_ord_strip.py`, `or8_ord_join.py`.

Driver repro: 9/9 family samples rc=0 Verification SUCCESS on main 78b519f63 at 2026-10-28T10:12Z, each violating under CPython (scratchpad/rt34/driver-repro.txt).

```
#434 ord() OF A STRING NOT OF LENGTH 1 OWES NO TypeError   (7)
  or2  ord(s[0:2]) PROVED; f("abc")                                                            CPython TypeError
  bb02 ord of a 2-char argument   or0 ord("")   or1 ord("ab")   or4 ord(s.upper()) ("ß" -> "SS")   or6 ord(s.strip())
  or8 ord("".join(..))
  REPAIR (proposed, allow-list / refuse by default): `ord(s)` with s a str owes `len(s) == 1` (bytes / bytearray: likewise) under `\all`; register it with the erased-obligation
  census like the #417 rows.
```

## REPAIR (executor g5, driver run #3, 2026-10-28, off 1c083dcbe; annotations §7.136, translational §T.6.147)

Repaired TOGETHER with #435 / #436 by one shared, fail-closed mechanism (the supervisor's "systematic,
not one-off" directive): each of the three call forms is an OBLIGATION or an allow-list decision made where
Module 6 lowers the call, and the driver RECOUNTS every site from the IR so that a lowering path that never
reaches the check (an opaque comprehension, a `for` iterable, a fold) is refused instead of trusted.

- `_handle_call_expr`'s `ord` arm (mirror twin `\trusted`), under `\all` only (TypeError is not Phase 1,
  §7.19): `ord(s[i])` of a str owes nothing more (IndexError row; a character has length 1); a str literal is
  decided at emission (one character: nothing; else REFUSED `PYCSL-R434-ORD-LENGTH`); another str-read
  argument is let-bound once and owes `String.length _o434 = 1`, tagged `[@r434_<h>]`; a non-str argument
  (`ord(b[0])` of a bytes is an int) is REFUSED `PYCSL-R434-ORD-LENGTH`.
- `_run_pipeline` (twin `\trusted`): after `transpile()`, every site (`ord(x)` with x not a one-character
  str literal; §T.6.148 / §T.6.149 sites) of every verified `\all` body (comprehension / lambda bodies
  included) is counted per tag; a tag occurring in the module plus in the driver-owned list `r434_ok`
  (sites the emitter checked and found owing nothing) fewer times than its sites is REFUSED
  `PYCSL-R434-UNCHECKED-SITE` (`[ord(w) for w in ws]`, `for w in s.split(",", n)`).
- `_reset_function_state`'s route #178 summary (twin `\trusted`): a same-file function holding such a site
  and not claiming `\all` carries the TypeError token (#430's), so a `\all` caller is REFUSED
  `PYCSL-R434-CALLEE-UNCHECKED-SITE` (measured: an un-claimed `h(s): return ord(s)` under a `\all` caller
  PROVED at base).

Witnesses (expected FAIL; PROVED rc=0 at base 78b519f63, CPython TypeError): 6550-6556 (the 7 red-team
probes; FAIL on the `TypeError reachable` goal, 6552 REFUSED), 6570 `[ord(w) for w in ws]` (REFUSED,
UNCHECKED-SITE), 6571 `ord(b[0])` (REFUSED, ORD-LENGTH), 6572 un-claimed callee (REFUSED, CALLEE).
Controls (expected PASS, PROVED at base and candidate): 6580 (`len(s) == 1`, `ord(t[1])`, `ord("a")`),
6583 (a callee claiming `\all` itself).

## REPAIR, increment 2 (executor g5, 2026-10-28, off 86f9efa51): PATH VALUES

Found while writing the residuals of increment 1: the front end ERASES a `pathlib.Path` annotation to `str`
(route #31's path model: a Path is a Why3 `string`; the IR symbol table and `param_annotations` say `str`),
so Module 6's rule stated `String.length p = 1` for `ord(p)` of a `p: Path`. MEASURED at 86f9efa51 (and at base
78b519f63), CPython TypeError whatever the length: `#@ requires len(str(p)) == 1`, `return ord(p)` PROVED, as did
`ord(p[0])` (a Path is not subscriptable) and an alias `q = p.parent; ord(q)`. Only the SOURCE keeps the
annotation, so `_run_pipeline` (twin `\trusted`) reads the AST: in a `def` named like an IR function claiming
`no_exception_all`, a Path value (a name annotated `*Path*` or bound from a Path value, to a fixpoint;
`x.parent`; a `/` join with a Path operand; `Path(..)` / `PurePath(..)` / a Path-only method call; a
subscript / conditional / walrus of one) under `ord`, or as the first argument of an unbound `str.m(..)`
(route #435's `str` row passed the erased annotation: `str.upper(p)`), is REFUSED `PYCSL-R434-ORD-PATH`.
Witnesses 6579 (`ord(p)`), 6573 (alias), 6586 (`ord(p[0])`), 6588 (`str.upper(p)`, filed under #435); control
6587 (`ord(str(p)[0])`, the message's advice).

Increment-2 gates (candidate = the increment-2 commit; logs `battery-c2.txt`,
`increment2-witness-base-inc1-cand.txt`): witnesses 6573 / 6579 / 6586 / 6588 PROVED rc=0 at base 78b519f63 AND
at 86f9efa51, REFUSED (`PYCSL-R434-ORD-PATH`) at the candidate; control 6587 and advice probe a434_path_drop_all
PROVE at all three / the candidate. Root 2518 -> 2536 0 MOVED / 0 GONE / 0 APPEARED vs `v8/cb` (and 2535 -> 2536
0/0/0 vs increment 1's sweep), pyref 2186 0/0/0, mirrors 53/53 0/0/0 vs `v8/mb`; sync / mirror-check rc=0;
planes 61/61; refusal-witness-coverage rc=0 (338 demonstrated, 4 more census rows), refusal-advice-audited rc=0
(165 audited; the new message followed both ways), doc-coherency / trusted-reasons / getattr-erasure /
clause-survival / assumed-facts / open-route-carriers rc=0; `\trusted` 442. Over-refusal cost 0.

## GATES (executor g5, candidate = this commit; base = 78b519f63, emission-identical to 1c083dcbe; logs in
`getting-better/systematic-soundness-r3/g5-r434-436/`)

- Witnesses / controls, base (worktree pycsl-v-s1base at 78b519f63) vs candidate, every run through heavy.sh
  (`witness-base-vs-cand.txt`, `advice-probes.txt`): 27 of the 28 witnesses PROVED rc=0 at base (6574 FAILED
  at base by a Why3 type error) and every one FAILS on its new goal or is REFUSED at the candidate; the 6
  controls 6580-6585 PROVE rc=0 at base AND candidate.
- Fidelity: `bin/check-self-annotate-sync.sh` rc=0 (932 un-trusted mirror functions verbatim),
  `bin/self-annotate-mirror-check.sh` rc=0 (53 mirrors).
- Corpus inertness vs the driver's base sweep `v8/cb`: root 2518 baseline / 2535 candidate .mlw, 0 MOVED /
  0 GONE / 0 APPEARED (17 of the 34 new sources emit; the other 17 are refused witnesses); pyref 2186 / 2186,
  0 / 0 / 0.
- Mirrors: `bin/mirror-emit-sweep.sh` 53 / 53 vs the driver's base `v8/mb` (78b519f63): 0 MOVED / 0
  GONE / 0 APPEARED -- no MOVED mirror, nothing OWED. (A first compare against a partial `git archive` of
  1c083dcbe showed 2 MOVED -- json stub `val`s -- because that export lacked the root-level `json/` package:
  an environment artefact, discarded.)
- `bin/run-soundness-planes.sh` (fast 61) rc=0, all 61 green (after the census rows; the first run, before
  them, was red on refusal-witness-coverage only: 6 new raise sites without a witness row, as expected).
  getattr-erasure / clause-survival (--emit-dir) / assumed-facts (--emit-dir) / open-route-carriers /
  doc-coherency / trusted-reasons rc=0; `\trusted` lines 442 (unchanged), no new axiom, no new def in a
  mirrored file.
- Census: 28 rows appended for 6550-6578 by the tool's own `_census_row` (scoped: the tree's `--append-new`
  would also run 358 unrelated row-less witnesses); refusal-witness-coverage rc=0, 337 demonstrated / 5
  undemonstrated (ceiling 5). Advice audit: the 5 advice-bearing messages followed and run (probes
  `advice/`, all VERIFY), refusal-advice-audited rc=0, 164 of 227 audited.
- OVER-REFUSAL COST: 0 -- no root / pyref corpus file and no mirror moved or was newly refused; the rows are
  gated on `no_exception \all`, which no mirror and no `pycsl_lib` file claims. Known over-refusals by design
  (not in any corpus): `[ord(c) for c in s]` (6570's census refuses every comprehension site, even a safe
  one), `for w in s.split(",", n)` (the `for` iterable path), an un-annotated local as `T.m`'s receiver,
  a file class's own `split(a, n)` method owing the ssize_t bound.

## RESIDUALS (honest, routes #434-#436)

- OVER-REFUSALS by design (none in any corpus / mirror / `pycsl_lib`): every comprehension / lambda site is
  refused by the census, even a safe `[ord(c) for c in s]`; `for w in s.split(",", n)` (the `for` iterable path
  never reaches the call handler; `k += len(s.split(",", n))` verifies); an un-annotated local (or an attribute) as
  `T.m`'s first argument; a `float` / `complex` parameter as `float.m(x)`'s receiver (PEP 484 admits an int); a
  file class's own `split(a, n)` / `replace(a, b, n)` / ... owing the ssize_t bound (selected by NAME, as route #72).
- NOT COVERED: builtins outside the method rows that convert to `ssize_t` -- `bytes(n)`, `bytearray(n)`, `"a" * n`
  / `b"a" * n` (measured CPython OverflowError at `10**20`; NOT measured in PyCSL here -- route #414 bounds only
  `[x] * n`); `int.to_bytes` / `bytes.hex` rows are wired but unreachable today (route #161 refuses both names).
- ANNOTATIONS ARE TRUSTED: a parameter annotated `bytes` is read as exactly `bytes` (a caller passing a
  `bytearray` under a type checker's bytes promotion would make `bytes.upper(x)` raise); the same holds for `str`
  / `int` / `list` annotations everywhere in PyCSL.
- PATH VALUES: closed for `ord` and #435's `str.m(p, ..)` by increment 2 (the AST pass). The same erasure
  makes every OTHER str operation on a Path a str operation (`len(p)`, `p.upper()`, `p + "x"`): a
  cross-cutting #31 path-model residual, NOT addressed here.
  The Path-value pass follows names, not containers or `for` targets (`for q in p.iterdir(): ord(q)` is not
  caught; `iterdir` is refused under `no_exception` by route #161 today).
- CALLEES: the TypeError / OverflowError token reaches route #178's summary for SAME-FILE callees only (as
  #430); an imported module's un-claimed function holding such a site is not summarised.
- The `PYCSL-R417-ERASED-OBLIGATION` mechanism (#417 / #426) is unchanged: its registry still counts only the
  `list` / `sorted` / `float` / FormattedValue sites it registered; the #434 census is the fail-closed form
  (sites recounted from the IR) and was not retro-fitted to #417's rows.

## DRIVER INTEGRATION NOTE (run #3, 2026-10-28)

The combined g4+g5+g6 candidate broke the trusted param-frame ratchet (10 > 9). The cause was this repair's `args[0] = ...`
in `ExpressionEmissionMixin._call_named_builtins`, whose `\trusted` mirror frame omits `args` (route #401). The driver
fixed it (c8b0aa205) by rebinding a fresh local list. The emission is byte-identical to the v9 candidate (root 2553 /
pyref 2186 / mirror 53, all 0/0/0); frame-honesty rc=0 (9, all ledgered); the ord witnesses still FAIL and the
controls PASS. g5's own planes did not include `check-trusted-frame-honesty.py`.
