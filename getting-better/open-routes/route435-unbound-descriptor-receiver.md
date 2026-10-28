# OPEN ROUTE #435 — AN UNBOUND str / bytes METHOD DESCRIPTOR APPLIED TO A WRONG-TYPE FIRST ARGUMENT OWES NO TypeError
**Status: REPAIRED (candidate, executor g5, driver run #3), Severity 1.** Red-team round 34 (2026-10-28, convergence measurement after #418-#431 + R-gate on 78b519f63; 497 written / 474 fully proved / 63 confirmed; FINDINGS salvaged by the driver from the stalled executor's on-disk outputs); driver-reproduced on main (see `scratchpad/rt34/FINDINGS.txt` and the driver repro line below).
Witnesses `witnesses-r435/` (8): `c0_str_unbound_bytes.py`, `c1_bytes_unbound_str.py`, `c09_str_lower_bytes.py`, `c10_str_strip_bytes.py`, `c13_str_upper_bytearray.py`, `c14_bytes_upper_bytearray.py`, `c15_bytes_lower_str.py`, `c18_str_upper_list.py`.

Driver repro: 9/9 family samples rc=0 Verification SUCCESS on main 78b519f63 at 2026-10-28T10:12Z, each violating under CPython (scratchpad/rt34/driver-repro.txt).

```
#435 AN UNBOUND str / bytes METHOD DESCRIPTOR APPLIED TO A WRONG-TYPE FIRST ARGUMENT OWES NO TypeError   (8)
  c0   x: bytes; str.upper(x) PROVED; f(b"a")                                                 CPython TypeError (descriptor)
  c1 bytes.upper(str)   c09 str.lower(bytes)   c10 str.strip(bytes)   c13 str.upper(bytearray)   c14 bytes.upper(bytearray)
  c15 bytes.lower(str)   c18 str.upper(list)
  (route #422's row gives `str.m(x, ..)` the RECEIVER class `str` -- it reads the callee's class, not x's.)
  REPAIR (proposed, allow-list / refuse by default): `T.m(x, ..)` for T in {str, bytes, bytearray, int, ..} is admitted only when x's derived class is exactly T (or a subclass
  the file defines); otherwise refused under `no_exception` (TypeError).
```

## REPAIR (executor g5, driver run #3, 2026-10-28, off 1c083dcbe; annotations §7.137, translational §T.6.148)

Allow-list, refuse by default, under `\all` (TypeError is not Phase 1): at the head of `_handle_call_expr`
(mirror twin `\trusted`), a receiver-less call `T.m(x, ..)` with `T` in `str bytes bytearray int float
complex bool list dict set frozenset tuple type object` (not the class-level `maketrans` / `fromhex` /
`from_bytes` / `fromkeys` / `from_number`) is admitted only when the class of `x` BY ITS FORM is exactly
`T`: a name annotated `T` (`str bytes bytearray int list dict set tuple frozenset`; a `float` / `complex`
annotation admits an int under PEP 484, so it never counts), a str / int / bool literal, an f-string for
`str`, a call of a builtin returning `T` (`str(..)`, `len(..)`, `bytes(..)`, ...); `object` admits every
`x`. Anything else -- an un-annotated local, an attribute, a display (`b".."` and `[..]` are ONE IR form,
so neither is admitted for `bytes` / `list`) -- is REFUSED `PYCSL-R435-UNBOUND-DESCRIPTOR`. The admitted
call records its tag in `r434_ok`, and route #434's driver census refuses a `T.m(..)` site the emitter
never reached (`PYCSL-R434-UNCHECKED-SITE`); an un-claimed callee holding one makes a `\all` caller
refused (`PYCSL-R434-CALLEE-UNCHECKED-SITE`). Route #422's `_ty383` row (the RECEIVER class for hashing) is
unchanged: it answers a different question (the result's class).

Witnesses (expected FAIL): 6557-6564 (the 8 red-team probes, PROVED rc=0 at base 78b519f63, CPython
TypeError; all REFUSED), 6574 `int.bit_length(x)` with `x: float` (FAILED at base only by a Why3 type
error; REFUSED). Control (expected PASS, PROVED at base and candidate): 6581 (`str.upper(s)` s: str,
`bytes.upper(b)` b: bytes, `str.lower("AB")`, `int.bit_length(n)` n: int).

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
