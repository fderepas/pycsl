# OPEN ROUTE #417 — SEVEN LIVE FALSE PROOFS: SEQUENCE REPETITION, CONTRACT STRING ESCAPES, RANGE / FLOAT OVERFLOW, HASH SOURCES
**Status: REPAIRED (candidate; executor r417, completed and gated by r417b, driver run #3), Severity 1.** Suspects (a)-(g) of the r417 brief (residuals
recorded by routes #414, #406 and #409, plus two new lowering defects; a starred list element (#417a') was found
along the way). Each was CONFIRMED on 930d68ed5: the probe PROVED
(rc=0 "Verification SUCCESS") and CPython violates the contract. Suspect (h) (isinstance narrowing for a field-wise
`__eq__(self, o: object)`, #403's over-refusal) is NOT addressed (optional; not cheap: see Residuals).

```
#417a  `[1, 2] * 3` lowered to `Array.make 3 1` (length 3, CPython 6); `[] * 3` to `Array.make 3 0` (CPython 0)
       a1 len(xs) == 3 / a2 xs[1] == 1 / a5 len([] * 3) == 3                               PROVED, CPython 6 / 2 / 0
#417b  `(0,) * 3` -> `(0) * 3` (Why3 INT multiplication)
       b1 `if (0,) * 3: return 1` -> \result == 0;  b4 `3 * (0,)` the same;  b2 `(1,) * n` returned as `n`
                                                                                            PROVED, CPython 1 / 1 / a tuple
#417c  contract "a\nb" reached the model as backslash + n (the raw token text)
       c1 `ensures \result == "a\nb"` of `return "a\\nb"`; c3 `"\n"` vs `"\\n"`               PROVED, CPython False
#417d  list(range(n)) / sorted(range(n)), requires n >= 0, no_exception \all, n = 10**20     PROVED, CPython OverflowError
       (`for x in sorted(range(n))` erased the iterable to `(any int)`)
#417e  x = float(n), no_exception \all, n = 10**400                                          PROVED, CPython OverflowError
#417f  setattr(self, "x", [1]) in __init__, then {r.x} under no_exception \all               PROVED, CPython TypeError
#417g  {shlex.split("a b")} / {split("a b"): 1} under no_exception \all                       PROVED, CPython TypeError
#417a' xs = [*range(n)] lowered to a ONE-element list: len(xs) == 1                         PROVED, CPython n
```

## REPAIR (executor r417, completed by r417b, driver run #3, 2026-10-27, off 930d68ed5; annotations §7.80-§7.83, translational §T.6.91-§T.6.94)

- (a)+(b) `_handle_binop`: `*` with a list display of length != 1 on the left, or a tuple display on either side, is
  REFUSED (NEW `PYCSL-R417-SEQUENCE-REPEAT`); `[x] * n` keeps its lowering (and #414's bound). Polarity: only the modelled
  shape is admitted. (a') `ArrayLit` with a `Starred` element: a fresh unconstrained `(any (array int))` in a body (the
  contract grammar cannot spell `*x`; `any` is not a logic term).
- (c) `_ContractParser._parse_atom_primary` (mirror twin `\trusted`): a contract `STRING` token is decoded with
  `ast.literal_eval` (Python's escape semantics, as the body literal); an undecodable escape is a contract syntax error.
- (d) `_handle_call_expr` (mirror twin `\trusted`): under `\all`, `list(range(..))` / `sorted(range(..))` wrap the range
  argument with #414's operand bound (`stop <= 2**63 - 1`, ...). `_classify_iterable` (twin `\trusted`): when the int
  coercion of a `for` iterable drops a term carrying an `OverflowError reachable` assertion, the assertions are
  materialised in a `let` before the loop (Python evaluates the iterable once, there). `tuple(range(10**20))` raises
  MemoryError (measured), not OverflowError: not modelled (#414's decision).
- (e) `_handle_call_expr`: under `\all`, `float(x)` with `x` int-read owes `-DBL_MAX <= x <= DBL_MAX` (#413's literal,
  `x` let-bound once); str / float / bool reads owe nothing; any other argument is REFUSED (NEW
  `PYCSL-R417-UNCHECKED-FLOAT-CONVERSION`, witness 6113 `float(g(n))`).
- (d)+(e) ERASED obligations: every obligation carries `[@r417_<h>]` (h = hash of the call's IR) and its tag is appended
  to the driver-owned list `transpiler.r417_obls`; after `transpile()` `_run_pipeline` REFUSES (NEW
  `PYCSL-R417-ERASED-OBLIGATION`) a tag occurring fewer than max(1, n_src) times, n_src = the calls of the IR with that tag.
  r417b found the salvaged presence-only check unsound: textually identical calls share a tag, so a KEPT twin hid an
  ERASED occurrence (6116: bounded `for x in sorted(range(n))` + unbounded `set(sorted(range(n)))`; 6117: guarded
  `float(n)` + `isinstance(float(n), float)`; both PROVED at base AND at r417's salvaged candidate d4e3ed21a, CPython
  OverflowError). r417b also replaced r417's `self._r417_obls = ..` transpiler-field write (assigns-underdeclaration
  TRAP 4 > 3) by the driver-owned list, and r417's nested recursive `_ir417` helper (mirror-coverage 550 > 549) by an
  inline worklist.
- (f) `_run_pipeline` (twin `\trusted`): `_sa417`, the attribute names written by a CONSTANT-name dynamic store anywhere in
  the file (`setattr(o, "x", v)`, `o.__setattr__("x", v)`, `object.__setattr__(o, "x", v)`, `o.__dict__["x"] = v`,
  `vars(o)["x"] = v`); a hashed field / class-attribute read of such a name is `#UNK` (`PYCSL-R349-UNHASHABLE-RECORD`).
- (g) `_run_pipeline`: a call whose callee resolves (`_nd409`) to a callable standard-library object that is not a class
  and not a `builtins` name has the class of a fixed allow-list `_hr417` (functions that always return a hashable str /
  int / float / bool: `os.getcwd`, `os.path.join` / `basename` / ..., `shlex.quote` / `join`, `re.escape`, `json.dumps`,
  `math.sqrt` / ..., `time.time`, ...) and is `#UNK` otherwise.

Witnesses (corpus, expected FAIL; every one PROVED rc=0 at base 930d68ed5 and is violated under CPython):
6100-6105 (a/b) REFUSED, 6106-6107 (c) FAIL, 6108-6110 (d/e) FAIL, 6111 (f) REFUSED, 6112 (g) REFUSED, 6113 (e) REFUSED,
6114 (a') FAIL, 6115-6117 (erased) REFUSED. Controls (expected PASS, PROVED at base and candidate): 6118 (kept twins),
6120 (a), 6121 (c), 6122 (d), 6123 (e), 6124 (f), 6125 (g).

## MEASUREMENTS (r417b, final candidate = commit 097e71f89 + docs; base worktree at 930d68ed5; logs and probe files in
`getting-better/systematic-soundness-r3/r417b/`)

- byte-diff (chunked, resumable replica of `bin/byte-diff-sweep.sh`, same commands, cwd = tree root): root 2484 -> 2497
  .mlw, 3 MOVED, 0 GONE, 0 APPEARED, 13 new emitting sources (`cmp-root.log`); pyref 2186 -> 2186, 0 / 0 / 0
  (`cmp-pyref.log`). M1: the 3 MOVED (3570 / 3571 / 3575, route #299 hval starred lists) lose ONE unused `val py_range_1`
  declaration (the starred element's operand is no longer translated); re-proved: 3570 FAIL -> FAIL, 3571 FAIL -> FAIL
  (both expected FAIL), 3575 PROVED -> PROVED.
- mirrors (`mirror-chunk.sh`, replica of `bin/mirror-emit-sweep.sh`): 53/53, 2 MOVED, 0 GONE, 0 APPEARED: `frontend/
  Module3_Weaver` and `frontend/Module5_IREmitter` gain `exception SyntaxError` / `exception ValueError` (they import the
  live `Module2_Parser`, whose contract-literal decoding catches both). Both type-check (--no-proof rc=0).
  Module3_Weaver whole-file proof: 288 Valid / 0 non-Valid. **OWED: Module5_IREmitter whole-file proof** (3558 lines,
  not run inside the time box; the move is two exception declarations only).
- fidelity (`check-self-annotate-sync.sh && self-annotate-mirror-check.sh`) rc=0 (929 verbatim, 53 in sync).
- fast planes 61/61 green (`planes.log`, chunked replica of `bin/run-soundness-planes.sh` on a pre-emitted shared mirror
  emission; 40 + 21 planes), incl. mirror-coverage 549, assigns-underdeclaration TRAP 3, refusal-witness-coverage
  (325 demonstrated / 5 undemonstrated, ceiling 5), refusal-advice-audited (153 audited, floor 133).
- check-getattr-erasure rc=0; check-clause-survival --emit-dir rc=0 (1464 compared, 10 deficits, all ledgered; base 1457 /
  10); check-assumed-facts --emit-dir rc=0 (88 facts, same families as base: ledger unchanged); check-open-route-carriers
  rc=0 (10 carriers).
- pycsl_lib --no-proof screen: 104 files, 87 rc 0 / 17 rc 1, identical base vs candidate.
- census: 18 new rows (6100-6117 expected-FAIL witnesses) via `_census_row` on absolute paths; every one of the 1589
  existing REFUSAL rows re-measured at base and candidate: byte-identical messages (`refmsg-base-equals-cand.tsv`).
- advice audit: PYCSL-R417-UNCHECKED-FLOAT-CONVERSION and PYCSL-R417-ERASED-OBLIGATION followed and run (FOLLOWABLE;
  `advice/`); SEQUENCE-REPEAT carries no advice the audit recognises.
- `\trusted` markers: 445 at base and candidate (no mirror file changed; no new axiom, no new def in a mirrored file).

## RESIDUALS (honest)

- (f) a NON-constant-name dynamic store: `setattr(self, nm, [1])` then `{r.x}` still PROVES `no_exception \all` (CPython
  TypeError; probe `probes/q09_setattr_dyn.py`, PROVED at base and candidate). Folding it in GONEs the
  `frontend/pure_ast.py` mirror (route #406's measurement). OPEN.
- (d)+(e) the erased-obligation count can be masked if the emitter DUPLICATES a kept term (two `[@t]` for one source
  occurrence) while a textual twin is erased in the same file; not observed, not excluded.
- (c) a decoded contract literal with a non-printable / `"` / `\` character inherits route #411's Why3 -> Z3 `\xHH`
  encoding issue exactly as a body literal does (both sides now agree; lengths do not, see #411).
- (g) the allow-list covers resolvable standard-library modules only (`_OKM381`); a callee of an unresolvable module keeps
  its previous derivation.
- (h) isinstance narrowing for a field-wise `__eq__(self, o: object)` (#403's over-refusal): NOT addressed (an
  over-refusal, not a false proof; not cheap).
- Probes that stayed closed at base and candidate (no false proof): `3 * [1, 2]`, `ys * 3`, `[1] * 2 * 3`, `n * [1]`,
  `sorted(range(n), reverse=True)`, `len(list(range(n)))` (refused); `(*range(n),)`, `{*range(n)}`, `t * 2` of a typed tuple
  (FAIL). `float(n + 1)` and `list(range(0, n, 1))` PROVED at base and FAIL at candidate (`probes/q-base-cand.tsv`).
