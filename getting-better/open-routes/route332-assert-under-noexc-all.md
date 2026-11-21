# OPEN ROUTE #332 — `assert c` IS ERASED EVEN UNDER `#@ no_exception \all` (CPython raises AssertionError)
**Status: REPAIRED (gen #37, 2026-10-24; candidate, r332 executor off e9a499e6 — see REPAIR), was OPEN (2026-10-24), Severity 1.** Found by the r327 executor; driver-reproduced on main (rc=0; CPython raises).
Witness `witnesses-r332/a01_assert_noexc_all.py`: `x = 1; assert x == 2; return 7` with `ensures \result == 7`, `no_exception \all` proves.
`assert` lowers to `()` by design (route #84, annotations §7.1), and AssertionError is outside the Phase-1 KNOWN_EXCEPTIONS set; but since
route #304 `\all` means ANY exception, so a reachable failing assert under `no_exception \all` is a false no-exception claim.
Repair: under `no_exception \all` (and under a named set that includes AssertionError or a base of it: Exception/BaseException), lower
`assert c[, msg]` to a proof obligation `assert { c }` (labelled `no_exception: AssertionError reachable`) — or refuse; elsewhere keep the
documented erasure (partial correctness; python -O). Check `assert` inside loops/branches/methods and with an effectful message.

## REPAIR (2026-10-24, r332 executor off e9a499e6; commits bd0dc43e (code + witnesses + contract-truth names), 4ad3c60e (witness drivers + docs), df884823 (census rows) + route docs)
Inline in `src/pycsl/module6_whyml/statements.py` (`_stmts_to_whyml`, the `AssertStmt` arm) and `src/pycsl/module6_whyml/functions.py`
(`_reset_function_state`: one local `_a332_live`). No new def/field/attribute, no helper; both mirror twins are `\trusted` with an unchanged
`assigns` list (sync 926 verbatim). Ledger 3. No gate loosened.

**Rules.**
1. **Live set.** `_a332_live` = `no_exception \all`, or a named set meeting {AssertionError, Exception, BaseException}. The named arm is
   DEFENSIVE: Module 4 refuses those three names as unknown today (probe p06-p08 / corpus 4396 REFUSED at base and after).
2. **Obligation.** When live, `assert c[, m]` lowers to
   `if <c> then () else assert { [@expl:no_exception: AssertionError reachable] false }`, `<c>` = `_to_bool(_expr_to_whyml(c))`, i.e.
   EXACTLY the `if`-test lowering: program code (its own IndexError/ZeroDivisionError/KeyError triggers are discharged — 4386), Python
   truthiness (`assert xs` -> `Array.length xs <> 0` — 4387). The route #84 effect screen (`PYCSL-M6-ASSERT-EFFECTFUL-TEST`) still runs first,
   so a test that cannot lower as an effect-free term is still refused.
3. **Message.** CPython evaluates `m` only on the failing branch, which the VC proves unreachable, so an effectful message never runs and
   is not translated (4385 FAILS on the obligation; control 4394 with `xs.pop()` as message PROVES). No refusal needed.
4. **Loop-target analyses** (routes #36/#301/#302 in `_reset_function_state`) skipped reads inside an `assert` "because Module 6 drops
   it" (comment there said: "if a Python `assert` ever becomes a real obligation, this line goes with it"). The three skips now apply only
   when NOT live, so a `for` target read in a live assert after its loop gets the havoc/write-back (4388 FAILS; without this the read
   would see the stale pre-loop value).
5. Elsewhere (no `no_exception`, or a named set without AssertionError) the documented erasure (annotations §7.1, `python -O`) is
   byte-identical (4390, 4395).

**Probe table** (probes under the worktree `.r332tmp/pr/`, corpus copies 4380-4396; base = e9a499e6; heavy.sh; CPython ground truth):

| file | shape | CPython | base | after |
|---|---|---|---|---|
| 4380 / a01 witness | `x=1; assert x == 2; return 7`, `\all` | AssertionError | PROVED rc0 | FAIL rc1 (AssertionError reachable) |
| 4381 | failing assert in a `while` body | AssertionError | PROVED | FAIL (same label) |
| 4382 | failing assert on a branch (`g(1)`) | AssertionError | PROVED | FAIL |
| 4383 | failing assert in a method | AssertionError | PROVED | FAIL |
| 4384 | failing assert in a nested def | AssertionError | PROVED | FAIL |
| 4385 | failing assert, effectful msg `xs.pop()` | AssertionError | PROVED | FAIL |
| 4386 | test raises: `assert xs[3] == 0 or True`, len 1 | IndexError | PROVED | FAIL (index bounds) |
| 4387 | `assert xs`, xs maybe empty | AssertionError | PROVED | FAIL |
| 4388 | `for` target read in assert after loop (`i == 5`) | AssertionError | PROVED | FAIL |
| 4389 | true `assert x == 2, "msg"` (control) | 7 | PROVED | PROVED |
| 4390 | failing assert, NO no_exception (control) | AssertionError | PROVED | PROVED (erasure kept) |
| 4391 | true assert on a branch (control) | 1 | PROVED | PROVED |
| 4392 | true assert in a `while` body (control) | 3 | PROVED | PROVED |
| 4393 | `assert xs` under `requires len(xs) >= 1` (control) | 7 | PROVED | PROVED |
| 4394 | true assert, effectful msg (control) | 7 | PROVED | PROVED |
| 4395 | failing assert under `no_exception IndexError` (control) | AssertionError | PROVED | PROVED (erasure kept; claim true) |
| 4396 / p06-p08 | `no_exception AssertionError` / `Exception` / `BaseException` | AssertionError | REFUSED (M4) | REFUSED (M4) |
| probe c06 | `for i in range(3)`; `assert i == 2` after loop, `\all` | 7 | PROVED | FAIL (incompleteness: havocked target, fails closed) |

**Census / M1.** Static walk of corpus root, python-reference and the 53 mirror files: 150 functions under `no_exception \all`, ZERO of
them contain an `assert` (outside the new witnesses). Measured accordingly: corpus root 0 MOVED / 0 GONE / 0 APPEARED (2197/2197),
pyref 0/0/0 (2186/2186), mirror 0/0/0 (53/53). No latent false proof, no mirror mover, nothing OWED.

**Gates** (logs in the worktree `.r332tmp/`, all heavy jobs via heavy.sh): witnesses/controls table above; byte-diff-compare root rc=0,
pyref `--min-files 2000` rc=0; mirror-emit-sweep base/after rc=0, compare `--min-files 50` rc=0; check-self-annotate-sync.sh rc=0 (926
verbatim); self-annotate-mirror-check.sh rc=0 (53); run-soundness-planes.sh fast 61/61 rc=0; doc-coherency --check rc=0;
check-assumed-facts rc=0; check-trusted-raises-honesty rc=0 (61 silent, ratchet 61); check-refusal-witness-coverage rc=0 (276
demonstrated / 5); check-dropped-mutation rc=0 (0 dropped); check-corpus-contract-truth rc=0 (4390/4395 named in NEVER_RETURNS with the
§7.1 reason — deliberately-raising erasure controls), -args rc=0, check-corpus-executes rc=0. Census rows for 4380-4388 (VERIFY-FAIL) and
4396 (REFUSAL) measured by `_census_row`. `--slow` planes not run.
Docs: annotations §7.1 (pointer) + §7.19; translational §T.5.8 (pointer) + §T.6.30.

**Residuals.** (a) An assert over a `for` target after its loop no longer proves under `\all` (probe c06): the target is havocked by
route #36 — sound, incomplete. (b) The named-set arm is unreachable until Module 4 admits AssertionError/Exception/BaseException
names. (c) `try: ... except AssertionError` around an assert stays refused (route 16) everywhere; under `\all` it could now be modelled
as an explicit raise — not attempted.

