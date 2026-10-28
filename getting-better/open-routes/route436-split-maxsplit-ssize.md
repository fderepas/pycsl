# OPEN ROUTE #436 — str.split / rsplit WITH maxsplit OUTSIDE C ssize_t OWES NO OverflowError
**Status: REPAIRED (candidate, executor g5, driver run #3), Severity 1.** Red-team round 34 (2026-10-28, convergence measurement after #418-#431 + R-gate on 78b519f63; 497 written / 474 fully proved / 63 confirmed; FINDINGS salvaged by the driver from the stalled executor's on-disk outputs); driver-reproduced on main (see `scratchpad/rt34/FINDINGS.txt` and the driver repro line below).
Witnesses `witnesses-r436/` (5): `m04_split_maxsplit.py`, `t0_split_param.py`, `t4_split_neg_ok.py`, `t7_split_ens.py`, `t9_split_loop.py`.

Driver repro: 9/9 family samples rc=0 Verification SUCCESS on main 78b519f63 at 2026-10-28T10:12Z, each violating under CPython (scratchpad/rt34/driver-repro.txt).

```
#436 str.split / rsplit WITH maxsplit OUTSIDE C ssize_t OWES NO OverflowError   (5)
  t0   s.split(" ", n) PROVED; n = 10**20                                                      CPython OverflowError
  m04 maxsplit= keyword   t4 negative huge   t7 ensures-bearing   t9 in a loop
  REPAIR (proposed, allow-list / refuse by default): An int-read `maxsplit` (positional or keyword) of split / rsplit / splitlines-like C-ssize_t parameters owes
  `-2**63 <= n < 2**63` under `\all`; enumerate the other ssize_t-parameter methods (str.replace count, expandtabs, ..)
  and either add the obligation or refuse a non-literal argument.
```

## REPAIR (executor g5, driver run #3, 2026-10-28, off 1c083dcbe; annotations §7.138, translational §T.6.149)

ENUMERATION (CPython 3.14, measured with `10**20` / `-10**20` / `2**63` / `2**31`): `Py_ssize_t`
parameters -- `str` / `bytes` / `bytearray` `split` / `rsplit` maxsplit, `replace` count, `center` / `ljust`
/ `rjust` / `zfill` width, `list` / `bytearray` `insert` index, `int.to_bytes` length; C `int` -- `expandtabs`
tabsize, `bytes.hex` bytes_per_sep. NOT raising: `find` / `rfind` / `index` / `count` / `startswith` /
`endswith` start / end, `list.index` / `tuple.index` start / end (slice-index CLAMP), `splitlines` keepends
(a truth value), `round` ndigits, `enumerate` start, `sum` start; `pop(i)` past ssize_t is out of range
(its IndexError row). REACHABLE under `no_exception` (route #161's method allow-list): `split` (positional maxsplit, with a
literal str separator: route #72 refuses any other separator, so `bytes.split(b" ", n)` is refused, and the
`maxsplit=` keyword is refused by the keyword-argument rule -- both measured, pre-existing refusals), `replace`
(3-argument form: does not type-check today, FAILS), `insert` (refused as an unmodelled receiver mutation);
every other row only through a file class's same-named method, which route #161 admits by NAME (probe:
`s.rsplit(" ", n)` beside `class C: def rsplit(..)` PROVED at base, witness 6576). Builtins outside the
method rows (`bytes(n)`, `bytearray(n)`, `"a" * n`: OverflowError past ssize_t) are NOT covered here (see
RESIDUALS).

RULE, under `\all` (OverflowError is not Phase 1), at the head of `_handle_call_expr` (mirror twin
`\trusted`), by method NAME whatever the receiver (route #72's convention; a file class's own `split(a, n)`
owes the bound too -- an over-approximation, never a hole): the parameter is the positional argument (one
further for an unbound `str.split(s, ..)`) or the keyword; an int literal is decided at emission (out of
range: REFUSED `PYCSL-R436-SSIZE-ARGUMENT`); a str / float / bool argument owes nothing (it is not an int;
recorded in `r434_ok`); a PURE int form (a name, an int literal, `+ - *` / unary `-` of those, `len(name)`)
owes `- 2**63 <= n < 2**63` (C int: `2**31`) asserted before the call, tagged `[@r434_<h>]`; any other
argument is REFUSED `PYCSL-R436-SSIZE-ARGUMENT` (bind it to a local first). Route #434's driver census and
callee summary cover these sites (the `for w in s.split(",", n)` witness 6569 is refused by the census: the
`for` iterable path never reaches the call handler).

Witnesses (expected FAIL; PROVED rc=0 at base 78b519f63, CPython OverflowError): 6565-6569 (the 5 red-team
probes: 6565-6568 FAIL on the `OverflowError reachable` goal, 6569 REFUSED UNCHECKED-SITE), 6575 un-claimed
callee (REFUSED, CALLEE), 6576 rsplit by name collision (FAIL), 6577 `s.split(" ", g(n))` (REFUSED,
SSIZE-ARGUMENT), 6578 a literal `10**20` (REFUSED, SSIZE-ARGUMENT). Controls (expected PASS, PROVED at base
and candidate): 6582 (`n`, `n + 1` with `0 <= n <= 100`, literals 1 / -1), 6584 (6569's loop written
`k += len(s.split(",", n))`), 6585 (`m = g(n)` bound first).

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
- PATH VALUES: a `pathlib.Path` is modelled as a Why3 `string`, so `ord(p)` of a `p: Path` parameter gets the
  length obligation instead of a refusal (CPython: TypeError whatever the length). `Path(..)` itself is refused
  under `no_exception` (route #161); an obligation `String.length p = 1` needs a contract fact about the path's
  length to discharge. Measured: emitted with the obligation (probe z02).
- CALLEES: the TypeError / OverflowError token reaches route #178's summary for SAME-FILE callees only (as
  #430); an imported module's un-claimed function holding such a site is not summarised.
- The `PYCSL-R417-ERASED-OBLIGATION` mechanism (#417 / #426) is unchanged: its registry still counts only the
  `list` / `sorted` / `float` / FormattedValue sites it registered; the #434 census is the fail-closed form
  (sites recounted from the IR) and was not retro-fitted to #417's rows.
